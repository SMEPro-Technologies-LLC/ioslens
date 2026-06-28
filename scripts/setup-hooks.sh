#!/usr/bin/env bash
# setup-hooks.sh — Install Git pre-commit hooks for iOSLENS
set -euo pipefail

HOOKS_DIR="$(git rev-parse --git-dir)/hooks"

echo "==> Installing Git hooks to $HOOKS_DIR..."

# pre-commit hook: run lint + unit tests
cat > "$HOOKS_DIR/pre-commit" << 'EOF'
#!/usr/bin/env bash
set -euo pipefail
echo "--- pre-commit: running lint ---"
flake8 src/ioslens/ --max-line-length=100 --ignore=E203,W503 || {
    echo "Lint failed. Fix errors before committing."
    exit 1
}
black src/ioslens/ --check --line-length=100 || {
    echo "Formatting check failed. Run: black src/ --line-length=100"
    exit 1
}
echo "--- pre-commit: running unit tests ---"
PYTHONPATH=src pytest tests/unit/ -q --tb=short || {
    echo "Unit tests failed. Fix tests before committing."
    exit 1
}
echo "--- pre-commit: all checks passed ---"
EOF

chmod +x "$HOOKS_DIR/pre-commit"

echo "==> Git hooks installed successfully."
echo "    pre-commit: lint + unit tests"
