#!/bin/bash
# Entrypoint for HuggingFace Spaces: init PostgreSQL + Odoo DB, then launch supervisord
set -e

PGDATA="/var/lib/postgresql/15/main"
PGRUN="/var/run/postgresql"

echo "[entrypoint] Initializing AI Employee (all-in-one mode)..."

# --- PostgreSQL Setup ---
mkdir -p "$PGRUN"
chown postgres:postgres "$PGRUN"

if [ ! -f "$PGDATA/PG_VERSION" ]; then
    echo "[entrypoint] Initializing PostgreSQL data directory..."
    mkdir -p "$PGDATA"
    chown -R postgres:postgres /var/lib/postgresql
    su - postgres -c "/usr/lib/postgresql/15/bin/initdb -D $PGDATA --encoding=UTF8 --locale=C"
fi

# Start PostgreSQL temporarily to create odoo user/db
echo "[entrypoint] Starting PostgreSQL for initial setup..."
su - postgres -c "/usr/lib/postgresql/15/bin/pg_ctl -D $PGDATA -l /tmp/pg_setup.log start -w -t 30"

# Create odoo role and database if they don't exist
su - postgres -c "psql -tc \"SELECT 1 FROM pg_roles WHERE rolname='odoo'\" | grep -q 1 || psql -c \"CREATE ROLE odoo WITH LOGIN PASSWORD 'odoo' CREATEDB;\""
su - postgres -c "psql -tc \"SELECT 1 FROM pg_database WHERE datname='odoo'\" | grep -q 1 || psql -c \"CREATE DATABASE odoo OWNER odoo ENCODING 'UTF8' TEMPLATE template0;\""

# Stop PostgreSQL (supervisord will manage it from here)
su - postgres -c "/usr/lib/postgresql/15/bin/pg_ctl -D $PGDATA stop -w -t 10"

echo "[entrypoint] PostgreSQL setup complete."

# --- Ensure directories exist ---
mkdir -p /var/lib/odoo
chown -R odoo:odoo /var/lib/odoo 2>/dev/null || true

echo "[entrypoint] Starting all services via supervisord..."
exec supervisord -c /etc/supervisord.conf
