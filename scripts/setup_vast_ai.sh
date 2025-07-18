#!/bin/bash
# Setup script for Vast.ai instances
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$SCRIPT_DIR/.."

# install system dependencies
apt-get update
apt-get install -y ffmpeg sox
apt-get clean

# install Python packages
pip install -r "$REPO_ROOT/requirements.txt"

# create persistent directories
mkdir -p "$REPO_ROOT/INANNA_AI/models"
mkdir -p "$REPO_ROOT/output"
mkdir -p "$REPO_ROOT/logs" "$REPO_ROOT/data"

# download optional models
if [ -n "${DOWNLOAD_MODELS:-}" ]; then
    for model in $DOWNLOAD_MODELS; do
        python "$REPO_ROOT/download_models.py" "$model" || true
    done
fi

# backward compatibility flag
if [ "$1" = "--download" ]; then
    python "$REPO_ROOT/download_models.py" deepseek || true
fi
