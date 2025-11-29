#!/bin/bash

# HOLLY Fish-Speech-1.5 TTS - Hetzner Deployment Script
# This script deploys Fish-Speech-1.5 on a fresh Ubuntu 22.04 server

set -e  # Exit on any error

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎤 HOLLY Fish-Speech-1.5 TTS Deployment"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Update system
echo "[1/10] Updating system packages..."
apt-get update -qq
apt-get upgrade -y -qq

# Install dependencies
echo "[2/10] Installing system dependencies..."
apt-get install -y -qq \
    python3.11 \
    python3.11-venv \
    python3-pip \
    git \
    build-essential \
    ffmpeg \
    libsndfile1 \
    curl

# Create application directory
echo "[3/10] Creating application directory..."
mkdir -p /opt/holly-tts
cd /opt/holly-tts

# Create virtual environment
echo "[4/10] Setting up Python virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

# Install Python packages
echo "[5/10] Installing Fish-Speech-1.5..."
cat > requirements.txt << 'REQS'
torch>=2.0.0
transformers>=4.35.0
fish-speech>=1.5.0
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.0.0
numpy>=1.24.0
soundfile>=0.12.0
librosa>=0.10.0
requests>=2.31.0
REQS

pip install --upgrade pip -q
pip install -r requirements.txt -q

# Download application files from GitHub
echo "[6/10] Downloading HOLLY TTS application..."
curl -sL https://raw.githubusercontent.com/iamhollywoodpro/holly-fish-tts/main/app.py -o app.py
curl -sL https://raw.githubusercontent.com/iamhollywoodpro/holly-fish-tts/main/holly_fish_voice.py -o holly_fish_voice.py

# Create systemd service
echo "[7/10] Setting up systemd service..."
cat > /etc/systemd/system/holly-tts.service << 'SERVICE'
[Unit]
Description=HOLLY Fish-Speech-1.5 TTS Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/holly-tts
Environment="PATH=/opt/holly-tts/venv/bin"
ExecStart=/opt/holly-tts/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE

# Configure firewall
echo "[8/10] Configuring firewall..."
ufw allow 22/tcp  # SSH
ufw allow 80/tcp  # HTTP
ufw allow 443/tcp # HTTPS
ufw allow 8000/tcp # TTS API
ufw --force enable

# Start service
echo "[9/10] Starting HOLLY TTS service..."
systemctl daemon-reload
systemctl enable holly-tts
systemctl start holly-tts

# Wait for service to start
echo "[10/10] Waiting for service to start..."
sleep 10

# Get server IP
SERVER_IP=$(curl -s ifconfig.me)

# Test health
echo ""
echo "Testing HOLLY TTS health..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ HOLLY TTS is LIVE!"
else
    echo "⚠️  Waiting for service to fully start..."
    sleep 10
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ HOLLY TTS is LIVE!"
    else
        echo "❌ Service may need more time to download models"
        echo "Check logs: journalctl -u holly-tts -f"
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ DEPLOYMENT COMPLETE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎯 Your HOLLY TTS API:"
echo "   http://$SERVER_IP:8000"
echo ""
echo "🔍 Test endpoints:"
echo "   Health: http://$SERVER_IP:8000/health"
echo "   Voice:  http://$SERVER_IP:8000/generate?text=Hello%20Hollywood"
echo ""
echo "📊 Check logs:"
echo "   journalctl -u holly-tts -f"
echo ""
echo "🎤 HOLLY is ready to speak!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
