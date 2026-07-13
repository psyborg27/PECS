# PECS Object Evidence Capture Implementation Plan

## Objective

Define the smallest implementation required to recover true Object Authority on top of current PECS architecture.

Assumptions accepted from prior audits:
- Object Groups are the primary authority unit.
- `locality_index.json` becomes the canonical object registry.
- `ai_chat_history.json` remains the canonical event sink.
- Current retrieval, locality, topology, continuity, projection, daemon, and consumer integrations must remain compatible.
- Object Capture and Object Correlation are the missing components.
- Line ranges are never authoritative and must be resolved at query time.

This plan is an implementation roadmap only. No code changes are made here.

---

## Part 1: Object Registry Design

### 1.1 Object definitions

- **File object**: a canonical object representing a source file.
- **Class object**: a canonical object representing a named class or struct within a file.
- **Function object**: a canonical object representing a named function, method, or procedure within a class or file.

### 1.2 Required object fields

Extend `locality_index.json` object registry entries to include:
- `file`: existing source path string
- `class`: class name string, empty if not applicable
- `function` or `method`: function/method name string, empty if not applicable
- `object_type`: one of `file`, `class`, `function`
- `canonical_name`: stable fully qualified identifier such as `module`, `module.Class`, or `module.Class.method`
- `object_id`: stable registry key, equal to the current `PECS_ID:` registry key
- `current_location`: current file path string
- `current_scope`: optional inferred scope string when class/function metadata exists

### 1.3 Stable object IDs

- Use the existing registry keys in `locality_index.json` as canonical stable IDs.
- Preserve current `PECS_ID:` prefix semantics.
- Object ID forms:
  - file object: `PECS_ID:<module>`
  - class object: `PECS_ID:<module>.<Class>`
  - function object: `PECS_ID:<module>.<Class>.<method>` or `PECS_ID:<module>.<function>`
- IDs must not include line ranges.
- IDs must be stable across modularization as long as the canonical object retains its identity.

### 1.4 Modularization-safe identity rules

- Prefer symbol-qualified IDs over path-qualified IDs when the registry can resolve current location from the workspace.
- If the same object is moved or renamed, the object registry must preserve stable `object_id` via deterministic object identity rules in `locality_index.json`.
- Current location resolution is allowed to change; object IDs remain stable.

### 1.5 Current-location resolution rules

- Resolve `current_location` from the current workspace state at query time.
- Do not store line ranges in the registry.
- Store only path and symbol metadata in `locality_index.json`.
- At query time, use workspace symbol resolution and the current `locality_index.json` entry to derive exact location.

### 1.6 Exact `locality_index.json` extension

Extend existing entries with:
- `object_type`
- `canonical_name`
- explicit `class` and `function` fields
- `current_location`

Leave existing fields intact.
Add new object entries for class and function objects where missing.

---

## Part 2: Object Evidence Capture

### 2.1 Event roles to capture

PECS should capture the following event types and attach them to `object_ids`:
- `User Request`
- `AI Response`
- `AI Edit`
- `User Acceptance`
- `User Rejection`
- `Validation Success`
- `Validation Failure`
- `Runtime Confirmation`
- `Runtime Failure`

### 2.2 Exact event fields in `ai_chat_history.json`

Extend `ai_chat_history.json` event records with:
- `event_id`: existing stable unique event identifier
- `source`: existing source marker (`copilot`, `continue`, `kimi`, `manual`, etc.)
- `event_type`: explicit type such as `user_request`, `ai_response`, `ai_edit`, `accepted_fix`, `rejected_fix`, `validation_success`, `validation_failure`, `runtime_confirmation`, `runtime_failure`
- `event_role`: categorical role to simplify deterministic correlation (`request`, `response`, `edit`, `validation`, `runtime`)
- `message`: existing human readable description
- `ts`: existing timestamp
- `episode_id`: optional grouping identifier for event sequence if used, but not primary authority
- `parent_event_id`: optional parent linkage for exact request-response chains
- `object_ids`: array of canonical object IDs
- `correlation`: object containing:
  - `validation_outcome`: normalized value in `accepted|rejected|regression|unresolved|observed|unknown`
  - `runtime_effect_confirmed`: boolean or absent
  - `runtime_failure`: boolean or absent
  - `runtime_confirmation_signal`: boolean or absent
  - `accepted_fix`: boolean or absent
  - `rejected_fix`: boolean or absent
  - `regression_confirmed`: boolean or absent
  - `attempted_locality`: optional file-level hint only
  - `runtime_authority_candidate`: optional object candidate hint only

