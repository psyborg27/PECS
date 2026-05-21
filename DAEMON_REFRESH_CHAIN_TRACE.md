# DAEMON_REFRESH_CHAIN_TRACE

## Current chain after repair

1. `.py` file change or explicit runtime topology rebuild
2. `WorkspaceContinuityDaemon._rebuild_runtime_topology()` executes
   - discovers entrypoints
   - resolves runtime-reachable files
   - populates runtime-locality payload
   - infers active focus from chat
   - infers locality activation
   - builds `compact_bundle`
   - builds `active_context`
   - writes core artifacts
3. At the end of `_rebuild_runtime_topology()`, the daemon now calls:
   - `_run_continuity_refresh(trigger="runtime_topology", reason="runtime topology rebuild")`
4. `_run_continuity_refresh()` performs:
   - throttle check
   - writes `.pecs/continuity_refresh_state.json`
   - executes bridge refresh
5. `_execute_bridge_refresh()` performs:
   - if `.pecs/bridge/run_bridge.sh` exists and is executable, run it
   - otherwise run Python bridge via `.pecs/bridge/run_bridge.py refresh --workspace <root>`
6. `scripts/export_workspace_continuity.py` regenerates hydrated continuity exports
   - `.pecs/continuity/active_topology.json`
   - `.pecs/continuity/locality_state.json`
   - `.pecs/continuity/engineering_continuity_state.json`
   - associated hydration reports

## Effect

- Topology/locality rebuild now propagates through the full continuity hydration chain.
- Compact export refresh and bridge-driven hydration are now linked to runtime topology changes.
- Projection consumers see refreshed continuity artifacts without extra manual refresh steps.
