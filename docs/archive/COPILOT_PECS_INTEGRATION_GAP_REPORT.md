# Copilot PECS Integration Gap Report

## Scope
This audit inspects the installed Copilot integration in `/Users/raj/Developer/PECS` and evaluates whether Copilot:
- guarantees PECS consultation,
- uses PECS authority output correctly,
- exposes the available evidence fields,
- and whether the current evidence flow is limited by the observed `Chat -> Authority` authority generation path.

Sources:
- `integrations/copilot_adapter.py`
- `integrations/continue_adapter.py`
- `integrations/pecs_lite_runtime_adapter.py`
- `integrations/pecs_lite_projection_hardener.py`
- `.github/copilot-instructions.md`
- `.continue/rules/pecs-first-routing.yaml`
- `PECS_QUERY_CONTRACT.md`
- `PECS_QUERY_FLOW_REPORT.md`
- `PECS_AUTHORITY_FUSION_FINAL_REPORT.md`

## Summary Findings

1. Copilot is configured to query PECS via `CopilotAdapter.build_copilot_context()`.
2. The integration is advisory, not enforced; fallback behavior exists and means Copilot can proceed without PECS.
3. The current adapter path exposes additional artifact evidence beyond the exported `engineering_continuity_state.json` authority payload.
4. The canonical continuity export remains weakly fused: `engineering_continuity_state.json` is built from `ai_chat_history.json` rather than fully fused runtime/locality evidence.
5. Therefore, Copilot access is not purely `Chat -> Authority`; the query layer is capable of consuming runtime/locality/validation evidence, but the exported authority payload remains Chat-centric.

## Installed Instruction and Routing Evidence

### Copilot guidance
`.github/copilot-instructions.md` contains explicit PECS-first guidance:
- instructs Copilot to inspect `.pecs` artifacts first
- advises use of `PECS-LITE` for runtime locality projection
- calls out `.pecs/active_context.json`, `.pecs/locality_index.json`, `.pecs/active_topology.json`, and `.continue/rules/CONTINUITY_MAP.md`
- declares PECS artifacts as continuity infrastructure only

### Continue routing rule
`.continue/rules/pecs-first-routing.yaml` is installed and includes:
- `alwaysApply: true`
- `pecs_enabled: true`
- `pecs_priority: high`
- a fallback clause: `Repository search only if PECS insufficient`

### Enforcement reality
- These files are guidance and rule definitions, not compiled enforcement hooks inside Copilot.
- External tooling or the Copilot service must honor them; the repository contains no hard runtime blocker that prevents non-PECS search.

## Copilot Integration Path

### Query invocation
`integrations/copilot_adapter.py` calls:
- `PECSLiteRuntimeAdapter.build_projection_safe(..., query_source="copilot")`
- emits telemetry events `copilot_query_received` and `copilot_projection_finalized`

This is a direct PECS query path from Copilot.

### Fallback path
If the projection returns an error schema, `CopilotAdapter` uses:
- `TopologyRetriever.build_minimal_context(object_id)`

That means Copilot can proceed without PECS retrieval when PECS-LITE fails.

### Evidence availability
`ProjectionExporter.export_projection()` in `integrations/pecs_lite_projection_hardener.py` includes:
- `runtime_targets`
- `secondary_neighbors`
- `continuity_supporting_artifacts`
- `pecs_lite_status`
- `active_engineering_continuity`
- `engineering_continuity_summary`
- `runtime_context`
- `evidence_fusion`
- `pecs_runtime_report`
- `emitted_advisory_cognition`
- `final_emission_observability`

So Copilot receives a rich projection payload containing both evidence and diagnostics.

## PECS Consultation Observability

### Observable signals
The integration emits telemetry for:
- query reception (`copilot_query_received`)
- projection finalization (`copilot_projection_finalized`)
- runtime adapter invocation and completion via `PECSLiteRuntimeAdapter`
- diagnostics via `ProjectionHardener.record_query_diagnostics()`

### Diagnostics fields
The projection includes observable fields such as:
- `queried_pecs_pro`
- `workspace_scan_performed`
- `topology_reconstructed`
- `continuity_state_owned`
- `continuity_supporting_artifacts`
- `artifact_writes`
- `pecs_lite_status.runtime_observability_used`
- `pecs_lite_status.engineering_continuity_used`

So yes, PECS consultation is observable.

## Can Copilot bypass PECS entirely?

- Yes.
- The installed guidance is advisory only.
- The adapter path contains a deliberate fallback to minimal topology context.
- `PECSLiteRuntimeAdapter.build_projection_safe()` also swallows exceptions and returns an error payload rather than crashing.

## Can Copilot inspect artifacts directly?

- Indirectly yes.
- `CopilotAdapter` itself does not manually read `.pecs` files, but it delegates to `PECSLiteRuntimeAdapter` and ultimately to `PECSLiteRuntimeV2`, which reads `.pecs` artifacts.
- The projection output includes evidence derived from `.pecs` artifacts.

