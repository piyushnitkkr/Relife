#!/bin/bash
# ============================================================
# ReLife AI — EC2 Deployment Script (Amazon Linux 2 / t2.micro)
# Run this on a fresh EC2 instance
# ============================================================

set -e

echo "🌿 ReLife AI — Setting up EC2 instance..."

# Update system
sudo yum update -y
sudo yum install -y git python3.11 python3.11-pip

# Clone repo (or upload via scp)
# git clone <your-repo-url> /home/ec2-user/relife-ai
cd /home/ec2-user/relife-ai/server

# Install Python dependencies
pip3.11 install -r requirements.txt

# Copy your .env file (uploaded separately via scp)
# scp .env ec2-user@<ip>:/home/ec2-user/relife-ai/server/.env

# Create ML models directory
mkdir -p ml/models

# Create systemd service for auto-restart
sudo tee /etc/systemd/system/relife-ai.service > /dev/null <<EOF
[Unit]
Description=ReLife AI FastAPI Server
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/relife-ai/server
ExecStart=/usr/local/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3
Environment=PATH=/usr/local/bin:/usr/bin

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable relife-ai
sudo systemctl start relife-ai

echo "✅ ReLife AI running on port 8000"
echo "   Health check: curl http://localhost:8000/health"
