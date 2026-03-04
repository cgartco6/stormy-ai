#!/bin/bash
#
# Stormy AI - Universal Deployment Script
# Supports: local install, Netlify (frontend), Oracle Cloud (full)
#

set -e  # Exit on error

# Color codes for pretty output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# Detect OS
detect_os() {
    case "$(uname -s)" in
        Linux*)     OS="linux";;
        Darwin*)    OS="macos";;
        *)          error "Unsupported OS: $(uname -s)";;
    esac
    info "Detected OS: $OS"
}

# Check for Python 3.8+
check_python() {
    if command -v python3 &>/dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
            info "Python $PYTHON_VERSION found"
            return 0
        fi
    fi
    error "Python 3.8+ required. Please install Python 3.8 or higher."
}

# Install system dependencies (Linux/macOS)
install_system_deps() {
    info "Installing system dependencies..."
    if [ "$OS" = "linux" ]; then
        if command -v apt &>/dev/null; then
            sudo apt update
            sudo apt install -y python3-pip python3-venv vlc ffmpeg git curl
        elif command -v yum &>/dev/null; then
            sudo yum install -y python3-pip vlc ffmpeg git curl
        else
            warn "Unknown package manager. Please install manually: python3-pip, vlc, ffmpeg, git"
        fi
    elif [ "$OS" = "macos" ]; then
        if command -v brew &>/dev/null; then
            brew install python@3.10 vlc ffmpeg git
        else
            warn "Homebrew not found. Please install manually: Python 3, VLC, ffmpeg, git"
        fi
    fi
}

# Clone repository (if not already in it)
clone_repo() {
    if [ ! -d "stormy-ai" ]; then
        info "Cloning Stormy AI repository..."
        git clone https://github.com/yourusername/stormy-ai.git
        cd stormy-ai
    else
        cd stormy-ai
        info "Repository already exists, updating..."
        git pull
    fi
}

# Setup virtual environment and install Python dependencies
setup_venv() {
    info "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    success "Virtual environment ready"
}

# Configure environment variables
configure_env() {
    if [ ! -f .env ]; then
        info "Creating .env file from template..."
        cp .env.example .env
        warn "Please edit .env to add your API keys (OpenAI, Twilio, etc.)"
        if [ "$1" != "--non-interactive" ]; then
            read -p "Press Enter to continue after editing .env (or Ctrl+C to exit)..."
        fi
    else
        info ".env already exists, skipping"
    fi
}

# Local web server launch
run_local() {
    info "Starting Stormy AI web server on http://localhost:5000"
    source venv/bin/activate
    python -m stormy.api.routes
}

# Netlify deployment (frontend only)
deploy_netlify() {
    info "Preparing for Netlify deployment (frontend-only)..."
    source venv/bin/activate
    pip install frozen-flask
    python freeze.py  # expects freeze.py in root
    if [ ! -d "build" ]; then
        error "Freeze failed: build directory not found"
    fi
    info "Static site generated in ./build"
    if command -v netlify &>/dev/null; then
        netlify deploy --dir=build --prod
    else
        warn "Netlify CLI not installed. Install with: npm install -g netlify-cli"
        info "You can manually deploy the 'build' folder to Netlify."
    fi
}

# Oracle Cloud deployment (full backend)
deploy_oracle() {
    info "Deploying to Oracle Cloud Free Tier..."
    # This assumes you have an Oracle Cloud account and CLI configured
    # Alternatively, provide SSH-based deployment
    warn "Oracle Cloud deployment requires manual steps:"
    echo "1. Create an Ubuntu VM on Oracle Cloud (free tier)"
    echo "2. SSH into the VM and run:"
    echo "   curl -sL https://raw.githubusercontent.com/yourusername/stormy-ai/main/oracle-deploy.sh | bash"
    echo "3. Open port 5000 in security list"
    echo "4. Access your Stormy at http://<public-ip>:5000"
    read -p "Press Enter when ready to continue with local setup (or Ctrl+C)..." 
    # Optionally, automate with oci CLI and ansible (advanced)
}

# Docker deployment
deploy_docker() {
    info "Building and running Docker container..."
    docker-compose up -d
    success "Docker container running on http://localhost:5000"
}

# Main menu
main() {
    echo "====================================="
    echo "   Stormy AI Universal Deployment   "
    echo "====================================="
    echo "Select deployment target:"
    echo "1) Local installation (run on this machine)"
    echo "2) Netlify (frontend only)"
    echo "3) Oracle Cloud (full backend)"
    echo "4) Docker (local container)"
    echo "5) Exit"
    read -p "Enter choice [1-5]: " choice

    detect_os
    check_python
    install_system_deps
    clone_repo
    setup_venv
    configure_env

    case $choice in
        1) run_local ;;
        2) deploy_netlify ;;
        3) deploy_oracle ;;
        4) deploy_docker ;;
        5) exit 0 ;;
        *) error "Invalid choice" ;;
    esac
}

# Run main
main
