#!/bin/bash
echo "========================================"
echo "   Stormy AI - One-Click Installer"
echo "========================================"
echo

# Install system dependencies (optional, for VLC)
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv vlc ffmpeg

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.8+"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "Failed to create virtual environment."
    exit 1
fi

# Activate and install dependencies
echo "Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Failed to install dependencies."
    exit 1
fi

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
