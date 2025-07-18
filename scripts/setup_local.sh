#!/usr/bin/env bash
# Copy secrets.env.example to secrets.env and prompt for tokens/ports
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
EXAMPLE="$REPO_ROOT/secrets.env.example"
TARGET="$REPO_ROOT/secrets.env"

if [ ! -f "$EXAMPLE" ]; then
    echo "Example secrets file not found: $EXAMPLE" >&2
    exit 1
fi

if [ -f "$TARGET" ]; then
    read -p "secrets.env already exists, overwrite? [y/N] " ans
    case "$ans" in
        y|Y ) ;;
        * ) echo "Aborted."; exit 1;;
    esac
fi

cp "$EXAMPLE" "$TARGET"

prompt_var() {
    local var="$1"
    local default="$2"
    read -p "Enter $var [${default}]: " value
    value=${value:-$default}
    sed -i "s|^$var=.*|$var=$value|" "$TARGET"
}

# Tokens
prompt_var HF_TOKEN ""
prompt_var GITHUB_TOKEN ""
prompt_var OPENAI_API_KEY ""
prompt_var GLM_API_KEY ""
prompt_var GLM_COMMAND_TOKEN ""
prompt_var GLM_SHELL_KEY ""

# Ports / URLs
read -p "Port for GLM API [8001]: " port
port=${port:-8001}
sed -i "s|^GLM_API_URL=.*|GLM_API_URL=http://localhost:$port|" "$TARGET"

read -p "Port for GLM shell [8011]: " port
port=${port:-8011}
sed -i "s|^GLM_SHELL_URL=.*|GLM_SHELL_URL=http://localhost:$port|" "$TARGET"

read -p "Port for DeepSeek [8002]: " port
port=${port:-8002}
sed -i "s|^DEEPSEEK_URL=.*|DEEPSEEK_URL=http://localhost:$port|" "$TARGET"

read -p "Port for Mistral [8003]: " port
port=${port:-8003}
sed -i "s|^MISTRAL_URL=.*|MISTRAL_URL=http://localhost:$port|" "$TARGET"

read -p "Port for Kimi-K2 [8010]: " port
port=${port:-8010}
sed -i "s|^KIMI_K2_URL=.*|KIMI_K2_URL=http://localhost:$port|" "$TARGET"

printf "Secrets written to %s\n" "$TARGET"
