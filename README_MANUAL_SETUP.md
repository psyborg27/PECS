
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

## Status

PECS is transitioning from experimental to persistent infrastructure. Validate all outputs manually. Use backups, version control, and human supervision. PECS does not replace engineering judgment.

## Supported AI tooling

PECS is currently designed and tested primarily for:

- GitHub Copilot Chat
- Continue

Other VS Code AI extensions may not preserve compatible continuity/workflow behavior.
PECS does not claim universal compatibility.

## What to copy into the workspace

Copy these files from the PECS package folder into the target workspace:

- `.continue/rules/PECS_CONTEXT_RULE.md`
- `.continue/rules/PECS_APPEND_RULE.md`
- `.github/copilot-instructions.md`
- `.pecs/tools/append_ai_chat_history.py`
- `.pecs/tools/update_ai_chat_history.sh`
- `.pecs/README_WORKSPACE_INTEGRATION.md`

**Important:** `.pecs` artifacts are generated continuity infrastructure only. Do not edit `.pecs` files as if they were engineering sourcecode. Use them only to locate runtime workspace targets and verify locality.

Create these files if they do not already exist:

- `.pecs/ai_chat_history.json` with an initial value of `[]` (optional)
- `.vscode/tasks.json`
- `.vscode/settings.json`

## Environment setup commands

Clone the PECS repository into a stable install location before initializing a workspace.

```bash
git clone <your-repo-url> ~/Developer/pecs_pro
cd ~/Developer/pecs_pro
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
python -m pip install -e .
```

Then confirm the install:

```bash
pecs doctor
```

If you want to install from a local source checkout only for the PECS package, use:

```bash
python -m pip install -e /path/to/PECS
```

## PECS Preserve-First Operational Lifecycle

PECS now distinguishes between bootstrap, refresh/rebind, and rebuild operations.

- **Bootstrap / install** is used when `.pecs` does not exist in the workspace.
  It installs managed assets, creates workspace launchers, and writes continuity-aware configuration.
- **Refresh / rebind** is used when `.pecs` already exists and PECS or runtime logic evolves.
  It preserves current continuity state and history while updating managed assets, runtime bindings, and derived continuity artifacts.
- **Rebuild / continuity regeneration** is used when derived topology/continuity artifacts need to be regenerated with current algorithms.
  It preserves historical continuity, chat history, and telemetry history without destructive resets.
- **Reset** remains an explicit manual action only, not a default flow.

Use preserve-first flows whenever workspace continuity must survive upgrade and evolution.

### Recommended non-destructive commands

```bash
pecs install-workspace-assets "/path/to/your/workspace" --preserve
pecs refresh-workspace-bindings "/path/to/your/workspace" --preserve
pecs rebuild-continuity "/path/to/your/workspace"
pecs rebuild-topology "/path/to/your/workspace"
pecs restart-daemon "/path/to/your/workspace"
```

### Required PECS task lifecycle

1. Query PECS first using canonical observe-projection commands.
2. Perform engineering reasoning and bounded edits on runtime workspace modules.
3. Refresh and rebuild PECS artifacts using lifecycle commands.
4. Never hand-edit `.pecs` artifacts or continuity outputs.

### When to use each command

- `install-workspace-assets` / `bootstrap-workspace` / `setup-workspace`
  for initial workspace installation or managed asset refresh.
- `refresh-workspace-bindings` / `rebind-workspace` / `safe-migration`
  when the install root moved or PECS bindings changed.
- `rebuild-continuity` / `rebuild-topology`
  when continuity or topology artifacts must be regenerated from the same workspace state.
- `restart-daemon`
  when the daemon needs a clean runtime restart after configuration or asset refresh.

## Rebinding a Workspace After Relocation

If PECS moves to a new install root, rerun the package bootstrap and then refresh workspace bindings:

```bash
git clone <your-repo-url> ~/Developer/pecs_pro
cd ~/Developer/pecs_pro
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
python -m pip install -e .
pecs rebind-workspace "/path/to/your/workspace" --upgrade
```

This updates all workspace integration files and replaces stale PECS path references.

## Configure VS Code

The auto-installer normally writes these for you, but manually you should ensure:

- `.vscode/tasks.json` contains PECS start/stop/chat append tasks
- `.vscode/tasks.json` contains `PECS: Manual Update Chat History`
- `.vscode/settings.json` includes `pecs.contextPath` pointing to `.pecs/active_context.json`
- Workspace settings are saved in the target workspace, not in the PECS package folder

After setup, open tasks using:

- VSCode
- Terminal
- Run Task
- select a PECS task

Expected task names include:

- `PECS: Start Daemon`
- `PECS: Stop Daemon`
- `PECS: Refresh Continuity State`
- `PECS: Validate Continuity State`

## Configure Continue

Continue reads rules from `.continue/rules/`.
Make sure these are present:

- `.continue/rules/PECS_CONTEXT_RULE.md`
- `.continue/rules/PECS_APPEND_RULE.md`
- Keep `.continue/rules/CONTINUITY_MAP.md` in the workspace if you already use it

## Configure Copilot

Copilot reads workspace instructions from:

- `.github/copilot-instructions.md`

