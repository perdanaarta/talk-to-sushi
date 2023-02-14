#!/usr/bin/bash

set -e

home="$(dirname "$0")/.."
log_dir=$home/logs

mv $log_dir/latest.log $log_dir/$(date '+%Y-%m-%d').log
touch $log_dir/latest.log