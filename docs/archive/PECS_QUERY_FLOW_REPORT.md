# PECS Query Flow Report

## Summary

The current workspace contains an installed PECS integration with active `.pecs` artifacts and daemon state. The expected path for Copilot/LLM agents is instruction-driven rather than hardwired in the codebase.

## 1. Mechanisms currently available for querying PECS

- Shell scripts
  - `.vscode/tasks.json` invokes `.pecs/run_pecs_daemon.sh` and `.pecs/bridge/run_bridge.sh`
  - `.pecs/run_pecs.sh` / `.pecs/run_pecs_daemon.sh` resolve the PECS runtime and start the daemon
  - `.pecs/bridge/run_bridge.sh` launches `run_bridge.py`
- Bridge scripts
  - `.pecs/bridge/run_bridge.py`
  - `.pecs/bridge/export_workspace_continuity.py`
  - `.pecs/bridge/validate_workspace_continuity.py`
- Continuity files
  - `.pecs/daemon_health.json`
  - `.pecs/daemon_state.json`
  - `.pecs/active_context.json`
  - `.pecs/compact_bundle.json`
  - `.pecs/session_context.json`
  - `.pecs/locality_index.json`
  - `.pecs/topology_compact.json`
  - `.pecs/continuity/active_topology.json`
  - `.pecs/continuity/locality_state.json`
- Topology files
  - `.pecs/topology_compact.json`
  - `.pecs/continuity/active_topology.json`
- Daemon APIs / runtime components
  - `run_pecs_daemon.py`
  - `runtime/daemon/workspace_continuity_daemon.py`
  - `run_pecs_pro.py`
- JSON artifacts
  - active context and locality artifacts under `.pecs`
  - `.pecs/config/install_root.json`
- Markdown artifacts
  - `.github/copilot-instructions.md`
  - `.continue/config.yaml`
  - `.continue/rules/pecs-first-routing.yaml`
  - `.continue/rules/PECS_CONTEXT_RULE.md`
  - `.continue/rules/PECS_APPEND_RULE.md`
- Environment variables
  - `PECS_DAEMON_STARTUP_TIMEOUT` / `PECS_DAEMON_STARTUP_INTERVAL` in `.pecs/run_pecs_daemon.sh`
  - `PYTHONPATH` / `PATH` resolved by `.pecs/run_pecs_daemon.sh` and `.pecs/run_pecs.sh`
- VS Code tasks
  - `.vscode/tasks.json` contains daemon start, auto-start, stop, refresh, validate, and chat append tasks
- MCP interfaces
  - `workspace_bridge_cli.py` exposes `bootstrap-workspace`, `install-workspace-assets`, `refresh-workspace`, `validate-workspace`, and status commands
- Hooks / wrappers
  - `.pecs/run_pecs.sh` and `.pecs/run_pecs_daemon.sh` are wrappers around installed runtime executables
  - `install_workspace_integration.py` creates integration assets and wrappers
- Symlinks
  - None required or visible in this workspace; integration uses generated shell wrappers and JSON config instead of symlinks
- Launch scripts
  - `launch_pecs_daemon.sh`
  - `launch_pecs_lite_v2_daemon.sh`
  - `.pecs/run_pecs_daemon.sh`
  - `.pecs/bridge/run_bridge.sh`

## 2. Intended retrieval flow

The documented intended flow is:

1. User task / assistant request begins
2. Workspace daemon is available and `.pecs` artifacts exist
3. `.vscode/tasks.json` can start or auto-start the daemon on folder open
4. `.pecs/run_pecs_daemon.sh` starts `pecs-pro-daemon` or Python module `run_pecs_daemon`
5. Daemon writes continuity artifacts into `.pecs/`
6. `.continue/config.yaml` with `pecs-first-routing.yaml` instructs Continue to load `.pecs` artifacts first
7. `.github/copilot-instructions.md` instructs Copilot to inspect `.pecs` artifacts and query PECS-LITE
8. External Continue/Copilot middleware reads `.pecs/active_context.json`, `.pecs/locality_index.json`, and `.pecs/topology_compact.json`
9. Query adapters (`integrations/copilot_adapter.py`, `integrations/continue_adapter.py`, `integrations/pecs_pro_query_adapter.py`) build compact locality context
10. `topology.retrieval.topology_retriever.TopologyRetriever.build_minimal_context()` produces anchor-based locality guidance
11. Candidate runtime targets are selected and returned to the model
12. Code edits are made in live runtime workspace modules, not `.pecs` files

## 3. Actual observed runtime behavior

