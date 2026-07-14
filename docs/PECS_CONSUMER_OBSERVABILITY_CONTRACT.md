# PECS Consumer Observability Contract

## Purpose

This document finalizes the canonical observability contract that Copilot, Continue, and Kimi must implement.

It defines the response schema, required versus optional fields, producers, preservation rules, ordering, and duplicate elimination.

This is a decision document only. No code changes are proposed.

---

## 1. Canonical response schema

The canonical wrapper for every consumer response is:

- `schema`: string
- `query_id`: string
- `workspace_id`: string
- `status`: string (`success|partial|failed`)
- `PECS_Status`: object
- `PECS_Query`: object
- `PECS_Response`: object
- `PECS_Confidence`: object
- `Relying_On_PECS`: object
- `Reason`: string

This shape is consumer-agnostic and must be identical for Copilot, Continue, and Kimi.

---

## 2. Canonical field classification

### 2.1 Required fields

These fields are mandatory for full observability.

- `schema`
- `query_id`
- `workspace_id`
- `status`
- `PECS_Status.queried_pegs`
- `PECS_Status.query_source`
- `PECS_Status.runtime_mode`
- `PECS_Status.projection_mode`
- `PECS_Status.runtime_observability_used`
- `PECS_Status.engineering_continuity_used`
- `PECS_Status.consulted_artifacts`
- `PECS_Query.source`
- `PECS_Query.issue_query`
- `PECS_Query.profile`
- `PECS_Query.projection_profile`
- `PECS_Query.timestamp`
- `PECS_Response.runtime_targets`
- `Relying_On_PECS.pegs_used`
- `Relying_On_PECS.pegs_observed`
- `Relying_On_PECS.pegs_influence`
- `Reason`
- `PECS_Response.final_locality_selected`
- `PECS_Response.final_authority_selected`

### 2.2 Optional fields

These fields are useful for richer observability but are not mandatory.

- `PECS_Status.missing_artifacts`
- `PECS_Status.artifact_writes`
- `PECS_Status.validation_state`
- `PECS_Status.fallback_reason`
- `PECS_Query.requested_fields`
- `PECS_Query.metadata`
- `PECS_Response.secondary_neighbors`
- `PECS_Response.continuity_evidence`
- `PECS_Response.validation_evidence`
- `PECS_Response.locality_evidence`
- `PECS_Response.divergence_evidence`
- `PECS_Response.advisory_cognition`
- `PECS_Response.influential_artifacts`
- `PECS_Confidence.authority_confidence`
- `PECS_Confidence.authority_confidence_band`
- `PECS_Confidence.tier_contributions`
- `PECS_Confidence.evidence_balance`
- `Relying_On_PECS.fallback_reason`
- `Relying_On_PECS.partial_use_reason`
- `Relying_On_PECS.reject_reason`

### 2.3 Debug-only fields

These fields must be allowed but are not required for normal observability.

- `PECS_Response.diagnostics`
- `PECS_Confidence` details beyond `authority_confidence` and `authority_confidence_band`
- `PECS_Response.continuity_evidence` when it is only advisory
- `PECS_Response.divergence_evidence`
- `PECS_Response.advisory_cognition`
- any field labelled `*_debug` or `*_telemetry` in runtime outputs

### 2.4 Internal-only fields

These fields are runtime implementation details and should not be considered part of the public consumer contract.

- `pecs_lite_telemetry`
- `final_emission_observability` (unless surfaced explicitly in `PECS_Response`)
- adapter-internal diagnostic envelopes not normalized to the canonical schema
- `PECS_Status.artifacts_not_generated`
- any internal adapter method names

---

## 3. Field producers

| Field | Produced by | Notes |
|---|---|---|
| `schema` | Consumer Adapter | fixed contract identifier |
| `query_id` | Consumer Adapter | generated per request |
| `workspace_id` | Consumer Adapter | from consumer context |
| `status` | Consumer Adapter | derived from PECS-LITE response state |
| `PECS_Status` | PECS-LITE / PECS-PRO | assembled by the consumer adapter from runtime and adapter diagnostics |
| `PECS_Query` | Consumer Adapter | produced in full by adapter; profile values may come from Consumer Config |
| `PECS_Response` | PECS-LITE / PECS-PRO | produced by runtime projection and evidence fusion |
| `PECS_Confidence` | PECS-LITE | produced by runtime projection confidence scoring |
| `Relying_On_PECS` | Consumer Adapter | produced by consumer based on whether it intends to rely on PECS evidence |
| `Reason` | Consumer Adapter | human-readable final decision summary |
| `consulted_artifacts` | PECS-PRO | produced by artifact access diagnostics |
| `influential_artifacts` | PECS-LITE / PECS-PRO | derived from evidence contribution and scoring |
| `runtime_targets` | PECS-LITE | direct projection output |
| `final_locality_selected` | Consumer Adapter | derived by consumer from the chosen target(s) |
| `final_authority_selected` | Consumer Adapter | derived summary of the chosen authority source |

### Producer guidance

- `Consumer Config` defines defaults only; it does not directly emit the contract.
- `Consumer Adapter` is responsible for wiring config into `PECS_Query` and for emitting `Relying_On_PECS` and `Reason`.
- `PECS-LITE` produces the evidence payload and runtime-target fields.
- `PECS-PRO` produces artifact provenance and continuity diagnostics.
- Some fields are derived by consumers from the response rather than directly emitted by runtime.

