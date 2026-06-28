#!/usr/bin/env bash
# scripts/setup-hooks.sh — Install git pre-commit hooks

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOOKS_DIR="${REPO_ROOT}/.git/hooks"

if [ ! -d "$HOOKS_DIR" ]; then
  echo "ERROR: Not inside a git repository (expected .git/hooks)" >&2
  exit 1
fi

echo "==> [hooks] Installing pre-commit hook..."
cat > "${HOOKS_DIR}/pre-commit" << 'HOOK'
#!/usr/bin/env bash
set -e
echo "==> [pre-commit] Lint check..."
ruff check src/ioslens || { echo "Ruff lint failed. Fix before committing."; exit 1; }
ruff format --check src/ioslens || { echo "Ruff format check failed. Run: ruff format src/ioslens"; exit 1; }
echo "==> [pre-commit] Passed."
HOOK
chmod +x "${HOOKS_DIR}/pre-commit"

echo "==> [hooks] Installing pre-push hook..."
cat > "${HOOKS_DIR}/pre-push" << 'HOOK'
#!/usr/bin/env bash
set -e
echo "==> [pre-push] Running unit tests..."
PYTHONPATH=src python -m pytest tests/unit -q || { echo "Tests failed. Fix before pushing."; exit 1; }
echo "==> [pre-push] Passed."
HOOK
chmod +x "${HOOKS_DIR}/pre-push"

echo "==> [hooks] Git hooks installed in ${HOOKS_DIR}/"
