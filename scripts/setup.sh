#!/usr/bin/bash
 
set -e

home="$(dirname "$0")/.."
source $home/.env
python=python$PYTHON_VERSION

mkdir $home/.venv
$python -m venv $home/.venv