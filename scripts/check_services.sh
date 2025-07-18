#!/bin/bash
# Query /health and /ready for each configured LLM service.
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

check_service() {
    local base="${1%/}"
    for path in health ready; do
        if ! curl -fsS -m 5 "$base/$path" >/dev/null; then
            echo "Service at $base failed $path check" >&2
            return 1
        fi
    done
}

failed=0
for url in "$GLM_API_URL" "${DEEPSEEK_URL:-}" "${MISTRAL_URL:-}" "${KIMI_K2_URL:-}"; do
    [ -n "$url" ] || continue
    echo "Checking $url..."
    if ! check_service "$url"; then
        echo "Service $url not responding" >&2
        failed=1
    fi
done

if [ "$failed" -ne 0 ]; then
    exit 1
fi

echo "All services are healthy."
