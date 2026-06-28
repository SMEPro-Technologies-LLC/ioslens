#!/usr/bin/env bash
# scripts/test.sh — Run pytest with coverage report

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

export PYTHONPATH="${REPO_ROOT}/src"

# Defaults for CI / local runs
export JWT_SECRET="${JWT_SECRET:-dev-test-secret-local}"
export DATABASE_URL="${DATABASE_URL:-postgresql://ioslens:ioslens@localhost:5432/ioslens}"
export REDIS_URL="${REDIS_URL:-redis://localhost:6379/0}"

echo "==> [test] Running unit tests..."
python -m pytest tests/unit \
  --cov=ioslens \
  --cov-report=term-missing \
  --cov-report=html:htmlcov \
  -v \
  "$@"

echo ""
echo "==> [test] Coverage report: htmlcov/index.html"
