#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 [workspace-root] <source> <message>"
  echo "Example (explicit path): $0 \"/Users/raj/Downloads/auto OCR app\" copilot \"session started\""
  echo "Example (current directory): $0 copilot \"session started\""
  exit 1
fi

WORKSPACE_ROOT=""
SOURCE=""
MESSAGE=""

if [[ $# -ge 3 ]]; then
  WORKSPACE_ROOT="$1"
  SOURCE="$2"
  MESSAGE="$3"
else
  WORKSPACE_ROOT="$PWD"
  SOURCE="$1"
  MESSAGE="$2"
fi

# Treat placeholder path as "use current directory".
if [[ "$WORKSPACE_ROOT" == "/path/to/workspace" ]]; then
  WORKSPACE_ROOT="$PWD"
fi

# If first arg is not an existing path, treat call style as: <source> <message>
if [[ ! -d "$WORKSPACE_ROOT" ]]; then
  if [[ $# -ge 2 ]]; then
    WORKSPACE_ROOT="$PWD"
    SOURCE="$1"
    MESSAGE="$2"
  fi
fi

if [[ ! -d "$WORKSPACE_ROOT" ]]; then
  echo "Workspace root does not exist: $WORKSPACE_ROOT"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$WORKSPACE_ROOT"
if [[ -f ".venv/bin/activate" ]]; then
  source ".venv/bin/activate"
fi

PYTHON_CMD="python3"
if ! command -v "$PYTHON_CMD" >/dev/null 2>&1; then
  PYTHON_CMD="python"
fi
if ! command -v "$PYTHON_CMD" >/dev/null 2>&1; then
  echo "ERROR: Python is not available on PATH." >&2
  exit 1
fi

"$PYTHON_CMD" "$SCRIPT_DIR/append_ai_chat_history.py" "$WORKSPACE_ROOT" --source "$SOURCE" --message "$MESSAGE"