---

## 4. Exact preservation rules

### 4.1 PECS query

- `PECS_Query.issue_query` MUST contain the exact original consumer query string.
- `PECS_Query.source` MUST contain the exact consumer name (`copilot|continue|kimi|other`).
- `PECS_Query.profile` MUST reflect the exact profile chosen, even if it was derived from config defaults.
- `PECS_Query.projection_profile` MUST preserve the exact profile object used for the runtime call.
- `PECS_Query.metadata` MAY contain derived metadata, but raw `user_intent` and `reasoning_capability_class` must preserve original values when present.

### 4.2 PECS response

- `PECS_Response` MUST preserve the full evidence payload returned by PECS-LITE, including `runtime_targets`.
- Fields in `PECS_Response` MAY include derived summaries such as `influential_artifacts` and `final_locality_selected`.
- `PECS_Response.runtime_targets` MUST preserve the exact target file/object identifiers returned by PECS-LITE.
- `PECS_Response.secondary_neighbors` MAY be omitted if empty.
- `PECS_Response.diagnostics` MAY contain internal or debug-only values, but the contract does not require them for functional observability.

### 4.3 consulted_artifacts

- `PECS_Status.consulted_artifacts` MUST list the exact `.pecs` artifacts read or consulted by the query flow.
- This list MUST be generated by PECS-PRO diagnostics and included in the final wrapper.
- It must not be a derived summary of the selected targets; it must reflect artifact access.

### 4.4 influential_artifacts

- `PECS_Response.influential_artifacts` MAY list the artifacts that materially contributed to the final selected locality/authority.
- This field MAY be derived by PECS-LITE and PECS-PRO from evidence fusion scoring.
- It is optional but recommended for full observability.

### 4.5 runtime_targets

- `PECS_Response.runtime_targets` MUST contain the exact runtime target list produced by PECS-LITE.
- The target entries may include `tier_scores`, `evidence_sources`, and `provenance`.
- The contract must preserve these values exactly, not replace them with summaries.

### 4.6 authority selection

- `PECS_Response.final_authority_selected` MUST include:
  - `authority_type`
  - `authority_confidence`
  - `authority_confidence_band`
  - any authority source summary used for final selection
- These fields MAY be derived by the consumer adapter from the PECS response.
- `PECS_Confidence` is a canonical optional summary of authority evidence.

### 4.7 locality selection

- `PECS_Response.final_locality_selected` MUST capture the final locality anchor selected by the consumer.
- It MAY be a target file/object identifier or a short structured summary.
- It must preserve the consumer’s actual chosen locality, not a different inferred locality.

---

## 5. Canonical response ordering

Consumers must serialize the contract in the following canonical order:

1. `schema`
2. `query_id`
3. `workspace_id`
4. `status`
5. `PECS_Status`
6. `PECS_Query`
7. `PECS_Response`
8. `PECS_Confidence`
9. `Relying_On_PECS`
10. `Reason`

Within `PECS_Response`, the ordering should be:

1. `runtime_targets`
2. `secondary_neighbors`
3. `continuity_evidence`
4. `validation_evidence`
5. `locality_evidence`
6. `divergence_evidence`
7. `advisory_cognition`
8. `diagnostics`
9. `influential_artifacts`
10. `final_locality_selected`
11. `final_authority_selected`

This ordering is authoritative for contract consistency.

---

## 6. Duplicate field assessment

The following fields are duplicates and should be consolidated where possible:

- `PECS_Status.fallback_reason` and `Relying_On_PECS.fallback_reason` are duplicates. Keep `Relying_On_PECS.fallback_reason` as the consumer-facing observability field and remove the duplicate from `PECS_Status` if contract minimization is required.
- `PECS_Query.profile` and `PECS_Query.projection_profile.profile` are duplicates. Maintain both for compatibility, but treat `projection_profile.profile` as canonical.
- `PECS_Confidence.authority_confidence` and `PECS_Response.final_authority_selected.authority_confidence` are duplicates. Keep `final_authority_selected.authority_confidence` as the chosen authority summary and make `PECS_Confidence` optional.
- `Reason` and `PECS_Status.reason` are duplicates. Keep only top-level `Reason` in the minimal contract.

### Minimal contract recommendation

For a minimal contract, the preferred canonical fields are:

- `PECS_Query.profile`
- `PECS_Query.projection_profile.profile`
- `Relying_On_PECS.fallback_reason`
- `PECS_Response.final_authority_selected.authority_confidence`
- top-level `Reason`

All other duplicate fields should be treated as optional compatibility aliases.

---

## 7. Consumer compatibility

### Can this contract be implemented identically by Copilot, Continue, and Kimi?

**Answer: YES**

### Justification

- Current adapters already share the same PECS-LITE runtime path and use the same projection/profile conventions.
- The only consumer-specific variance is `query_source` and event naming; the wrapper contract itself can remain identical.
- A single contract is sufficient because all three consumers can emit the same top-level fields and differ only in source metadata.
- The current architecture supports a shared runtime/evidence shape, so no consumer-specific structural differences are required.

---

## 8. Implementation note

This contract is authoritative for observability. Consumer adapters must preserve the shape and field semantics exactly, while allowing optional debug fields as additive metadata.

Any future expansion should add optional fields, not change required structural elements.
