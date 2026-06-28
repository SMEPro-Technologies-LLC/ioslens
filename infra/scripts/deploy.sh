#!/usr/bin/env bash
# iOSLENS deploy.sh — CI/CD deployment script
set -euo pipefail

ENVIRONMENT="${ENVIRONMENT:-staging}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
REGISTRY="${REGISTRY:-gcr.io/ioslens}"

echo "==> Deploying iOSLENS to $ENVIRONMENT (tag: $IMAGE_TAG)"

echo "[1/3] Building and pushing images..."
docker build -t "${REGISTRY}/api:${IMAGE_TAG}" -f Dockerfile --target api .
docker build -t "${REGISTRY}/mcp:${IMAGE_TAG}" -f Dockerfile --target mcp .
docker push "${REGISTRY}/api:${IMAGE_TAG}"
docker push "${REGISTRY}/mcp:${IMAGE_TAG}"

echo "[2/3] Updating Kubernetes deployments..."
kubectl set image deployment/ioslens-api \
    api="${REGISTRY}/api:${IMAGE_TAG}" \
    -n ioslens

kubectl set image deployment/ioslens-mcp \
    mcp="${REGISTRY}/mcp:${IMAGE_TAG}" \
    -n ioslens

echo "[3/3] Waiting for rollout..."
kubectl rollout status deployment/ioslens-api -n ioslens --timeout=300s
kubectl rollout status deployment/ioslens-mcp -n ioslens --timeout=300s

echo "==> Deployment to $ENVIRONMENT complete."
