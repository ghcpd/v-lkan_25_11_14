#!/usr/bin/env bash
set -e

if [ ! -d "venv" ]; then
  python -m venv venv
fi

. venv/bin/activate
pip install -r requirements.txt

echo "Setup complete. To run the app: source venv/bin/activate && python app.py"