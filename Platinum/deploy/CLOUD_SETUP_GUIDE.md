# AI Employee Platinum Tier - Cloud VM Setup Guide

This guide walks you through deploying the Cloud Agent on Oracle Cloud Free Tier.

## Prerequisites

- Oracle Cloud account (Free Tier eligible)
- Gmail account with App Password enabled
- GitHub repository for your vault
- Local machine with the AI Employee vault configured

---

## Step 1: Create Oracle Cloud VM

1. Log into [Oracle Cloud Console](https://cloud.oracle.com/)
2. Navigate to **Compute > Instances > Create Instance**
3. Configure:
   - **Name**: `ai-employee-cloud`
   - **Image**: Ubuntu 22.04 (or latest LTS)
   - **Shape**: VM.Standard.A1.Flex (Always Free ARM)
   - **OCPUs**: 1-2
   - **Memory**: 2-4 GB
   - **Boot Volume**: 50 GB
4. Add your SSH public key
5. Create the instance

## Step 2: Configure Firewall

In Oracle Cloud Console:
1. Go to **Networking > Virtual Cloud Networks**
2. Select your VCN > Security Lists
3. Add Ingress Rules:
   - Port 80 (HTTP)
   - Port 443 (HTTPS)
   - Port 22 (SSH) - restrict to your IP

On the VM:
```bash
sudo iptables -I INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT -p tcp --dport 443 -j ACCEPT
sudo netfilter-persistent save
```

## Step 3: Run Setup Script

SSH into your VM and run:

```bash
# Download and run setup script
curl -fsSL https://raw.githubusercontent.com/yourusername/AI_Employee_vault/main/Platinum/deploy/setup-cloud-vm.sh | sudo bash
```

Or manually:

```bash
sudo bash /path/to/setup-cloud-vm.sh
```

## Step 4: Clone Your Vault Repository

```bash
# Configure git
git config --global user.name "AI Employee Cloud"
git config --global user.email "ai-employee@your-domain.com"

# Clone vault (use HTTPS first, switch to SSH after key setup)
sudo git clone https://github.com/yourusername/AI_Employee_vault.git /opt/ai-employee/vault
```

## Step 5: Configure SSH Key for Git Sync

The setup script generates an SSH key. Add it to GitHub:

1. View the public key:
   ```bash
   sudo cat /opt/ai-employee/.ssh/vault_sync_key.pub
   ```

2. Go to GitHub > Your Repo > Settings > Deploy Keys
3. Click "Add deploy key"
4. Paste the public key
5. Check "Allow write access"
6. Click "Add key"

Update git remote to use SSH:
```bash
cd /opt/ai-employee/vault
sudo git remote set-url origin git@github.com:yourusername/AI_Employee_vault.git
```

## Step 6: Generate Gmail App Password

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Factor Authentication if not already
3. Go to **App passwords**
4. Generate a new app password for "Mail"
5. Copy the 16-character password

## Step 7: Configure Environment

```bash
sudo cp /opt/ai-employee/.env.template /opt/ai-employee/.env
sudo nano /opt/ai-employee/.env
```

Fill in:
```env
PLATINUM_IMAP_USER=your-email@gmail.com
PLATINUM_IMAP_PASSWORD=xxxx-xxxx-xxxx-xxxx  # App password
PLATINUM_ODOO_USER=admin
PLATINUM_ODOO_PASSWORD=your-secure-password
POSTGRES_PASSWORD=your-secure-db-password
DOMAIN=your-domain.com  # Or leave as localhost
```

## Step 8: Start Services

```bash
cd /opt/ai-employee
sudo docker compose -f docker-compose.cloud.yml up -d
```

Check status:
```bash
sudo docker compose -f docker-compose.cloud.yml ps
sudo docker compose -f docker-compose.cloud.yml logs -f cloud-agent
```

## Step 9: Enable Auto-Start (Optional)

```bash
sudo cp /opt/ai-employee/vault/Platinum/deploy/ai-employee-cloud.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ai-employee-cloud
sudo systemctl start ai-employee-cloud
```

## Step 10: Configure DNS (Optional)

For HTTPS with Caddy:
1. Point your domain's A record to your VM's public IP
2. Update `.env` with your domain
3. Restart Caddy: `sudo docker compose -f docker-compose.cloud.yml restart caddy`

---

## Verification

### Check Cloud Agent
```bash
# View heartbeat
cat /opt/ai-employee/vault/Platinum/Updates/cloud_heartbeat.json

# View logs
sudo docker compose -f docker-compose.cloud.yml logs cloud-agent
```

### Check Health Monitor
```bash
cat /opt/ai-employee/vault/Platinum/Updates/health_status.json
```

### Check Odoo
Open in browser: `http://your-vm-ip:8069` (or `https://your-domain.com`)

### Test Email Triage
Send an email to your configured Gmail. Within a few minutes, check:
```bash
ls /opt/ai-employee/vault/Platinum/Needs_Action/email/
```

---

## Troubleshooting

### Docker issues
```bash
sudo docker compose -f docker-compose.cloud.yml logs
sudo docker compose -f docker-compose.cloud.yml restart
```

### Git sync issues
```bash
# Test SSH connection
sudo ssh -i /opt/ai-employee/.ssh/vault_sync_key git@github.com

# Manual sync
cd /opt/ai-employee/vault
sudo git pull origin main
```

### IMAP connection issues
- Verify App Password is correct
- Check if "Less secure app access" is needed (shouldn't be with App Password)
- Test connection manually in Python

### Firewall issues
```bash
sudo iptables -L -n
sudo ufw status
```

---

## Security Considerations

1. **NEVER put SMTP credentials in Cloud .env** - Cloud agent only reads email
2. **Use strong passwords** for Odoo and PostgreSQL
3. **Restrict SSH access** to your IP only
4. **Enable fail2ban** for additional protection
5. **Keep system updated**: `sudo apt update && sudo apt upgrade`

---

## Local Agent Setup

On your local machine, configure `.env` with full credentials:
- SMTP for sending emails
- Twitter API keys for posting
- WhatsApp/Banking credentials (when ready)

The Local Agent reviews and approves drafts created by the Cloud Agent.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Oracle Cloud VM                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │Cloud Agent  │  │Health Monitor│  │   Sync Daemon       │  │
│  │(IMAP read)  │  │             │  │   (git push/pull)   │  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │
│         │                │                     │             │
│         └────────────────┴─────────────────────┘             │
│                          │                                   │
│                    ┌─────┴─────┐                            │
│                    │   Vault   │◄──── git sync ────┐        │
│                    │ (shared)  │                   │        │
│                    └───────────┘                   │        │
│                          │                         │        │
│  ┌───────────────────────┴───────────────────┐    │        │
│  │              Odoo + PostgreSQL             │    │        │
│  └───────────────────────────────────────────┘    │        │
│                          │                         │        │
│  ┌───────────────────────┴───────────────────┐    │        │
│  │           Caddy (HTTPS reverse proxy)     │    │        │
│  └───────────────────────────────────────────┘    │        │
└─────────────────────────────────────────────────────────────┘
                           │
                      ◄────┘ git sync
                           │
┌─────────────────────────────────────────────────────────────┐
│                    Local Machine                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                    Local Agent                       │    │
│  │  - Reviews drafts from Cloud                        │    │
│  │  - Approves/rejects                                 │    │
│  │  - Sends emails (SMTP)                              │    │
│  │  - Posts to social media                            │    │
│  │  - Confirms Odoo invoices                           │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```
