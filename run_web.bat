@echo off
call venv\Scripts\activate
python -m stormy.api.routes
pause
