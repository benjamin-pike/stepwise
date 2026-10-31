import os
import sys

from paths import paths


def main():
    environment = os.environ.copy()
    environment.setdefault('DAGSTER_HOME', str(paths.analysis.dagster))
    
    paths.analysis.dagster.mkdir(parents = True, exist_ok = True)
    os.chdir(paths.analysis.directory)
    
    arguments = [
        sys.executable,
        '-m',
        'dagster',
        'dev',
        '-f',
        str(paths.analysis.workflow),
        '--host',
        '127.0.0.1',
        '--port',
        '3001',
        *sys.argv[1:]
    ]
    os.execve(sys.executable, arguments, environment)


if __name__ == '__main__':
    main()
