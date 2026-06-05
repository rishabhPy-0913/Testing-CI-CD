#!/bin/bash
set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration — override via environment variables or edit defaults below
# ---------------------------------------------------------------------------
DEPLOY_PATH="${DEPLOY_PATH:-/home/azureuser/dev/elie-platform/ai/backend/Testing-CI-CD}"

REGISTRY="${REGISTRY:-myregistry.azurecr.io}"
IMAGE_NAME="${IMAGE_NAME:-test-app}"
COMPOSE_FILE="${COMPOSE_FILE:-$DEPLOY_PATH/docker-compose.yml}"
CONFIG_REPO="${CONFIG_REPO:-https://${GH_PAT_RISHABH}@github.com/rishabhPy-0913/Testing-CI-CD.git}"
CONFIG_DIR="${CONFIG_DIR:-$DEPLOY_PATH}"
VERSION_FILE="${VERSION_FILE:-$DEPLOY_PATH/.previous_version}"
HEALTH_URL="${HEALTH_URL:-http://localhost:80/health}"
HEALTH_RETRIES="${HEALTH_RETRIES:-10}"
HEALTH_INTERVAL="${HEALTH_INTERVAL:-6}"
LOG_FILE="${LOG_FILE:-$DEPLOY_PATH/deploy.log}"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

die() {
  log "ERROR: $*"
  exit 1
}

health_check() {
  local attempt=1
  while [ "$attempt" -le "$HEALTH_RETRIES" ]; do
    log "Health check attempt $attempt/$HEALTH_RETRIES..."
    if curl -sf --max-time 5 "$HEALTH_URL" > /dev/null 2>&1; then
      log "Health check passed."
      return 0
    fi
    sleep "$HEALTH_INTERVAL"
    attempt=$((attempt + 1))
  done
  log "Health check failed after $HEALTH_RETRIES attempts."
  return 1
}

# ---------------------------------------------------------------------------
# Step 1: Record the currently running image tag as the previous version
# ---------------------------------------------------------------------------
log "=== Starting deployment ==="

CURRENT_TAG=$(docker inspect \
  --format='{{index .Config.Image}}' \
  "$(docker compose -f "$COMPOSE_FILE" ps -q app 2>/dev/null | head -1)" \
  2>/dev/null | awk -F: '{print $NF}' || echo "")

if [ -n "$CURRENT_TAG" ]; then
  log "Current running image tag: $CURRENT_TAG"
  echo "$CURRENT_TAG" > "$VERSION_FILE"
else
  log "No previous deployment detected — fresh install."
  echo "" > "$VERSION_FILE"
fi

# ---------------------------------------------------------------------------
# Step 2: Pull latest deployment config from config repo
# ---------------------------------------------------------------------------
log "Pulling latest deployment config..."

if [ -d "$CONFIG_DIR/.git" ]; then
  git -C "$CONFIG_DIR" remote set-url origin "$CONFIG_REPO"
  git -C "$CONFIG_DIR" pull --rebase origin dev \
    || die "Failed to pull deployment config repo."
else
  git clone "$CONFIG_REPO" "$CONFIG_DIR" \
    || die "Failed to clone deployment config repo."
fi

# ---------------------------------------------------------------------------
# Step 3: Pull the latest Docker image from ACR
# ---------------------------------------------------------------------------
log "Pulling latest image: $REGISTRY/$IMAGE_NAME:latest"
docker compose -f "$COMPOSE_FILE" pull \
  || die "Failed to pull Docker image."

# ---------------------------------------------------------------------------
# Step 4: Bring up the new container
# ---------------------------------------------------------------------------
log "Deploying new container..."
docker compose -f "$COMPOSE_FILE" up -d --remove-orphans \
  || die "docker compose up failed."

# ---------------------------------------------------------------------------
# Step 5: Health check — trigger rollback on failure
# ---------------------------------------------------------------------------
if ! health_check; then
  log "Deployment unhealthy. Triggering rollback..."
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  bash "$SCRIPT_DIR/rollback.sh"
  exit 1
fi

# ---------------------------------------------------------------------------
# Step 6: Tag the new version as the new "previous" stable baseline
# ---------------------------------------------------------------------------
NEW_TAG=$(docker inspect \
  --format='{{index .Config.Image}}' \
  "$(docker compose -f "$COMPOSE_FILE" ps -q app 2>/dev/null | head -1)" \
  2>/dev/null | awk -F: '{print $NF}' || echo "latest")

log "Deployment successful. Running image tag: $NEW_TAG"
echo "$NEW_TAG" > "$VERSION_FILE"

log "=== Deployment complete ==="
