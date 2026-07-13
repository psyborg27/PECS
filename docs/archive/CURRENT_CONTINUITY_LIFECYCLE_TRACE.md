# CURRENT_CONTINUITY_LIFECYCLE_TRACE

## 1. Entrypoint

- `run_pecs_daemon.py` launches `WorkspaceContinuityDaemon` with:
  - `workspace_root`
  - `runtime_session`
  - `compact_builder`
- `WorkspaceContinuityDaemon.start()` is the runtime orchestrator.

## 2. Startup flow

- Set up `.pecs/ai_chat_history.json` and initial `mtime`.
- Evaluate `_should_full_scan()` using existing `.pecs/compact_bundle.json` and `.pecs/locality_index.json`.
- If a full scan is required, `_clean_core_artifacts()` removes core artifacts.
- `_run_cycle_locked(... _rebuild_runtime_topology())` runs runtime-topology bootstrap.
- If `runtime_locality_payload` is still empty, `_rebuild_runtime_topology()` runs again.
- If runtime locality exists, `_run_continuity_refresh(trigger="startup", reason="daemon startup full scan or topology bootstrap")` executes.

## 3. File monitoring and event triggers

- A `watchdog.Observer` watches the workspace recursively.
- Monitored changes include:
  - `.pecs/ai_chat_history.json`
  - `.pecs/runtime_activation.jsonl`
  - `.py` files outside hard exclusions
- Additionally, `_poll_chat_history()` checks chat history every second.

## 4. Event handling chain

- Filesystem events call `_record_change()`, which collects changes and runs `_process_changes()`.
- `_process_changes_unlocked()` performs:
  - chat history changed → `_on_chat_history_update_unlocked()`
  - runtime activation changed → `_on_activation_update()`
  - `.py` changed → `_rebuild_runtime_topology(changed_files=python_changed_files)`

## 5. Topology/locality rebuild path

- `_rebuild_runtime_topology()` does:
  - `_discover_entrypoints()` using `ENTRYPOINT_CANDIDATES` and fallbacks
  - `_resolve_runtime_reachable_files(entrypoints)` following import targets
  - `_populate_runtime_indexes(reachable_files)`
  - `_infer_active_focus_from_chat()`
  - `_infer_locality_activation(focus)`
  - `_build_compact_bundle(focus, activation)`
  - `_build_active_context_payload(focus, compact_bundle, activation)`
  - write artifacts:
    - `.pecs/locality_index.json`
    - `.pecs/topology_compact.json`
    - `.pecs/compact_bundle.json`
    - `.pecs/active_context.json`
    - `.pecs/session_context.json`
    - `.pecs/daemon_state.json`
  - `_write_health_state()`

## 6. Compact continuity artifact generation

- `_populate_runtime_indexes()` builds runtime-locality payload from reachable `.py` files.
- `runtime_locality_payload` entries include `pecs_id`, `file`, `class`, `method`, and `runtime_zone`.
- `_build_compact_bundle()` uses:
  - activation `activated_objects`
  - active topology zone
  - focus terms from chat
  - `RuntimeEdgeReinforcement.weighted_edges()` over topology edges
  - `locality_traversal.traverse()` to select seed neighborhood
- `_build_active_context_payload()` uses compact bundle IDs and runtime topology edges to write active context.

## 7. Continuity refresh flow

- `_run_continuity_refresh()` is triggered on:
  - startup (if runtime locality exists)
  - chat history update
  - runtime activation update
- It writes `.pecs/continuity_refresh_state.json`.
- It calls `_execute_bridge_refresh()`:
  - `.pecs/bridge/run_bridge.sh refresh` or
  - `.pecs/bridge/run_bridge.py refresh --workspace <root>`
- `run_bridge.refresh` calls `scripts/export_workspace_continuity.py`.

## 8. Export hydration chain

- `export_workspace_continuity()` reads:
  - `.pecs/topology_compact.json`
  - `.pecs/locality_index.json`
  - `.pecs/compact_bundle.json`
  - `.pecs/active_context.json`
  - `.pecs/session_context.json`
  - `.pecs/daemon_state.json`
  - `.pecs/runtime_activation.jsonl`
- It writes:
  - `.pecs/continuity/active_topology.json`
  - `.pecs/continuity/locality_state.json`
  - `.pecs/continuity/engineering_continuity_state.json`
  - `.pecs/continuity/continuity_hydration_report.json`
  - `.pecs/continuity/architectural_decisions.md`
  - `.pecs/continuity/unresolved_tensions.md`
  - `.pecs/continuity/current_workspace_focus.md`

## 9. Runtime activation flow

- `runtime_activation.jsonl` is produced by `RuntimeActivationLogger.append_event()`.
- `LocalityActivationEngine.infer_locality()` reads recent runtime activation events and builds:
  - `activated_objects`
  - `active_runtime_zones`
  - `activated_object_details`
  - `observed_edges`
  - `activation_confidence`
  - `activation_reasons`
  - `activation_diagnostics`
- Activation update calls `_on_activation_update()`, which refreshes compact_bundle and active_context, then runs continuity refresh.

## 10. Key current observations

- The daemon is functional and maintains a runtime topology-first pipeline.
- `compact_bundle` and `active_context` are rebuilt on topology, chat, or activation changes.
- Continuity export hydration is only performed via bridge refresh triggers.
- Py file changes rebuild core runtime artifacts, but do not directly invoke bridge refresh.
- Existing artifacts may be reused on startup without a forced rebuild, which can leave continuity exports stale if the workspace changed while the daemon was down.
