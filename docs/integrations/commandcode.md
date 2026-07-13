# CommandCode Integration

PECS provides deterministic locality projections for CommandCode through the same stateless PECS-LITE runtime used by other consumers.

## Query Path

1. CommandCode emits a query tagged `source="commandcode"`.
2. `PECSLiteRuntimeAdapter.build_projection_safe(..., query_source="commandcode")` is invoked.
3. `RuntimeContextResolver` loads `.pecs` artifacts in read-only mode.
4. `PECSProQueryAdapter` retrieves runtime targets, ownership hotspots, and evidence fusion.
5. `ProjectionExporter` builds the final deterministic projection.

## Projection Profile

CommandCode should use a bounded profile:

- `profile`: `medium`
- `projection_profile.reasoning_budget`: `medium`
- `projection_profile.exploration_constraints`: `bounded`
- `projection_profile.target_count`: `10`
- `projection_profile.continuity_depth`: `balanced`
- `projection_profile.include_advisories`: `true`

## Continuity Taste

CommandCode may learn workspace conventions through the taste file at `.commandcode/taste/taste.md`. PECS artifacts provide the authoritative runtime topology; taste files provide stylistic continuity only.

## Response Fields

CommandCode should expose:

- `runtime_targets` with `fused_score`
- `ownership_hotspots`
- `tier_1_runtime` and `tier_2_continuity` summaries
- `consulted_artifacts`
- `fallback_reason` when projection fails

## See Also

- [Query Pipeline](../query-pipeline.md) — canonical query contract
- [PECS-LITE](pecs-lite.md) — stateless projection protocol
- [Continue](continue.md), [Copilot](copilot.md), [Kimi](kimi.md) — other consumer integrations
