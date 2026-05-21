#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="${1:-}"
OLD_IFS="$IFS"
ORIG_STTY=""
DEBUG_INSTALL="${DEBUG_INSTALL:-0}"

function error_exit() {
  echo "ERROR: $1" >&2
  echo "Copy the full error output, include OS/version, branch name, and report the issue on GitHub." >&2
  restore_terminal_state
  exit 1
}

function restore_terminal_state() {
  if [[ -t 0 ]]; then
    stty sane >/dev/null 2>&1 || true
    if [[ -n "${ORIG_STTY:-}" ]]; then
      stty "$ORIG_STTY" >/dev/null 2>&1 || true
    fi
  fi
}

function cleanup() {
  local exit_code=$?
  IFS="$OLD_IFS"
  restore_terminal_state
  return $exit_code
}

function handle_interrupt() {
  echo "\nInstaller interrupted by user." >&2
  restore_terminal_state
  exit 1
}

function handle_suspend() {
  restore_terminal_state
  trap - TSTP
  kill -TSTP "$$"
}

function handle_continue() {
  save_terminal_state
}

trap handle_interrupt INT TERM
trap handle_suspend TSTP
trap handle_continue CONT
trap cleanup EXIT

function save_terminal_state() {
  if [[ -t 0 ]]; then
    ORIG_STTY="$(stty -g 2>/dev/null || true)"
  fi
}

function normalize_workspace_path() {
  local raw="$1"
  local normalized="$raw"

  # Trim leading/trailing whitespace
  normalized="${normalized#${normalized%%[![:space:]]*}}"
  normalized="${normalized%${normalized##*[![:space:]]}}"

  # Remove surrounding quotes if present
  if [[ "${normalized:0:1}" == '"' && "${normalized: -1}" == '"' ]] || \
     [[ "${normalized:0:1}" == "'" && "${normalized: -1}" == "'" ]]; then
    normalized="${normalized:1:-1}"
  fi

  # Unescape escaped spaces for shell-style paths
  normalized="${normalized//\\ / }"

  # Expand tilde at the beginning of the path
  if [[ "$normalized" == "~" ]] || [[ "$normalized" == ~/* ]]; then
    normalized="${HOME}${normalized:1}"
  fi

  # Normalize trailing slashes except root
  if [[ "$normalized" != "/" ]]; then
    while [[ "$normalized" == */ ]]; do
      normalized="${normalized%/}"
    done
  fi

  printf '%s' "$normalized"
}

function log_path_diagnostics() {
  local raw="$1"
  local normalized="$2"
  local expanded="$3"
  local exists="$4"

  printf 'RAW INPUT: %s\n' "$raw" >&2
  printf 'NORMALIZED PATH: %s\n' "$normalized" >&2
  printf 'EXPANDED PATH: %s\n' "$expanded" >&2
  printf 'DIRECTORY EXISTS: %s\n' "$exists" >&2
}

function prompt_workspace_root() {
  save_terminal_state
  local prompt_message="Enter the target workspace root path"
  local previous_input=""
  local retries=0
  local max_retries=3

  while true; do
    if [[ -n "$WORKSPACE_ROOT" ]]; then
      previous_input="$WORKSPACE_ROOT"
    fi

    echo "Valid examples: '/Users/raj/Downloads/auto OCR app'  \"/Users/raj/Downloads/auto OCR app\"  ~/Downloads/auto OCR app" >&2
    if [[ -n "$previous_input" ]]; then
      echo "Previous entry: $previous_input" >&2
    fi

    local read_status=0
    if [[ -n "${BASH_VERSION:-}" ]] && [[ "${BASH_VERSINFO[0]:-0}" -ge 4 ]]; then
      read -r -e -i "$previous_input" -p "$prompt_message: " WORKSPACE_ROOT
      read_status=$?
    elif [[ -n "${BASH_VERSION:-}" ]]; then
      read -r -e -p "$prompt_message: " WORKSPACE_ROOT
      read_status=$?
    else
      printf '%s: ' "$prompt_message"
      IFS= read -r WORKSPACE_ROOT
      read_status=$?
    fi

    if [[ $read_status -ne 0 || -z "$WORKSPACE_ROOT" ]]; then
      if [[ $read_status -ne 0 ]]; then
        restore_terminal_state
        echo "\nInstaller cancelled by user." >&2
        exit 1
      fi
      echo "Workspace path is required." >&2
      previous_input=""
      retries=$((retries + 1))
      if [[ $retries -ge $max_retries ]]; then
        echo "Workspace path was invalid too many times. Terminating installer." >&2
        exit 1
      fi
      continue
    fi

    if [[ "$WORKSPACE_ROOT" == *$'\e'* ]]; then
      restore_terminal_state
      echo "\nInstaller cancelled by user." >&2
      exit 1
    fi

    local raw_input="$WORKSPACE_ROOT"
    local normalized_input
    normalized_input="$(normalize_workspace_path "$raw_input")"
    WORKSPACE_ROOT="$normalized_input"

    if [[ -z "$WORKSPACE_ROOT" ]]; then
      echo "Workspace path is required." >&2
      previous_input="$raw_input"
      retries=$((retries + 1))
      if [[ $retries -ge $max_retries ]]; then
        echo "Workspace path was invalid too many times. Terminating installer." >&2
        exit 1
      fi
      continue
    fi

    if [[ ! -d "$WORKSPACE_ROOT" ]]; then
      log_path_diagnostics "$raw_input" "$WORKSPACE_ROOT" "$WORKSPACE_ROOT" false
      echo "Workspace path does not exist: $WORKSPACE_ROOT" >&2
      previous_input="$raw_input"
      retries=$((retries + 1))
      if [[ $retries -ge $max_retries ]]; then
        echo "Workspace path was invalid too many times. Terminating installer." >&2
        exit 1
      fi
      continue
    fi

    if [[ ! -w "$WORKSPACE_ROOT" ]]; then
      log_path_diagnostics "$raw_input" "$WORKSPACE_ROOT" "$WORKSPACE_ROOT" false
      echo "Workspace path is not writable: $WORKSPACE_ROOT" >&2
      previous_input="$raw_input"
      retries=$((retries + 1))
      if [[ $retries -ge $max_retries ]]; then
        echo "Workspace path was invalid too many times. Terminating installer." >&2
        exit 1
      fi
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
