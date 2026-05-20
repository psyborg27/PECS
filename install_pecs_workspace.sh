#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="${1:-}"

function error_exit() {
  echo "ERROR: $1" >&2
  echo "Copy the full error output, include OS/version, branch name, and report the issue on GitHub." >&2
  exit 1
}

function prompt_workspace_root() {
  while true; do
    if [[ -z "$WORKSPACE_ROOT" ]]; then
      read -r -p "Enter the target workspace root path: " WORKSPACE_ROOT
    fi

    if [[ -z "$WORKSPACE_ROOT" ]]; then
      echo "Workspace path is required." >&2
      continue
    fi

    if [[ ! -d "$WORKSPACE_ROOT" ]]; then
      echo "Workspace path does not exist: $WORKSPACE_ROOT" >&2
      WORKSPACE_ROOT=""
      continue
    fi

    if [[ ! -w "$WORKSPACE_ROOT" ]]; then
      echo "Workspace path is not writable: $WORKSPACE_ROOT" >&2
      WORKSPACE_ROOT=""
      continue
    fi

    WORKSPACE_ROOT="$(cd "$WORKSPACE_ROOT" && pwd)"
    break
  done
}

function confirm_pecs_visibility() {
  local step=0
  while true; do
    read -r -p "Is the .pecs folder visible in the workspace explorer? [y/N] " answer
    case "$answer" in
      [Yy]*)
        return 0
        ;;
      [Nn]*)
        echo "Please re-enter the correct workspace root path." >&2
        read -r -p "Workspace root: " WORKSPACE_ROOT
        if [[ -z "$WORKSPACE_ROOT" ]]; then
          error_exit "Installer aborted by user."
        fi
        prompt_workspace_root
        mkdir -p "$WORKSPACE_ROOT/.pecs"
        ;;
      *)
        echo "Please answer y or n."
        ;;
    esac

    step=$((step + 1))
    if [[ $step -ge 3 ]]; then
      error_exit "Unable to confirm .pecs visibility. Please verify the workspace path and retry."
    fi
  done
}

trap 'error_exit "Installer failed at line $LINENO."' ERR

# --- Install-root safety checks ---
UNSTABLE_ROOT=0
case "$SCRIPT_DIR" in
  *Downloads*|*Desktop*|/tmp/*|/private/tmp/*|/Volumes/*)
    echo "WARNING: PECS is being installed from an unstable or transient location: $SCRIPT_DIR" >&2
    echo "It is strongly recommended to install PECS in a stable, user-owned directory such as ~/Developer/PECS or ~/Applications/PECS." >&2
    UNSTABLE_ROOT=1
    ;;
esac

prompt_workspace_root
mkdir -p "$WORKSPACE_ROOT/.pecs"
echo "Created or verified workspace integration folder: $WORKSPACE_ROOT/.pecs"
confirm_pecs_visibility

echo "Checking required Python runtime..."
PYTHON_EXEC="python3"
if ! command -v "$PYTHON_EXEC" >/dev/null 2>&1; then
  PYTHON_EXEC="python"
fi
if ! command -v "$PYTHON_EXEC" >/dev/null 2>&1; then
  error_exit "Python is not available on PATH. Install Python 3 or ensure python/py is in PATH."
fi

echo "Bootstrapping workspace: $WORKSPACE_ROOT"
cd "$SCRIPT_DIR"
"$PYTHON_EXEC" -m workspace_bridge_cli bootstrap-workspace "$WORKSPACE_ROOT" --repo-root "$SCRIPT_DIR" --upgrade

echo "Workspace bootstrap completed successfully."
if [[ $UNSTABLE_ROOT -eq 1 ]]; then
  echo "WARNING: PECS was installed from an unstable location. Move to a stable directory for persistent use." >&2
fi

echo "To verify, run: $PYTHON_EXEC -m workspace_bridge_cli status \"$WORKSPACE_ROOT\""
