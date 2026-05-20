#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_ROOT="${1:-.}"
WORKSPACE_ROOT="$(cd "$WORKSPACE_ROOT" && pwd)"

LAUNCHER="$WORKSPACE_ROOT/.pecs/run_pecs_daemon.sh"
if [[ -x "$LAUNCHER" ]]; then
  exec "$LAUNCHER" "$WORKSPACE_ROOT"
fi

echo "ERROR: Workspace daemon launcher missing: $LAUNCHER" >&2
echo "Run install-workspace-assets or bootstrap-workspace first." >&2
exit 1
