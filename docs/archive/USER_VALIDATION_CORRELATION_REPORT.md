# User Validation Correlation Report

## Objective

Strengthen normalized runtime/user validation evidence without storing raw conversation as authority.

## Implemented

### Structured correlation normalization in ingestion

In `append_ai_chat_history.py`:

- Normalized and persisted deterministic fields:
  - `object_ids`
  - `error_ids`
  - `result_ids`
  - `validation_outcome`
  - `accepted_fix`
  - `rejected_fix`
  - `regression_confirmed`
  - existing runtime locality/authority signals
- Lists are deduplicated + sorted.
- `validation_outcome` is normalized to allowed enum:
  - `accepted`, `rejected`, `regression`, `unresolved`, `observed`, `unknown`
- chat history write now uses `sort_keys=True` for canonical object key ordering.

### Structured correlation usage in continuity export

In `scripts/export_workspace_continuity.py`:

- `_normalize_chat_history_entries()` now preserves normalized object/error/result and validation outcome fields.
- `_build_engineering_continuity_state()` now accumulates deterministic validation counters:
  - `validation_accept_count`
  - `validation_reject_count`
  - `validation_regression_count`
  - `validation_unresolved_count`
- Added deterministic object-error linkage map per continuity chain:
  - `object_error_links`
- Continuity outcome now reflects normalized validation state (`regression` / `unresolved` where appropriate).

### Bridge/tool parity sync

Synchronized workspace-local runtime copies:

- `.pecs/tools/append_ai_chat_history.py`
- `.pecs/bridge/export_workspace_continuity.py`

## Authority preservation

- Raw conversational narrative remains non-authoritative.
- Only normalized correlation records influence continuity evidence.

## Files changed

- `append_ai_chat_history.py`
- `scripts/export_workspace_continuity.py`
- `.pecs/tools/append_ai_chat_history.py` (synced)
- `.pecs/bridge/export_workspace_continuity.py` (synced)
