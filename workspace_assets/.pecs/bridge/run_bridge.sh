#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_ROOT="${1:-.}"
COMMAND="${2:-refresh}"
BRIDGE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$BRIDGE_DIR/../config/install_root.json"
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

if [[ -n "$INSTALL_ROOT" && -f "$INSTALL_ROOT/.venv/bin/activate" ]]; then
  source "$INSTALL_ROOT/.venv/bin/activate"
fi

if [[ "$WORKSPACE_ROOT" == "refresh" || "$WORKSPACE_ROOT" == "validate" ]]; then
    COMMAND="$WORKSPACE_ROOT"
    WORKSPACE_ROOT="$(pwd)"
fi

cd "$WORKSPACE_ROOT"
PYTHON_CMD="python3"
if ! command -v "$PYTHON_CMD" >/dev/null 2>&1; then
  PYTHON_CMD="python"
fi
"$PYTHON_CMD" .pecs/bridge/run_bridge.py "$COMMAND" --workspace "$WORKSPACE_ROOT"