Keep the instructions focused on reading `.pecs` artifacts before edits.

## Start the daemon

After installation and workspace setup, start the daemon:

```bash
pecs-pro-daemon "/path/to/your/workspace"
```

If you are starting from the source checkout directly:

```bash
cd /path/to/PECS
source .venv/bin/activate
python -m run_pecs_daemon "/path/to/your/workspace"
```

The daemon is intentionally manual-start during active AI-assisted development sessions.
It does not auto-start from package installation.
After stabilization, no-op cycles are intentionally mostly silent
(no rewrites, no log spam, no continuity churn).

## Bridge lifecycle

Users normally do not run bridge scripts directly.
Use standard refresh flow (`pecs-pro refresh` or `PECS: Refresh Continuity State`).
The bridge remains lightweight, deterministic, and non-semantic.

## Non-destructive refresh behavior

When reinstalling or rebinding into an already active workspace:

- Existing `.pecs` continuity state is preserved.
- Existing `.pecs/ai_chat_history.json` is preserved.
- Existing runtime telemetry/history is preserved.
- Continue and Copilot assets are merged/appended when possible.
- Managed launcher/bridge/tool updates are backup-aware before replacement.

Use upgrade-preserving flows for active workspaces:

```bash
pecs install-workspace-assets "/path/to/workspace" --upgrade
pecs rebind-workspace "/path/to/workspace" --upgrade
```

## Optional emitted-envelope observation mode

These commands are visibility-only and do not alter continuity topology/state. They are the canonical PECS-LITE query entrypoints and should be run before broad workspace inspection.

For local/continue models:

```bash
pecs observe-projection-snapshot "/path/to/workspace" \
  --query "runtime locality reconciliation" \
  --query-source "continue" \
  --model-name "unknown" \
  --profile-class local \
  --local-vs-frontier local
```

For copilot/frontier models:

```bash
pecs observe-projection-snapshot "/path/to/workspace" \
  --query "runtime locality reconciliation" \
  --query-source "copilot" \
  --model-name "unknown" \
  --profile-class frontier \
  --local-vs-frontier frontier
```

For bounded repeated observation:

```bash
pecs observe-projection-daemon "/path/to/workspace" \
  --query "runtime locality reconciliation" \
  --query-source "copilot" \
  --model-name "unknown" \
  --profile-class frontier \
  --local-vs-frontier frontier \
  --iterations 20 \
  --interval-seconds 2.0
```

Observation modes:
- `observe-projection-snapshot` performs one optional visibility-only capture and writes one snapshot record.
- `observe-projection-daemon` performs bounded repeated observation and writes repeated projection and emitted envelope records.
- `Stop Observation Daemon` is available as an opt-in task when a repeated observation process needs manual termination.

What gets logged:
- `query`, `query_source`, `model_name`, `profile_class`, `local_vs_frontier`, `session_id`
- `request_id`, `trace_id`, `causality_chain_id`, `projection_id`, `parent_event_id`
- lifecycle events for snapshot start/completed/failed and daemon start/completed
- optional advisory outputs, discarded cognition, shaping losses, runtime target counts, and continuity metrics

Where logs are stored:
- `.pecs/logs/observation/projection_snapshot.jsonl`
- `.pecs/logs/observation/emitted_envelope.jsonl`
- `.pecs/logs/lifecycle_commands.jsonl`

How to start diagnostics:
- run `pecs observe-projection-snapshot "<workspace>" --query "..." --query-source "copilot" --model-name "unknown" --profile-class frontier --local-vs-frontier frontier`
- or run `pecs observe-projection-daemon "<workspace>" --query "..." --query-source "copilot" --model-name "unknown" --profile-class frontier --local-vs-frontier frontier --iterations 20 --interval-seconds 2.0`

How to stop diagnostics:
- stop the observation daemon task in VS Code if using the opt-in background task
- or use `PECS: Stop Observation Daemon (Opt-In)` when the running process is visible to the shell

Observation logs are written to:

- `.pecs/logs/observation/projection_snapshot.jsonl`
- `.pecs/logs/observation/emitted_envelope.jsonl`
- `.pecs/logs/lifecycle_commands.jsonl`

## New AI session handoff

For a new AI session, provide:

- current task/problem
- `.pecs` continuity state

Prefer this over large historical chat dumps.
Chat-history replay is optional and experimental.

## What automatic installation does

If you use `pecs-pro-install-workspace`, it installs all of the above for you and also creates the PECS tasks in `.vscode/tasks.json`.

## Workspace launchers

The workspace integration also generates install-root-aware workspace launchers in `.pecs/`:

- `.pecs/run_pecs.sh`
- `.pecs/run_pecs.cmd`
- `.pecs/run_pecs_daemon.sh`
- `.pecs/run_pecs_daemon.cmd`
- `.pecs/config/install_root.json`

These wrappers resolve the correct PECS install root and runtime explicitly, so commands still work even when the active shell is using a different workspace venv.

- `.pecs/run_pecs_daemon.cmd`
- `.pecs/config/install_root.json`

These wrappers resolve the correct PECS install root and runtime explicitly, so commands still work even when the active shell is using a different workspace venv.
