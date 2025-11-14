#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-python3}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Python runtime not found in PATH. Set PYTHON_BIN to a working interpreter."
  exit 1
fi

if [[ -d ".venv" ]]; then
  echo "Using existing .venv"
else
  "$PYTHON_BIN" -m venv .venv
fi

source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "Environment ready. Activate with 'source .venv/bin/activate'."
