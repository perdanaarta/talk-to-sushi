#!/usr/bin/bash
 
set -e

home="$(dirname "$0")/.."
source $home/.env
python=python$PYTHON_VERSION

source $home/.venv/bin/activate
$python $home/src/main.py