#!/usr/bin/env bash
# dev-start.sh — Start the iOSLENS local dev stack and run migrations
set -euo pipefail

echo "==> Starting iOSLENS dev stack..."
docker compose -f docker-compose.yml up -d --build

echo "==> Waiting for Postgres to be ready..."
until docker compose exec -T postgres pg_isready -U ioslens 2>/dev/null; do
    printf '.'
    sleep 1
done
echo ""

echo "==> Running database migrations..."
for f in database/migrations/*.sql; do
    echo "  Applying $(basename "$f")..."
    docker compose exec -T postgres psql -U ioslens -d ioslens < "$f"
done

echo "==> Seeding UDM reference data..."
docker compose exec -T postgres psql -U ioslens -d ioslens < database/seeds/seed_udm.sql

echo ""
echo "==> iOSLENS dev stack ready!"
echo "    API:        http://localhost:8000"
echo "    MCP:        http://localhost:8001"
echo "    Grafana:    http://localhost:3000  (admin/admin)"
echo "    Prometheus: http://localhost:9090"
echo "    Postgres:   localhost:5432  (ioslens/ioslens_dev)"
