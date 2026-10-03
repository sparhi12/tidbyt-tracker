#!/usr/bin/env bash
# ==============================================================================
# Tidbyt Flight Tracker - Automated GCP VM Setup Script
# Works on Debian 11/12, Ubuntu 20.04/22.04/24.04 (GCP e2-micro Free Tier)
# ==============================================================================
set -euo pipefail

echo "=========================================================="
echo "  Provisioning Tidbyt Flight Tracker on GCP e2-micro VM   "
echo "=========================================================="

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$APP_DIR"

# 1. Update OS packages & install runtime dependencies
echo "[1/5] Installing system packages..."
sudo apt-get update -y
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    tar \
    libjpeg-dev \
    zlib1g-dev

# 2. Install Pixlet binary (Linux amd64)
if ! command -v pixlet &> /dev/null; then
    echo "[2/5] Downloading and installing Pixlet (Linux amd64)..."
    PIXLET_TAG=$(curl -s https://api.github.com/repos/tidbyt/pixlet/releases/latest | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/' || echo "v0.34.0")
    if [ -z "$PIXLET_TAG" ]; then PIXLET_TAG="v0.34.0"; fi
    PIXLET_VER="${PIXLET_TAG#v}"
    
    TMP_DIR=$(mktemp -d)
    TAR_URL="https://github.com/tidbyt/pixlet/releases/download/${PIXLET_TAG}/pixlet_${PIXLET_VER}_linux_amd64.tar.gz"
    echo "Fetching $TAR_URL..."
    curl -fsSL "$TAR_URL" -o "$TMP_DIR/pixlet.tar.gz"
    tar -xzf "$TMP_DIR/pixlet.tar.gz" -C "$TMP_DIR"
    sudo mv "$TMP_DIR/pixlet" /usr/local/bin/pixlet
    sudo chmod +x /usr/local/bin/pixlet
    rm -rf "$TMP_DIR"
    echo "Pixlet installed successfully: $(pixlet version 2>/dev/null || echo 'ready')"
else
    echo "[2/5] Pixlet is already installed: $(which pixlet)"
fi

# 3. Create Python virtual environment & install requirements
echo "[3/5] Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
venv/bin/pip install --upgrade pip --quiet
venv/bin/pip install -r requirements.txt --quiet
echo "Python dependencies installed."

# 4. Configure .env if not present
if [ ! -f ".env" ]; then
    echo "[4/5] Creating .env from template..."
    cp .env.example .env
    echo "Created .env. IMPORTANT: Please edit .env with your Tidbyt credentials!"
else
    echo "[4/5] Existing .env found."
fi

# 5. Install Systemd Services & Timer
echo "[5/5] Configuring systemd services and auto-updater timer..."
git config --global --add safe.directory "$APP_DIR" 2>/dev/null || true
sudo cp deploy/tidbyt-tracker.service /etc/systemd/system/
sudo cp deploy/tidbyt-updater.service /etc/systemd/system/
sudo cp deploy/tidbyt-updater.timer /etc/systemd/system/

# Substitute actual application directory and user in service files
CURRENT_USER="${SUDO_USER:-$(whoami)}"
sudo sed -i "s|__APP_DIR__|$APP_DIR|g" /etc/systemd/system/tidbyt-tracker.service
sudo sed -i "s|__USER__|$CURRENT_USER|g" /etc/systemd/system/tidbyt-tracker.service
sudo sed -i "s|__APP_DIR__|$APP_DIR|g" /etc/systemd/system/tidbyt-updater.service

sudo systemctl daemon-reload
sudo systemctl enable tidbyt-tracker.service
sudo systemctl enable --now tidbyt-updater.timer

echo "=========================================================="
echo "  Setup Complete!                                        "
echo "  1. Edit your .env file: nano .env                       "
echo "  2. Start tracker: sudo systemctl start tidbyt-tracker   "
echo "  3. Check logs: journalctl -u tidbyt-tracker -f          "
echo "=========================================================="
