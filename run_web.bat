@echo off
REM Change to the directory of this batch file
cd /d "%~dp0"

REM Activate virtual environment
call venv\Scripts\activate

REM Run the Flask app
python -m stormy.api.routes
pause
