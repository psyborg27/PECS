# PECS Object ID Producer Design

## Objective

Design the missing object ID production layer for PECS. This design is implementation planning only and does not redesign authority scoring, continuity export, or the PECS architecture.

## Summary

- `locality_index.json` is the canonical object registry.
- `append_ai_chat_history.py` already stores `object_ids` in event correlation.
- `scripts/export_workspace_continuity.py` already consumes `object_ids`.
- `object_ids` are the primary linkage mechanism.
- Object Groups are the primary authority unit.

## Verdict

**Answer: PARTIAL**

### Justification

PECS can reliably generate `object_ids` without manual tagging and without LLM inference from deterministic structured sources:

- `git diff` file/path evidence can map reliably to registry entries.
- runtime activation anchors are already `PECS_ID:` values or can be resolved deterministically.
- consumer locality projections already carry explicit `object_id` input.
- validation events carry structured locality hints.

However, sources that are only natural-language or acceptance/rejection prose cannot be mapped reliably to canonical object IDs without additional structured locality hints. Therefore the producer layer is viable for a large subset of engineering activity, but not universal.

## Source classification

| Source | Classification | Confidence | Notes |
|---|---|---|---|
| AI edit reports | SECONDARY | medium | Works when reports include explicit file/symbol metadata; not reliable from freeform text alone. |
| Git diffs | PRIMARY | high | Deterministic file path -> object id mapping via `locality_index.json`. |
| Runtime activations | PRIMARY | high | `runtime_activation.jsonl` already records runtime anchors; active context can map those to object groups. |
| Validation events | PRIMARY | medium-high | Structured locality fields are available and can be resolved to registry entries. |
| User acceptance / rejection | FALLBACK | medium-low | Best used by inheriting object_ids from prior associated events in the chain, not as a standalone source. |
| Consumer locality projections | PRIMARY | very high | Consumer adapters already operate on explicit `object_id` values. |

## Exact files to modify

### Required

- `append_ai_chat_history.py`
  - This is the canonical event ingestion and normalization path.
  - Add a deterministic object ID resolution layer here.

### Optional / supporting

- `runtime/daemon/workspace_continuity_daemon.py`
  - If runtime-specific object evidence must be aligned with chat events at ingestion time.
  - This file already reads `ai_chat_history.json`, runtime activations, and active context.

- `integrations/copilot_adapter.py`
- `integrations/continue_adapter.py`
  - These are the consumer projection entrypoints.
  - Use them to ensure projection-based events preserve explicit `object_ids` in event correlation.

## Exact event generation points

### AI edit reports

- Event source: AI-assisted edit summary or report generation.
- Producer point: wherever the event is created and sent to `append_ai_chat_history.py`.
- Candidate correlation hints:
  - `correlation.file`
  - `correlation.target_file`
  - `correlation.class`
  - `correlation.method`
  - `correlation.locality`
  - `correlation.attempted_locality`
  - explicit `PECS_ID:` anchors if present
- Minimal implementation: detect structured target metadata and resolve it into `object_ids` in `append_ai_chat_history.py`.

### Git diffs

- Event source: changed file lists or patch metadata from git integration.
- Producer point: event creation path that observes `correlation.changed_files`, `correlation.git_diff`, or `correlation.changed_paths`.
- Exact registry lookup path: map each changed file to `object_ids` using `.pecs/locality_index.json`.
- Minimal implementation:
  - build `file_path -> [object_ids]` index from `locality_index.json`
  - resolve changed files by normalized workspace-relative path
  - inject resolved `object_ids` before event append

### Runtime activations

- Event source: runtime activation signals emitted by `runtime/runtime_activation_events.py`.
- Producer point: `emit_runtime_activation()` callers, plus the daemon's runtime activation refresh in `runtime/daemon/workspace_continuity_daemon.py`.
- Exact registry lookup path:
  - if activation `source`/`target` are already `PECS_ID:` anchors, preserve them
  - otherwise use `.pecs/locality_index.json` and `active_context.json` to resolve file/symbol anchors into canonical object IDs
- Minimal implementation:
  - add a deterministic resolver that reads `.pecs/runtime_activation.jsonl` and `active_context.json` at event append time
  - if the chat event is tied to runtime activity, merge those runtime anchors into `correlation.object_ids`

### Validation events

