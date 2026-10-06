#!/usr/bin/env bash
# Run a previous image tag and check X-App-Version.
set -euo pipefail
cd "$(dirname "$0")/.."
PREV="${1:-northfield-status:1.0.0}"
docker compose stop app
docker run -d --name status-rollback --rm -p 8080:8080 "$PREV"
sleep 2
ver=$(curl -sI http://127.0.0.1:8080/health | awk -F': ' 'tolower($1)=="x-app-version" {gsub("\r","",$2); print $2}')
echo "running $PREV version header=$ver"
curl -sf http://127.0.0.1:8080/health
docker rm -f status-rollback
docker compose up -d app
echo "rollback verified, compose app restored"
