# HYDRATION_AUTOMATION_REPORT

## What hydration means in the current codebase

- Core runtime continuity artifacts are:
  - `.pecs/locality_index.json`
  - `.pecs/topology_compact.json`
  - `.pecs/compact_bundle.json`
  - `.pecs/active_context.json`
  - `.pecs/session_context.json`
- Hydrated continuity exports are:
  - `.pecs/continuity/active_topology.json`
  - `.pecs/continuity/locality_state.json`
  - `.pecs/continuity/engineering_continuity_state.json`
  - `.pecs/continuity/continuity_hydration_report.json`
  - associated markdown summaries

## Automation entrypoints

- `WorkspaceContinuityDaemon.start()` may call `_run_continuity_refresh()` on startup.
- `_on_chat_history_update_unlocked()` calls `_run_continuity_refresh()`.
- `_on_activation_update()` calls `_run_continuity_refresh()`.

## Manual hydration paths

- `.pecs/bridge/run_bridge.sh refresh`
- `.pecs/bridge/run_bridge.py refresh`
- `scripts/export_workspace_continuity.py`

These manual commands are still available, but the daemon is intended to cover ordinary live updates.

## What is actually automatic today

- Runtime topology rebuilds are automatic on `.py` changes.
- `compact_bundle` and `active_context` are updated automatically on:
  - topology rebuild
  - chat updates
  - runtime activation updates
- Continuity exports are automatically refreshed only on:
  - startup
  - chat updates
  - runtime activation updates

## What is NOT automated today

- Continuity export refresh is NOT triggered after every runtime topology rebuild.
- If a Python file change causes a topology rebuild but no chat or runtime activation event follows, `.pecs/continuity/*` may remain stale.
- A daemon restart can preserve old artifacts and skip a rebuild if `.pecs/compact_bundle.json` and `.pecs/locality_index.json` appear valid.

## Stale-state causes

- `_rebuild_runtime_topology()` updates core artifacts but does not call `_run_continuity_refresh()`.
- `_should_full_scan()` can skip rebuild on startup when artifacts exist, so stale artifacts can survive a restart.
- Continuity refresh is throttled to 60 seconds, so rapid repeated updates can defer hydration.

## Propagation chain

1. `.py` change → topology rebuild → core artifacts updated
2. `chat` or `runtime_activation` event → compact bundle / active context updated → bridge refresh → continuity exports updated

This means `.py` changes alone do not complete the chain to continuity export hydration.

## Conclusion

Hydration automation exists, but it is incomplete. The missing propagation is the bridge refresh after direct runtime topology rebuilds, meaning a full hydration cycle is only guaranteed when chat or activation activity also occurs.
