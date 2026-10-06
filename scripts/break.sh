#!/usr/bin/env bash
# Make /health return 503 so Prometheus/Grafana show northfield_health=0.
set -euo pipefail
cd "$(dirname "$0")/.."
docker compose exec -T app sh -c 'true'
# Recreate with fail flag
STATUS_FAIL=1 docker compose up -d --no-deps --force-recreate app
sleep 2
curl -s -o /tmp/h.json -w "%{http_code}" http://127.0.0.1:8080/health || true
echo
echo "break complete: expect 503"
