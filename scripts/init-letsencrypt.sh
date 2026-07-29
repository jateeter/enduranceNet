#!/usr/bin/env bash
# init-letsencrypt.sh
# Bootstrap Let's Encrypt TLS certificates using Certbot before starting
# the full production stack.  Run once on initial deployment.
#
# Usage:
#   export DOMAIN=www.endurance.net
#   export EMAIL=admin@endurance.net
#   ./scripts/init-letsencrypt.sh

set -euo pipefail

DOMAIN="${DOMAIN:?Set the DOMAIN environment variable first}"
EMAIL="${EMAIL:?Set the EMAIL environment variable first (used for cert expiry alerts)}"
STAGING="${STAGING:-0}"   # set to 1 to test against Let's Encrypt staging API

DATA_PATH="$(cd "$(dirname "$0")/.." && pwd)/nginx/ssl"
CERTBOT_WWW="$(cd "$(dirname "$0")/.." && pwd)/nginx/certbot-www"

mkdir -p "$DATA_PATH" "$CERTBOT_WWW"

# ── 1. Start nginx on port 80 only so Certbot can complete the ACME challenge ──
echo "⏳  Starting nginx for ACME challenge…"
docker compose up -d nginx

# ── 2. Obtain certificate ──────────────────────────────────────────────────────
STAGING_FLAG=""
[[ "$STAGING" == "1" ]] && STAGING_FLAG="--staging"

echo "🔐  Requesting certificate for $DOMAIN…"
docker run --rm \
  -v "$(cd "$(dirname "$0")/.." && pwd)/letsencrypt:/etc/letsencrypt" \
  -v "$CERTBOT_WWW:/var/www/certbot" \
  certbot/certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    $STAGING_FLAG \
    -d "$DOMAIN"

echo "✅  Certificate obtained. Now starting the full production stack…"

# ── 3. Launch the full production stack ────────────────────────────────────────
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

echo ""
echo "🚀  EnduranceNet is live at https://$DOMAIN"
