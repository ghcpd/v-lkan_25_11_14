#!/usr/bin/env bash
set -e

if [ ! -d "venv" ]; then
  python -m venv venv
fi
. venv/bin/activate
pip install -r requirements.txt

# Start the server in the background
python app.py &
SERVER_PID=$!
sleep 1

# Run pytest
pytest -q

kill $SERVER_PID || true

echo "All tests passed"
