@echo off
REM Run tests and start/stop app
start /B python app.py
REM Wait a second for the server to start
ping -n 2 127.0.0.1 >nul
pytest -q
REM Try to kill all python.exe processes (be careful in multi-python environments)
taskkill /IM python.exe /F >nul 2>&1
exit /B %ERRORLEVEL%
