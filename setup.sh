#!/usr/bin/env bash
# Setup script: create a venv and install dependencies
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "Setup complete. Activate with: source venv/bin/activate"