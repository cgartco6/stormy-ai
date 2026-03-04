#!/bin/bash
# oracle-deploy.sh – run on fresh Oracle Cloud Ubuntu VM
set -e
echo "🚀 Deploying Stormy AI on Oracle Cloud..."

sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv vlc ffmpeg git

git clone https://github.com/yourusername/stormy-ai.git
cd stormy-ai

./install_linux.sh  # runs the Linux installer

# Configure firewall
sudo ufw allow 5000

# Create systemd service for auto-start
sudo tee /etc/systemd/system/stormy.service > /dev/null <<EOF
[Unit]
Description=Stormy AI
After=network.target

[Service]
User=$USER
WorkingDirectory=$PWD
ExecStart=$PWD/venv/bin/python -m stormy.api.routes
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable stormy
sudo systemctl start stormy

echo "✅ Stormy AI deployed!"
echo "🌐 Access at: http://$(curl -s ifconfig.me):5000"
