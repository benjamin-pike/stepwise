import os
import sys

from paths import paths


def main():
    environment = os.environ.copy()
    environment['DAGSTER_HOME'] = str(paths.preprocessing.dagster)
    environment['PYTHONPATH'] = os.pathsep.join(
        filter(None, [str(paths.root), environment.get('PYTHONPATH')])
    )
    paths.preprocessing.dagster.mkdir(parents = True, exist_ok = True)
    os.chdir(paths.root)
    arguments = [
        sys.executable,
        '-m',
        'dagster',
        'dev',
        '-f',
        str(paths.preprocessing.workflow),
        '--host',
        '127.0.0.1',
        '--port',
        '3000',
        *sys.argv[1:],
    ]
    os.execve(sys.executable, arguments, environment)


if __name__ == '__main__':
    main()
