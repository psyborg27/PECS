# PECS Optional AI Chat History Workflow

This document describes optional and experimental chat-history workflows.
PECS continuity is primarily deterministic continuity stabilization,
not full conversational replay.

## Experimental status

PECS is experimental and currently in an early proof-of-concept stage.
It has been developed through AI-assisted and agentic coding workflows,
primarily by a non-traditional software developer.

Validate all outputs manually.
Do not use on production or commercially critical systems.
Use backups, version control, and human supervision.
PECS does not replace engineering judgment.

## Supported AI tooling

PECS is currently designed and tested primarily for:

- GitHub Copilot Chat
- Continue

Other VS Code AI extensions may not preserve compatible continuity/workflow behavior.
PECS does not claim universal compatibility.

## One-command setup

Run this once per workspace:

```bash
/Users/raj/Downloads/PECS_PRO_V2_FINAL/pecs_pro/install_pecs_workspace.sh "/path/to/workspace"
```

Or, if installed via pip:

```bash
pecs-pro-install-workspace "/path/to/workspace"
```

For architecture, installation, and operational lifecycle guidance, use `README.md`.
For manual setup procedures, use `README_MANUAL_SETUP.md`.

## What gets installed automatically

- `.vscode/tasks.json`
	- `PECS: Start Daemon`
	- `PECS: Auto Start Daemon On Folder Open`
	- `PECS: Stop Daemon`
	- `PECS: Append Chat Event`
- `.continue/rules/PECS_CONTEXT_RULE.md`
- `.continue/rules/PECS_APPEND_RULE.md`
- `.github/copilot-instructions.md`
- `.pecs/tools/append_ai_chat_history.py`
- `.pecs/tools/update_ai_chat_history.sh`
- `.pecs/ai_chat_history.json`

Note:
- Chat-history files are optional telemetry inputs.
- Primary continuity handoff should use deterministic `.pecs` continuity state.

## Environment command behavior

Installed tasks and scripts run this when present:

```bash
cd "${workspaceFolder}"
source .venv/bin/activate
```

So workspace-local Python dependencies are used automatically.

## Chat append usage

Manual append (works now):

```bash
python3 .pecs/tools/append_ai_chat_history.py "/path/to/workspace" --source copilot --message "session started"
```

Manual shell updater:

```bash
bash .pecs/tools/update_ai_chat_history.sh "/path/to/workspace" copilot "session started"
```

Structured payload append:

```bash
python3 .pecs/tools/append_ai_chat_history.py "/path/to/workspace" --payload-json '{"source":"continue","messages":[{"role":"user","content":"..."}]}'
```

## Important limitation

Neither Copilot Chat nor Continue currently exposes a universal built-in "append every turn to file" switch in this repository by default.

What is now automated:
- rules/instructions are installed so agents use `.pecs`
- VS Code tasks are installed so daemon startup and manual appends are one-click
- the manual updater script is copied into `.pecs/tools/`
- `.pecs/ai_chat_history.json` watcher is active in daemon

## Daemon and bridge behavior

The daemon is manually started by the user during active sessions.
It does not auto-start from package installation.

After stabilization, PECS intentionally becomes mostly silent:

- no rewrites on no-op cycles
- no log spam on no-op cycles
- no continuity churn on no-op cycles

Bridge execution is part of daemon/refresh operational flow.
Users normally do not run bridge scripts directly.

## Recommended new-session handoff

In a new AI session, prefer handing off:

- current task/problem
- `.pecs` continuity state

Use large historical chat dumps only when required for edge cases.

If your Continue or custom tooling supports post-message hooks, point the hook to:

```bash
python3 .pecs/tools/append_ai_chat_history.py "${workspaceFolder}" --payload-json '<json-object>'
```
