# PECS Object Authority Recovery Plan

## Objective

Define the smallest incremental upgrade required to restore PECS Object Authority while preserving the current artifacts, daemon, continuity exports, and consumer integrations.

This recovery plan is based on actual implementation and artifacts in the workspace.

---

## 1. File → Class → Function Evidence Capture

### 1.1 Capture mechanism

Use stable object IDs that encode progressively finer object granularity.
The capture flow should be:
- File-level evidence captured as file-scoped object IDs.
- Class-level evidence captured as class-scoped object IDs.
- Function-level evidence captured as function-scoped object IDs.

### 1.2 Practical approach

- Record `object_ids` as an array in chat history events.
- Each `object_id` should resolve to a canonical registry entry in `.pecs/locality_index.json`.
- Object registry entries should carry file/class/function metadata so a single `object_id` can be dereferenced to:
  - `file`
  - `class`
  - `function`
- Do not create separate file/class/function arrays in the event sink; use object IDs as the linking mechanism.

### 1.3 Minimal event fields

Each captured event should include:
- `object_ids`: `["PECS_ID:module", "PECS_ID:module.Class", "PECS_ID:module.Class.method"]`
- `event_type`: existing formal types such as `attempted_fix`, `accepted_fix`, `validation`, `runtime_validation`
- `correlation.validation_outcome`: normalized acceptance/rejection outcome
- `correlation.runtime_effect_confirmed`: existing runtime confirmation signal
- `correlation.runtime_failure`: new explicit failure indicator if present

---

## 2. Engineering Intent Episodes Identification

### 2.1 Episode identity

Use an explicit `episode_id` for engineering intent episodes.
This is the smallest incremental upgrade to recover episode-based authority without redesigning current artifacts.

### 2.2 Source for episode IDs

- Leverage existing request/trace lineage semantics in `workspace_bridge_cli.py`.
- Define `episode_id` as a stable grouping key for a user request plus all follow-up AI and validation events.
- If available, reuse `causality_chain_id` or `trace_id` as the episode anchor, but add `episode_id` explicitly to the event sink for clarity.

### 2.3 Episode event linking

Events should include:
- `episode_id`
- `parent_event_id`
- `event_role`: one of `request`, `response`, `validation`, `runtime_observation`
- `request_id`/`trace_id` if already available from the existing request lineage infrastructure

This allows the current sink to support episode reconstruction without breaking existing event consumers.

---

## 3. Object ID Generation

### 3.1 Canonical object ID source

Use `.pecs/locality_index.json` as the canonical object registry if it is extended to include stable IDs for file, class, and function objects.

### 3.2 Generation rules

- Object IDs should be stable, human-readable, and scoped.
- Prefer existing `PECS_ID:` keys already present in `locality_index.json`.
- For new file/class/function objects, generate IDs like:
  - `PECS_ID:<module>` for file-level objects
  - `PECS_ID:<module>.<Class>` for class-level objects
  - `PECS_ID:<module>.<Class>.<method>` for function-level objects

### 3.3 Minimal extension

If `locality_index.json` lacks explicit class/function entries, add those as new registry objects rather than creating a second registry.

---

## 4. Object ID Linking Across the Lifecycle

### 4.1 Required event sequence

Use object IDs to link:
- `User Request`
- `AI Response`
- `Files`
- `Classes`
- `Functions`
- `Acceptance`
- `Rejection`
- `Runtime Validation`

### 4.2 Linking rules

- The request event records requested object IDs and `episode_id`.
- The AI response event records the same or derived object IDs plus `parent_event_id`.
- Acceptance/rejection events carry the same `episode_id` and object IDs, with `validation_outcome`.
- Runtime validation events carry the same object IDs and `runtime_effect_confirmed` plus optional `runtime_failure`.

### 4.3 Concrete link fields

In the canonical event sink, the following fields should be added or normalized:
- `episode_id`
- `parent_event_id`
- `event_role`
- `object_ids`
- `correlation.validation_outcome`
- `correlation.runtime_effect_confirmed`
- `correlation.runtime_failure`

These fields enable non-LLM reconstruction of object authority relationships.

---

## 5. Existing Files Requiring Modification

The smallest incremental upgrade touches the following files:

- `.pecs/tools/append_ai_chat_history.py`
  - Extend normalization to preserve `episode_id`, `parent_event_id`, `event_role`, and `object_ids`.
  - Normalize `runtime_failure` and preserve object-level correlation fields.

- `scripts/export_workspace_continuity.py`
  - Extend continuity export to preserve object IDs and episode IDs in derived chains.
  - Add object-group summaries and object-driven chain aggregation.

