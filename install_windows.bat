@echo off
title Stormy AI Installer
echo ========================================
echo    Stormy AI - One-Click Installer
echo ========================================
echo.

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo Failed to create virtual environment.
    pause
    exit /b 1
)

REM Activate and install dependencies
echo Installing dependencies...
call venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install dependencies.
    pause
    exit /b 1
)

REM Check for .env file
if not exist .env (
    echo Creating .env file from example...
    copy .env.example .env
    echo Please edit .env to add your API keys.
)

echo.
echo Installation complete!
echo.
echo To start Stormy, run: run_web.bat
echo Then open http://localhost:5000 in your browser.
echo.

pause
