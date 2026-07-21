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

WORKSPACE_ROOT="${1:-.}"
WORKSPACE_ROOT="$(cd "$WORKSPACE_ROOT" && pwd)"
LOG_DIR="$WORKSPACE_ROOT/.pecs"
LOG_FILE="$LOG_DIR/daemon.log"
PID_FILE="$LOG_DIR/daemon.pid"
HEALTH_FILE="$LOG_DIR/daemon_health.json"
STARTUP_TIMEOUT="${PECS_DAEMON_STARTUP_TIMEOUT:-30}"
STARTUP_INTERVAL="${PECS_DAEMON_STARTUP_INTERVAL:-0.5}"
mkdir -p "$LOG_DIR"
check_daemon_health() {
  if [[ ! -f "$HEALTH_FILE" ]]; then
    return 1
  fi
  if ! command -v "$PYTHON_CMD" >/dev/null 2>&1; then
    return 1
  fi
  local status
  status="$($PYTHON_CMD - "$HEALTH_FILE" <<'PY'
from pathlib import Path
import json, sys

path = Path(sys.argv[1])
try:
    data = json.loads(path.read_text(encoding='utf-8'))
except Exception:
    sys.exit(1)
if (
    data.get('status') == 'healthy'
    and data.get('retrieval_ready') is True
    and data.get('topology_ready') is True
    and data.get('continuity_ready') is True
):
    sys.stdout.write('healthy')
PY
)"
  [[ "$status" == "healthy" ]]
}
if [[ -f "$PID_FILE" ]]; then
  pid="$(tr -d '"[:space:]' < "$PID_FILE")"
  if [[ "$pid" =~ ^[0-9]+$ ]] && kill -0 "$pid" 2>/dev/null; then
    echo "PECS daemon is already running for workspace: $WORKSPACE_ROOT (pid=$pid)"
    exit 0
  fi
  rm -f "$PID_FILE"
fi
resolve_cmd() {
  if [[ -n "$PECS_DAEMON_EXE" && -x "$PECS_DAEMON_EXE" ]]; then
    echo "$PECS_DAEMON_EXE"
    return 0
  fi
  if command -v pecs-pro-daemon >/dev/null 2>&1; then
    echo "pecs-pro-daemon"
    return 0
  fi
  if [[ -n "$INSTALL_PYTHON" && -x "$INSTALL_PYTHON" ]]; then
    echo "$INSTALL_PYTHON"
    return 0
  fi
  return 1
}
DAEMON_CMD="$(resolve_cmd)"
if [[ -z "$DAEMON_CMD" ]]; then
  echo "ERROR: Could not resolve PECS daemon runtime from install root or PATH." >&2
  echo "Expected install root: $INSTALL_ROOT" >&2
  exit 1
fi
if [[ "$DAEMON_CMD" == "$INSTALL_PYTHON" ]]; then
  DAEMON_ARGS=(-m run_pecs_daemon "$WORKSPACE_ROOT")
else
  DAEMON_ARGS=("$WORKSPACE_ROOT")
fi
cd "$WORKSPACE_ROOT"
if command -v setsid >/dev/null 2>&1; then
  setsid "$DAEMON_CMD" "${DAEMON_ARGS[@]}" >> "$LOG_FILE" 2>&1 &
else
  nohup "$DAEMON_CMD" "${DAEMON_ARGS[@]}" >> "$LOG_FILE" 2>&1 &
fi
launcher_pid=$!
end_time=$(( $(date +%s) + STARTUP_TIMEOUT ))
while [[ $(date +%s) -lt $end_time ]]; do
  if [[ -f "$PID_FILE" ]]; then
    pid="$(tr -d '"[:space:]' < "$PID_FILE")"
    if [[ "$pid" =~ ^[0-9]+$ ]] && kill -0 "$pid" 2>/dev/null; then
      echo "Daemon started successfully (PID $pid)"
      exit 0
    fi
  fi
  if ! kill -0 "$launcher_pid" 2>/dev/null; then
    echo "Daemon launcher process exited before startup. Check $LOG_FILE" >&2
    tail -n 20 "$LOG_FILE" >&2 || true
    exit 1
  fi
  sleep "$STARTUP_INTERVAL"
done
echo "Daemon startup timed out waiting for daemon readiness. See $LOG_FILE" >&2
tail -n 20 "$LOG_FILE" >&2 || true
if [[ -f "$HEALTH_FILE" ]]; then
  echo "--- health artifact ---" >&2
  cat "$HEALTH_FILE" >&2 || true
fi
exit 1
