# MINIMAL_REPAIR_IMPLEMENTATION

## Changed file

- `runtime/daemon/workspace_continuity_daemon.py`

## What changed

1. Added an automatic continuity refresh trigger at the end of `_rebuild_runtime_topology()`.
   - Trigger: `runtime_topology`
   - Reason: `runtime topology rebuild`
2. Added a robust bridge refresh fallback in `_execute_bridge_refresh()`.
   - Use `.pecs/bridge/run_bridge.sh` only if it exists and is executable.
   - Otherwise fall back to Python execution of `.pecs/bridge/run_bridge.py`.

## Why this is minimal

- It does not redesign the PECS architecture.
- It does not modify the PECS-LITE projection contract.
- It preserves runtime-topology-first continuity behavior.
- It keeps the refresh path lightweight and incremental by reusing the existing continuity refresh mechanism.

## Behavior after the fix

- Any successful runtime topology rebuild now automatically attempts bridge-driven continuity hydration.
- If the shell wrapper is unavailable or not executable, the daemon still refreshes via the Python bridge.
- Core artifacts remain the authoritative inputs for continuity exports.
