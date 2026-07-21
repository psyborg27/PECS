#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/config/install_root.json"
INSTALL_ROOT=""
INSTALL_PYTHON=""
PECS_EXE=""
PECS_DAEMON_EXE=""

if [[ -f "$CONFIG_FILE" ]]; then
  PYTHON_CMD="python3"
  if ! command -v "$PYTHON_CMD" >/dev/null 2>&1; then
    PYTHON_CMD="python"
  fi
  if command -v "$PYTHON_CMD" >/dev/null 2>&1; then
    eval "$("$PYTHON_CMD" - "$CONFIG_FILE" <<'PY'
import json, pathlib, sys, shlex
path = pathlib.Path(sys.argv[1])
try:
    data = json.loads(path.read_text(encoding='utf-8'))
except Exception:
    data = {}
for key in ["install_root", "python_path"]:
    value = str(data.get(key, "") or "")
    print(f"{key.upper()}={shlex.quote(value)}")
console = data.get("console_scripts", {}) or {}
value = str(console.get("pecs", "") or "")
print(f"PECS={shlex.quote(value)}")
value = str(console.get("pecs-pro-daemon", "") or "")
print(f"PECS_PRO_DAEMON={shlex.quote(value)}")
PY
    )"
  fi
  INSTALL_ROOT="${INSTALL_ROOT:-}"
  INSTALL_PYTHON="${PYTHON_PATH:-}"
  PECS_EXE="${PECS:-}"
  PECS_DAEMON_EXE="${PECS_PRO_DAEMON:-}"
fi

if [[ -n "$PECS_EXE" && -x "$PECS_EXE" ]]; then
  exec "$PECS_EXE" "$@"
fi
if command -v pecs >/dev/null 2>&1; then
  exec pecs "$@"
fi
if [[ -n "$INSTALL_PYTHON" && -x "$INSTALL_PYTHON" ]]; then
  exec "$INSTALL_PYTHON" -m workspace_bridge_cli "$@"
fi
echo "ERROR: Could not resolve PECS runtime from install root or PATH." >&2
echo "Expected install root: $INSTALL_ROOT" >&2
exit 1
