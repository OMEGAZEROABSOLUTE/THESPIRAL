#!/bin/bash
# Launch Crown services and start the console
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

if [ -f "secrets.env" ]; then
    set -a
    # shellcheck source=/dev/null
    source "secrets.env"
    set +a
else
    echo "secrets.env not found" >&2
    exit 1
fi

./crown_model_launcher.sh

if [ -f "launch_servants.sh" ]; then
    ./launch_servants.sh
fi

wait_port() {
    local port=$1
    printf 'Waiting for port %s...\n' "$port"
    while ! nc -z localhost "$port"; do
        sleep 1
    done
}

parse_port() {
    local url=$1
    local port="${url##*:}"
    echo "${port%%/*}"
}

main_port=$(parse_port "$GLM_API_URL")
wait_port "$main_port"

for url in "${DEEPSEEK_URL:-}" "${MISTRAL_URL:-}" "${KIMI_K2_URL:-}"; do
    if [[ "$url" == http://localhost:* || "$url" == http://127.0.0.1:* ]]; then
        wait_port "$(parse_port "$url")"
    fi
done

python console_interface.py
