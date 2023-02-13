#!/bin/bash

set -e

script_dir=$(dirname "$0")

mv $script_dir/../logs/latest.log $script_dir/../logs/$(date '+%Y-%m-%d').log
touch $script_dir/../logs/latest.log