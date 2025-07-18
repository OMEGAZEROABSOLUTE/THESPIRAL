#!/bin/bash
# Launch GLM model with environment setup
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

mkdir -p logs
LOG_FILE="logs/glm_service.log"
MAIN_LOG="logs/INANNA_AI.log"

log_failure() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - glm_service exited unexpectedly" >> "$MAIN_LOG"
}

# Load secrets
if [ -f "secrets.env" ]; then
    set -a
    source "secrets.env"
    set +a
else
    echo "secrets.env not found" >&2
    exit 1
fi

: "${HF_TOKEN?HF_TOKEN not set}"
: "${GLM_API_URL?GLM_API_URL not set}"
: "${GLM_API_KEY?GLM_API_KEY not set}"

MODEL_DIR="INANNA_AI/models/GLM-4.1V-9B"
if [ ! -d "$MODEL_DIR" ]; then
    python download_models.py glm41v_9b --int8
fi

WEIGHT_FILE=$(find "$MODEL_DIR" -type f \( -name '*.bin' -o -name '*.safetensors' \) | sort | head -n 1)
if [ -z "$WEIGHT_FILE" ]; then
    echo "No weights found in $MODEL_DIR" >&2
    exit 1
fi

if [ -n "${GLM_SHA256:-}" ]; then
    calc=$(sha256sum "$WEIGHT_FILE" | awk '{print $1}')
    if [ "$calc" != "$GLM_SHA256" ]; then
        echo "Checksum mismatch for $WEIGHT_FILE" >&2
        exit 1
    fi
else
    echo "GLM_SHA256 not set; skipping checksum validation" >&2
fi

if command -v docker >/dev/null 2>&1; then
    docker run --rm -v "$MODEL_DIR":/model -p 8001:8000 \
        -e GLM_API_URL="$GLM_API_URL" -e GLM_API_KEY="$GLM_API_KEY" \
        --name glm_service glm-service:latest \
        >"$LOG_FILE" 2>&1 &
else
    python -m vllm.entrypoints.openai.api_server \
        --model "$MODEL_DIR" --port 8001 \
        >"$LOG_FILE" 2>&1 &
fi || { log_failure; exit 1; }

printf '%s\n' "$MODEL_DIR"
