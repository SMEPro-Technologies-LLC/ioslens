#!/usr/bin/env bash
# iOSLENS bootstrap.sh — First-time environment setup
set -euo pipefail

echo "==> iOSLENS Bootstrap"

# Check required tools
for tool in docker terraform kubectl gcloud psql; do
    if ! command -v "$tool" &>/dev/null; then
        echo "ERROR: $tool is not installed or not on PATH" >&2
        exit 1
    fi
done

echo "[1/4] Authenticating with GCP..."
gcloud auth application-default login

echo "[2/4] Initializing Terraform..."
cd "$(dirname "$0")/../terraform"
terraform init
terraform workspace select "${ENVIRONMENT:-development}" || \
    terraform workspace new "${ENVIRONMENT:-development}"

echo "[3/4] Creating GCP infrastructure..."
terraform plan -out=tfplan
read -rp "Apply plan? [y/N] " confirm
if [[ "$confirm" =~ ^[Yy]$ ]]; then
    terraform apply tfplan
fi

echo "[4/4] Configuring kubectl..."
gcloud container clusters get-credentials \
    "ioslens-${ENVIRONMENT:-development}" \
    --region "${REGION:-us-central1}" \
    --project "${GCP_PROJECT_ID}"

echo "==> Bootstrap complete."
