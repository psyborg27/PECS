# MINIMAL_DOWNSTREAM_REPAIR_PLAN

## Goal

Restore continuous runtime continuity hydration without redesigning PECS.
Keep the fix narrow: repair pipeline links, not architecture.

## Minimal repair steps

1. Add an explicit freshness check before or during bridge refresh.
   - In `WorkspaceContinuityDaemon._execute_bridge_refresh()` or `_run_continuity_refresh()`,
     validate that core runtime artifacts exist and are newer than the last known workspace trigger.
   - If stale, force a local `_rebuild_runtime_topology()` or at minimum rebuild `compact_bundle.json` / `active_context.json`.
   - This prevents `continuity_refresh_state.json` success from masking stale runtime artifacts.

2. Harden `ai_chat_history.json` ingestion tracing.
   - Confirm that external events written to `.pecs/ai_chat_history.json` are the only accepted source.
   - Add a debug state or sentinel that records the last successful chat append event timestamp.
   - If `ai_chat_history.json` does not change after Copilot/Continue activity, surface the missing integration rather than treat the refresh as complete.

3. Ensure runtime topology rebuild is never skipped by stale startup state.
   - Review `_should_full_scan()` logic to avoid skipping rebuild when `compact_bundle.json`/`locality_index.json` are present but likely stale.
   - At least during daemon startup, perform a lightweight validation of `topology_compact.json` freshness or sanity-check file count.

4. Surface authority evidence into projection build.
   - Wire `locality_authority_state.json` or the internal archaeology evidence into `_build_compact_bundle()` or `_build_active_context_payload()`.
   - This keeps chat-derived authority from being orphaned and supports fresh projection regeneration when continuity evidence changes.

5. Keep the bridge export path read-only.
   - Do not change `.pecs/bridge/export_workspace_continuity.py` into a reconstruction engine.
   - Instead, ensure it reports if upstream core artifacts are stale or missing, and let the daemon fix them before export.

## Verification checkpoints

After repair, confirm that the following update sequences refresh all target artifacts:
- Copilot activity → `.pecs/ai_chat_history.json` updated → `compact_bundle.json` / `active_context.json` rebuilt → `continuity_refresh_state.json` success
- Continue activity → `.pecs/ai_chat_history.json` updated → same as above
- Topology rebuild → `.pecs/topology_compact.json`, `compact_bundle.json`, `active_context.json` rebuilt → `continuity_refresh_state.json` success
- Runtime activation update → `compact_bundle.json`, `active_context.json` rebuilt → `continuity_refresh_state.json` success

## Risk minimization

- Do not redesign the PECS architecture.
- Do not add large off-path rebuild logic.
- Do not broaden active context aggressively.
- Only tighten the chain between existing triggers and the actual artifact writers.
