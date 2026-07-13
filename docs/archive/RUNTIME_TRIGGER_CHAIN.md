# RUNTIME_TRIGGER_CHAIN

## Trigger chain coverage

The daemon now logs the full runtime trigger chain from workspace activity through continuity propagation.

### Observed triggers

1. `file_change_detected`
   - logged when the daemon detects a filesystem event for a monitored file
   - this includes Python files, `.pecs/ai_chat_history.json`, and runtime activation events

2. `copilot_activity_detected`
   - logged when the latest chat event source contains `copilot`
   - indicates a Copilot-originated AI interaction was observed in `.pecs/ai_chat_history.json`

3. `continue_activity_detected`
   - logged when the latest chat event source contains `continue`
   - indicates a Continue-originated AI interaction was observed in `.pecs/ai_chat_history.json`

4. `runtime_activation_detected`
   - logged when `runtime_activation.jsonl` changes and the daemon has runtime locality available

5. `topology_rebuild_started` / `topology_rebuild_completed`
   - logged around `_rebuild_runtime_topology()`
   - includes changed file context and resulting topology counts

6. `continuity_refresh_started` / `continuity_refresh_completed`
   - logged around bridge refresh execution
   - includes trigger and status

7. `projection_refresh_started` / `projection_refresh_completed`
   - logged when compact/active projection writes happen in chat, activation, or topology rebuild paths

## Downstream regeneration events

The following events now prove actual downstream execution:
- `topology_compact_refreshed`
- `locality_index_refreshed`
- `compact_bundle_refreshed`
- `active_context_refreshed`

These show that the daemon did not merely update health state; it also regenerated specific PECS artifacts.

## Skip and no-op events

The daemon can now explicitly log when a step is skipped or no-op:
- `projection_skipped`
- `projection_no_changes`
- `continuity_entries_skipped`
- `continuity_noop`

This ensures the chain is visible even when a refresh decision is intentionally bypassed.

## Failure events

Failures in the chain are now visible with structured error events:
- `write_retry`
- `write_timeout`
- `bridge_execution_failed`
- `projection_refresh_failed`
- `continuity_extraction_failed`
- `incremental_sync_failed`

## Resulting chain

The effective runtime visibility chain is now:

workspace activity
→ `file_change_detected`
→ event-specific trigger detection (`copilot_activity_detected` / `continue_activity_detected` / `runtime_activation_detected`)
→ topology build or compact/context rebuild
→ `projection_refresh_started`
→ artifact refresh events
→ `continuity_refresh_started`
→ bridge export
→ `continuity_refresh_completed`

This chain is logged step-by-step in `.pecs/logs`.
