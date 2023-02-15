#!/usr/bin/bash
 
set -e

home="$(dirname "$0")/.."
source $home/.env
python=python$PYTHON_VERSION

mkdir $home/.venv
$python -m venv $home/.venv

source $home/.venv/bin/activate
pip install -r $home/requirements.txt
sudo apt install ffmpeg -y