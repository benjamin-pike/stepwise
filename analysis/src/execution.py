import os
import sys

import nbformat
from nbclient import NotebookClient

from paths import paths


def run_notebook(name, context = None):
    notebook = nbformat.read(paths.analysis.notebooks[name], as_version = 4)
    output = paths.analysis.executed[name]
    output.parent.mkdir(parents = True, exist_ok = True)

    for cell in notebook.cells:
        if cell.cell_type == 'code':
            cell.outputs = []
            cell.execution_count = None

    class StudyNotebookClient(NotebookClient):
        def process_message(self, message, cell, cell_index):
            result = super().process_message(message, cell, cell_index)

            if context and message['msg_type'] == 'stream':
                context.log.info(message['content']['text'].rstrip())

            return result

    client = StudyNotebookClient(
        notebook, timeout = None, kernel_name = 'python3', resources = {'metadata': {'path': str(paths.analysis.directory)}}
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

    try:
        environment = os.environ.copy()
        environment['PYTHONPATH'] = os.pathsep.join(filter(None, [str(paths.root), environment.get('PYTHONPATH')]))
        client.execute(env = environment)
    finally:
        nbformat.write(notebook, output)

    return output
