@echo off
title Stormy AI Universal Deployment
echo =====================================
echo    Stormy AI Universal Deployment
echo =====================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check Python version
python -c "import sys; exit(0) if sys.version_info >= (3,8) else exit(1)" >nul 2>&1
if errorlevel 1 (
    echo Python 3.8 or higher is required.
    pause
    exit /b 1
)

REM Clone repo if not exists
if not exist stormy-ai (
    echo Cloning Stormy AI repository...
    git clone https://github.com/yourusername/stormy-ai.git
    cd stormy-ai
) else (
    cd stormy-ai
    echo Repository exists, updating...
    git pull
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
call venv\Scripts\activate

REM Install dependencies
echo Installing Python dependencies...
pip install --upgrade pip
pip install -r requirements.txt

REM Create .env if missing
if not exist .env (
    echo Creating .env from template...
    copy .env.example .env
    echo Please edit .env to add your API keys.
)

REM Menu
echo.
echo Select deployment target:
echo 1) Local installation (run on this machine)
echo 2) Netlify (frontend only)
echo 3) Oracle Cloud (full backend)
echo 4) Docker (local container)
echo 5) Exit
set /p choice="Enter choice [1-5]: "

if "%choice%"=="1" (
    echo Starting Stormy AI web server on http://localhost:5000
    python -m stormy.api.routes
)
if "%choice%"=="2" (
    echo Preparing Netlify deployment...
    pip install frozen-flask
    python freeze.py
    echo Static site generated in build folder.
    echo You can manually deploy to Netlify.
)
if "%choice%"=="3" (
    echo Oracle Cloud deployment requires manual steps.
    echo See documentation for details.
)
if "%choice%"=="4" (
    echo Building and running Docker container...
    docker-compose up -d
)
if "%choice%"=="5" exit /b 0

pause