### 2.3 Capture rules

- All event records must include `object_ids` when object evidence is available.
- `ai_edit`, `user_acceptance`, `user_rejection`, `validation_success`, `validation_failure`, `runtime_confirmation`, and `runtime_failure` events must include corresponding correlation booleans.
- `User Request` events should record `object_ids` for requested artifacts.
- `AI Response` and `AI Edit` events should inherit or derive `object_ids` from the request or from detected impacted objects.

### 2.4 Minimal changes to current sink

- Keep `ai_chat_history.json` as the sole canonical event sink.
- Add the new fields additively.
- Ensure the current daemon and continuity exporter continue to read the file.

---

## Part 3: Object Correlation

### 3.1 Object Group construction rules

Construct an Object Group deterministically from the union of object IDs referenced by events.

- A single Object Group is defined by a set of matched canonical object IDs from `locality_index.json`.
- If events share the same canonical object IDs, they belong to the same Object Group.
- If events reference file, class, and function object IDs, use the full set of IDs to determine the Object Group.

### 3.2 Deterministic correlation rules

Use only explicit event metadata, not inference:
- Group events by exact `object_ids` membership.
- If an event has multiple `object_ids`, it contributes to all corresponding Object Groups.
- Do not infer object groups from free-text `message` or `attempted_locality` alone.
- Use `source`, `event_type`, and boolean correlation signals to build evidence for each object group.

### 3.3 Evidence aggregation

For each Object Group, aggregate evidence deterministically from events:
- `acceptance evidence`: count of events where `validation_outcome == accepted` or `accepted_fix == true`
- `rejection evidence`: count of events where `validation_outcome == rejected` or `rejected_fix == true`
- `runtime evidence`: count of events where `runtime_effect_confirmed == true` or `runtime_failure == true`
- `validation evidence`: count of validation events with normalized outcomes
- `ownership evidence`: source counts and `source` provenance per object ID
- `historical evidence`: all prior events attached to the object IDs

### 3.4 Object Group identity

- Object Group ID may be derived from the sorted list of canonical object IDs.
- The group is a deterministic aggregation over explicit object IDs, not a new artifact store.

---

## Part 4: Authority Generation

### 4.1 Authority types and required inputs

#### Ownership Authority
- Evidence sources:
  - `source` counts across events (`copilot`, `continue`, `kimi`, `manual`)
  - object-specific edit and validation events
- Required inputs:
  - `object_ids`
  - `source`
  - `event_type`
  - `accepted_fix`, `rejected_fix`
  - `validation_outcome`
- Weighting inputs:
  - relative frequency per source
  - recency of acceptance/rejection
  - object-level source uniqueness

#### Runtime Authority
- Evidence sources:
  - `runtime_effect_confirmed`
  - `runtime_failure`
  - runtime validation events
- Required inputs:
  - `object_ids`
  - `runtime_effect_confirmed`
  - `runtime_failure`
  - `runtime_confirmation_signal`
  - event roles labeled `runtime`
- Weighting inputs:
  - confirmation count
  - failure count
  - ratio of successes to failures
  - whether runtime evidence is direct or inferred from event roles

#### Validation Authority
- Evidence sources:
  - `validation_outcome`
  - `accepted_fix`
  - `rejected_fix`
  - `regression_confirmed`
- Required inputs:
  - `object_ids`
  - `validation_outcome`
  - `accepted_fix`
  - `rejected_fix`
  - `event_type`
- Weighting inputs:
  - accepted versus rejected counts
  - regression evidence
  - unresolved counts
  - validation event recency

#### Historical Authority
- Evidence sources:
  - aggregated object group event history from `ai_chat_history.json`
  - continuity chain summaries in `engineering_continuity_state.json`
- Required inputs:
  - `object_ids`
  - event counts over time
  - continuity chain metrics such as `continuity_confidence`
- Weighting inputs:
  - historical depth of object evidence
  - continuity chain confidence
  - source diversity over time

#### Cross-Agent Authority
- Evidence sources:
  - object group event provenance across `source` values
  - explicit multi-source evidence counts
- Required inputs:
  - `object_ids`
  - `source`
  - `object_group` event counts per source
- Weighting inputs:
  - cross-source agreement
  - source-specific acceptance/rejection patterns
  - source diversity within the same object group

