#!/bin/bash
echo "========================================"
echo "   Stormy AI - One-Click Installer"
echo "========================================"
echo

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Installing..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv
fi

# Install system dependencies
echo "Installing system dependencies..."
sudo apt update
sudo apt install -y vlc ffmpeg git curl

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check for .env file
if [ ! -f .env ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
    echo "Please edit .env to add your API keys."
fi

echo
echo "Installation complete!"
echo
echo "To start Stormy, run: ./run_web.sh"
echo "Then open http://localhost:5000 in your browser."
echo
