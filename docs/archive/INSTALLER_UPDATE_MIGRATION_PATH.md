# INSTALLER_UPDATE_MIGRATION_PATH

## Purpose

Provide a minimal migration path for updating the PECS daemon and continuity refresh behavior across the three target workspaces.

## Migration steps for each workspace

1. Stop the existing PECS daemon if running.
2. Pull or install the updated `runtime/daemon/workspace_continuity_daemon.py` patch.
3. Ensure the workspace `.pecs/bridge/run_bridge.py` exists and is available.
4. Restart the daemon using the normal workspace startup method:
   - `bash .pecs/run_pecs_daemon.sh <workspace_root>`
   - or the equivalent `run_pecs_daemon.py` invocation.
5. Trigger a workspace topology rebuild:
   - edit a monitored `.py` file, or
   - manually invoke the daemon's continuity refresh task if available.
6. Verify the refresh by checking:
   - `.pecs/continuity_refresh_state.json`
   - `.pecs/continuity/active_topology.json`
   - `.pecs/continuity/locality_state.json`
   - `.pecs/continuity/engineering_continuity_state.json`

## Notes

- The fix is incremental; it does not require workspace-wide reindexing.
- Existing PECS-LITE projection contract remains unchanged.
- If `run_bridge.sh` is not executable, the daemon will now fall back to `run_bridge.py` automatically.
- For environments that do not support shell wrapper execution, no additional installer changes are needed.

## Recommended verification

For each workspace, after restart:
- ensure `.pecs/compact_bundle.json` and `.pecs/active_context.json` are present
- ensure `.pecs/continuity/*` artifacts are refreshed after a topology change
- confirm the daemon health state reports `retrieval_ready: True`
