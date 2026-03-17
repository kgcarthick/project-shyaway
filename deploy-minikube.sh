#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
#  deploy-minikube.sh  —  Full Minikube + Docker + Kubernetes automation
#  Usage:
#    ./deploy-minikube.sh            # deploy (or redeploy)
#    ./deploy-minikube.sh teardown   # delete deployment and stop minikube
#    ./deploy-minikube.sh status     # show pod / service status
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

IMAGE_NAME="shyaway-dashboard"
IMAGE_TAG="local"
NAMESPACE="default"
SECRET_NAME="shyaway-secrets"

# ── colour helpers ────────────────────────────────────────────────────────────
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
info()    { echo -e "${GREEN}[INFO]${NC}  $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error()   { echo -e "${RED}[ERR]${NC}   $*"; exit 1; }

# ── pre-flight checks ─────────────────────────────────────────────────────────
check_deps() {
  for cmd in minikube kubectl docker; do
    command -v "$cmd" &>/dev/null || error "$cmd not found — please install it first."
  done
}

# ── secrets prompt ────────────────────────────────────────────────────────────
apply_secrets() {
  if kubectl get secret "$SECRET_NAME" -n "$NAMESPACE" &>/dev/null; then
    warn "Secret '$SECRET_NAME' already exists — skipping. Run 'kubectl delete secret $SECRET_NAME' to recreate."
    return
  fi

  info "DB secrets not found. Enter connection details (input is hidden):"
  read -rp "  DB_HOST     : " DB_HOST
  read -rp "  DB_PORT     : " DB_PORT
  read -rp "  DB_USER     : " DB_USER
  read -rsp "  DB_PASSWORD : " DB_PASSWORD; echo
  read -rp "  DB_NAME     : " DB_NAME

  kubectl create secret generic "$SECRET_NAME" \
    --from-literal=DB_HOST="$DB_HOST" \
    --from-literal=DB_PORT="$DB_PORT" \
    --from-literal=DB_USER="$DB_USER" \
    --from-literal=DB_PASSWORD="$DB_PASSWORD" \
    --from-literal=DB_NAME="$DB_NAME" \
    -n "$NAMESPACE"
  info "Secret '$SECRET_NAME' created."
}

# ── deploy ────────────────────────────────────────────────────────────────────
deploy() {
  check_deps

  # 1. Start Minikube if not running
  info "Checking Minikube status..."
  if ! minikube status --format='{{.Host}}' 2>/dev/null | grep -q "Running"; then
    info "Starting Minikube..."
    minikube start --driver=docker --memory=2048 --cpus=2
  else
    info "Minikube already running."
  fi

  # 2. Point Docker CLI at Minikube's daemon so the image is visible to k8s
  info "Switching Docker context to Minikube daemon..."
  eval "$(minikube docker-env)"

  # 3. Build image inside Minikube's Docker
  info "Building Docker image '${IMAGE_NAME}:${IMAGE_TAG}'..."
  docker build -t "${IMAGE_NAME}:${IMAGE_TAG}" .
  info "Image built."

  # 4. Apply secrets (prompts if missing)
  apply_secrets

  # 5. Apply k8s manifests
  info "Applying Kubernetes manifests..."
  kubectl apply -f k8s/deployment-local.yaml -n "$NAMESPACE"
  kubectl apply -f k8s/service-nodeport.yaml  -n "$NAMESPACE"

  # 6. Wait for rollout
  info "Waiting for deployment to be ready..."
  kubectl rollout status deployment/shyaway-dashboard -n "$NAMESPACE" --timeout=120s

  # 7. Print access URL
  echo ""
  info "Deployment complete!"
  MINIKUBE_IP=$(minikube ip)
  echo -e "  ${GREEN}Dashboard URL:${NC}  http://${MINIKUBE_IP}:30851"
  echo ""
  echo "  To open in browser: minikube service shyaway-dashboard-service --url"
}

# ── teardown ──────────────────────────────────────────────────────────────────
teardown() {
  info "Deleting Kubernetes resources..."
  kubectl delete -f k8s/deployment-local.yaml --ignore-not-found
  kubectl delete -f k8s/service-nodeport.yaml  --ignore-not-found
  kubectl delete secret "$SECRET_NAME" --ignore-not-found
  info "Stopping Minikube..."
  minikube stop
  info "Teardown complete."
}

# ── status ────────────────────────────────────────────────────────────────────
status() {
  echo "── Minikube ──────────────────────────────────────────"
  minikube status || true
  echo ""
  echo "── Pods ──────────────────────────────────────────────"
  kubectl get pods -n "$NAMESPACE" -l app=shyaway-dashboard -o wide
  echo ""
  echo "── Service ───────────────────────────────────────────"
  kubectl get svc shyaway-dashboard-service -n "$NAMESPACE"
  echo ""
  echo "── Logs (last 30 lines) ──────────────────────────────"
  kubectl logs -n "$NAMESPACE" -l app=shyaway-dashboard --tail=30 || true
}

# ── entrypoint ────────────────────────────────────────────────────────────────
case "${1:-deploy}" in
  deploy)   deploy   ;;
  teardown) teardown ;;
  status)   status   ;;
  *) echo "Usage: $0 [deploy|teardown|status]"; exit 1 ;;
esac
