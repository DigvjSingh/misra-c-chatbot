@echo off
python -m venv .venv
call .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller
pyinstaller --onefile --noconsole app.py
pause
