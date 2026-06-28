#!/usr/bin/env bash
# iOSLENS migrate.sh — Database migration runner
set -euo pipefail

MIGRATIONS_DIR="$(dirname "$0")/../../database/migrations"
DATABASE_URL="${DATABASE_URL:-postgresql://ioslens:ioslens_dev@localhost:5432/ioslens}"

echo "==> Running iOSLENS database migrations"
echo "    Database: $DATABASE_URL"
echo "    Migrations: $MIGRATIONS_DIR"

if [ ! -d "$MIGRATIONS_DIR" ]; then
    echo "ERROR: migrations directory not found: $MIGRATIONS_DIR" >&2
    exit 1
fi

for f in "$MIGRATIONS_DIR"/*.sql; do
    echo "  --> Applying $(basename "$f")..."
    psql "$DATABASE_URL" -f "$f" -v ON_ERROR_STOP=1
done

echo "==> Migrations complete."
