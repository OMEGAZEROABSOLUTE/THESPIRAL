#!/bin/bash
# Stop Crown services and video stream.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

stop_container() {
    local name="$1"
    if command -v docker >/dev/null 2>&1 && docker ps --format '{{.Names}}' | grep -wq "$name"; then
        docker stop "$name" >/dev/null
        echo "Stopped container $name"
    fi
}

stop_pid() {
    local file="$1"
    if [ -f "$file" ]; then
        local pid
        pid=$(cat "$file")
        if kill "$pid" 2>/dev/null; then
            echo "Stopped process $pid from $file"
        fi
        rm -f "$file"
    fi
}

stop_container glm_service
stop_container deepseek_service
stop_container mistral_service
stop_container kimi_k2_service

for f in glm_service.pid deepseek_service.pid mistral_service.pid kimi_k2_service.pid video_stream.pid; do
    stop_pid "$f"
done

pkill -f video_stream.py 2>/dev/null || true
pkill -f openai.api_server 2>/dev/null || true

printf 'Crown services terminated.\n'
