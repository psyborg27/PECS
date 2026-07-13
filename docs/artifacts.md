# PECS Artifacts

PECS divides generated continuity infrastructure from authoritative engineering sourcecode. Everything under `.pecs/` in a target workspace is generated infrastructure. Live workspace modules remain the only source of engineering truth.

## Generated `.pecs/` Artifacts

Artifacts written by the daemon refresh cycle:

- `.pecs/locality_index.json` — runtime locality payload
- `.pecs/topology_compact.json` — topology edges and entrypoints
- `.pecs/active_context.json` — active continuity context
- `.pecs/session_context.json` — session continuity context
- `.pecs/compact_bundle.json` — compact context bundle
- `.pecs/daemon_state.json` — daemon state snapshot
- `.pecs/daemon_health.json` — daemon health snapshot

Optional dumps (when enabled):

- `.pecs/workspace_graph.json` — dumped Workspace Graph
- `.pecs/workspace_graph_validation.json` — graph validation output
- `.pecs/workspace_registry.json` — dumped Workspace Registry
- `.pecs/workspace_registry_validation.json` — registry validation output

Continuity and audit artifacts:

- `.pecs/continuity/engineering_continuity_state.json`
- `.pecs/continuity/continuity_hydration_report.json`
- `.pecs/continuity/active_topology.json`
- `.pecs/continuity/locality_state.json`
- `.pecs/logs/lifecycle_commands.jsonl`
- `.pecs/ai_chat_history.json`

## Installed Workspace Assets

The installer copies managed assets into the target workspace. These assets configure editors and AI tooling to use PECS-first routing. They are described in:

- `workspace_assets/IMPLEMENTATION_SUMMARY.md` — ingress implementation overview
- `workspace_assets/README_WORKSPACE_INTEGRATION.md` — installed asset list and rules
- `workspace_assets/README_WORKSPACE_PREPARATION.md` — workspace preparation guide
- `workspace_assets/WORKSPACE_BOOTSTRAP.md` — bootstrap checkpoint

## Bridge and Launcher Scripts

Installed under `.pecs/`:

- `.pecs/run_pecs.sh` / `.pecs/run_pecs.cmd` / `.pecs/run_pecs.ps1`
- `.pecs/run_pecs_daemon.sh` / `.pecs/run_pecs_daemon.cmd` / `.pecs/run_pecs_daemon.ps1`
- `.pecs/bridge/run_bridge.py`
- `.pecs/bridge/run_bridge.sh` / `.cmd` / `.ps1`
- `.pecs/bridge/export_workspace_continuity.py`
- `.pecs/bridge/validate_workspace_continuity.py`
- `.pecs/tools/append_ai_chat_history.py`
- `.pecs/tools/update_ai_chat_history.sh`

## Editor Configuration

- `.vscode/tasks.json` — PECS start/stop/refresh/validate/chat-append tasks
- `.vscode/settings.json` — `pecs.contextPath` pointing to `.pecs/active_context.json`
- `.continue/config.yaml` — Continue configuration with PECS rules
- `.continue/rules/pecs-first-routing.yaml` — PECS-first routing rule
- `.continue/rules/PECS_CONTEXT_RULE.md` — context guidance
- `.continue/rules/PECS_APPEND_RULE.md` — chat append guidance
- `.github/copilot-instructions.md` — Copilot ingress instructions

## Important Rules

- `.pecs/` files are generated infrastructure only. Do not edit them as sourcecode.
- Use `.pecs/` artifacts to identify locality and execution neighborhood, then edit live runtime workspace modules.
- Do not treat raw chat narratives as locality authority.
- Accepted engineering continuity chains preserve high-signal issue-locality-outcome guidance.

For installation and refresh details, see [installation.md](installation.md). For the query and projection contract, see [query-pipeline.md](query-pipeline.md).
