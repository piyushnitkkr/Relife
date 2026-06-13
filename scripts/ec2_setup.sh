#!/bin/bash
# ============================================================
# ReLife AI — One-command EC2 Setup
# Run on a fresh Amazon Linux 2023 / Ubuntu EC2 t2.micro
#
# Usage:
#   chmod +x scripts/ec2_setup.sh
#   ./scripts/ec2_setup.sh
# ============================================================

set -e

echo "🌿 ReLife AI — EC2 Setup Starting..."

# Install Docker
if ! command -v docker &> /dev/null; then
    echo "📦 Installing Docker..."
    sudo yum update -y 2>/dev/null || sudo apt-get update -y
    sudo yum install -y docker 2>/dev/null || sudo apt-get install -y docker.io
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker $USER
    echo "⚠️  Log out and back in for docker group to take effect, then re-run this script."
    exit 0
fi

# Install Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "📦 Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
        -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Build and start
echo "🔨 Building containers..."
docker compose build

echo "🚀 Starting ReLife AI..."
docker compose up -d

echo ""
echo "============================================================"
echo "✅ ReLife AI is running!"
echo ""
echo "   Frontend:  http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8080"
echo "   API:       http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):80"
echo "   Health:    http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):80/health"
echo ""
echo "   Logs:      docker compose logs -f"
echo "   Stop:      docker compose down"
echo "   Restart:   docker compose restart"
echo "============================================================"
