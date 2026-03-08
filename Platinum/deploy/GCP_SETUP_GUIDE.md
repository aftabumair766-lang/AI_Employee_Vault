# AI Employee Platinum Tier - Google Cloud Setup Guide

Deploy the AI Employee Cloud Agent on Google Cloud (GCE VM + Docker Compose).

---

## Prerequisites

- Google Cloud account (free trial gives $300 credit)
- `gcloud` CLI installed on your local machine
- Gmail account with App Password enabled
- GitHub repository for your vault

---

## Step 1: Create GCP Project & VM

### Option A — gcloud CLI (Recommended)

Run these commands on your **local machine**:

```bash
# Login to GCP
gcloud auth login

# Create a new project (or use existing)
gcloud projects create ai-employee-vault --name="AI Employee Vault"
gcloud config set project ai-employee-vault

# Enable Compute Engine API
gcloud services enable compute.googleapis.com

# Create VM (e2-medium = 2 vCPU, 4GB RAM — $35/mo or use free trial)
gcloud compute instances create ai-employee-cloud \
  --zone=us-central1-a \
  --machine-type=e2-medium \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=50GB \
  --tags=ai-employee
```

> **Budget option**: Use `e2-micro` (free tier — 1 shared vCPU, 1GB RAM) for testing only.
> Not recommended for production (7 containers need at least 2GB RAM).

### Option B — GCP Console

1. Go to [Compute Engine > VM Instances](https://console.cloud.google.com/compute/instances)
2. Click **Create Instance**
3. Configure:
   - **Name**: `ai-employee-cloud`
   - **Region**: `us-central1` (or closest to you)
   - **Machine type**: `e2-medium` (2 vCPU, 4 GB RAM)
   - **Boot disk**: Ubuntu 22.04 LTS, 50 GB
4. Click **Create**

---

## Step 2: Open Firewall Ports

### Via gcloud CLI

```bash
gcloud compute firewall-rules create allow-ai-employee \
  --direction=INGRESS \
  --action=ALLOW \
  --rules=tcp:80,tcp:443,tcp:8000,tcp:8069 \
  --target-tags=ai-employee \
  --description="AI Employee: HTTP, HTTPS, API, Odoo"
```

### Via GCP Console

1. Go to **VPC Network > Firewall**
2. Click **Create Firewall Rule**
3. Configure:
   - **Name**: `allow-ai-employee`
   - **Targets**: Specified target tags → `ai-employee`
   - **Source filter**: `0.0.0.0/0`
   - **Protocols/ports**: `tcp:80, tcp:443, tcp:8000, tcp:8069`
4. Click **Create**

---

## Step 3: SSH Into Your VM

```bash
# Via gcloud (no SSH key setup needed)
gcloud compute ssh ai-employee-cloud --zone=us-central1-a

# Or get the external IP and use regular SSH
gcloud compute instances describe ai-employee-cloud \
  --zone=us-central1-a \
  --format='get(networkInterfaces[0].accessConfigs[0].natIP)'
```

---

## Step 4: Run Setup Script

On the **GCP VM**:

```bash
# Download and run setup script from your repo
curl -fsSL https://raw.githubusercontent.com/yourusername/AI_Employee_Vault/main/Platinum/deploy/setup-gcp-vm.sh | sudo bash
```

Or manually:

```bash
sudo bash /path/to/setup-gcp-vm.sh
```

The script will:
- Install Docker + Docker Compose
- Create `/opt/ai-employee/` directory structure
- Open firewall ports (ufw)
- Generate an SSH key for Git sync

---

## Step 5: Clone Your Vault

```bash
# HTTPS clone (easier, switch to SSH later)
sudo git clone https://github.com/yourusername/AI_Employee_Vault.git /opt/ai-employee/vault

# OR SSH clone (after adding deploy key to GitHub)
sudo git clone git@github.com:yourusername/AI_Employee_Vault.git /opt/ai-employee/vault
```

---

## Step 6: Add SSH Deploy Key to GitHub

The setup script generates an SSH key. Add it to GitHub:

```bash
sudo cat /opt/ai-employee/.ssh/vault_sync_key.pub
```

1. Copy the output
2. Go to **GitHub > Your Repo > Settings > Deploy Keys**
3. Click **Add deploy key**
4. Title: `AI Employee GCP VM`
5. Paste the key, check **Allow write access**
6. Click **Add key**

Update git remote to use SSH:
```bash
cd /opt/ai-employee/vault
sudo git remote set-url origin git@github.com:yourusername/AI_Employee_Vault.git
```

---

## Step 7: Generate Gmail App Password

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable **2-Factor Authentication** if not already enabled
3. Search for **App passwords**
4. Generate a new app password for **Mail**
5. Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)

---

## Step 8: Configure Environment

```bash
sudo cp /opt/ai-employee/.env.template /opt/ai-employee/vault/Platinum/.env
sudo nano /opt/ai-employee/vault/Platinum/.env
```

Fill in at minimum:

```env
PLATINUM_IMAP_USER=your-email@gmail.com
PLATINUM_IMAP_PASSWORD=abcd-efgh-ijkl-mnop   # App password (no spaces)

PLATINUM_ODOO_PASSWORD=your-strong-password
POSTGRES_PASSWORD=your-strong-db-password

PLATINUM_GIT_REMOTE=git@github.com:yourusername/AI_Employee_Vault.git

# Your VM's external IP or domain
DOMAIN=:80   # or 34.xx.xx.xx.nip.io for auto-HTTPS
```

---

## Step 9: Start Services

