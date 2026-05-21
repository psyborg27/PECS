# PROJECTION_COMPATIBILITY_REPORT

## PECS-LITE and large-model projection contracts

### Required artifacts for PECS-LITE runtime resolution

`PECS_LITE v2/pecs_lite v2/runtime/runtime_context_resolver.py` requires:
- `.pecs/active_context.json`
- `.pecs/compact_bundle.json`
- `.pecs/locality_index.json`
- `.pecs/topology_compact.json`
- `.pecs/continuity/locality_state.json`
- `.pecs/continuity/active_topology.json`
- `.pecs/continuity/engineering_continuity_state.json`

### Required artifacts for `PECSProQueryAdapter`

`integrations/pecs_pro_query_adapter.py` depends on:
- `.pecs/active_context.json`
- `.pecs/compact_bundle.json`
- `.pecs/locality_index.json`
- `.pecs/topology_compact.json`
- `.pecs/continuity/locality_state.json`
- `.pecs/continuity/active_topology.json`
- `.pecs/continuity/engineering_continuity_state.json`

### Projection inputs and evidence fusion

- `evidence_fusion_lookup()` uses:
  - `compact_bundle` entries
  - `locality_state.active_runtime_touched_files`
  - active object files from `active_context`
  - topology edges from `topology_compact`
  - engineering continuity scores from `engineering_continuity_state`

- `runtime_target_candidates()` ranks files from fused evidence.
- `resolve_symbol_authority()` uses object metadata from `locality_index.json`.

## What compact projection expects

- a compact bundle of active objects and runtime neighborhoods
- a current topology zone and runtime zone set
- issue term context for clustering
- a deterministic, low-token continuity selection
- topology-first locality anchors rather than broad search

## What large-model projection expects

- the same core artifacts as PECS-LITE
- additional enrichment in `execution_enrichment`
- `continuity_context` for active runtime zones and confirmation density
- provenance-aware evidence fusion
- deterministic file-scoped predictions with background artifact health checks

## Compatibility status

### What still works

- The core artifacts exist and are written by the daemon.
- `PECSProQueryAdapter.refresh()` only reloads artifacts; it does not mutate workspace state.
- `ProjectionHardener` and `RuntimeContextResolver` are read-only and rely on artifact existence.

### What is partially degraded

- If `.pecs/compact_bundle.json` or `.pecs/active_context.json` are stale, projection still loads them as current.
- `PECSProQueryAdapter` will report `runtime_observability_fallback_reason` or `engineering_continuity_fallback_reason` if artifacts are missing or empty.
- Large-model projection still functions, but may be using stale execution and continuity evidence.

### Main projection risk

- The projection pipeline is vulnerable to stale artifact hydration because the adapter does not rebuild artifacts.
- `compact_bundle` freshness is the gating factor for both small-model and large-model projections.
- If `.pecs/continuity/*` exports are stale, evidence fusion still uses stale locality state and active topology.

## Conclusion

Projection compatibility remains intact at the artifact contract level. The practical risk is stale artifact propagation: the projections still operate, but they depend on the daemon to keep `.pecs` artifacts fresh, and that automation is currently incomplete.
