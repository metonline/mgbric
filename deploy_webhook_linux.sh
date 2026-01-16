#!/bin/bash
# Production Webhook Server Deployment Script
# For Linux/Ubuntu servers

set -e

echo "========================================================"
echo "GitHub Webhook Server - Production Deployment"
echo "========================================================"

# Configuration
WEBHOOK_USER="webhookbot"
WEBHOOK_HOME="/opt/github-webhook"
WEBHOOK_SECRET="${GITHUB_WEBHOOK_SECRET:-}"
REPO_URL="https://github.com/YOUR_USERNAME/BRIC.git"

echo "[INFO] System check..."
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed!"
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo "[ERROR] Git is not installed!"
    exit 1
fi

echo "[OK] Python and Git are installed"

# Create webhook user
if ! id "$WEBHOOK_USER" &>/dev/null; then
    echo "[INFO] Creating webhook user..."
    sudo useradd -r -s /bin/bash -d "$WEBHOOK_HOME" -m "$WEBHOOK_USER"
    echo "[OK] User created: $WEBHOOK_USER"
else
    echo "[OK] User exists: $WEBHOOK_USER"
fi

# Create webhook directory
if [ ! -d "$WEBHOOK_HOME" ]; then
    echo "[INFO] Creating webhook directory..."
    sudo mkdir -p "$WEBHOOK_HOME"
    sudo chown "$WEBHOOK_USER:$WEBHOOK_USER" "$WEBHOOK_HOME"
    echo "[OK] Directory created: $WEBHOOK_HOME"
fi

# Clone or update repository
echo "[INFO] Setting up repository..."
if [ ! -d "$WEBHOOK_HOME/repo" ]; then
    sudo -u "$WEBHOOK_USER" git clone "$REPO_URL" "$WEBHOOK_HOME/repo"
    echo "[OK] Repository cloned"
else
    sudo -u "$WEBHOOK_USER" git -C "$WEBHOOK_HOME/repo" pull
    echo "[OK] Repository updated"
fi

# Install Python dependencies
echo "[INFO] Installing Python dependencies..."
sudo -u "$WEBHOOK_USER" python3 -m venv "$WEBHOOK_HOME/venv"
sudo -u "$WEBHOOK_USER" "$WEBHOOK_HOME/venv/bin/pip" install flask requests beautifulsoup4 --quiet
echo "[OK] Dependencies installed"

# Create systemd service file
echo "[INFO] Creating systemd service..."
sudo tee /etc/systemd/system/webhook.service > /dev/null <<EOF
[Unit]
Description=GitHub Webhook Server
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=$WEBHOOK_USER
WorkingDirectory=$WEBHOOK_HOME/repo
Environment="GITHUB_WEBHOOK_SECRET=$WEBHOOK_SECRET"
ExecStart=$WEBHOOK_HOME/venv/bin/python webhook_server.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "[OK] Service file created"

# Enable and start service
echo "[INFO] Enabling and starting service..."
sudo systemctl daemon-reload
sudo systemctl enable webhook.service
sudo systemctl start webhook.service
echo "[OK] Service started"

# Check service status
sleep 2
if sudo systemctl is-active --quiet webhook.service; then
    echo "[OK] Service is running"
else
    echo "[WARNING] Service may not be running. Check logs:"
    echo "  sudo journalctl -u webhook.service -n 20"
fi

echo ""
echo "========================================================"
echo "[SUCCESS] Deployment complete!"
echo "========================================================"
echo ""
echo "Next steps:"
echo "1. Set webhook secret in /opt/github-webhook/repo/.env.webhook"
echo "2. Configure GitHub webhook:"
echo "   URL: https://your-domain.com/webhook"
echo "3. Test webhook:"
echo "   sudo journalctl -u webhook.service -f"
echo ""
