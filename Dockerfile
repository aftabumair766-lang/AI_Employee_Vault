# AI Employee - All-in-One HuggingFace Spaces Deployment
# Includes: PostgreSQL 15, Odoo 17, Caddy, FastAPI + background agents
# All services run under supervisord in one container
#
# Build context: repository root (AI_Employee_Vault/)

FROM python:3.11-slim-bookworm

LABEL maintainer="AI Employee <noreply@example.com>"
LABEL description="AI Employee Vault - all-in-one deployment (API + Odoo + PostgreSQL)"

# Prevent interactive prompts during package install
ENV DEBIAN_FRONTEND=noninteractive

# --- System Dependencies ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    openssh-client \
    supervisor \
    gnupg2 \
    curl \
    lsb-release \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# --- PostgreSQL 15 ---
RUN echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" \
    > /etc/apt/sources.list.d/pgdg.list \
    && curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor -o /etc/apt/trusted.gpg.d/postgresql.gpg \
    && apt-get update && apt-get install -y --no-install-recommends \
    postgresql-15 \
    postgresql-client-15 \
    && rm -rf /var/lib/apt/lists/*

# --- Odoo 17 ---
RUN curl -fsSL https://nightly.odoo.com/odoo.key | gpg --dearmor -o /etc/apt/trusted.gpg.d/odoo.gpg \
    && echo "deb http://nightly.odoo.com/17.0/nightly/deb/ ./" > /etc/apt/sources.list.d/odoo.list \
    && apt-get update && apt-get install -y --no-install-recommends \
    odoo \
    && rm -rf /var/lib/apt/lists/*

# --- Caddy ---
RUN curl -fsSL https://dl.cloudsmith.io/public/caddy/stable/gpg.key | gpg --dearmor -o /etc/apt/trusted.gpg.d/caddy.gpg \
    && echo "deb https://dl.cloudsmith.io/public/caddy/stable/deb/debian any-version main" > /etc/apt/sources.list.d/caddy.list \
    && apt-get update && apt-get install -y --no-install-recommends caddy \
    && rm -rf /var/lib/apt/lists/*

# --- App Setup ---
WORKDIR /opt/ai-employee

# Copy requirements and install Python dependencies
COPY Platinum/requirements-docker.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Platinum package (source code + __init__.py)
COPY Platinum/__init__.py ./Platinum/__init__.py
COPY Platinum/src/ ./Platinum/src/

# Copy the API code from Working_Gold/TASK_206
COPY Working_Gold/TASK_206/api/ ./api/

# Copy deployment configs
COPY Platinum/deploy/supervisord.conf /etc/supervisord.conf
COPY Platinum/deploy/Caddyfile.hf /etc/caddy/Caddyfile
COPY Platinum/deploy/odoo-hf.conf /etc/odoo/odoo.conf
COPY Platinum/deploy/entrypoint-hf.sh /opt/ai-employee/entrypoint.sh
RUN chmod +x /opt/ai-employee/entrypoint.sh

# Create vault directory structure
RUN mkdir -p /opt/ai-employee/vault/Platinum/{Needs_Action,Pending_Approval,In_Progress,Done,Plans,Updates,Logs,Signals}/{email,social,accounting,monitoring}

# Create Odoo data directory
RUN mkdir -p /var/lib/odoo && chown -R odoo:odoo /var/lib/odoo 2>/dev/null || true

# Ensure PostgreSQL directories exist
RUN mkdir -p /var/run/postgresql /var/log/postgresql \
    && chown postgres:postgres /var/run/postgresql /var/log/postgresql \
    && chmod 775 /var/run/postgresql

# --- Environment Variables ---
ENV PYTHONPATH=/opt/ai-employee
ENV PYTHONUNBUFFERED=1
ENV PLATINUM_AGENT_ROLE=cloud
ENV PLATINUM_VAULT_PATH=/opt/ai-employee/vault

# Odoo running locally in same container
ENV PLATINUM_ODOO_URL=http://localhost:8069
ENV PLATINUM_ODOO_DB=odoo
ENV PLATINUM_ODOO_USER=admin
ENV PLATINUM_ODOO_PASSWORD=admin

# Database URL for FastAPI (explicit, avoids .env parsing issues)
ENV PLATINUM_DATABASE_URL=sqlite:///./ai_employee.db

# Health monitor: API is local, Cloud VM not applicable
ENV PLATINUM_HEALTH_API_URL=http://localhost:8000
ENV PLATINUM_HEALTH_CLOUD_URL=

# API listens on 8000 internally, Caddy on 7860
ENV PORT=8000
EXPOSE 7860

# Health check via Caddy (the externally exposed port)
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:7860/health')" || exit 1

# Entrypoint: init PostgreSQL, then launch supervisord
CMD ["/opt/ai-employee/entrypoint.sh"]
