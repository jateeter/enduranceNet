#!/usr/bin/env bash
# deploy.sh
# Build and deploy (or re-deploy) the EnduranceNet production stack.
#
# Usage:
#   export DOMAIN=www.endurance.net
#   export APPLICATION_SECRET=<min-32-char-random-secret>
#   ./scripts/deploy.sh

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

: "${DOMAIN:?Set DOMAIN env var (e.g. www.endurance.net)}"
: "${APPLICATION_SECRET:?Set APPLICATION_SECRET env var (min 32 chars)}"

if [[ ${#APPLICATION_SECRET} -lt 32 ]]; then
  echo "❌  APPLICATION_SECRET must be at least 32 characters for security." >&2
  exit 1
fi

echo "🔨  Building Docker images…"
docker compose -f "$ROOT/docker-compose.yml" -f "$ROOT/docker-compose.prod.yml" \
  build --pull --no-cache

echo "🔄  Replacing running containers with zero-downtime rolling update…"
docker compose -f "$ROOT/docker-compose.yml" -f "$ROOT/docker-compose.prod.yml" \
  up -d --remove-orphans

echo ""
echo "✅  EnduranceNet deployed!"
echo "    URL : https://$DOMAIN"
echo "    API : https://$DOMAIN/api/health"
docker compose -f "$ROOT/docker-compose.yml" -f "$ROOT/docker-compose.prod.yml" ps