### 4.2 No scoring formulas yet

This plan defines required evidence inputs only, not exact score formulas.

---

## Part 5: Projection Generation

### 5.1 Final projection format

For large models, return a ranked candidate list of object groups.

Each candidate contains:
- `candidate_rank`
- `object_group_id`
- `object_ids`
- `file_objects`
- `class_objects`
- `function_objects`
- `authority_breakdown`:
  - `ownership_authority`
  - `runtime_authority`
  - `validation_authority`
  - `historical_authority`
  - `cross_agent_authority`
- `current_location`:
  - resolved current file path(s)
  - resolved current symbol scope
- `current_line_range`: dynamic query-time resolved range, not stored in artifacts
- `evidence_summary`:
  - counts of acceptance, rejection, runtime confirmation, runtime failure, validation outcomes
  - source provenance summary
  - event recency summary

Example candidate structure:
- `Candidate 1`
  - `Object Group`
  - `File`
  - `Class`
  - `Function`
  - `Authority Breakdown`
  - `Current Location`
  - `Current Line Range`
  - `Evidence Summary`

### 5.2 Small model projection format

For small models, return only the highest-confidence candidate with the same fields, possibly in condensed form.

Small model fields:
- `object_group_id`
- `object_ids`
- `top_file`
- `top_class`
- `top_function`
- `authority_breakdown`
- `current_location`
- `current_line_range`
- `evidence_summary`

---

## Part 6: Implementation Order

### Phase 1: Registry and event sink extension

Modify:
- `.pecs/tools/append_ai_chat_history.py`
- `locality_index.json` schema and generation rules
- `scripts/export_workspace_continuity.py`

Tasks:
- extend `append_ai_chat_history.py` to normalize new event fields: `object_ids`, `event_role`, `validation_outcome`, `runtime_failure`, `parent_event_id`, `episode_id`
- extend `locality_index.json` entries with `object_type`, `canonical_name`, `class`, `function`, `current_location`
- preserve current event sink and daemon watch behavior
- preserve current continuity export input expectations

### Phase 2: Object group correlation and exporter support

Modify:
- `scripts/export_workspace_continuity.py`
- possibly object-group summary generation in continuity export

Tasks:
- aggregate explicit object group evidence from `object_ids`
- preserve existing chain metrics and add object-group references
- ensure old events without new fields are still processed

### Phase 3: Projection format and retrieval compatibility

Modify:
- retrieval/projection adapter integration points only as needed
- existing consumer-facing projection serialization

Tasks:
- define final projection candidate format with object group authority breakdown
- keep current retrieval engine inputs unchanged while optionally reading new object group fields
- ensure small-model output remains backward compatible by falling back to current candidate semantics when necessary

### Phase 4: Compatibility and migration

Modify:
- documentation and optional integration tests only

Tasks:
- support old event records without `object_ids`
- gradually populate object IDs and new fields in new events
- keep daemon, continuity export, retrieval engine, and consumers working with current fields
- add a migration path where `locality_index.json` extensions are backward compatible

### Lowest-risk sequence

1. Add additive event fields and registry metadata.
2. Preserve old event processing in `export_workspace_continuity.py`.
3. Introduce object group aggregation downstream.
4. Roll out projection formatting as optional enhanced output.

### Backward compatibility strategy

- treat new event fields as optional
- continue processing legacy events without `object_ids`
- preserve all current artifact formats and file names
- extend existing continuity exports rather than replace them

### Migration strategy

- gradually populate `object_ids` in new event production
- extend `locality_index.json` in place with new fields
- allow mixed old/new event records in `ai_chat_history.json`
- do not require a bulk migration before new object authority consumers can use enhanced data

---

## Most Important Question

### Can Object Authority be implemented incrementally on top of current PECS architecture without replacing:
- daemon
- continuity export
- retrieval engine
- consumer integrations

**Answer: YES**

### Justification

- The current daemon already watches `ai_chat_history.json` and can continue to do so.
- The current continuity export path can be extended to read additional event fields without changing its artifact target.
- The retrieval engine already uses `locality_index.json`; that artifact can be extended in place.
- Consumer integrations can remain compatible by continuing to consume existing fields and optionally using the new object authority fields.

---

## Summary

This implementation plan adds object registry extensions and object event capture fields as the smallest fix to recover Object Authority.
It preserves existing storage artifacts, daemon behavior, and consumer compatibility, and it uses deterministic object correlation rather than LLM inference.
