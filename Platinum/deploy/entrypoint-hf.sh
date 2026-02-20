#!/bin/bash
# Entrypoint for HuggingFace Spaces: init PostgreSQL + Odoo DB, then launch supervisord
set -e

PGDATA="/opt/ai-employee/pgdata"
PGRUN="/var/run/postgresql"
ODOO_INIT_FLAG="/var/lib/odoo/.initialized"

echo "[entrypoint] Initializing AI Employee (all-in-one mode)..."

# --- PostgreSQL Setup ---
# Use a fresh data directory (not the Debian auto-created cluster)
mkdir -p "$PGRUN"
chown postgres:postgres "$PGRUN"
chmod 775 "$PGRUN"

if [ ! -f "$PGDATA/PG_VERSION" ]; then
    echo "[entrypoint] Initializing fresh PostgreSQL cluster..."
    rm -rf "$PGDATA"
    mkdir -p "$PGDATA"
    chown postgres:postgres "$PGDATA"
    su -s /bin/bash postgres -c "/usr/lib/postgresql/15/bin/initdb -D $PGDATA --encoding=UTF8 --locale=C"

    # Configure pg_hba.conf
    cat > "$PGDATA/pg_hba.conf" <<'PGHBA'
local   all   postgres   trust
local   all   all        md5
host    all   all        127.0.0.1/32   md5
host    all   all        ::1/128        md5
PGHBA
    chown postgres:postgres "$PGDATA/pg_hba.conf"

    # Tune postgresql.conf for HF free tier
    cat >> "$PGDATA/postgresql.conf" <<'PGCONF'
listen_addresses = 'localhost'
port = 5432
max_connections = 50
shared_buffers = 128MB
unix_socket_directories = '/var/run/postgresql'
PGCONF
fi

chown -R postgres:postgres "$PGDATA"

# Start PostgreSQL
echo "[entrypoint] Starting PostgreSQL..."
PG_LOGFILE="/tmp/pg_startup.log"
touch "$PG_LOGFILE" && chown postgres:postgres "$PG_LOGFILE"
su -s /bin/bash postgres -c "/usr/lib/postgresql/15/bin/pg_ctl -D $PGDATA start -w -t 60 -l $PG_LOGFILE" || {
    echo "[entrypoint] PostgreSQL failed to start. Log output:"
    cat "$PG_LOGFILE"
    exit 1
}

echo "[entrypoint] PostgreSQL started. Setting up Odoo database..."

# Create odoo role and database if they don't exist
su -s /bin/bash postgres -c "psql -tc \"SELECT 1 FROM pg_roles WHERE rolname='odoo'\" | grep -q 1 || psql -c \"CREATE ROLE odoo WITH LOGIN PASSWORD 'odoo' CREATEDB;\""
su -s /bin/bash postgres -c "psql -tc \"SELECT 1 FROM pg_database WHERE datname='odoo'\" | grep -q 1 || psql -c \"CREATE DATABASE odoo OWNER odoo ENCODING 'UTF8' TEMPLATE template0;\""

# --- Odoo initialization (first run only) ---
mkdir -p /var/lib/odoo
chown -R odoo:odoo /var/lib/odoo 2>/dev/null || true

if [ ! -f "$ODOO_INIT_FLAG" ]; then
    echo "[entrypoint] Initializing Odoo base module (first run, takes ~60s)..."
    su -s /bin/bash odoo -c "/usr/bin/odoo --config=/etc/odoo/odoo.conf -i base --stop-after-init --no-http" || {
        echo "[entrypoint] WARNING: Odoo base init failed, will retry on service start"
    }
    touch "$ODOO_INIT_FLAG"
    echo "[entrypoint] Odoo initialization complete."
else
    echo "[entrypoint] Odoo already initialized, skipping."
fi

# Stop PostgreSQL (supervisord will manage it from here)
su -s /bin/bash postgres -c "/usr/lib/postgresql/15/bin/pg_ctl -D $PGDATA stop -w -t 10"

echo "[entrypoint] Setup complete. Starting all services via supervisord..."
exec supervisord -c /etc/supervisord.conf
