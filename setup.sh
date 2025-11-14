#!/bin/bash

set -e

echo ""
echo "========================================"
echo "User Management Dashboard - Setup"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.8+ from https://www.python.org/"
    exit 1
fi

echo "[1/4] Python found:"
python3 --version

echo ""
echo "[2/4] Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists. Skipping..."
else
    python3 -m venv venv
    echo "Virtual environment created successfully"
fi

echo ""
echo "[3/4] Activating virtual environment and installing dependencies..."
source venv/bin/activate

python -m pip install --upgrade pip setuptools wheel > /dev/null 2>&1 || echo "Warning: Could not upgrade pip"

pip install -r requirements.txt

echo "Dependencies installed successfully"

echo ""
echo "[4/4] Initializing application..."
python -c "from app.models import UserDatabase; UserDatabase.init_db(); print('Database initialized successfully')"

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "To run the application, execute:"
echo "  source venv/bin/activate"
echo "  python run.py"
echo ""
echo "Then open http://localhost:5000 in your browser"
echo ""
