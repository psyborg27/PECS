# PECS Configuration

This document describes the current configuration files, workspace assets, CLI options, environment variables, and runtime settings used by PECS Alpha 1.

## Configuration Files

PECS uses a combination of repository config files and workspace asset templates.

### Repository configuration

- `pyproject.toml` / `setup.py` — package metadata and install entrypoints.
- `requirements.txt` — Python runtime dependency list.
- `workspace_assets/workspace_assets_manifest.json` — deployable workspace asset manifest.

### Workspace asset templates

Workspace asset files are installed into the target workspace, typically under `.continue/`, `.github/`, `.vscode/`, and `.pecs/`.

Key workspace asset files:

- `.continue/config.yaml`
- `.continue/rules/pecs-first-routing.yaml`
- `.continue/rules/PECS_CONTEXT_RULE.md`
- `.continue/rules/PECS_APPEND_RULE.md`
- `.github/copilot-instructions.md`
- `.vscode/tasks.json`
- `.pecs/bridge/run_bridge.py`
- `.pecs/bridge/run_bridge.sh`
- `.pecs/bridge/export_workspace_continuity.py`
- `.pecs/bridge/validate_workspace_continuity.py`
- `.pecs/tools/append_ai_chat_history.py`
- `.pecs/tools/update_ai_chat_history.sh`

## Environment Variables

PECS does not require a fixed set of runtime environment variables for normal operation. Common variables that may be used in scripts or examples include:

- `PECS_PRO_REPO` — path to the PECS repository root used by bootstrap or daemon scripts.
- `VIRTUAL_ENV` — Python virtual environment path when running in `.venv`.

## CLI Options and Profiles

The main CLI is `pecs`, implemented in `workspace_bridge_cli.py`.

Common CLI options across commands:

- `workspace_root` — target workspace path.
- `--repo-root` — path to the PECS repository root.
- `--preserve-user-config` — preserve local workspace settings during asset install or migration.
- `--output` — file path for command output, typically used by `query-pipeline`.
- `--json` — optional JSON output flag for verify commands.

### Query profile configuration

`pecs query-pipeline` accepts query budget options:

- `--max-clusters` — maximum evidence clusters to select (default 3).
- `--max-nodes` — maximum navigation graph nodes (default 40).
- `--max-depth` — maximum graph expansion depth (default 2).
- `--prefer-daemon-dumps` — prefer existing `.pecs/workspace_graph.json` and `.pecs/workspace_registry.json` when available.

### Projection and observation configuration

`pecs observe-projection-snapshot` and `pecs observe-projection-daemon` accept model and profile fields:

- `--query` — text query to capture.
- `--query-source` — provenance string for the snapshot.
- `--model-name` — required model identifier.
- `--model-source` — optional provider or agent name.
- `--provider` — optional provider identifier.
- `--model-size` — model size classification.
- `--profile-class` — required profile class: `local`, `frontier`, or `unknown`.
- `--local-vs-frontier` — required classification: `local`, `frontier`, or `unknown`.
- `--reasoning-capability-class` — capability classification: `small`, `medium`, `frontier`, or `unknown`.
- `--context-window` — context window size.
- `--session-id` — optional session identifier.
- `--max-records` — maximum records to capture.

## Daemon Configuration

The daemon is launched through scripts and CLI wrappers. It does not expose a separate configuration file in Alpha 1.

Key launcher scripts:

- `run_pecs_daemon.py` — daemon entrypoint.
- `.pecs/run_pecs_daemon.sh` — workspace bridge daemon launcher.
- `.pecs/run_pecs.sh` — workspace command launcher.

## Logging

PECS writes logs into the workspace `.pecs/logs/` directory.

Common log files:

- `.pecs/logs/daemon_activity.log`
- `.pecs/logs/daemon_errors.log`
- `.pecs/logs/continuity_sync.log`
- `.pecs/logs/lifecycle_commands.jsonl`

Logging is primarily JSON/JSONL for structured event records.

## Paths

Recommended paths:

- PECS repo install root: `~/Developer/PECS/`
- Workspace root: project repository root containing source files.
- Generated artifacts: `.pecs/` in the workspace root.

## Recommended Settings

- Keep the PECS repository in a stable location, not `Downloads`, `Desktop`, or removable media.
- Use an editable install with `pip install -e .`.
- Bootstrapped workspaces should preserve user configuration when possible.
- Avoid manual edits to `.pecs/` artifacts.
- Prefer `pecs refresh`, `pecs validate`, and `pecs doctor` for operations.

## Notes

This document describes current Alpha 1 configuration behavior. It does not describe future configuration formats or external runtime agents.
