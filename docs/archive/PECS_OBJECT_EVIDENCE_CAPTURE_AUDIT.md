# PECS Object Evidence Capture Audit

## Scope

This audit evaluates actual implementation and actual stored evidence in the workspace.
It is based on:
- `.pecs/ai_chat_history.json`
- `append_ai_chat_history.py`
- `scripts/export_workspace_continuity.py`
- `.pecs/locality_index.json`
- `.pecs/continuity/engineering_continuity_state.json`

This audit does not consider design intent, architecture documents, or proposed changes.

---

## Part 1: Capture Audit

For each item, the status reflects the actual stored evidence and implementation behavior in this workspace.

- `File`: PARTIAL
  - Actual stored evidence: `engineering_continuity_state.json` uses inferred `accepted_locality` strings like `workspace_bridge_cli.py` and `install_workspace_integration.py`.
  - `.pecs/locality_index.json` contains explicit file mappings for object IDs.
  - Missing: no direct file field on actual AI continuity events and no robust event-to-file object mapping.

- `Class`: MISSING
  - Actual stored artifacts do not record class-level linkage in AI event history or continuity chains.
  - `.pecs/locality_index.json` contains class metadata for object IDs, but those object IDs are not wired into the current chat history evidence in this workspace.

- `Function`: MISSING
  - No actual function-level capture is present in `ai_chat_history.json` or `engineering_continuity_state.json`.
  - `locality_index.json` has `method` metadata, but it is not connected to chat events.

- `Object ID`: PARTIAL
  - `append_ai_chat_history.py` supports `object_ids`, and `scripts/export_workspace_continuity.py` consumes `object_ids`.
  - Actual stored evidence in `.pecs/ai_chat_history.json` does not include `object_ids`; it contains unrelated correlation keys such as `objects`, `errors`, `fixes`, `outcome`.
  - So the capability exists, but the actual evidence is absent in this workspace.

- `Episode ID`: MISSING
  - No `episode_id`, `episode`, or equivalent identifier appears in `ai_chat_history.json` or continuity artifacts.
  - No code path in the inspected files normalizes or exports an episode identifier.

- `AI Edit Event`: PARTIAL
  - `ai_chat_history.json` records event entries with `event_type` and `source`.
  - Actual workspace events are mostly `attempted_fix`, `daemon_started`, and validation markers.
  - There is no standardized explicit AI edit event object beyond generic event history.

- `User Acceptance`: PARTIAL
  - `append_ai_chat_history.py` normalizes `validation_outcome` when present.
  - `scripts/export_workspace_continuity.py` counts `validation_accept_count`.
  - Actual stored evidence in this workspace does not include normalized `validation_outcome`; the sample history has only legacy correlation keys.

- `User Rejection`: PARTIAL
  - Similar to acceptance: support exists in normalization/export, but actual stored evidence in `.pecs/ai_chat_history.json` does not show normalized rejection outcomes.

- `Validation Outcome`: PARTIAL
  - `append_ai_chat_history.py` normalizes `validation_outcome` into allowed values.
  - `scripts/export_workspace_continuity.py` derives `validation_accept_count`, `validation_reject_count`, etc.
  - Actual evidence in this workspace is weak because stored entries do not contain `validation_outcome` directly.

- `Runtime Confirmation`: SUPPORTED
  - Actual stored evidence contains at least one event with `correlation.runtime_effect_confirmed = false`.
  - The export code also supports fallback from `runtime_confirmation_signal`.

- `Runtime Failure`: MISSING
  - No field named `runtime_failure` or equivalent failure indicator exists in the inspected artifacts.
  - `runtime_effect_confirmed = false` appears, but explicit runtime failure metadata is not stored.

---

## Part 2: Correlation Audit

### What the system can correlate today

- `append_ai_chat_history.py` is the actual ingestor for chat events.
- `scripts/export_workspace_continuity.py` is the actual exporter that groups normalized chat events into continuity chains.
- `_normalize_chat_history_entries()` extracts `object_ids`, `error_ids`, `result_ids`, `validation_outcome`, and `runtime_effect_confirmed` from event correlation.
- `_build_engineering_continuity_state()` groups entries by inferred topic and locality.

### What the system cannot correlate without LLM inference

- `User Request → AI Response`: no explicit request/response pairing is persisted in `ai_chat_history.json`.
  - There are no `request_id`, `parent_event_id`, `trace_id`, or `causality_chain_id` fields in the actual chat-history entries.
- `Files / Classes / Functions`: only indirect locality inference exists.
  - `_infer_engineering_continuity_locality()` uses message text heuristics to map messages to file names like `workspace_bridge_cli.py`.
  - There is no direct, non-inference-derived connection from chat events to class or function metadata.
