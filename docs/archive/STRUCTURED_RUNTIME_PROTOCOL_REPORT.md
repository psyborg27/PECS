# Structured Runtime Protocol Report

## Objective

Harden runtime projection output into deterministic, structured, machine-stable protocol sections.

## Implemented protocol sections

`integrations/pecs_lite_projection_hardener.py` now emits deterministic runtime report sections in order:

- `PECS STATUS`
- `PECS ARTIFACTS`
- `EVIDENCE FUSION`
- `LOCALITY RESOLUTION`
- `SEARCH PLAN`
- `EXECUTION SCOPE`
- `UNRESOLVED`

## Removed narrative runtime commentary

Structured target entries no longer include narrative prose fields such as:

- `why_this_location`
- `recommended_first_action`

Targets now use structured fields:

- `evidence_tiers`
- `evidence_sources`
- `predicted_failure_mode`
- deterministic `search_budget`

## Provenance and protocol hardening

Projection payload now includes:

- `evidence_fusion` (schema + weights + ranked files + provenance)
- `runtime_context` (read-only resolver output)
- deterministic metadata (`deterministic`, `runtime_mode`, `artifact_writes`)

## Canonical serialization hardening

`export_runtime_projection()` now writes JSON with `sort_keys=True` for stable key ordering.

## Verification

Runtime check confirms protocol sections and no narrative target field leakage.

## Files changed

- `integrations/pecs_lite_projection_hardener.py`
- `PECS_LITE v2/pecs_lite v2/runtime/pecs_lite_runtime_v2.py`
- `PECS_LITE v2/pecs_lite v2/runtime/runtime_context_resolver.py`
