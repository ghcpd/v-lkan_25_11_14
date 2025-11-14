@echo off
setlocal enabledelayedexpansion

echo.
echo ========================================
echo User Management Dashboard - Tests
echo ========================================
echo.

REM Activate virtual environment
if exist venv (
    call venv\Scripts\activate.bat
) else (
    echo Error: Virtual environment not found
    echo Please run setup.bat first
    exit /b 1
)

echo [1] Running Unit Tests...
echo.
python -m pytest tests/ -v 2>nul || python -m unittest discover -s tests -p "test_*.py" -v

echo.
echo [2] Starting Flask Application...
echo.
echo Flask app is starting on http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

python run.py
