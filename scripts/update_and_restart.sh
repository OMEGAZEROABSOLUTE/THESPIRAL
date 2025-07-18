#!/usr/bin/env bash
# Update repository, install dependencies and restart containers
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_ROOT"

printf "Updating repository...\n"
git pull

printf "Installing dependencies...\n"
pip install -r requirements.txt

printf "Restarting containers...\n"
docker-compose pull
docker-compose down
docker-compose up -d

printf "Done.\n"
