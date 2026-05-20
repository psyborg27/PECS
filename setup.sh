#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$SCRIPT_DIR"
WORKSPACE_ROOT="${1:-}"

function error_exit() {
  echo "ERROR: $1" >&2
  echo "Copy the full error output, include OS/version, branch name, and report the issue on GitHub." >&2
  exit 1
}

function prompt_workspace_root() {
  local value="${1:-}"
  while true; do
    if [[ -z "$value" ]]; then
      read -r -p "Enter the target workspace root path: " value
    fi

    if [[ -z "$value" ]]; then
      echo "Workspace path is required." >&2
      continue
    fi

    if [[ ! -d "$value" ]]; then
      echo "Workspace path does not exist: $value" >&2
      value=""
      continue
    fi

    if [[ ! -w "$value" ]]; then
      echo "Workspace path is not writable: $value" >&2
      value=""
      continue
    fi

    value="$(cd "$value" && pwd)"
    break
  done
  printf '%s' "$value"
}

function confirm_pecs_visibility() {
  local tries=0
  local answer
  while true; do
    read -r -p "Is the .pecs folder visible in the workspace explorer? [y/N] " answer
    case "$answer" in
      [Yy]*) return 0 ;; 
      [Nn]*)
        echo "Please re-enter the correct workspace root path." >&2
        WORKSPACE_ROOT="$(prompt_workspace_root)"
        mkdir -p "$WORKSPACE_ROOT/.pecs"
        ;;
      *)
        echo "Please answer y or n."
        ;;
    esac
    tries=$((tries + 1))
    if [[ $tries -ge 3 ]]; then
      error_exit "Unable to confirm .pecs visibility. Please verify the workspace path and retry."
    fi
  done
}

function find_python() {
  local candidate="python3"
  if command -v "$candidate" >/dev/null 2>&1; then
    printf '%s' "$candidate"
    return 0
  fi

  candidate="python"
  if command -v "$candidate" >/dev/null 2>&1; then
    printf '%s' "$candidate"
    return 0
  fi

  return 1
}

WORKSPACE_ROOT="$(prompt_workspace_root "$WORKSPACE_ROOT")"
mkdir -p "$WORKSPACE_ROOT/.pecs"
echo "Created or verified workspace integration folder: $WORKSPACE_ROOT/.pecs"
confirm_pecs_visibility

PYTHON_CMD="$(find_python || true)"
if [[ -z "$PYTHON_CMD" ]]; then
  error_exit "Python is not available on PATH. Install Python 3 or ensure python is available."
fi

echo "Using Python: $PYTHON_CMD"
cd "$REPO_ROOT"

if [[ ! -d ".venv" ]]; then
  echo "Creating Python virtual environment in .venv..."
  "$PYTHON_CMD" -m venv .venv
fi

VENV_PYTHON="$REPO_ROOT/.venv/bin/python"
if [[ ! -x "$VENV_PYTHON" ]]; then
  error_exit "Virtual environment python not found at $VENV_PYTHON"
fi

echo "Upgrading pip, setuptools, and wheel..."
"$VENV_PYTHON" -m pip install --upgrade pip setuptools wheel

if [[ -f "requirements.txt" ]]; then
  echo "Installing required dependencies..."
  "$VENV_PYTHON" -m pip install -r requirements.txt
fi

echo "Installing PECS-PRO in editable mode..."
"$VENV_PYTHON" -m pip install -e .

echo "Bootstrapping workspace: $WORKSPACE_ROOT"
"$VENV_PYTHON" -m workspace_bridge_cli bootstrap-workspace "$WORKSPACE_ROOT" --repo-root "$REPO_ROOT" --upgrade

echo "PECS onboarding completed successfully."
echo "Run: $VENV_PYTHON -m workspace_bridge_cli status \"$WORKSPACE_ROOT\""