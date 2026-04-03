#!/usr/bin/env bash
set -euo pipefail

db_name="${1:-rtdl_postgis}"
db_owner="${2:-$USER}"

sudo apt-get update
sudo apt-get install -y \
  postgresql \
  postgresql-contrib \
  postgis \
  postgresql-16-postgis-3 \
  postgresql-16-postgis-3-scripts \
  python3-psycopg2

sudo systemctl enable --now postgresql

if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname = '$db_owner'" | grep -q 1; then
  sudo -u postgres createuser "$db_owner" -s
fi

if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname = '$db_name'" | grep -q 1; then
  sudo -u postgres createdb -O "$db_owner" "$db_name"
fi

sudo -u postgres psql -d "$db_name" -c "CREATE EXTENSION IF NOT EXISTS postgis;"
sudo -u postgres psql -d "$db_name" -c "SELECT PostGIS_Full_Version();"