- `Outcome`: the exporter can count outcome signals only if events carry normalized `validation_outcome` or runtime confirmation.
  - In this workspace, the actual events do not carry normalized accepted/rejected outcomes.

### Exact code paths responsible

- `append_ai_chat_history.py`:
  - `_normalize_payload()` handles correlation field normalization.
  - `_event_id()` deduplicates events.
- `scripts/export_workspace_continuity.py`:
  - `_normalize_chat_history_entries()` converts raw entries into normalized event records.
  - `_build_engineering_continuity_state()` groups events by topic and locality.
  - `_infer_engineering_continuity_locality()` maps messages to file names.
  - runtime confirmation and validation counts are derived from `correlation.runtime_effect_confirmed`, `correlation.runtime_confirmation_signal`, and `entry.validation_outcome`.

### Conclusion

- The current code path can correlate event-level evidence into continuity chains.
- It cannot reliably correlate user request → AI response → file/class/function → outcome without text-based inference and without explicit event linkage.

---

## Part 3: Object Group Audit

### Current artifact content

- `.pecs/locality_index.json` contains object metadata:
  - object ID → file
  - object ID → class
  - object ID → method/function
- `.pecs/ai_chat_history.json` contains chat events and correlation payloads.
- `.pecs/continuity/engineering_continuity_state.json` contains chain-level counts for:
  - `validation_accept_count`
  - `validation_reject_count`
  - `validation_regression_count`
  - `runtime_effect_confirmed`
  - `object_error_links`

### Is there enough information to build Object Groups today?

- File-level grouping: PARTIAL
  - `accepted_locality` in continuity chains can resolve to file names.
  - Locality strings are not a formal object group key, but they provide some file-level evidence.
- Class/function grouping: MISSING
  - No event history links class/function names to AI evidence.
  - `locality_index.json` contains class/function metadata, but no event mapping exists in actual chat history.
- Runtime evidence: PARTIAL
  - Runtime confirmation is recorded and exported.
  - No explicit runtime failure field is present.
- Ownership evidence: MISSING/PARTIAL
  - Continuity chains record `source_counts` and `source_tags`, which is a weak ownership signal.
  - There is no object-level ownership assignment.
- Validation evidence: PARTIAL
  - Export chains can accumulate validation counts.
  - Actual stored evidence lacks normalized `validation_outcome` values in this workspace.
- Acceptance/Rejection evidence: PARTIAL
  - Code paths exist for accepted/rejected counts.
  - Actual stored events are not using those normalized fields.

### Conclusion

Current artifacts do not contain enough explicit object-group linkage to build robust object groups that include class/function boundaries and ownership evidence.
They are sufficient only for coarse chain-level groupings and some file-level inference.

---

## Part 4: Most Important Question

### Primary missing component for the original PECS Object Authority model

**B. Object Correlation**

### Justification

- `append_ai_chat_history.py` and `scripts/export_workspace_continuity.py` support object-level fields such as `object_ids`, `error_ids`, `result_ids`, and `runtime_effect_confirmed`.
- Actual stored evidence in `.pecs/ai_chat_history.json` does not contain normalized `object_ids` or episode identifiers.
- Continuity chains are derived by topic/locality inference rather than explicit object-event linkage.
- `engineering_continuity_state.json` contains chain metrics and confidence scores, so authority scoring machinery exists, but it is built on weak object correlation.

Thus the primary gap is not the scoring code or projection generation path; it is the missing explicit linkage that ties events to object identities and object groups.

---

## Part 5: Implementation Impact

### Would the current storage model remain usable if PECS were upgraded to true Object Authority?

**PARTIAL**

### Explanation

- The current storage model already has useful pieces:
  - a single canonical event sink in `.pecs/ai_chat_history.json`
  - object metadata in `.pecs/locality_index.json`
  - chain-level authority metrics in `.pecs/continuity/engineering_continuity_state.json`
- However, the current stored evidence lacks explicit object-level linkage and episode identifiers.
- Therefore the storage model can be reused, but it is incomplete for true Object Authority without richer object/event correlation in the existing artifacts.

---

## Summary

The actual code supports many of the required fields, but the current stored evidence in this workspace is incomplete:
- file-level capture is only partial,
- class/function capture is missing,
- object ID support exists in code but not in actual events,
- episode IDs are missing,
- runtime confirmation is supported,
- runtime failure is missing,
- correlation is currently based on inference and not explicit non-LLM linkage.

The most important missing component is object correlation.
