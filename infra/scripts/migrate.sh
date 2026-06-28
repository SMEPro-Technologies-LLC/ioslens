#!/usr/bin/env bash
# infra/scripts/migrate.sh — Run all pending database migrations in order

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../" && pwd)"
MIGRATIONS_DIR="${REPO_ROOT}/database/migrations"

: "${DATABASE_URL:?DATABASE_URL must be set}"

echo "==> [migrate] Applying migrations from ${MIGRATIONS_DIR}"

# Extract psql-compatible components from DATABASE_URL
# Accepts: ******host:port/db or postgres://...
PGURL="${DATABASE_URL/postgresql+asyncpg:\/\//postgresql://}"

for migration in "${MIGRATIONS_DIR}"/*.sql; do
  name="$(basename "$migration")"
  echo "    Applying ${name}..."
  psql "${PGURL}" --set ON_ERROR_STOP=1 -f "$migration"
  echo "    OK: ${name}"
done

echo "==> [migrate] All migrations applied successfully."
