#!/usr/bin/env bash
# infra/scripts/deploy.sh — CI/CD deployment script

set -euo pipefail

: "${ENVIRONMENT:?ENVIRONMENT must be set (staging|production)}"
: "${KUBECONFIG:?KUBECONFIG must be set}"
: "${IMAGE_TAG:?IMAGE_TAG must be set}"

IMAGE_REPO="ghcr.io/smepro-technologies-llc/ioslens"
NAMESPACE="ioslens"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
K8S_DIR="$(cd "${SCRIPT_DIR}/../kubernetes" && pwd)"

echo "==> [deploy] Environment: ${ENVIRONMENT}"
echo "==> [deploy] Image: ${IMAGE_REPO}:${IMAGE_TAG}"

echo "==> [deploy] Applying namespace and configmap"
kubectl apply -f "${K8S_DIR}/namespace.yaml"
kubectl apply -f "${K8S_DIR}/configmap.yaml"

echo "==> [deploy] Applying postgres statefulset"
kubectl apply -f "${K8S_DIR}/postgres/"

echo "==> [deploy] Applying API deployment"
kubectl set image deployment/ioslens-api api="${IMAGE_REPO}:${IMAGE_TAG}" -n "${NAMESPACE}" || \
  kubectl apply -f "${K8S_DIR}/api/"

echo "==> [deploy] Applying MCP deployment"
kubectl set image deployment/ioslens-mcp mcp="${IMAGE_REPO}:${IMAGE_TAG}" -n "${NAMESPACE}" || \
  kubectl apply -f "${K8S_DIR}/mcp/"

echo "==> [deploy] Applying ingress"
kubectl apply -f "${K8S_DIR}/ingress.yaml"

echo "==> [deploy] Waiting for rollout..."
kubectl rollout status deployment/ioslens-api -n "${NAMESPACE}" --timeout=300s
kubectl rollout status deployment/ioslens-mcp -n "${NAMESPACE}" --timeout=300s

echo "==> [deploy] Deployment complete for ${ENVIRONMENT}."
