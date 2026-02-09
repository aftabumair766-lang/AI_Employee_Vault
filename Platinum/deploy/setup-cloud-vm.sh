#!/bin/bash
# Oracle Cloud VM Setup Script for AI Employee Platinum Tier
# Run as root or with sudo
#
# This script installs Docker, creates directory structure, sets up
# SSH keys for GitHub sync, and configures the firewall.

set -e

echo "=== AI Employee Cloud VM Setup ==="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root or with sudo"
    exit 1
fi

# Update system
echo "[1/8] Updating system packages..."
apt-get update && apt-get upgrade -y

# Install Docker
echo "[2/8] Installing Docker..."
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
echo "[3/8] Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    apt-get install -y docker-compose-plugin
fi

# Create directory structure
echo "[4/8] Creating directory structure..."
mkdir -p /opt/ai-employee/{vault,config,.ssh}
mkdir -p /opt/ai-employee/vault/Platinum/{Needs_Action,Pending_Approval,In_Progress,Done,Plans,Updates,Logs,Signals}/{email,social,accounting,monitoring}

# Set permissions
chmod 700 /opt/ai-employee/.ssh

# Configure firewall (UFW)
echo "[5/8] Configuring firewall..."
if command -v ufw &> /dev/null; then
    ufw allow 22/tcp comment 'SSH'
    ufw allow 80/tcp comment 'HTTP (Caddy)'
    ufw allow 443/tcp comment 'HTTPS (Caddy)'
    ufw allow 8000/tcp comment 'API (FastAPI)'
    ufw allow 8069/tcp comment 'Odoo Web'
    # Enable ufw if not already active
    ufw --force enable
    echo "Firewall configured: ports 22, 80, 443, 8000, 8069 open"
else
    echo "UFW not found - configuring iptables directly..."
    iptables -A INPUT -p tcp --dport 22 -j ACCEPT
    iptables -A INPUT -p tcp --dport 80 -j ACCEPT
    iptables -A INPUT -p tcp --dport 443 -j ACCEPT
    iptables -A INPUT -p tcp --dport 8000 -j ACCEPT
    iptables -A INPUT -p tcp --dport 8069 -j ACCEPT
    # Save rules
    if command -v netfilter-persistent &> /dev/null; then
        netfilter-persistent save
    fi
fi

# Clone/setup vault repository
echo "[6/8] Setting up vault repository..."
if [ ! -d "/opt/ai-employee/vault/.git" ]; then
    echo "Please clone your vault repository to /opt/ai-employee/vault"
    echo "Example: git clone git@github.com:yourusername/AI_Employee_Vault.git /opt/ai-employee/vault"
else
    echo "Vault repository already exists"
fi

# Setup SSH key for git sync
echo "[7/8] SSH key setup..."
if [ ! -f "/opt/ai-employee/.ssh/vault_sync_key" ]; then
    echo "Generating SSH key for vault sync..."
    ssh-keygen -t ed25519 -f /opt/ai-employee/.ssh/vault_sync_key -N "" -C "ai-employee-cloud"
    echo ""
    echo "=== ADD THIS PUBLIC KEY TO YOUR GITHUB REPO ==="
    echo "Go to: GitHub Repo > Settings > Deploy Keys > Add deploy key"
    echo "Title: AI Employee Cloud VM"
    echo "Key:"
    cat /opt/ai-employee/.ssh/vault_sync_key.pub
    echo "================================================"
    echo "(Check 'Allow write access' so the VM can push sync commits)"
    echo ""
else
    echo "SSH key already exists"
fi

# Copy deployment files
echo "[8/8] Setting up deployment files..."
if [ -f "/opt/ai-employee/vault/Platinum/deploy/docker-compose.cloud.yml" ]; then
    echo "Deployment files found in vault"
else
    echo "Warning: Deployment files not found in vault"
    echo "Make sure to clone your repo first."
fi

# Create .env file template
echo "[*] Creating .env template..."
cat > /opt/ai-employee/.env.template << 'EOF'
# AI Employee Cloud Configuration
# Copy to Platinum/.env and fill in values:
#   cp /opt/ai-employee/.env.template /opt/ai-employee/vault/Platinum/.env

# Gmail IMAP (Cloud reads inbox)
PLATINUM_IMAP_USER=your-email@gmail.com
PLATINUM_IMAP_PASSWORD=your-16-char-app-password

# Odoo
PLATINUM_ODOO_USER=admin
PLATINUM_ODOO_PASSWORD=change-me-to-strong-password
POSTGRES_PASSWORD=change-me-to-strong-password

# Sync
PLATINUM_SYNC_INTERVAL=300
PLATINUM_HEARTBEAT_INTERVAL=30
PLATINUM_HEALTH_CHECK_INTERVAL=60

# Domain (for Caddy HTTPS - leave empty for HTTP only)
# Examples: your-domain.com, 123.45.67.89.nip.io, or :80
DOMAIN=:80
EOF

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Clone your vault:"
echo "   git clone git@github.com:yourusername/AI_Employee_Vault.git /opt/ai-employee/vault"
echo ""
echo "2. Add SSH public key to GitHub (shown above)"
echo ""
echo "3. Create your .env file:"
echo "   cp /opt/ai-employee/.env.template /opt/ai-employee/vault/Platinum/.env"
echo "   nano /opt/ai-employee/vault/Platinum/.env"
echo ""
echo "4. Start services:"
echo "   cd /opt/ai-employee/vault"
echo "   docker compose -f Platinum/deploy/docker-compose.cloud.yml up -d --build"
echo ""
echo "5. (Optional) Install systemd service for auto-start:"
echo "   cp /opt/ai-employee/vault/Platinum/deploy/ai-employee-cloud.service /etc/systemd/system/"
echo "   systemctl enable ai-employee-cloud"
echo "   systemctl start ai-employee-cloud"
echo ""
echo "6. Verify:"
echo "   curl http://localhost:8000/health"
echo "   curl http://localhost:8000/api/v1/platinum/status"
echo "   docker ps"
