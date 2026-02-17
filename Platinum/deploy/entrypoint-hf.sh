#!/bin/bash
# Entrypoint for HuggingFace Spaces: init PostgreSQL + Odoo DB, then launch supervisord
set -e

PGDATA="/var/lib/postgresql/15/main"
PGRUN="/var/run/postgresql"
PGLOG="/var/log/postgresql"
ODOO_INIT_FLAG="/var/lib/odoo/.initialized"

echo "[entrypoint] Initializing AI Employee (all-in-one mode)..."

# --- PostgreSQL Setup ---
mkdir -p "$PGRUN" "$PGLOG"
chown postgres:postgres "$PGRUN" "$PGLOG"
chmod 775 "$PGRUN"

# Debian's postgresql-15 package auto-creates a cluster during install.
# If PG_VERSION doesn't exist (e.g. fresh volume), init manually.
if [ ! -f "$PGDATA/PG_VERSION" ]; then
    echo "[entrypoint] Initializing PostgreSQL data directory..."
    mkdir -p "$PGDATA"
    chown -R postgres:postgres /var/lib/postgresql
    su -s /bin/bash postgres -c "/usr/lib/postgresql/15/bin/initdb -D $PGDATA --encoding=UTF8 --locale=C"
fi

# Ensure postgres owns the data directory
chown -R postgres:postgres "$PGDATA"

# Configure pg_hba.conf for local trust (so odoo can connect)
cat > "$PGDATA/pg_hba.conf" <<'PGHBA'
# TYPE  DATABASE  USER      METHOD
local   all       postgres  trust
local   all       all       md5
host    all       all       127.0.0.1/32  md5
host    all       all       ::1/128       md5
PGHBA
chown postgres:postgres "$PGDATA/pg_hba.conf"

# Start PostgreSQL temporarily for setup
echo "[entrypoint] Starting PostgreSQL for initial setup..."
su -s /bin/bash postgres -c "/usr/lib/postgresql/15/bin/pg_ctl -D $PGDATA -l $PGLOG/startup.log start -w -t 60"

echo "[entrypoint] PostgreSQL started. Setting up Odoo database..."

# Create odoo role and database if they don't exist
su -s /bin/bash postgres -c "psql -tc \"SELECT 1 FROM pg_roles WHERE rolname='odoo'\" | grep -q 1 || psql -c \"CREATE ROLE odoo WITH LOGIN PASSWORD 'odoo' CREATEDB;\""
su -s /bin/bash postgres -c "psql -tc \"SELECT 1 FROM pg_database WHERE datname='odoo'\" | grep -q 1 || psql -c \"CREATE DATABASE odoo OWNER odoo ENCODING 'UTF8' TEMPLATE template0;\""

# --- Odoo initialization (first run only) ---
mkdir -p /var/lib/odoo
chown -R odoo:odoo /var/lib/odoo 2>/dev/null || true

if [ ! -f "$ODOO_INIT_FLAG" ]; then
    echo "[entrypoint] Initializing Odoo base module (first run, this takes a while)..."
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

echo "[entrypoint] PostgreSQL setup complete."
echo "[entrypoint] Starting all services via supervisord..."
exec supervisord -c /etc/supervisord.conf
