# PECS Object Authority Implementation Readiness

## Objective

Assess whether PECS is ready to begin implementation of the Object ID Producer using current architecture, source, and documentation.

## 1. Architectural decisions resolved?

### Resolved

- `append_ai_chat_history.py` is the canonical event ingestion path and already normalizes `object_ids` and correlation fields.
- `scripts/export_workspace_continuity.py` already consumes `object_ids` and currently supports `validation_outcome` and runtime confirmation signals.
- `.pecs/locality_index.json` is the canonical object registry and already contains `file`, `class`, and `method` metadata for many entries.
- `workspace_bridge_cli.py` already carries request/trace/parent_event lineage fields, so episode/group linkage can be wired without a new protocol.
- `PECSProQueryAdapter` already provides deterministic file/symbol resolution helpers that can be reused for object ID derivation.

### Unresolved architectural questions

- Should `episode_id` be derived from existing `trace_id`/`causality_chain_id` or generated as a new explicit event field? The docs recommend explicit `episode_id`, but implementation details are not fully fixed.
- Can function-level `PECS_ID` resolution be guaranteed from the current `locality_index.json` content alone, or will the registry need additional class/method entries as a preparatory step? The workspace shows partial method metadata, but completeness is uncertain.
- Will the Object ID Producer assume all sources provide structured locality hints, or must it also include a generic fallback resolver for unstructured events? The design suggests structured hints are primary, but the exact fallback contract is not fully specified.
- Is `append_ai_chat_history.py` the only producer modification required for Phase 1, or must event generators like consumer adapters also be modified immediately to preserve explicit `object_ids` on projection-initiated events? The docs indicate `append_ai_chat_history.py` is primary, but adapters are optional supporting paths.

## 2. Phase readiness classification

### Object ID Producer
- Status: **PARTIAL**
- Why: Architecture is ready. `append_ai_chat_history.py` already normalizes correlation fields and supports `object_ids`, and `locality_index.json` exists as the registry. Implementation still requires code to derive canonical object IDs deterministically from structured hints and registry lookup.

### Object Evidence Capture
- Status: **PARTIAL**
- Why: The event sink and export path already support object-level fields, but actual evidence capture is not yet wired end-to-end. Existing history shows legacy `objects/errors/fixes/outcome` rather than normalized `object_ids`.

### Object Correlation
- Status: **PARTIAL**
- Why: Correlation schema is mostly present in the event normalization layer, but explicit episode/parent linkage and runtime failure capture are not present in current stored events. The system can support them, but the producer and ingestion paths need extension.

### Authority Projection
- Status: **PARTIAL**
- Why: `export_workspace_continuity.py` already reads `object_ids` and can preserve them. However, object-group projection and object-driven authority chain summarization are not yet implemented, so this phase is not fully ready.

## 3. Exact code changes required for Phase 1 only

### Primary required file

- `append_ai_chat_history.py`

### Required implementation work

- Add a new deterministic object ID derivation helper in `append_ai_chat_history.py`.
- Load `.pecs/locality_index.json` or a cached file-to-object map during event normalization.
- In `_normalize_payload()` or `_build_payload()`, merge derived canonical `object_ids` into `payload["correlation"]["object_ids"]` before final normalization.
- Use existing normalized fields and structured hints only:
  - `correlation.object_ids`
  - `correlation.file` / `correlation.target_file`
  - `correlation.class`
  - `correlation.method` / `correlation.function`
  - `correlation.changed_files`
  - `correlation.attempted_locality`
  - `correlation.runtime_authority_candidate`
  - direct `PECS_ID:` anchors
- Preserve current `object_ids` if already supplied.
- Ensure `object_ids` remains a sorted unique list in the final payload.

### Optional supporting change if needed for Phase 1

- Add a small helper function to `append_ai_chat_history.py` for normalized path matching against `locality_index.json`.

## 4. Existing subsystem refactoring required before Phase 1?

- No major subsystem refactoring is required.
- The implementation can be contained within `append_ai_chat_history.py`.
- Existing `PECSProQueryAdapter` utilities are usable without refactor, so the core runtime/locality subsystems need not be changed.
- One area of caution: `locality_index.json` may need schema extension later for richer class/method metadata, but that is not a blocker for Phase 1 if Phase 1 starts with file-level and structured registry resolution.

## 5. Tests, validation paths, and artifacts sufficiency

### Existing coverage

- `append_ai_chat_history.py` normalization path is present, but no direct unit tests are visible for this file in the repository.
- `scripts/export_workspace_continuity.py` already validates and consumes `object_ids`, so it can exercise downstream artifacts once object IDs are produced.
- Runtime/locality tests exist in `runtime/daemon/test_runtime_locality.py`, but they do not cover chat history ingestion.
- Validation tests exist for determinism and runtime projection, but not for the new object ID producer.

### Sufficiency assessment

- Sufficient to verify behavior after implementing Phase 1 if new targeted tests are added.
- Current test suite is not sufficient by itself to guarantee Phase 1 correctness because it lacks append_ai_chat_history-specific coverage.
- Existing artifact validation (`validate_workspace_continuity.py`, `export_workspace_continuity.py`) can verify generated event shape and object_id propagation once producer code is present.

## Most Important Question

### Can implementation begin now?

**Answer: PARTIAL**

### Exact blockers

- No direct architectural blocker prevents starting work.
- The implementation requires a clear deterministic object-id derivation contract for `append_ai_chat_history.py` that is not yet fully specified for all source hint types.
- The current `locality_index.json` completeness for class/method entries is uncertain; if Phase 1 intends function-level IDs, the registry may need preparatory enrichment.
- There is no existing append_ai_chat_history producer test coverage, so implementation must include new tests to avoid regression.

## Recommendation

Begin Phase 1 implementation with `append_ai_chat_history.py` and a small object-id resolver, while preserving backward compatibility. Add unit tests for object-id derivation and event normalization before completing the phase.
