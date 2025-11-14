#!/usr/bin/env bash
set -euo pipefail

if [ ! -d .venv ]; then
    echo "Virtual environment not found. Run ./setup.sh first." >&2
    exit 1
fi

. .venv/bin/activate
pytest -q
