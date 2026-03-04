#!/bin/bash
echo "========================================"
echo "   Stormy AI - One-Click Installer"
echo "========================================"
echo

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.8+ from https://python.org"
    exit 1
fi

# Check Python version
PY_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d. -f1-2)
if (( $(echo "$PY_VERSION < 3.8" | bc -l) )); then
    echo "Python 3.8+ required. Found $PY_VERSION"
    exit 1
fi

# Install Homebrew if missing (for VLC, ffmpeg)
if ! command -v brew &> /dev/null; then
    echo "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Install system dependencies
echo "Installing system dependencies..."
brew install vlc ffmpeg git

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install -e

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
