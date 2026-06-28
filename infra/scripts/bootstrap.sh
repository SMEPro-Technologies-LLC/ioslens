#!/usr/bin/env bash
# infra/scripts/bootstrap.sh — First-time environment setup

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../" && pwd)"

echo "==> [bootstrap] iOSLENS environment setup"

# Check required tools
for cmd in docker docker-compose python3 psql; do
  if ! command -v "$cmd" &>/dev/null; then
    echo "ERROR: '$cmd' not found. Install it and re-run." >&2
    exit 1
  fi
done

echo "==> [bootstrap] Pulling container images"
cd "$REPO_ROOT"
docker-compose pull

echo "==> [bootstrap] Starting Postgres and Redis"
docker-compose up -d postgres redis

echo "==> [bootstrap] Waiting for Postgres to be ready..."
until docker-compose exec -T postgres pg_isready -U "${POSTGRES_USER:-ioslens}" -d "${POSTGRES_DB:-ioslens}"; do
  echo "    Still waiting..."
  sleep 2
done

echo "==> [bootstrap] Running migrations"
"${SCRIPT_DIR}/migrate.sh"

echo "==> [bootstrap] Bootstrap complete."
echo "    Run: docker-compose up -d api mcp"
