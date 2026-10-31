#!/usr/bin/env bash
set -euo pipefail

python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e .

exec python -m preprocessing.src.launch "$@"