- `workspace_bridge_cli.py`
  - Optionally export or propagate request/trace lineage metadata into any emitted `ai_chat_history.json` events if the event ingestion is triggered there.
  - Reuse existing request/trace/causality identifiers to generate `episode_id`.

- Optional integration points if they already produce chat events or locality metadata:
  - `integrations/copilot_adapter.py`
  - `integrations/continue_adapter.py`

Those adapter files may only need minimal metadata propagation support for object IDs if they are actual event generators.

---

## 6. Existing Artifacts Requiring Extension

The plan requires extending these artifacts only:

- `.pecs/ai_chat_history.json`
  - Remains canonical event sink.
  - New fields added in event records: `episode_id`, `parent_event_id`, `event_role`, `object_ids`, and optional `runtime_failure`.

- `.pecs/locality_index.json`
  - Extended into the canonical object registry.
  - Add or normalize stable object ID entries for file/class/function.
  - Preserve existing registry fields and file-level mappings.

- `.pecs/continuity/engineering_continuity_state.json`
  - Extend derived chain summaries to include object group references and episode anchoring.
  - Preserve existing metrics and chain semantics.

No new artifact store is required.

---

## 7. Required New Artifact Fields

### In `.pecs/ai_chat_history.json`

- `episode_id`
- `parent_event_id`
- `event_role` (`request`, `response`, `validation`, `runtime_observation`)
- `object_ids` (array of canonical object registry IDs)
- `correlation.runtime_failure` (optional explicit failure indicator)

### In `.pecs/locality_index.json`

- `object_id` if not already implied by the registry key
- `file` (already present)
- `class` (add if missing)
- `function` or `method` (add if missing)
- `canonical_name` or equivalent human-facing name for registry entries

### In `.pecs/continuity/engineering_continuity_state.json`

- `object_ids` per chain
- `episode_ids` per chain or `episode_summary`
- `object_group_ids` or `object_group_metadata` if grouping is useful
- `validation_accept_count`, `validation_reject_count`, `runtime_effect_confirmed` already exist and should be preserved

---

## 8. Can `locality_index.json` Become the Canonical Object Registry?

Yes, with extension.

### Why yes

- It already contains object metadata and file mappings.
- It is already referenced by runtime and continuity components.
- It can be extended incrementally without adding a new registry artifact.

### Required extension

- Normalize stable object IDs as registry keys.
- Add missing class/function metadata entries.
- Ensure event object IDs map directly to these registry entries.

---

## 9. Can `ai_chat_history.json` Remain the Canonical Event Sink?

Yes.

### Why yes

- It is already the existing canonical chat history sink.
- The daemon and continuity refresh path already depend on it.
- Additive field extensions preserve backward compatibility.

### Preservation approach

- Keep current event shape and history semantics.
- Add new fields only; do not replace the sink or create a parallel event store.

---

## 10. Can the Upgrade Be Implemented Incrementally Without Breaking Retrieval?

Yes, partially.

### Incremental path

- Add new fields to `ai_chat_history.json` and `locality_index.json` while leaving existing entries valid.
- Modify `append_ai_chat_history.py` and `scripts/export_workspace_continuity.py` to handle old events gracefully.
- Use optional new fields rather than requiring them on every event.
- Preserve current chain export behavior and add object-group metadata downstream.

### Compatibility outcome

- Existing retrieval and continuity consumers can continue operating on current fields.
- New object authority consumers can begin using the extended object IDs and episode fields as they become available.
- The upgrade does not require a new backend or new artifact store.

---

## Recommended Minimal Implementation Roadmap

1. Extend `.pecs/tools/append_ai_chat_history.py`:
   - normalize `episode_id`, `parent_event_id`, `event_role`, `object_ids`, and `runtime_failure`.
   - preserve existing `source`, `event_type`, and `correlation` semantics.

2. Extend `scripts/export_workspace_continuity.py`:
   - carry `object_ids` and `episode_id` through continuity chains.
   - add object-group-aware chain summaries.
   - keep existing continuity confidence and locality scoring.

3. Extend `.pecs/locality_index.json` semantics:
   - declare it as the canonical object registry.
   - ensure stable object ID semantics for file/class/function entries.

4. Use request/trace lineage metadata in `workspace_bridge_cli.py` if available:
   - generate or propagate `episode_id` in any event-producing path.

5. Preserve current artifacts and consumers:
   - no new artifact store
   - no change to the daemon’s event sink/watch behavior
   - additive field extension only

---

## Conclusion

The smallest incremental recovery is to make `ai_chat_history.json` a richer event sink and make `locality_index.json` the canonical object registry.
The recovery plan does not require a new artifact store, does not require replacing the daemon, and can be implemented additively.
