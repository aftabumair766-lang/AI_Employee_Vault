#!/bin/bash
# Oracle Cloud VM Setup Script for AI Employee Platinum Tier
# Run as root or with sudo

set -e

echo "=== AI Employee Cloud VM Setup ==="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root or with sudo"
    exit 1
fi

# Update system
echo "[1/7] Updating system packages..."
apt-get update && apt-get upgrade -y

# Install Docker
echo "[2/7] Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
    # Add current user to docker group (if not root)
    if [ -n "$SUDO_USER" ]; then
        usermod -aG docker "$SUDO_USER"
    fi
else
    echo "Docker already installed"
fi

# Install Docker Compose
echo "[3/7] Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    apt-get install -y docker-compose-plugin
fi

# Create directory structure
echo "[4/7] Creating directory structure..."
mkdir -p /opt/ai-employee/{vault,config,.ssh}
mkdir -p /opt/ai-employee/vault/Platinum/{Needs_Action,Pending_Approval,In_Progress,Done,Plans,Updates,Logs,Signals}/{email,social,accounting,monitoring}

# Set permissions
chmod 700 /opt/ai-employee/.ssh

# Clone/setup vault repository
echo "[5/7] Setting up vault repository..."
if [ ! -d "/opt/ai-employee/vault/.git" ]; then
    echo "Please clone your vault repository to /opt/ai-employee/vault"
    echo "Example: git clone git@github.com:yourusername/AI_Employee_vault.git /opt/ai-employee/vault"
else
    echo "Vault repository already exists"
fi

# Setup SSH key for git sync
echo "[6/7] SSH key setup..."
if [ ! -f "/opt/ai-employee/.ssh/vault_sync_key" ]; then
    echo "Generating SSH key for vault sync..."
    ssh-keygen -t ed25519 -f /opt/ai-employee/.ssh/vault_sync_key -N "" -C "ai-employee-cloud"
    echo ""
    echo "=== ADD THIS PUBLIC KEY TO YOUR GITHUB REPO ==="
    cat /opt/ai-employee/.ssh/vault_sync_key.pub
    echo "================================================"
    echo ""
else
    echo "SSH key already exists"
fi

# Copy deployment files
echo "[7/7] Setting up deployment files..."
if [ -f "/opt/ai-employee/vault/Platinum/deploy/docker-compose.cloud.yml" ]; then
    cp /opt/ai-employee/vault/Platinum/deploy/docker-compose.cloud.yml /opt/ai-employee/
    cp /opt/ai-employee/vault/Platinum/deploy/Caddyfile /opt/ai-employee/
    echo "Deployment files copied"
else
    echo "Warning: Deployment files not found in vault"
fi

# Create .env file template
echo "[*] Creating .env template..."
cat > /opt/ai-employee/.env.template << 'EOF'
# AI Employee Cloud Configuration
# Copy to .env and fill in values

# Gmail IMAP (read-only inbox access)
PLATINUM_IMAP_USER=your-email@gmail.com
PLATINUM_IMAP_PASSWORD=your-app-password

# Odoo
PLATINUM_ODOO_USER=admin
PLATINUM_ODOO_PASSWORD=admin
POSTGRES_PASSWORD=odoo

# Sync
PLATINUM_SYNC_INTERVAL=300
PLATINUM_HEARTBEAT_INTERVAL=30
PLATINUM_HEALTH_CHECK_INTERVAL=60

# Domain (for Caddy HTTPS)
DOMAIN=your-domain.com
EOF

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Clone your vault: git clone <your-repo> /opt/ai-employee/vault"
echo "2. Add SSH public key to GitHub (shown above)"
echo "3. Copy and fill: cp /opt/ai-employee/.env.template /opt/ai-employee/.env"
echo "4. Start services: cd /opt/ai-employee && docker compose -f docker-compose.cloud.yml up -d"
echo ""
echo "Optional: Install systemd service for auto-start"
echo "  cp /opt/ai-employee/vault/Platinum/deploy/ai-employee-cloud.service /etc/systemd/system/"
echo "  systemctl enable ai-employee-cloud"
echo "  systemctl start ai-employee-cloud"