```bash
cd /opt/ai-employee/vault
sudo docker compose -f Platinum/deploy/docker-compose.cloud.yml up -d --build
```

Check status:
```bash
sudo docker compose -f Platinum/deploy/docker-compose.cloud.yml ps
sudo docker compose -f Platinum/deploy/docker-compose.cloud.yml logs -f cloud-agent
```

---

## Step 10: Enable Auto-Start on Reboot (Optional)

```bash
sudo cp /opt/ai-employee/vault/Platinum/deploy/ai-employee-cloud.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ai-employee-cloud
sudo systemctl start ai-employee-cloud
```

---

## Step 11: Configure Domain + HTTPS (Optional)

If you have a domain name:

1. Set your domain's **A record** → VM's external IP
2. Update `.env`:
   ```env
   DOMAIN=your-domain.com
   ```
3. Restart Caddy:
   ```bash
   sudo docker compose -f Platinum/deploy/docker-compose.cloud.yml restart caddy
   ```

Caddy will auto-provision a **Let's Encrypt SSL certificate**.

**No domain? Use nip.io:**
- Your VM IP: `34.123.45.67`
- Set `DOMAIN=34.123.45.67.nip.io` — works for HTTPS without buying a domain.

---

## Verification

### Check Services

```bash
# All containers running?
sudo docker ps

# API health check
curl http://localhost:8000/health

# Odoo running?
curl http://localhost:8069/web/health
```

### Check Cloud Agent

```bash
# View agent logs
sudo docker compose -f Platinum/deploy/docker-compose.cloud.yml logs cloud-agent

# View heartbeat
cat /opt/ai-employee/vault/Platinum/Updates/cloud_heartbeat.json
```

### Access in Browser

| Service | URL |
|---------|-----|
| API Dashboard | `http://YOUR_VM_IP:8000/dashboard` |
| API Docs | `http://YOUR_VM_IP:8000/docs` |
| Odoo | `http://YOUR_VM_IP:8069` |

---

## Troubleshooting

### Containers not starting
```bash
sudo docker compose -f Platinum/deploy/docker-compose.cloud.yml logs
```

### API not responding
```bash
sudo docker compose -f Platinum/deploy/docker-compose.cloud.yml logs api
```

### Port not accessible from outside
```bash
# Check GCP firewall rules
gcloud compute firewall-rules list --filter="name:allow-ai-employee"

# Check ufw on VM
sudo ufw status
```

### Out of memory (e2-micro only)
Upgrade to `e2-small` or `e2-medium`:
```bash
# Stop VM first, then resize
gcloud compute instances stop ai-employee-cloud --zone=us-central1-a
gcloud compute instances set-machine-type ai-employee-cloud \
  --zone=us-central1-a --machine-type=e2-medium
gcloud compute instances start ai-employee-cloud --zone=us-central1-a
```

### Git sync issues
```bash
# Test SSH connection
sudo ssh -i /opt/ai-employee/.ssh/vault_sync_key -T git@github.com

# Manual sync
cd /opt/ai-employee/vault && sudo git pull origin main
```

---

## Cost Estimate

| Machine Type | vCPU | RAM | Monthly Cost |
|---|---|---|---|
| `e2-micro` | 0.25 shared | 1 GB | ~$0 (free tier in us-central1) |
| `e2-small` | 0.5 shared | 2 GB | ~$13/mo |
| `e2-medium` | 1 shared | 4 GB | ~$25/mo |
| `e2-standard-2` | 2 | 8 GB | ~$50/mo |

**Recommended**: `e2-medium` for comfortable operation of all 7 services.

> Free trial: $300 credit for 90 days — enough to test everything for free.

---

## Security Checklist

- [ ] Use strong passwords for Odoo and PostgreSQL
- [ ] Restrict SSH firewall rule to your IP only
- [ ] Never put SMTP credentials in Cloud `.env` (Cloud agent is read-only)
- [ ] Enable VM OS login via GCP IAM (more secure than SSH keys)
- [ ] Keep system updated: `sudo apt update && sudo apt upgrade`

---

## Architecture

```
┌──────────────────────────────────────────────┐
│              Google Cloud VM (GCE)            │
│                                               │
│  ┌──────────────┐  ┌──────────┐  ┌─────────┐ │
│  │ Cloud Agent  │  │  Health  │  │  Sync   │ │
│  │ (IMAP read)  │  │ Monitor  │  │ Daemon  │ │
│  └──────┬───────┘  └────┬─────┘  └────┬────┘ │
│         └───────────────┴─────────────┘      │
│                         │                    │
│               ┌──────────┴──────────┐        │
│               │    FastAPI (8000)   │        │
│               └──────────┬──────────┘        │
│                          │                   │
│          ┌───────────────┼──────────────┐    │
│          │               │              │    │
│  ┌───────┴──────┐  ┌─────┴──────┐      │    │
│  │     Odoo     │  │ PostgreSQL  │      │    │
│  │    (8069)    │  │            │      │    │
│  └──────────────┘  └────────────┘      │    │
│                          │              │    │
│  ┌───────────────────────┴──────────┐  │    │
│  │     Caddy (80/443 → HTTPS)       │  │    │
│  └──────────────────────────────────┘  │    │
└──────────────────────────────────────────────┘
                           │
                    git sync (SSH)
                           │
               ┌───────────┴───────────┐
               │   GitHub Repository   │
               └───────────────────────┘
                           │
               ┌───────────┴───────────┐
               │    Local Machine      │
               │   (Local Agent)       │
               └───────────────────────┘
```
