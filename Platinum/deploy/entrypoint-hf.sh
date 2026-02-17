#!/bin/bash
# Entrypoint for HuggingFace Spaces: init PostgreSQL + Odoo DB, then launch supervisord
set -e

PGDATA="/var/lib/postgresql/15/main"
PGRUN="/var/run/postgresql"
PGLOG="/var/log/postgresql"

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

# Ensure postgresql.conf has correct settings for our setup
cat > "$PGDATA/conf.d/hf.conf" 2>/dev/null <<'PGCONF' || true
listen_addresses = 'localhost'
port = 5432
max_connections = 50
shared_buffers = 128MB
unix_socket_directories = '/var/run/postgresql'
logging_collector = off
PGCONF
# If conf.d doesn't exist, append to postgresql.conf directly
if [ ! -d "$PGDATA/conf.d" ]; then
    mkdir -p "$PGDATA/conf.d"
    chown postgres:postgres "$PGDATA/conf.d"
    # Ensure include_dir is set
    grep -q "include_dir" "$PGDATA/postgresql.conf" || echo "include_dir = 'conf.d'" >> "$PGDATA/postgresql.conf"
    cat > "$PGDATA/conf.d/hf.conf" <<'PGCONF'
listen_addresses = 'localhost'
port = 5432
max_connections = 50
shared_buffers = 128MB
unix_socket_directories = '/var/run/postgresql'
logging_collector = off
PGCONF
    chown postgres:postgres "$PGDATA/conf.d/hf.conf"
fi

# Start PostgreSQL temporarily to create odoo user/db
echo "[entrypoint] Starting PostgreSQL for initial setup..."
su -s /bin/bash postgres -c "/usr/lib/postgresql/15/bin/pg_ctl -D $PGDATA -l $PGLOG/startup.log start -w -t 60"

echo "[entrypoint] PostgreSQL started. Setting up Odoo database..."

# Create odoo role and database if they don't exist
su -s /bin/bash postgres -c "psql -tc \"SELECT 1 FROM pg_roles WHERE rolname='odoo'\" | grep -q 1 || psql -c \"CREATE ROLE odoo WITH LOGIN PASSWORD 'odoo' CREATEDB;\""
su -s /bin/bash postgres -c "psql -tc \"SELECT 1 FROM pg_database WHERE datname='odoo'\" | grep -q 1 || psql -c \"CREATE DATABASE odoo OWNER odoo ENCODING 'UTF8' TEMPLATE template0;\""

# Stop PostgreSQL (supervisord will manage it from here)
su -s /bin/bash postgres -c "/usr/lib/postgresql/15/bin/pg_ctl -D $PGDATA stop -w -t 10"

echo "[entrypoint] PostgreSQL setup complete."

# --- Ensure Odoo directories exist ---
mkdir -p /var/lib/odoo
chown -R odoo:odoo /var/lib/odoo 2>/dev/null || true

echo "[entrypoint] Starting all services via supervisord..."
exec supervisord -c /etc/supervisord.conf
