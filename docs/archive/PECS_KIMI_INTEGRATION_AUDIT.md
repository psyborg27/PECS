# PECS KIMI INTEGRATION AUDIT

## Summary

This audit reviews the current PECS installation in `/Users/raj/Developer/PECS` and documents the architecture, integration points, retrieval pipeline, installer behavior, and extension support for Continue and Copilot. No code changes were made.

## PECS Version

- Package name: `pecs_pro`
- Version: `0.1.0`
- Source: `pyproject.toml`

## Continuity Architecture

### Core artifacts

PECS continuity infrastructure is centered on `.pecs/` in the workspace root. Key files and directories:

- `.pecs/ai_chat_history.json` — retained interaction history
- `.pecs/locality_index.json` — file/object locality mapping
- `.pecs/compact_bundle.json` — compact execution context
- `.pecs/active_context.json` — active runtime objects
- `.pecs/session_context.json` — session-level context
- `.pecs/runtime_activation.jsonl` — runtime activation events
- `.pecs/continuity/` — exported continuity summaries
- `.pecs/bridge/` — continuity bridge runtime and scripts
- `.pecs/tools/` — workspace chat append/update utilities

### Engineering continuity export

Continuity export is implemented in `.pecs/bridge/export_workspace_continuity.py` and the legacy `scripts/export_workspace_continuity.py` file. It reads workspace artifacts and writes:

- `.pecs/continuity/active_topology.json`
- `.pecs/continuity/locality_state.json`
- `.pecs/continuity/engineering_continuity_state.json`
- `.pecs/continuity/continuity_hydration_report.json`
- `.pecs/continuity/architectural_decisions.md`
- `.pecs/continuity/current_workspace_focus.md`
- `.pecs/continuity/unresolved_tensions.md`

The export path also uses historical chat events and runtime evidence to derive continuity confidences, divergence indicators, hotspots, and workspace trajectory.

## Daemon Architecture

### Main daemon

- Runtime class: `runtime/daemon/workspace_continuity_daemon.py`
- Entrypoint: `.pecs/config/continuity_bridge.json` or `run_pecs_daemon.py`
- Runtime bootstrap: `run_pecs_pro.py` provides `PECSProRuntime` and initializes the following components:
  - `ContinuityRegistry`
  - `RuntimeRegistry`
  - `GraphIndex`, `ExecutionIndex`, `OwnershipIndex`
  - `LocalityIndex`
  - `TopologyRetriever`
  - `IncrementalTopologyUpdater`
  - `WorkspaceRuntimeSession`
  - `CompactContextBuilder`

### Daemon responsibilities

- Monitor workspace Python files and `.pecs/ai_chat_history.json`
- Rebuild runtime topology and compact context after file or activation changes
- Detect runtime activation updates
- Write `.pecs/compact_bundle.json` and `.pecs/active_context.json`
- Trigger bridge-based continuity refresh with `_execute_bridge_refresh()`
- Write continuity refresh state to `.pecs/continuity_refresh_state.json`

### Refresh mechanics

- `_run_continuity_refresh()` is throttled to 60 seconds
- It calls either `.pecs/bridge/run_bridge.sh` or `.pecs/bridge/run_bridge.py`
- `run_bridge` executes `export_workspace_continuity()` to regenerate continuity exports
- The daemon logs events such as `projection_refresh_started`, `compact_bundle_refreshed`, `active_context_refreshed`, `continuity_refresh_started`, and `continuity_refresh_completed`

## Retrieval Pipeline

### PECS-LITE adapter

- `integrations/pecs_lite_runtime_adapter.py` loads PECS-LITE v2 runtime from `PECS_LITE v2/pecs_lite v2`
- Core method: `PECSLiteRuntimeAdapter.build_projection_safe(...)`
- It normalizes model identity and returns either a runtime projection or an error payload
- Projections include:
  - `runtime_targets`
  - `secondary_neighbors`
  - `emitted_advisory_cognition`
  - `discarded_cognition_summary`
  - `shaping_losses`
  - `final_emission_observability`

### Continue / Copilot integration

Both downstream adapters reuse the same retrieval layer:

- `integrations/continue_adapter.py`
- `integrations/copilot_adapter.py`

Common behavior:

- Accept object_id query, model metadata, and profile parameters
- Emit telemetry and downstream query events
- Call `PECSLiteRuntimeAdapter.build_projection_safe(...)`
- If projection fails, fall back to `TopologyRetriever.build_minimal_context(object_id)`
- Return advisory context without hard enforcement

### Canonical query entrypoints

