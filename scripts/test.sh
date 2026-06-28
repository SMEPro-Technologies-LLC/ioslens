#!/usr/bin/env bash
# test.sh — Run pytest with coverage report
set -euo pipefail

PYTHONPATH="${PYTHONPATH:-src}"
export PYTHONPATH

echo "==> Installing test dependencies..."
pip install -q -r src/requirements-dev.txt

echo "==> Running unit tests..."
PYTHONPATH=src pytest tests/unit/ -v --tb=short \
    --cov=src/ioslens \
    --cov-report=term-missing \
    --cov-report=html:htmlcov \
    --cov-fail-under=50

echo ""
echo "==> Running integration tests..."
PYTHONPATH=src pytest tests/integration/ -v --tb=short

echo ""
echo "==> Coverage report written to htmlcov/index.html"
