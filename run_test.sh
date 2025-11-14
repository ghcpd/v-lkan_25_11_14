#!/usr/bin/env bash
set -euo pipefail

if [[ -f ".venv/bin/activate" ]]; then
  # prefer the project virtual environment when available
  source .venv/bin/activate
fi

echo "Running backend and UI tests..."
python -m pytest tests
