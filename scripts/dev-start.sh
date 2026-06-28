#!/usr/bin/env bash
# scripts/dev-start.sh — Start the local development stack

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "==> [dev-start] Pulling images..."
docker-compose pull --quiet postgres redis

echo "==> [dev-start] Starting Postgres + Redis..."
docker-compose up -d postgres redis

echo "==> [dev-start] Waiting for Postgres..."
until docker-compose exec -T postgres pg_isready -U "${POSTGRES_USER:-ioslens}" -q; do
  sleep 1
done

echo "==> [dev-start] Running migrations..."
for migration in database/migrations/*.sql; do
  echo "    $(basename "$migration")"
  docker-compose exec -T postgres psql \
    -U "${POSTGRES_USER:-ioslens}" \
    -d "${POSTGRES_DB:-ioslens}" \
    -f "/docker-entrypoint-initdb.d/$(basename "$migration")" 2>/dev/null || \
  psql "${DATABASE_URL:-postgresql://ioslens:ioslens@localhost:5432/ioslens}" \
    --set ON_ERROR_STOP=1 -f "$migration"
done

echo "==> [dev-start] Starting API and MCP services..."
docker-compose up -d api mcp

echo "==> [dev-start] Stack is running."
echo "    API:     http://localhost:8000"
echo "    MCP:     http://localhost:8001"
echo "    Docs:    http://localhost:8000/docs"
echo ""
echo "    To stop: docker-compose down"
