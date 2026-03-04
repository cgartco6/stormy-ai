@echo off
setlocal enabledelayedexpansion
title Stormy AI Universal Deployment for Windows

echo =====================================
echo    Stormy AI Universal Deployment
echo =====================================
echo.

REM Check if running as administrator (required for some installs)
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo This script needs administrator privileges.
    echo Please right-click and select "Run as administrator".
    pause
    exit /b 1
)

REM Function to check and install Chocolatey (package manager for Windows)
:ensure_choco
where choco >nul 2>&1
if %errorLevel% neq 0 (
    echo Installing Chocolatey package manager...
    @"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "[System.Net.ServicePointManager]::SecurityProtocol = 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"
    if !errorLevel! neq 0 (
        echo Failed to install Chocolatey.
        pause
        exit /b 1
    )
)
goto :eof

REM Install Python 3.10+ via Chocolatey
:install_python
where python >nul 2>&1
if %errorLevel% neq 0 (
    echo Python not found. Installing Python 3.10...
    call :ensure_choco
    choco install python310 -y
    refreshenv
    set "PATH=%PATH%;C:\Python310;C:\Python310\Scripts"
) else (
    python --version | find "3.10" >nul
    if !errorLevel! neq 0 (
        python --version | find "3.11" >nul
        if !errorLevel! neq 0 (
            python --version | find "3.12" >nul
            if !errorLevel! neq 0 (
                echo Python version is too old. Please install Python 3.10+ manually.
                pause
                exit /b 1
            )
        )
    )
    echo Python is already installed.
)
goto :eof

REM Install Node.js (for Netlify CLI)
:install_node
where node >nul 2>&1
if %errorLevel% neq 0 (
    echo Installing Node.js...
    call :ensure_choco
    choco install nodejs-lts -y
    refreshenv
) else (
    echo Node.js already installed.
)
goto :eof

REM Install Git
:install_git
where git >nul 2>&1
if %errorLevel% neq 0 (
    echo Installing Git...
    call :ensure_choco
    choco install git -y
    refreshenv
) else (
    echo Git already installed.
)
goto :eof

REM Install VLC
:install_vlc
where vlc >nul 2>&1
if %errorLevel% neq 0 (
    echo Installing VLC media player...
    call :ensure_choco
    choco install vlc -y
) else (
    echo VLC already installed.
)
goto :eof

REM Clone repository
:clone_repo
if not exist stormy-ai (
    echo Cloning Stormy AI repository...
    git clone https://github.com/yourusername/stormy-ai.git
    cd stormy-ai
) else (
    cd stormy-ai
    echo Repository exists, updating...
    git pull
)
goto :eof

REM Setup virtual environment
:setup_venv
echo Creating virtual environment...
python -m venv venv
call venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
if %errorLevel% neq 0 (
    echo Failed to install Python dependencies.
    pause
    exit /b 1
)
goto :eof

REM Configure .env
:configure_env
if not exist .env (
    echo Creating .env from template...
    copy .env.example .env
    echo Please edit .env to add your API keys (OpenAI, Twilio, etc.)
    pause
) else (
    echo .env already exists.
)
goto :eof

REM Run local server
:run_local
echo Starting Stormy AI web server on http://localhost:5000
call venv\Scripts\activate
python -m stormy.api.routes
goto :eof

REM Netlify deployment
:deploy_netlify
echo Preparing Netlify deployment...
call :install_node
call venv\Scripts\activate
pip install frozen-flask
python freeze.py
if not exist build (
    echo Freeze failed.
    pause
    exit /b 1
)
echo Static site generated in build folder.
where netlify >nul 2>&1
if %errorLevel% neq 0 (
    echo Installing Netlify CLI...
    npm install -g netlify-cli
)
netlify deploy --dir=build --prod
pause
goto :eof

REM Oracle Cloud deployment guide
:deploy_oracle
echo Deploying to Oracle Cloud Free Tier...
echo.
echo Oracle Cloud deployment requires manual steps:
echo 1. Create an Ubuntu VM on Oracle Cloud (free tier: 4 ARM cores, 24GB RAM).
echo 2. SSH into the VM and run:
echo    curl -sL https://raw.githubusercontent.com/yourusername/stormy-ai/main/oracle-deploy.sh ^| bash
echo 3. Open port 5000 in security list.
echo 4. Access Stormy at http://^<public-ip^>:5000
echo.
pause
goto :eof

REM Docker deployment
:deploy_docker
where docker >nul 2>&1
if %errorLevel% neq 0 (
    echo Docker not found. Please install Docker Desktop for Windows first.
    pause
    exit /b 1
)
docker-compose up -d
echo Docker container running on http://localhost:5000
pause
goto :eof

REM Main menu
:main_menu
echo.
echo Select deployment target:
echo 1) Local installation (run on this machine)
echo 2) Netlify (frontend only)
echo 3) Oracle Cloud (full backend)
echo 4) Docker (local container)
echo 5) Exit
set /p choice="Enter choice [1-5]: "

if "%choice%"=="1" set target=local
if "%choice%"=="2" set target=netlify
if "%choice%"=="3" set target=oracle
if "%choice%"=="4" set target=docker
if "%choice%"=="5" exit /b 0

REM Run common setup
call :install_python
call :install_git
call :install_vlc
call :clone_repo
call :setup_venv
call :configure_env

REM Go to selected target
if "%target%"=="local" call :run_local
if "%target%"=="netlify" call :deploy_netlify
if "%target%"=="oracle" call :deploy_oracle
if "%target%"=="docker" call :deploy_docker

pause
goto :eof

REM Start
call :main_menu
