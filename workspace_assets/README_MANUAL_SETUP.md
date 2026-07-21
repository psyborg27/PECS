# PECS Manual Setup Guide

This guide is for users who want to install PECS into a workspace without using the auto-installer script.

## Persistent Infrastructure Notice

PECS is now persistent developer infrastructure. Do **NOT** install or run PECS from transient or unstable directories such as:
- Downloads
- Desktop
- /tmp or other temporary folders
- Removable/external drives

**Recommended install locations:**
- `~/Developer/PECS/`
- `~/Applications/PECS/`

PECS must reside in a stable, user-owned directory to ensure reliable operation and avoid accidental deletion or corruption. This is critical for continuity and daemon reliability.

## Dependency Requirements

- Python 3.9 or newer
- `watchdog` Python package (required for daemon monitoring)
- `pip`, `setuptools`, and `wheel` for install bootstrap

## Automated Onboarding Scripts

If you prefer a single onboarding entrypoint, use the provided scripts from the PECS repository root:

- `./setup.sh <workspace-root>` on macOS/Linux
- `.\setup.ps1 <workspace-root>` on Windows PowerShell
- `setup.bat <workspace-root>` on Windows CMD

These scripts create the repository virtual environment, install PECS in editable mode, install workspace assets, start the daemon, refresh continuity state, and validate the workspace.

## Installation Health Check

After manual setup, verify PECS installation and entrypoints:

```bash
# From the PECS repo root
pecs doctor
```

Or run the bootstrap health check directly:

```bash
python3 scripts/pecs_health_check.py
```

To validate dependencies only:

```bash
python3 install_workspace_integration.py <workspace-root> --validate-deps
```

## Supported AI tooling

PECS is currently designed and tested primarily for:

- GitHub Copilot Chat
- Continue

Other VS Code AI extensions may not preserve compatible continuity/workflow behavior.
PECS does not claim universal compatibility.
