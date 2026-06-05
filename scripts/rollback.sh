#!/bin/bash
set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration — must match values in deploy.sh
# ---------------------------------------------------------------------------
DEPLOY_PATH="${DEPLOY_PATH:-/home/azureuser/dev/elie-platform/ai/backend}"

REGISTRY="${REGISTRY:-myregistry.azurecr.io}"
IMAGE_NAME="${IMAGE_NAME:-test-app}"
COMPOSE_FILE="${COMPOSE_FILE:-$DEPLOY_PATH/docker-compose.yml}"
VERSION_FILE="${VERSION_FILE:-$DEPLOY_PATH/.previous_version}"
HEALTH_URL="${HEALTH_URL:-http://localhost:80/health}"
HEALTH_RETRIES="${HEALTH_RETRIES:-10}"
HEALTH_INTERVAL="${HEALTH_INTERVAL:-6}"
LOG_FILE="${LOG_FILE:-$DEPLOY_PATH/deploy.log}"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ROLLBACK] $*" | tee -a "$LOG_FILE"
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
# Step 1: Read the previous stable image tag
# ---------------------------------------------------------------------------
log "=== Starting rollback ==="

if [ ! -f "$VERSION_FILE" ]; then
  die "No previous version file found at $VERSION_FILE. Cannot rollback."
fi

PREVIOUS_TAG=$(cat "$VERSION_FILE")

if [ -z "$PREVIOUS_TAG" ]; then
  die "Previous version file is empty — no stable baseline to roll back to."
fi

log "Rolling back to image tag: $PREVIOUS_TAG"

# ---------------------------------------------------------------------------
# Step 2: Pin the compose file to the previous image tag
#
# This rewrites the image line in docker-compose.yml temporarily so Docker
# Compose pulls and runs the specific previous version, not `latest`.
# ---------------------------------------------------------------------------
COMPOSE_BACKUP="${COMPOSE_FILE}.rollback.bak"
cp "$COMPOSE_FILE" "$COMPOSE_BACKUP"
log "Compose file backed up to $COMPOSE_BACKUP"

# Replace the image tag in the compose file with the previous version tag
sed -i "s|$REGISTRY/$IMAGE_NAME:.*|$REGISTRY/$IMAGE_NAME:$PREVIOUS_TAG|g" "$COMPOSE_FILE" \
  || die "Failed to pin compose file to previous tag."

log "Compose file updated to use image: $REGISTRY/$IMAGE_NAME:$PREVIOUS_TAG"

# ---------------------------------------------------------------------------
# Step 3: Pull the previous image (should already be cached, but ensure it)
# ---------------------------------------------------------------------------
log "Pulling previous image: $REGISTRY/$IMAGE_NAME:$PREVIOUS_TAG"
docker pull "$REGISTRY/$IMAGE_NAME:$PREVIOUS_TAG" \
  || die "Failed to pull previous image from registry."

# ---------------------------------------------------------------------------
# Step 4: Restart the service with the previous image
# ---------------------------------------------------------------------------
log "Restarting service with previous image..."
docker compose -f "$COMPOSE_FILE" up -d --force-recreate \
  || die "docker compose up failed during rollback."

# ---------------------------------------------------------------------------
# Step 5: Health check the rolled-back deployment
# ---------------------------------------------------------------------------
if ! health_check; then
  log "CRITICAL: Rollback also failed health check."
  log "Restoring compose file from backup: $COMPOSE_BACKUP"
  cp "$COMPOSE_BACKUP" "$COMPOSE_FILE"
  die "Rollback failed. Manual intervention required. Check $LOG_FILE for details."
fi

# ---------------------------------------------------------------------------
# Step 6: Restore the compose file from backup so `latest` is used next time
# ---------------------------------------------------------------------------
cp "$COMPOSE_BACKUP" "$COMPOSE_FILE"
rm -f "$COMPOSE_BACKUP"
log "Compose file restored to original (latest tag)."

log "Rollback to $PREVIOUS_TAG successful. Service is healthy."
log "=== Rollback complete ==="

# ---------------------------------------------------------------------------
# Optional: Send an alert (uncomment and configure as needed)
# ---------------------------------------------------------------------------
# curl -s -X POST "$SLACK_WEBHOOK_URL" \
#   -H 'Content-type: application/json' \
#   --data "{\"text\":\"[ROLLBACK] $IMAGE_NAME rolled back to $PREVIOUS_TAG on $(hostname). Check logs at $LOG_FILE\"}"
