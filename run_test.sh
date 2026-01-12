#!/bin/bash

set -e

echo ""
echo "========================================"
echo "User Management Dashboard - Tests"
echo "========================================"
echo ""

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Error: Virtual environment not found"
    echo "Please run setup.sh first"
    exit 1
fi

echo "[1] Running Unit Tests..."
echo ""
python -m pytest tests/ -v 2>/dev/null || python -m unittest discover -s tests -p "test_*.py" -v

echo ""
echo "[2] Starting Flask Application..."
echo ""
echo "Flask app is starting on http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""

python run.py
