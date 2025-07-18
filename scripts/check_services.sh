#!/bin/bash
# Query /health and /ready until success or timeout.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# Load environment variables if not already set
if [ -f "$ROOT_DIR/secrets.env" ]; then
    set -a
    # shellcheck source=/dev/null
    source "$ROOT_DIR/secrets.env"
    set +a
fi


# Poll a service every second until both endpoints respond or a timeout occurs.
wait_for_service() {
    local base="${1%/}"
    local timeout="${2:-30}"
    local start
    start=$(date +%s)
    printf 'Waiting for %s...\n' "$base"
    while true; do
        local ok=1
        for path in health ready; do
            if ! curl -fsS -m 5 "$base/$path" >/dev/null; then
                ok=0
                break
            fi
        done
        if [ "$ok" -eq 1 ]; then
            printf '%s is healthy.\n' "$base"
            return 0
        fi
        if [ $(( $(date +%s) - start )) -ge "$timeout" ]; then
            printf 'Timeout waiting for %s\n' "$base" >&2
            return 1
        fi
        sleep 1
    done
}

main() {
    local timeout="${CHECK_TIMEOUT:-30}"
    if [ "$#" -gt 0 ]; then
        for url in "$@"; do
            wait_for_service "$url" "$timeout" || return 1
        done
    else
        for url in "$GLM_API_URL" "${DEEPSEEK_URL:-}" "${MISTRAL_URL:-}" "${KIMI_K2_URL:-}"; do
            [ -n "$url" ] || continue
            wait_for_service "$url" "$timeout" || return 1
        done
    fi
}

main "$@"
