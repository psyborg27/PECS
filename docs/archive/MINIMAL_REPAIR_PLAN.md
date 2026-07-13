# MINIMAL_REPAIR_PLAN

## Goal

Restore PECS-v2 continuity hydration, daemon orchestration, and projection synchronization with the smallest possible repair footprint.

## Current minimal repair points

### 1. Close the topology-to-hydration gap

- Add a continuity refresh trigger after successful `_rebuild_runtime_topology()`.
- Rationale: `.py` changes currently update core artifacts, but the bridge export layer is not automatically invoked.
- Effect: `.pecs/continuity/*` artifacts stay in sync with runtime topology and locality.

### 2. Preserve startup freshness

- Ensure startup does not rely solely on preexisting artifacts when the workspace has changed.
- Possible minimal fix: when `_should_full_scan()` is false, still perform a lightweight verification or force `_run_continuity_refresh()` after startup if core artifacts exist.
- Effect: avoids stale continuity on daemon restart.

### 3. Align activation and chat-based authority signals

- Ensure runtime activation updates and chat updates both refresh the downstream authority/continuity path.
- If needed, move `_refresh_locality_authority_state()` or its equivalent into both `_on_chat_history_update_unlocked()` and `_on_activation_update()` so authority evidence is not only chat-driven.
- Effect: reinforcement and rejection evidence propagate consistently.

### 4. Keep throttle but preserve pending refreshes

- Maintain `continuity_refresh_throttle_seconds` to avoid over-refreshing.
- Add a minimal deferral mechanism so skipped refreshes are not silently lost during rapid updates.
- Effect: balances automation with operational safety.

## Why this is minimal

- No new architecture is required.
- No workspace-wide indexing is added.
- No semantic memory or vector store is introduced.
- The fix stays within the existing daemon, bridge refresh, and export pathway.
- It preserves:
  - runtime-topology-first design
  - compact continuity discipline
  - PECS-LITE compatibility
  - large-model projection behavior

## Recommended implementation path

1. Instrument `_rebuild_runtime_topology()` to invoke `_run_continuity_refresh(trigger="runtime_topology", reason="topology rebuild")` after successful rebuild.
2. Optionally, add a small startup validation path when artifacts already exist.
3. Ensure `locality_authority_state.json` is updated whenever activation or chat-derived evidence changes.
4. Keep the existing guard that refresh only occurs when `runtime_locality_payload` exists.

## Expected result

- runtime topology rebuilds fully propagate into continuity exports.
- daemon-triggered hydration becomes reliable.
- PECS-LITE and large-model projections continue to read the same artifact contract.
- The runtime-local continuity pipeline remains compact and topology-first.
