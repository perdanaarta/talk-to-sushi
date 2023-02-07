#!/bin/bash

set -e

script_dir=$(dirname "$0")

mv $script_dir/latest.log $script_dir/$(date '+%Y-%m-%d').log
touch $script_dir/latest.log