Evidence from the current workspace:
- `.pecs/daemon.pid` exists and points to PID `34922`
- `.pecs/daemon_health.json` reports `status: "healthy"`, `retrieval_ready: true`, `topology_ready: true`, `continuity_ready: true`
- `.vscode/tasks.json` is installed and includes auto-start on folder open
- `.github/copilot-instructions.md` and `.continue/config.yaml` plus `.continue/rules/pecs-first-routing.yaml` are present
- `.pecs/daemon.log` exists but is empty, so runtime log output is currently not retained in the log file

## 4. Actual autocontext behavior

- The repository contains explicit PECS guidance and routing configuration.
- The codebase does not expose a direct embedded LLM runtime engine; instead it provides adapter modules and instruction artifacts.
- This means the actual agent behavior depends on external tooling honoring `.github/copilot-instructions.md` and `.continue` rules.
- Therefore, the current implementation is best described as: **partially querying PECS via external instruction files and bridge artifacts**.
- There is no in-repo guarantee that Copilot will automatically query PECS in all cases.

## 5. Files responsible for key roles

### Continuity discovery
- `.pecs/bridge/run_bridge.py`
- `scripts/export_workspace_continuity.py`
- `scripts/validate_workspace_continuity.py`
- `install_workspace_integration.py`
- `workspace_bridge_cli.py`

### Locality resolution
- `topology/retrieval/topology_retriever.py`
- `integrations/copilot_adapter.py`
- `integrations/continue_adapter.py`
- `integrations/context_export_adapter.py`
- `integrations/pecs_pro_query_adapter.py`
- `runtime/session/workspace_runtime_session.py`

### Architectural context synthesis
- `integrations/pecs_pro_query_adapter.py`
- `topology/compaction/compact_context_builder.py`
- `runtime/daemon/workspace_continuity_daemon.py`
- `.github/copilot-instructions.md`
- `.continue/rules/pecs-first-routing.yaml`

### Bridge refresh
- `.pecs/bridge/run_bridge.sh`
- `.pecs/bridge/run_bridge.py`
- `workspace_bridge_cli.py`
- `.pecs/bridge/export_workspace_continuity.py`

### Task routing
- `.vscode/tasks.json`
- `.continue/config.yaml`
- `.continue/rules/pecs-first-routing.yaml`
- `.github/copilot-instructions.md`
- `install_workspace_integration.py`

### Daemon logging
- `.pecs/run_pecs_daemon.sh`
- `install_workspace_integration.py` (daemon wrapper generation)
- `.pecs/daemon.log`
- `.pecs/daemon_health.json`
- `.pecs/daemon_state.json`
- `runtime/daemon/workspace_continuity_daemon.py`

### Audit logging / telemetry
- `.pecs/ai_chat_history.json`
- `.pecs/tools/append_ai_chat_history.py`
- `.pecs/chat_history_state.json`
- `runtime/daemon/workspace_continuity_daemon.py` (system chat event append)
- `workspace_bridge_cli.py` status/health commands

## 6. Why PECS locality/context may be bypassed

- `.github/copilot-instructions.md` is advisory guidance, not a compiled hook.
- `.continue` rules can be ignored by an external Continue runtime if misconfigured.
- `TopologyRetriever` explicitly allows semantic fallback and low-confidence retrieval.
- `pecs-first-routing.yaml` still defines fallback to repository search if PECS is insufficient.
- There is no repo-internal enforcement that forbids grep/search.
- The actual model-facing query path is external to this repo; if the LLM agent doesn’t use `.pecs` as instructed, it will fall back.

## 7. Observed deviations from intended architecture

- Intended: PECS-LITE should be stateless and query PECS-PRO; actual code is consistent with this intention.
- Intended: external tooling should consult `.pecs` artifacts first; actual enforcement is only advisory.
- Intended: daemon logs should capture runtime activity; actual `.pecs/daemon.log` is present but empty.
- Intended: `.continue` rules should prevent broad search; actual fallback behavior allows repository search if PECS is insufficient.

## 8. Evidence-backed actual execution chain

1. Open workspace or invoke `.vscode` task
2. `.vscode/tasks.json` calls `.pecs/run_pecs_daemon.sh`
3. `.pecs/run_pecs_daemon.sh` resolves `pecs-pro-daemon` via `.pecs/config/install_root.json` or PATH
4. `run_pecs_daemon.py` starts `WorkspaceContinuityDaemon`
5. Daemon writes `.pecs` artifacts and health files
6. `.continue/config.yaml` and `.github/copilot-instructions.md` are the external integration points
7. Agents are intended to call adapters via `TopologyRetriever` and related integration modules
8. The workspace shows healthy daemon state, but the actual model invocation path is external and not visible in the repository

## Conclusion

The current implementation provides the expected PECS infrastructure and integration artifacts. The core missing enforcement point is that Copilot/Continue query behavior depends on external tooling and guidance instead of internal runtime enforcement.
