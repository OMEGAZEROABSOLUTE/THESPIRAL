#!/bin/bash
# Setup GLM environment and directories
set -e

# install Python dependencies
pip install -r requirements.txt

# create directories for data and logs
mkdir -p /INANNA_AI
mkdir -p /QNL_LANGUAGE
mkdir -p /audit_logs

# copy ethics guidelines
cp "$(dirname "$0")/../ETHICS_GUIDELINES.md" /INANNA_AI/ETHICS_GUIDELINES.md
cp "$(dirname "$0")/../ETHICS_GUIDELINES.md" /QNL_LANGUAGE/ETHICS_GUIDELINES.md

cat <<'EON' > /audit_logs/README.txt
Audit logs for monitoring system behavior.
EON

printf "Setup complete.\n"
