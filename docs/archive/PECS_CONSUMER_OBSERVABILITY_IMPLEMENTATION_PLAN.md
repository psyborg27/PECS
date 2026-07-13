# PECS Consumer Observability Implementation Plan

## Objective

Design an observability layer that verifies actual PECS usage by Copilot, Continue, and Kimi using the current PECS architecture.

This is a planning document only. No code changes are proposed.

---

## 1. Exact fields every consumer must report

A minimal, audit-quality consumer report must include the following canonical fields.

### 1.1 PECS queried
- `PECS_Status.queried_pegs`: boolean
- `PECS_Status.query_source`: string (`copilot|continue|kimi|other`)
- `PECS_Query.query_id`: string
- `PECS_Query.timestamp`: string

### 1.2 PECS profile
- `PECS_Query.profile`: string (`small|medium|large` or richer profile name)
- `PECS_Query.projection_profile`: object with exact profile fields:
  - `profile`
  - `reasoning_budget`
  - `exploration_constraints`
  - `target_count`
  - `continuity_depth`
  - `include_advisories`

### 1.3 PECS query
- `PECS_Query.issue_query`: string
- `PECS_Query.source`: string
- `PECS_Query.metadata`: object

### 1.4 PECS response
- `PECS_Response`: object representing the full evidence payload returned by PECS
- `PECS_Response.runtime_targets`: list of target files/objects returned
- `PECS_Response.secondary_neighbors`: list of secondary files/objects returned
- `PECS_Response.continuity_evidence`: object
- `PECS_Response.diagnostics`: object
- `PECS_Response.advisory_cognition`: object

### 1.5 PECS relied upon
- `Relying_On_PECS.pegs_used`: boolean
- `Relying_On_PECS.pegs_observed`: boolean
- `Relying_On_PECS.pegs_influence`: string (`strong|moderate|weak|none`)
- `Relying_On_PECS.fallback_reason`: string

### 1.6 PECS rejection reason
- `PECS_Status.fallback_reason`: string
- `Relying_On_PECS.fallback_reason`: string
- `Relying_On_PECS.reject_reason`: string (if consumer explicitly rejects PECS evidence)
- `Relying_On_PECS.validation_state`: string (`accepted|rejected|partial|unresolved`)

### 1.7 PECS partial-use reason
- `Relying_On_PECS.partial_use_reason`: string
- `Relying_On_PECS.pegs_influence`: string
- `PECS_Status.reason`: string
- `PECS_Response.diagnostics.failure_modes`: list of strings

### 1.8 Final locality selected
- `PECS_Response.final_locality_selected`: object or string summarizing the chosen locality anchor
- `PECS_Response.runtime_targets[0]`: top selected locality target
- `PECS_Response.locality_evidence.active_locality_clusters`: list of selected clusters

### 1.9 Final authority selected
- `PECS_Response.final_authority_selected`: object with:
  - `authority_type`: string
  - `authority_confidence`: number
  - `authority_confidence_band`: string
  - `authority_concentration_score`: number
- `PECS_Response.runtime_targets[].tier_scores`: includes authority contributions
- `PECS_Response.continuity_evidence.locality_authority_confidence`: number

---

## 2. Where fields should be generated

### 2.1 Consumer adapter
Responsible for authoring the initial query, capturing the decision event, and emitting final selection metadata.

- `integrations/copilot_adapter.py`
- `integrations/continue_adapter.py`
- `integrations/kimi_adapter.py` (new)

This layer must generate:
- `PECS_Query` fields
- `query_id`, `source`, `issue_query`, `profile`, `projection_profile`
- `Relying_On_PECS` fields based on consumer decision logic
- `final_locality_selected` and `final_authority_selected` summaries
- explicit acceptance/rejection/partial-use payloads

### 2.2 PECS-LITE
Responsible for producing the actual projection evidence payload and runtime execution metadata.

- `integrations/pecs_lite_runtime_adapter.py`

This layer must generate:
- `PECS_Response` payload
- `PECS_Status` metadata
- `PECS_Confidence` / `final_emission_observability`
- exact profile selected and profile mapping
- `PECs_Response.diagnostics`
- raw projection response that can be preserved unchanged

### 2.3 PECS-PRO
Responsible for evidence provenance, artifact-access diagnostics, and continuity authority signals.

- `integrations/pecs_pro_query_adapter.py`

This layer must generate:
- `consulted_artifacts` list
- `artifact provenance` for evidence sources
- `engineering_continuity` and `locality_evidence`
- `evidence_sources` by target and tier
- query diagnostics proving PECS consultation
- `runtime_targets` and `leverage` information

### 2.4 Consumer config
Responsible for policy and enablement decisions, not for primary observability fields.

This layer should define:
- whether observability is active
- verbosity level (`summary|debug|audit`)
- profile defaults per consumer
- whether full response retention is permitted
- mapping from consumer names to `query_source`

Potential config surfaces:
- `.github/copilot-instructions.md`
- `.continue/rules/PECS_CONTEXT_RULE.md`
- `README_MANUAL_SETUP.md`
- future Kimi workspace config assets

---

## 3. Preserving exact PECS query and exact PECS response

### 3.1 Exact PECS query preservation
The query must be preserved as-is in both request and response.

