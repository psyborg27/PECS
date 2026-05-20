# Evidence Fusion Implementation Report

## Objective

Implement deterministic, explicit evidence fusion without redesigning PECS core architecture.

## Implemented

### Explicit tier model

Implemented in `integrations/pecs_pro_query_adapter.py` via `evidence_fusion_lookup()`:

- `tier_0_static`
  - import topology
  - dependency topology
  - filesystem structure
- `tier_1_runtime`
  - runtime activation evidence
  - runtime touched files
  - runtime chain neighborhood
- `tier_2_continuity`
  - ownership continuity
  - continuity hotspots
  - engineering continuity chains
- `tier_3_validation`
  - user-confirmed runtime validation
  - error-to-object correlation
  - accepted/rejected fix validation
  - unresolved persistence penalty

### Deterministic weighted scoring

Weights are explicit and serialized:

- `tier_0_static`: `0.20`
- `tier_1_runtime`: `0.35`
- `tier_2_continuity`: `0.25`
- `tier_3_validation`: `0.20`

Formula:

`fused_score = sum(weight[tier] * tier_score[tier])`

### Provenance visibility

Each ranked file now includes:

- `tier_scores`
- `tier_sources`
- `provenance`
- `fused_score`

No hidden ranking logic remains in runtime target candidate ordering.

### Runtime candidate ranking now fusion-driven

`runtime_target_candidates()` now ranks from explicit evidence fusion output rather than implicit base-confidence heuristics.

## Validation evidence

Functional verification executed:

- Top-5 evidence-fusion files remained identical across different prompt wordings.
- Projection output includes `evidence_fusion` and structured runtime report sections.

## Files changed

- `integrations/pecs_pro_query_adapter.py`
- `integrations/pecs_lite_projection_hardener.py`
- `PECS_LITE v2/pecs_lite v2/runtime/runtime_context_resolver.py`
