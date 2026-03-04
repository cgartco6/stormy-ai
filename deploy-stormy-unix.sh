#!/bin/bash
#
# Stormy AI - Universal Self-Contained Deployment Script for Unix/Linux/macOS
# This script installs all prerequisites and deploys Stormy AI.
#

set -e  # Exit on error

# Color codes
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

# Install Python 3.8+ and pip
install_python() {
    if command -v python3 &>/dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
            info "Python $PYTHON_VERSION already installed"
            return
        else
            warn "Python $PYTHON_VERSION found, but 3.8+ required. Upgrading..."
        fi
    fi

    info "Installing Python 3.8+..."
    if [ "$OS" = "linux" ]; then
        if command -v apt &>/dev/null; then
            sudo apt update
            sudo apt install -y software-properties-common
            sudo add-apt-repository -y ppa:deadsnakes/ppa
            sudo apt update
            sudo apt install -y python3.10 python3.10-venv python3.10-dev python3-pip
            sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
        elif command -v yum &>/dev/null; then
            sudo yum install -y epel-release
            sudo yum install -y python38 python38-devel python38-pip
        else
            error "Unsupported package manager. Please install Python 3.8+ manually."
        fi
    elif [ "$OS" = "macos" ]; then
        if ! command -v brew &>/dev/null; then
            info "Installing Homebrew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
        brew install python@3.10
    fi
}

# Install Node.js and npm (optional, for Netlify CLI)
install_node() {
    if command -v node &>/dev/null && command -v npm &>/dev/null; then
        info "Node.js and npm already installed"
    else
        info "Installing Node.js and npm..."
        if [ "$OS" = "linux" ]; then
            curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
            sudo apt install -y nodejs
        elif [ "$OS" = "macos" ]; then
            brew install node
        fi
    fi
}

# Install system dependencies (VLC, git, curl, etc.)
install_system_deps() {
    info "Installing system dependencies..."
    if [ "$OS" = "linux" ]; then
        if command -v apt &>/dev/null; then
            sudo apt install -y vlc ffmpeg git curl wget
        elif command -v yum &>/dev/null; then
            sudo yum install -y vlc ffmpeg git curl wget
        fi
    elif [ "$OS" = "macos" ]; then
        brew install vlc ffmpeg git curl wget
    fi
}

# Clone repository
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
        read -p "Press Enter to continue after editing .env (or Ctrl+C to exit)..."
    else
        info ".env already exists, skipping"
    fi
}

# Run local web server
run_local() {
    info "Starting Stormy AI web server on http://localhost:5000"
    source venv/bin/activate
    python -m stormy.api.routes
}

# Deploy to Netlify (frontend only)
deploy_netlify() {
    info "Preparing for Netlify deployment..."
    install_node
    source venv/bin/activate
    pip install frozen-flask
    python freeze.py
    if [ ! -d "build" ]; then
        error "Freeze failed: build directory not found"
    fi
    info "Static site generated in ./build"
    if command -v netlify &>/dev/null; then
        netlify deploy --dir=build --prod
    else
        warn "Installing Netlify CLI..."
        npm install -g netlify-cli
        netlify deploy --dir=build --prod
    fi
}

# Oracle Cloud deployment guide
deploy_oracle() {
    info "Deploying to Oracle Cloud Free Tier..."
    warn "Oracle Cloud deployment requires manual steps:"
    echo "1. Create an Ubuntu VM on Oracle Cloud (free tier: 4 ARM cores, 24GB RAM)."
    echo "2. SSH into the VM and run the following commands:"
    echo "   curl -sL https://raw.githubusercontent.com/yourusername/stormy-ai/main/oracle-deploy.sh | bash"
    echo "3. Open port 5000 in the security list."
    echo "4. Access Stormy at http://<public-ip>:5000"
    echo ""
    echo "The oracle-deploy.sh script will automatically install Python, VLC, and dependencies."
}

# Docker deployment
deploy_docker() {
    info "Building and running Docker container..."
    if ! command -v docker &>/dev/null; then
        warn "Docker not installed. Please install Docker first."
        exit 1
    fi
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
    install_python
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
