# Bootstrap Hardening Report

## Objective

Preserve cold-start topology bootstrapping while enabling deterministic runtime supersession over time.

## Preserved architecture

### Static bootstrap preserved

- Import/dependency topology remains sourced from:
  - `.pecs/topology_compact.json`
  - `.pecs/locality_index.json`
- Filesystem structure remains part of static evidence in Tier 0.

### Runtime supersession preserved

- Tier 1 runtime evidence (`runtime_activation`, touched files, runtime chain neighborhood) has the largest weight (`0.35`).
- Tier 2 continuity and Tier 3 validation further refine authority over time.

### Deterministic adaptation

Evidence fusion adjusts ranking deterministically based on available evidence density and confidence.

No prompt wording is used to override topology/ownership authority.

## Hardening implementation points

- `evidence_fusion_lookup()` formalized static/runtime/continuity/validation tiers.
- `runtime_target_candidates()` now derives candidate ranking from explicit fusion scores.
- `RuntimeContextResolver` surfaces top ranked fusion files in read-only context.

## Cold-start behavior

For new workspaces with sparse runtime evidence:

- Tier 0 static topology + filesystem evidence keeps locality resolution operational.
- As runtime/validation evidence accumulates, deterministic weighted fusion naturally reorders locality authority.

## Files changed

- `integrations/pecs_pro_query_adapter.py`
- `PECS_LITE v2/pecs_lite v2/runtime/runtime_context_resolver.py`
- `integrations/pecs_lite_projection_hardener.py`
