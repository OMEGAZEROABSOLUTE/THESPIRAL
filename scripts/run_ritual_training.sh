#!/bin/bash
# Start the ritual training loop in the background
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_ROOT"

python ritual_trainer.py --run --loop >/dev/null 2>&1 &
PID=$!
echo $PID > ritual_training.pid
printf "Ritual training started (PID %s)\n" "$PID"
