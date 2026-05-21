# DAEMON_AUTOMATION_ANALYSIS

## What the daemon currently automates

- `WorkspaceContinuityDaemon` watches the workspace recursively.
- It polls `.pecs/ai_chat_history.json` every second and also listens for file system events.
- It automatically rebuilds runtime topology on `.py` changes.
- It automatically refreshes continuity exports on:
  - startup when runtime locality is available
  - chat history updates
  - runtime activation event updates
- It writes a health state and continuity refresh state.

## What the daemon currently monitors

- `.pecs/ai_chat_history.json`
- `.pecs/runtime_activation.jsonl`
- `.py` files under the workspace
- hard exclusions are applied to generated and external artifacts

## Actual trigger chains

- `.py` changes → `_process_changes_unlocked()` → `_rebuild_runtime_topology()` → write core artifacts
- chat update → `_process_changes_unlocked()` or `_poll_chat_history()` → `_on_chat_history_update_unlocked()` → update `compact_bundle`, `active_context`, and run `_run_continuity_refresh()`
- runtime activation update → `_process_changes_unlocked()` → `_on_activation_update()` → update `compact_bundle`, `active_context`, and run `_run_continuity_refresh()`
- startup → optional full scan → optional topology bootstrap → `_run_continuity_refresh("startup")`

## What automates artifact refresh

- Core artifact refresh is automated for runtime topology and locality on `.py` changes.
- Continuity export hydration is automated for startup/chat/activation events only.
- The daemon does not automatically refresh `.pecs/continuity/*` after every topology rebuild.

## What automates topology/locality hydration

- `_rebuild_runtime_topology()` rebuilds runtime-locality payload, topology edges, compact bundle, active context, and session state.
- `_run_continuity_refresh()` hydrates continuity exports from core artifacts through the bridge.

## Partial or degraded automation points

- The daemon rebuilds core artifacts but does not invoke bridge refresh after pure topology rebuilds.
- Startup can skip rebuild if existing artifacts appear valid, which risks stale continuity after a daemon restart.
- Continuity refresh is throttled to 60 seconds, so repeated rapid changes may skip some refresh cycles.

## Silent gaps

- `.py` file changes update `.pecs/compact_bundle.json` and `.pecs/active_context.json`, but not `.pecs/continuity/*` unless another trigger occurs.
- Startup uses preexisting artifacts when artifacts are present, meaning continuity exports may not be rehydrated until chat or activation activity resumes.
- `runtime_locality_payload` is required for refresh; if topology bootstrap fails, all downstream refresh triggers are skipped.

## Conclusion

The daemon automation is mostly in place, but the missing link is that runtime topology rebuild does not directly propagate into the bridge-driven continuity hydration layer. This is the principal automation gap, not a missing watcher or absent bridge call.
