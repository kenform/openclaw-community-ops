#!/usr/bin/env bash
set -euo pipefail
ROLE="${1:-}"
if [[ -z "$ROLE" ]]; then
  echo "Usage: $0 <role>" >&2
  exit 2
fi
BASE="/home/openclawuser/.openclaw/workspace"
ENV_FILE="$BASE/config/agent-commands.env"
if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing $ENV_FILE" >&2
  exit 3
fi
# shellcheck disable=SC1090
source "$ENV_FILE"
KEY="AGENT_CMD_${ROLE^^}"
CMD="${!KEY:-}"
if [[ -z "$CMD" ]]; then
  echo "No command configured for role '$ROLE' (expected $KEY in $ENV_FILE)" >&2
  exit 4
fi
exec /usr/bin/env bash -lc "$CMD"