## Can Copilot proceed without PECS retrieval?

- Yes.
- Fallback to `TopologyRetriever.build_minimal_context()` allows operation without a valid `PECS-LITE` projection.
- This means Copilot can still continue if PECS is unavailable or projection fails.

## Is PECS consultation mandatory?

- No.
- The integration path is designed to use PECS, but it is not mandatory in the code.
- External agent behavior depends on whether Copilot honors `.github/copilot-instructions.md` and whether the tooling implements `pecs-first-routing` rules.

## Evidence field availability and consumption

The projection output is capable of exposing the following evidence categories.

| Evidence Category | Current Implementation State | Notes |
|---|---|---|
| runtime authority | IMPLEMENTED + CONSUMED | `runtime_targets` are built from `PECSProQueryAdapter` evidence and scored with `tier_1_runtime`. |
| validation authority | PARTIAL | `tier_3_validation`, fix validation, and `active_topology.runtime_validation` exist, but current Auto-TOC artifacts show weak runtime confirmation and low validation density. |
| accepted locality | IMPLEMENTED + CONSUMED | `engineering_continuity_lookup()` and canonical cluster signals are used in target scoring and projection enrichment. |
| rejected locality | IMPLEMENTED + IGNORED | `engineering_continuity_lookup()` can derive rejected locality and unresolved locality, but these are not clearly surfaced in the projected authority payload. |
| runtime confirmation | PARTIAL | runtime confirmed locality scores exist and are used in continuity summaries, but the actual file-level execution touch map is not strongly materialized in current artifacts (`active_runtime_touched_files` is empty in Auto-TOC). |
| ownership hotspots | IMPLEMENTED + CONSUMED | `ownership_locality_lookup()` and `locality_state.ownership_hotspots` feed projection enrichment and evidence sources. |
| authority divergence | PARTIAL | divergence-like scores are computed in cognition/shaping envelopes, but explicit `divergence_evidence` object fields are not exposed in the formal response contract. |
| continuity chains | PARTIAL | `active_engineering_continuity` chains are included if available, but the chain generation is currently derived from chat history and is sparse in practice. |

## Contract comparison against `PECS_QUERY_CONTRACT.md`

### What is implemented
- PECS query invocation is present.
- The projection payload contains `runtime_targets`, `continuity_supporting_artifacts`, `evidence_fusion`, `pecs_lite_status`, and diagnostics.
- Query flow is observable via telemetry and diagnostics.
- Projection profiles are selected according to model hints and profile class.

### What is only partially implemented / missing
- The exact contract schema is not fully matched. Current output is projection-oriented, not the proposed `PECS_Response` object shape.
- Explicit `validation_evidence`, `locality_evidence`, and `divergence_evidence` objects are only partially present through diagnostics and continuity summaries.
- The canonical authority payload is not guaranteed to carry the same fused evidence as the projection layer.

## Most Important Gap

If Copilot faithfully queries PECS today, the authority information that remains unavailable or weak because the authority export is still effectively `Chat -> Authority` is:

- explicit runtime/locality fusion in exported continuity authority,
- complete file-level runtime touch evidence (`active_runtime_touched_files`),
- explicit rejected locality scores and rejected-authority trace,
- a formal divergence evidence object with topology/historical mismatch metrics,
- a fully fused `engineering_continuity_state.json` that combines chat-derived chains with runtime/locality evidence.

Put another way:
- Copilot can see and consume evidence through the projection path,
- but the canonical continuity authority artifact (`engineering_continuity_state.json`) is not the fully fused authority source that the contract expects.

## Classification

- `runtime authority`: IMPLEMENTED + CONSUMED
- `validation authority`: PARTIAL
- `accepted locality`: IMPLEMENTED + CONSUMED
- `rejected locality`: IMPLEMENTED + IGNORED
- `runtime confirmation`: PARTIAL
- `ownership hotspots`: IMPLEMENTED + CONSUMED
- `authority divergence`: PARTIAL
- `continuity chains`: PARTIAL

## Practical conclusion

The installed Copilot integration:
- is intentionally PECS-aware,
- is observable via telemetry,
- can consume runtime/locality/ownership evidence from PECS artifacts,
- but is not hard-blocked to PECS,
- and still relies on a chat-derived canonical authority export path that leaves a gap in fused evidence.

This means the integration is not purely `A. merely consumes the current authority payload`; it is closer to `B. already has access to additional runtime/locality/validation/ownership evidence`, but the canonical authority export is still not fully aligned with that evidence.

## Recommended audit takeaway

The main gap is not the Copilot adapter itself; it is the authority export path. Closing the gap requires making `engineering_continuity_state.json` and related exported continuity artifacts genuinely fuse the same runtime/locality validation evidence that the projection layer already consumes.
