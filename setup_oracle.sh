#!/bin/bash
################################################################################
# HOLLY Fish-Speech TTS - Oracle Cloud Setup Script
# 
# This script sets up Fish-Speech-1.5 TTS on Oracle Cloud Free Tier
# Run this on a fresh Ubuntu 22.04 VM
#
# Usage: bash setup_oracle.sh
################################################################################

set -e  # Exit on error

echo "========================================================================"
echo "🎤 HOLLY Fish-Speech TTS - Oracle Cloud Setup"
echo "========================================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    print_error "Please do not run as root. Run as ubuntu user."
    exit 1
fi

print_status "Starting setup..."

# Step 1: Update system
print_status "Step 1/8: Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Step 2: Install Python 3.11
print_status "Step 2/8: Installing Python 3.11..."
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# Step 3: Install system dependencies
print_status "Step 3/8: Installing system dependencies..."
sudo apt-get install -y \
    git \
    wget \
    curl \
    build-essential \
    libsndfile1 \
    ffmpeg \
    nginx

# Step 4: Clone repository
print_status "Step 4/8: Cloning HOLLY Fish-Speech TTS repository..."
cd ~
if [ -d "holly-fish-tts" ]; then
    print_warning "Directory exists, pulling latest..."
    cd holly-fish-tts
    git pull
else
    git clone https://github.com/iamhollywoodpro/holly-fish-tts.git
    cd holly-fish-tts
fi

# Step 5: Create Python virtual environment
print_status "Step 5/8: Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Step 6: Install Python dependencies
print_status "Step 6/8: Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Note: Fish-Speech requires additional setup
print_warning "Installing Fish-Speech-1.5 (this may take 5-10 minutes)..."
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install git+https://github.com/fishaudio/fish-speech.git

# Step 7: Create systemd service
print_status "Step 7/8: Creating systemd service..."
sudo tee /etc/systemd/system/holly-tts.service > /dev/null <<EOF
[Unit]
Description=HOLLY Fish-Speech TTS API
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$HOME/holly-fish-tts
Environment="PATH=$HOME/holly-fish-tts/venv/bin"
ExecStart=$HOME/holly-fish-tts/venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Step 8: Configure Nginx reverse proxy
print_status "Step 8/8: Configuring Nginx..."
sudo tee /etc/nginx/sites-available/holly-tts > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts for long-running TTS generation
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/holly-tts /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# Start the service
print_status "Starting HOLLY TTS service..."
sudo systemctl daemon-reload
sudo systemctl enable holly-tts
sudo systemctl start holly-tts

# Wait for service to start
sleep 5

# Check service status
if sudo systemctl is-active --quiet holly-tts; then
    print_status "✅ HOLLY TTS service is running!"
else
    print_error "Service failed to start. Check logs with: sudo journalctl -u holly-tts -f"
    exit 1
fi

# Get public IP
PUBLIC_IP=$(curl -s ifconfig.me)

echo ""
echo "========================================================================"
echo "🎉 SETUP COMPLETE!"
echo "========================================================================"
echo ""
echo "Your HOLLY Fish-Speech TTS API is now running at:"
echo ""
echo "  🌐 Public URL: http://$PUBLIC_IP"
echo "  🔗 Health check: http://$PUBLIC_IP/health"
echo "  📊 API docs: http://$PUBLIC_IP/docs"
echo ""
echo "Test it with:"
echo "  curl http://$PUBLIC_IP/health"
echo ""
echo "Generate voice:"
echo "  curl -X POST http://$PUBLIC_IP/generate \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"text\":\"Hello Hollywood! I am HOLLY!\"}' \\"
echo "    --output holly_test.wav"
echo ""
echo "Useful commands:"
echo "  - View logs: sudo journalctl -u holly-tts -f"
echo "  - Restart service: sudo systemctl restart holly-tts"
echo "  - Stop service: sudo systemctl stop holly-tts"
echo ""
print_status "Setup complete! HOLLY is ready to speak! 🎤"
echo "========================================================================"
