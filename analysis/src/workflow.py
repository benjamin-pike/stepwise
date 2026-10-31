from dagster import (
    AssetKey,
    AssetSelection,
    Definitions,
    Nothing,
    asset,
    define_asset_job,
    multiprocess_executor,
)

from analysis.src.execution import run_notebook
from paths import paths

NOTEBOOKS = {
    'walkability/validation': [],
    'walkability/structure': [],
    'walkability/geography': [],
    'associations/primary': [],
    'associations/nonlinearity': [],
    'associations/interactions': [],
    'sensitivity/diagnostics': ['associations/primary'],
    'spatial/dependence': [],
    'spatial/boroughs': [],
    'spatial/radial': ['walkability/geography'],
    'spatial/conditional_null': ['walkability/geography'],
    'sensitivity/index': [],
    'sensitivity/walkshed': [],
    'sensitivity/qof': [],
    'spatial/cross_validation': [],
    'results/figures': [
        'walkability/geography',
        'associations/primary',
        'associations/nonlinearity',
        'spatial/dependence',
        'spatial/boroughs',
        'spatial/conditional_null',
        'spatial/cross_validation',
    ],
    'results/tables': [
        'associations/primary',
        'spatial/boroughs',
        'spatial/radial',
        'spatial/dependence',
        'spatial/conditional_null',
        'spatial/cross_validation',
    ],
    'results/accompanying': [
        'walkability/validation',
        'walkability/structure',
        'walkability/geography',
        'associations/primary',
        'associations/nonlinearity',
        'associations/interactions',
        'sensitivity/diagnostics',
        'spatial/dependence',
        'spatial/boroughs',
        'spatial/radial',
        'spatial/conditional_null',
        'sensitivity/index',
        'sensitivity/walkshed',
        'sensitivity/qof',
        'spatial/cross_validation',
    ],
}


def notebook_asset(name, dependencies):
    notebook = paths.analysis.notebooks[name]
    group = notebook.parent.name if notebook.parent.name != 'notebooks' else notebook.stem

    @asset(
        key = AssetKey(name.split('/')),
        deps = [AssetKey(parent.split('/')) for parent in dependencies],
        group_name = group,
        dagster_type = Nothing,
    )
    def execute(context):
        output = run_notebook(name, context)
        context.add_output_metadata({'executed_notebook': str(output)})

    return execute


defs = Definitions(
    assets = [
        notebook_asset(name, parents)
        for name, parents in NOTEBOOKS.items()
    ],
    jobs = [
        define_asset_job(
            'study',
            selection = AssetSelection.assets(
                *[AssetKey(name.split('/')) for name in NOTEBOOKS]
            ),
        ),
    ],
    executor = multiprocess_executor.configured({'max_concurrent': 3}),
)
