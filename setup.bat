@echo off
setlocal enabledelayedexpansion

echo.
echo ========================================
echo User Management Dashboard - Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    exit /b 1
)

echo [1/4] Python found: 
python --version

echo.
echo [2/4] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists. Skipping...
) else (
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        exit /b 1
    )
    echo Virtual environment created successfully
)

echo.
echo [3/4] Activating virtual environment and installing dependencies...
call venv\Scripts\activate.bat

python -m pip install --upgrade pip setuptools wheel >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Warning: Could not upgrade pip, continuing anyway...
)

pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    exit /b 1
)

echo Dependencies installed successfully
echo.
echo [4/4] Initializing application...
python -c "from app.models import UserDatabase; UserDatabase.init_db(); print('Database initialized successfully')"

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To run the application, execute:
echo   setup.bat (to activate environment)
echo   python run.py
echo.
echo Then open http://localhost:5000 in your browser
echo.