- `PECS_Query.issue_query` must equal the exact consumer query string.
- `PECS_Query.query_id` must be generated once and echoed through the response.
- `PECS_Query.projection_profile` must preserve the exact profile fields used.
- `PECS_Query.metadata` must preserve any consumer-specific metadata.

### 3.2 Exact PECS response preservation
The response must retain the full projection output.

- `PECS_Response` must include the complete evidence payload returned by PECS-LITE.
- The consumer adapter must not strip or redact `PECS_Response` before audit logging.
- The response payload should embed transparency fields such as
  - `consulted_artifacts`
  - `evidence_sources`
  - `runtime_targets`
  - `continuity_evidence`
  - `diagnostics`
- If response size is a concern, the system may also keep a hashed serialized backup for audit, but the response contract must preserve every field in the payload.

### 3.3 Implementation rule
The adapter should treat `PECS_Response` as a first-class audit object, not a transient internal result.

---

## 4. Capturing consumer acceptance/rejection decisions

### 4.1 In the response contract
Consumers must record decisions as explicit fields in the response.

- `Relying_On_PECS.pegs_used`
- `Relying_On_PECS.pegs_influence`
- `Relying_On_PECS.fallback_reason`
- `Relying_On_PECS.reject_reason`
- `Relying_On_PECS.partial_use_reason`
- `PECS_Status.validation_state`
- `PECS_Status.reason`

### 4.2 In runtime events
Consumer adapters must emit a finalization event for each query lifecycle.

- `copilot_projection_finalized`
- `continue_projection_finalized`
- `kimi_projection_finalized`

Payload fields should include:
- `query_id`
- `query`
- `projection_schema`
- `authority_confidence`
- `runtime_targets`
- `fallback_used`
- `projection_delivered`
- `pegs_used`
- `reject_reason`
- `partial_use_reason`
- `consumption_mode`
- `selected_locality`
- `selected_authority`

### 4.3 In chat/continuity history
If consumer acceptance or rejection is part of a broader engineering episode, it should also be appended to `.pecs/ai_chat_history.json` using `append_ai_chat_history.py`.

- `validation_outcome`: `accepted|rejected|partial|unresolved`
- `object_ids`: canonical object group identifiers
- `episode_id` / `parent_event_id`: request-response linkage
- `event_role`: `request|response|validation`

This ensures acceptance/rejection decisions are captured in the broader continuity record.

---

## 5. Observability mode: always enabled or audit mode only

### Recommended mode
- **Always enabled** at the adapter and PECS-LITE response layer.

### Rationale
- The goal is to verify actual usage, so observability must be available on every consumer request.
- Audit-only mode would miss normal requests and leave gaps in usage verification.
- The architecture already supports metadata-rich response payloads and diagnostics.

### Practical policy
- Always collect the core fields on every request.
- Allow consumer config to control verbosity and retention.
- Optionally support a lower-cost summary mode for production, but maintain the same structural fields.

---

## 6. Exact files requiring modification

### Required adapter/runtime files
- `integrations/copilot_adapter.py`
  - emit query/response audit fields
  - capture `Relying_On_PECS` fields
  - preserve `PECS_Response`
  - emit finalization runtime event

- `integrations/continue_adapter.py`
  - same responsibilities as Copilot adapter

- `integrations/pecs_lite_runtime_adapter.py`
  - preserve exact query and response contract
  - ensure profile and diagnostics fields are surfaced
  - maintain `pecs_lite_telemetry`

- `integrations/pecs_pro_query_adapter.py`
  - populate `consulted_artifacts`
  - expose evidence provenance and `evidence_sources`
  - expose `get_query_diagnostics()` and health metrics to consumers

### Optional / supporting files
- `integrations/kimi_adapter.py` (new)
  - if Kimi is added as a first-class consumer, it must support the same observability contract as Copilot/Continue

- `.pecs/tools/append_ai_chat_history.py`
  - to capture acceptance/rejection events and real consumer lifecycle signals in chat history

### Documentation and config files
- `PECS_QUERY_CONTRACT.md`
  - update contract language to include the observability fields

- `README_MANUAL_SETUP.md`
  - document the observability policy and consumer config options

- `workspace_assets_manifest.json` / consumer workspace assets
  - if Kimi integration is added, document its config assets

---

## 7. Answer to the most important question

### Would this observability layer make it possible to determine whether the previously identified “artifacts collected but not consumed” finding is true?

**Answer: YES**

### Justification
- With explicit `consulted_artifacts`, per-target `evidence_sources`, and `Relying_On_PECS` influence metadata, the system can show which artifacts were read and whether they contributed to the final selected targets.
- `PECS_Status` records whether PECS was queried and whether fallback or partial-use occurred.
- `PECS_Response` carries the final locality/authority selection and the exact projection payload.
- That combination makes it possible to distinguish:
  - artifacts consulted during PECS query execution,
  - artifacts referenced in the final evidence payload,
  - artifacts that were read but did not materially influence the selected output.

---

## 8. Implementation notes

- Do not change the PECS architecture. Use existing adapter and runtime layers.
- Keep the audit contract aligned with `PECS_QUERY_CONTRACT.md`.
- Use existing runtime event names and extension points.
- Preserve backward compatibility by emitting the new observability fields as additive metadata.
- Ensure the consumer adapters remain advisory/evidence-only and do not use PECS output as a decision engine.