- `workspace_bridge_cli.py` provides `observe-projection-snapshot` and `observe-projection-daemon`
- These commands call `PECSLiteRuntimeAdapter.build_projection_safe(...)`
- Query sources are explicitly tagged as `copilot` or `continue`

## Installer Architecture

### Primary installers

- `install_workspace_integration.py` — workspace integration installer and legacy fallback
- `workspace_assets_manager.py` — manifest-based workspace asset manager
- `workspace_bridge_cli.py` — CLI wrapper with bootstrap and lifecycle commands
- `setup.sh` / `install_pecs_workspace.sh` — repository-level onboarding shells

### Workspace asset handling

The manifest in `workspace_assets/workspace_assets_manifest.json` defines asset deployment policies and upgrade preservation rules.

Key install assets:

- `.github/copilot-instructions.md`
- `.continue/config.yaml`
- `.continue/rules/pecs-first-routing.yaml`
- `.continue/rules/PECS_CONTEXT_RULE.md`
- `.continue/rules/PECS_APPEND_RULE.md`
- `.pecs/README.md`
- `.pecs/README_WORKSPACE_INTEGRATION.md`

### Preservation and upgrade behavior

- Asset manager backs up existing workspace assets when `upgrade=True`
- Legacy installer uses `_write_managed_text_asset`, `_copy_canonical_asset`, and `_write_continue_config()` for safe update
- Existing `.pecs/ai_chat_history.json` and `.pecs/continuity/*.md` are preserved by default
- `.github/copilot-instructions.md` is appended if an existing Copilot file exists
- `.continue/config.yaml` is merged or appended rather than overwritten
- `.vscode/tasks.json` and `.vscode/settings.json` are merged using `merge_json_dict`

## Continue Integration

### Asset files

- `.continue/config.yaml`
- `.continue/rules/pecs-first-routing.yaml`
- `.continue/rules/PECS_CONTEXT_RULE.md`
- `.continue/rules/PECS_APPEND_RULE.md`
- `.continue/rules/CONTINUITY_MAP.md` (optional)

### Behavior

- Continue is instructed to prioritize PECS locality projection before broad repository search
- `PECS_APPEND_RULE.md` recommends appending events to `.pecs/ai_chat_history.json`
- `PECS_CONTEXT_RULE.md` instructs Continue to respect `.pecs` artifacts as continuity infrastructure only

## Copilot Integration

### Asset files

- `.github/copilot-instructions.md`

### Behavior

- Copilot is guided to inspect `.pecs` artifacts first before choosing edits
- The instructions explicitly call out `.pecs/active_context.json`, `.pecs/compact_bundle.json`, `.pecs/session_context.json`, `.pecs/locality_index.json`, and `.continue/rules/CONTINUITY_MAP.md`
- The install process preserves existing Copilot instructions and writes a `PECS_COPILOT_APPEND.md` when needed

## AI Chat History Architecture

### Source

- `.pecs/ai_chat_history.json` is the canonical chat history input
- `append_ai_chat_history.py` normalizes event payloads and deduplicates by generated `event_id`

### Normalization

- Adds workspace identity, workspace_id, continuity_namespace
- Standardizes `source`, `event_type`, `message`, `ts`, and `correlation`
- Converts correlation fields to canonical lists and booleans
- Supports both `--message` and `--payload-json`

### Daemon ingestion

- The daemon watches `.pecs/ai_chat_history.json`
- `_on_chat_history_update_unlocked()` is invoked after chat updates
- This triggers continuity refresh through the bridge when permitted

## Continuity Export Architecture

### Bridge runtime

- `.pecs/bridge/run_bridge.py` is the runtime bridge entrypoint
- It exposes `refresh` and `validate` commands
- `refresh` writes continuity artifacts
- `validate` performs read-only schema and size validation

### Export path

- `scripts/export_workspace_continuity.py` is the canonical export implementation
- It derives state from existing `.pecs` artifacts and runtime events
- It is invoked by both `.pecs/bridge/run_bridge.py` and workspace bridge shell wrappers

## Key Findings

- There is no evident Kimi integration in the current repository structure. No `kimi/` or `prompt_responses/` directories exist.
- Continue and Copilot both reuse the same PECS-LITE projection adapter and differ primarily in query_source tagging, telemetry, and wrapper payload shape.
- The installer is preserve-first and uses backups for existing workspace assets.
- `.pecs` continuity artifacts are treated as generated infrastructure and not authoritative source code.
- The daemon refresh path is explicit: runtime topology / activation updates rebuild core artifacts, and a separate bridge refresh writes `.pecs/continuity/*`.
- Existing continuity state is preserved by install/upgrade flows, but the bridge refresh path can regenerate continuity exports when triggered.
