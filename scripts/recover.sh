#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
STATUS_FAIL=0 docker compose up -d --no-deps --force-recreate app
sleep 2
code=$(curl -s -o /tmp/h.json -w "%{http_code}" http://127.0.0.1:8080/health)
echo "$code $(cat /tmp/h.json)"
test "$code" = "200"
echo "recover verified"
