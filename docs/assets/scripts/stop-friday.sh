#!/bin/sh
set -eu
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
: "${FRIDAY_PYTHON:=python3}"
: "${FRIDAY_SERVICE_CONFIG:=$script_dir/services.local.json}"
exec "$FRIDAY_PYTHON" "$script_dir/friday-services.py" stop --config "$FRIDAY_SERVICE_CONFIG" "$@"