- Event source: validation pipelines that emit outcome events; seen in chat history as `event_type` values like `attempted_fix` or `validation`.
- Producer point: event creation path for validation results feeding `append_ai_chat_history.py`.
- Exact registry lookup path:
  - use `correlation.attempted_locality`, `correlation.runtime_authority_candidate`, `correlation.locality`, and `correlation.validation_locality`
  - resolve those hints via `.pecs/locality_index.json` and `active_context.json`
- Minimal implementation:
  - when validation events arrive with structured locality hints, resolve them to canonical object IDs before appending

### User acceptance / rejection events

- Event source: user feedback events like `accepted_fix` or `rejected_fix`.
- Producer point: chat event ingestion in `append_ai_chat_history.py` or UI feedback pipeline.
- Exact registry lookup path: not direct; inherit from prior event object_ids in the same chain or session.
- Minimal implementation:
  - if the current event has no explicit `object_ids`, attempt to inherit from the most recent related event(s) in `.pecs/ai_chat_history.json`
  - rely on `source`, `event_type`, `parent_event_id`, or recency as weak chain signals

### Consumer locality projections

- Event source: consumer adapters that request projections for an explicit `object_id`.
- Producer point: `integrations/copilot_adapter.py` and `integrations/continue_adapter.py`.
- Exact registry lookup path: the object ID is already canonical; no lookup is required if it is the request target.
- Minimal implementation:
  - annotate any downstream chat/continuity event produced from projection activity with the same `object_id`
  - if the projection returns runtime targets, also preserve them as `object_ids`

## Exact registry lookup path

- Read `.pecs/locality_index.json` from workspace root.
- Build a deterministic object lookup index using each entry's `file` metadata.
- Resolve candidate file paths by normalized workspace-relative path.
- Support fallback matching for symbol anchors if the candidate hint includes a `PECS_ID:` prefix or a file+symbol reference.
- Preserve any direct `PECS_ID:` values already in the event.

## Exact object_id injection path

### Primary injection location

- `append_ai_chat_history.py`
  - add a new helper such as `_derive_object_ids_from_correlation()`
  - invoke it from `_normalize_payload()` or `_build_payload()` before the event is written
  - merge derived IDs into `payload["correlation"]["object_ids"]`
  - keep normalization/shallow sorting already present in `append_ai_chat_history.py`

### Supporting injection details

- If the event already supplies `correlation.object_ids`, preserve and normalize them.
- If the event supplies explicit `PECS_ID:` anchors, keep them.
- If the event supplies path or symbol hints, resolve them into canonical object IDs and append them.
- If the event is a user acceptance/rejection event with no explicit hints, inherit from recent related events in `ai_chat_history.json`.
- If the event originates from a consumer locality projection, attach the explicit requested `object_id`.

## Minimal implementation strategy

1. Create a deterministic object-id producer helper inside `append_ai_chat_history.py`.
2. Load `.pecs/locality_index.json` once per append or lazily when needed.
3. Derive `object_ids` from structured correlation hints and runtime/consumer projection evidence.
4. Inject resolved `object_ids` into `payload["correlation"]` before normalization and append.
5. Preserve existing event shape and export compatibility.

## Notes on design boundaries

- Do not alter `scripts/export_workspace_continuity.py` because it already consumes `object_ids` correctly.
- Do not alter scoring or authority derivation logic; this layer only feeds object_ids.
- Do not alter the continuity schema or export pipeline.
- Do not introduce LLM inference. All resolution must be deterministic from metadata, registry entries, or explicit projection targets.

## Confidence expectations by source

- `git diff` -> high confidence for file-scoped object groups, medium-high for symbol-scoped resolution.
- `runtime activations` -> high confidence when anchors are already canonical or when active context maps them deterministically.
- `consumer locality projections` -> very high confidence, because object IDs are explicit.
- `validation events` -> medium-high confidence if locality hints are structured.
- `AI edit reports` -> medium confidence when structured metadata exists; low confidence otherwise.
- `user acceptance / rejection` -> medium-low confidence; useful only as inherited evidence.

## Conclusion

The smallest implementation is a deterministic object ID producer in `append_ai_chat_history.py` that resolves structured locality hints and runtime/consumer evidence against `.pecs/locality_index.json`, then injects canonical `object_ids` into the event correlation.

The overall capability is **PARTIAL**: PECS can generate reliable object_ids from structured engineering activity without manual tagging or LLM inference, but it cannot guarantee coverage for purely unstructured AI edit summaries or freeform acceptance/rejection messages.
