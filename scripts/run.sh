#!/bin/bash

home="$(dirname "$0")/.."

source $home/.venv/bin/activate
python3.10 $home/src/main.py