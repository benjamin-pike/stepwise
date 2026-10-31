import os
import sys

import nbformat
from dagster import (
    AssetKey,
    AssetSelection,
    Definitions,
    Nothing,
    asset,
    define_asset_job,
    multiprocess_executor,
)
from nbclient import NotebookClient

from paths import paths, prepare_preprocessing


def run_notebook(name, context = None, *, mode = None):
    prepare_preprocessing()
    source = paths.preprocessing.notebooks[name]
    notebook = nbformat.read(source, as_version = 4)

    if mode is not None:
        output = paths.preprocessing.timetable_executions[mode]
    else:
        output = paths.preprocessing.executed_notebooks[name]

    output.parent.mkdir(parents = True, exist_ok = True)

    for cell in notebook.cells:
        if cell.cell_type == 'code':
            cell.outputs = []
            cell.execution_count = None

    class PreprocessingNotebookClient(NotebookClient):
        def process_message(self, message, cell, cell_index):
            result = super().process_message(message, cell, cell_index)

            if context and message['msg_type'] == 'stream':
                context.log.info(message['content']['text'].rstrip())

            return result

    client = PreprocessingNotebookClient(
        notebook,
        timeout = None,
        kernel_name = 'python3',
        resources = {'metadata': {'path': str(paths.preprocessing.directory)}},
    )

    client.create_kernel_manager().kernel_spec.argv = [
        sys.executable,
        '-m',
        'ipykernel_launcher',
        '-f',
        '{connection_file}'
    ]

    if context:
        client.on_cell_start = lambda cell, cell_index: context.log.info(f'{name}: cell {cell_index + 1}')

    environment = os.environ.copy()
    environment['PYTHONPATH'] = os.pathsep.join(filter(None, [str(paths.root), environment.get('PYTHONPATH')]))

    try:
        client.execute(env = environment)
    finally:
        nbformat.write(notebook, output)

    return output


def notebook_asset(name, dependencies = (), *, notebook = None):
    @asset(
        key = AssetKey(name.split('/')),
        deps = [AssetKey(parent.split('/')) for parent in dependencies],
        group_name = name.split('/')[0],
        dagster_type = Nothing,
    )
    def execute(context):
        output = run_notebook(notebook or name, context)
        context.add_output_metadata({'executed_notebook': str(output)})

    return execute


@asset(key = AssetKey(['preparation', 'inputs']), group_name = 'preparation', dagster_type = Nothing)
def prepared_inputs(context):
    required = {
        'amenity_classifications': paths.preprocessing.shared.grouped_tags,
        'bus_frequencies': paths.preprocessing.transport.bus,
        'rail_frequencies': paths.preprocessing.transport.rail,
        'tfl_frequencies': paths.preprocessing.transport.tfl
    }
    missing = [str(path) for path in required.values() if not path.is_file()]

    if missing:
        raise FileNotFoundError(
            'Missing supplied preprocessing inputs: ' + ', '.join(missing) + '. '
            'Restore these files from Git, or regenerate them with annotator.ipynb and timetables.ipynb '
            'in preprocessing/notebooks/walkability/preparation/.'
        )

    context.add_output_metadata({name: str(path) for name, path in required.items()})


assets = [
    prepared_inputs,
    notebook_asset('walkability/geometry/lsoa', ['preparation/inputs']),
    notebook_asset('walkability/geometry/isochrone', ['walkability/geometry/lsoa']),
    notebook_asset('health/patients', ['preparation/inputs']),
    notebook_asset('health/qof', ['health/patients']),
    notebook_asset('context/imd', ['preparation/inputs']),
    notebook_asset('context/ndvi', ['preparation/inputs']),
    notebook_asset('context/pollution', ['walkability/geometry/lsoa'])
]

components = ('amenities', 'dwellings', 'land_use', 'streets', 'transport')

for component in components:
    assets.append(notebook_asset(f'walkability/components/{component}', ['walkability/geometry/isochrone']))

assets.append(
    notebook_asset(
        'walkability/index',
        [f'walkability/components/{component}' for component in components],
        notebook = 'walkability/walkability',
    )
)

assets.append(
    notebook_asset(
        'results/analysis',
        ['walkability/index']
        + ['health/qof', 'context/imd', 'context/ndvi', 'context/pollution'],
        notebook = 'master',
    )
)

defs = Definitions(
    assets = assets,
    jobs = [define_asset_job('preprocessing', selection = AssetSelection.all())],
    executor = multiprocess_executor.configured({'max_concurrent': 1}),
)
