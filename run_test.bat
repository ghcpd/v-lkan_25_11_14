@echo off
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
start /b python app.py
REM Give server a second to spin up
ping -n 2 127.0.0.1 >nul
pytest -q
echo Tests finished
