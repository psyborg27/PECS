# Continue PECS Integration Plan

## Purpose
Design the final PECS integration architecture for Continue.

Requirements:
- local model optimized
- locality-first
- low token budget
- strong ownership guidance
- minimal context expansion

## Response Format
Continue should return a PECS-aware response with the following sections:

PECS Status:
- consultation status
- artifacts used
- runtime/continuity usage
- fallback state

PECS Query:
- source = `continue`
- issue_query
- profile = `small`
- projection_profile
- requested_fields
- metadata

PECS Locality:
- runtime_targets
- secondary_neighbors
- ownership hotspots
- locality clusters
- active continuity summary

PECS Confidence:
- authority_confidence
- tier contributions
- evidence balance
- token budget

Relying On PECS:
- whether runtime projection was authoritative
- whether continuity export was audited
- fallback reason

Reason:
- high-level justification for the chosen retrieval and authority path

## Retrieval Flow

1. `ContinueAdapter.build_continue_context()` is invoked.
2. Continue emits `continue_query_received` telemetry.
3. `PECSLiteRuntimeAdapter.build_projection_safe(..., query_source="continue")` is called.
4. `PECS-LITE` performs these steps:
   - `RuntimeContextResolver` loads runtime projection evidence from `.pecs` artifacts.
   - `PECSProQueryAdapter` retrieves runtime targets, evidence fusion, ownership locality, and continuity signals.
   - `ProjectionHardener.harden_projection()` applies a small-local profile.
   - `ProjectionExporter.export_projection()` builds the final projection.
5. If the projection fails or returns a projection error schema, Continue falls back to `TopologyRetriever.build_minimal_context(object_id)`.
6. The response is returned with `pecs_lite_telemetry` and `final_emission_observability` included.

## Exact Projection Profile

For Continue, use the `small` local profile:
- `profile`: `small`
- `projection_profile.reasoning_budget`: `low`
- `projection_profile.exploration_constraints`: `strict`
- `projection_profile.target_count`: `6`
- `projection_profile.continuity_depth`: `minimal`
- `projection_profile.include_advisories`: `false`
- `max_related_files`: 3
- `max_symbol_expansions`: 5
- `max_new_files_before_validation`: 2

## Exact Authority Fields Required

Continue should consume and expose these core fields:
- `runtime_targets`
- `secondary_neighbors`
- `evidence_fusion.weights`
- `evidence_fusion.ranked_files`
- `pecs_lite_status.authority_confidence`
- `pecs_lite_status.runtime_observability_used`
- `pecs_lite_status.engineering_continuity_used`
- `pecs_runtime_report.PECS STATUS`
- `continuity_supporting_artifacts`
- `runtime_context`
- `active_engineering_continuity` (shallow)
- `engineering_continuity_summary`
- `final_emission_observability`

## Which PECS Fields Should be Hidden

Hide fields that are too verbose or incidental for local-model, low-token contexts:
- full `continuity_evidence.active_engineering_chains`
- raw `evidence_fusion.rankings` beyond top 3
- low-level `behavioral_signals`
- deep `execution_enrichment` for large profiles
- `diagnostics.failure_modes` unless there is an error
- `emitted_advisory_cognition` unless it is needed for explicit guidance

## Which PECS Fields Should be Exposed

Expose only the most useful compact evidence:
- `PECS Status`: `queried_pegs`, `runtime_mode`, `projection_mode`, `consulted_artifacts`, `fallback_reason`
- `PECS Query`: all requested query metadata
- `PECS Locality`: up to 6 `runtime_targets`, 2 `secondary_neighbors`, ownership hotspot names, and `active_runtime_zones`
- `PECS Confidence`: `authority_confidence`, `tier_contributions`, `evidence_balance`, `token_budget`
- `Relying On PECS`: `runtime_projection_used=true`, `continuity_export_audited=maybe`, `fallback_triggered`

## Maximum Token Budget

For Continue:
- `token_budget`: `850-1500` tokens recommended
- `projection_profile.target_count`: 6
- `max_related_files`: 3
- `max_symbol_expansions`: 5
- `max_new_files_before_validation`: 2

Rationale:
- local models require a narrow runtime focus
- strong ownership guidance should not expand into broad architecture context
- minimal context expansion preserves local-model efficiency

## Runtime Authority Prioritization

Continue should prioritize runtime authority as:
1. `tier_1_runtime` evidence from `runtime_targets`
2. ownership locality from `ownership_hotspots`
3. continuity support only as a secondary audit signal

Prioritization rules:
- prefer targets with non-zero `tier_1_runtime`
- prefer targets with `ownership_hotspot` alignment
- use `tier_2_continuity` only to break ties or adjust confidence
- use `tier_3_validation` conservatively for local-model safety

## Ownership Hotspots Prioritization

Ownership should be surfaced as primary locality guidance:
- `ownership_locality_lookup()` should populate `possible_mutation_owner`
- `ownership_hotspots` should be part of `PECS Locality`
- if a target is both ownership-hotspot and runtime-authority, boost its confidence
- if a target is ownership-hotspot but low runtime support, preserve it as a candidate with lower confidence

## Design Summary

Continue should be a runtime-projection-first consumer with carefully constrained continuity audit support.
It should deliver compact locality guidance, strong ownership cues, and predictable token bounds.
Maintenance of `engineering_continuity_state.json` is useful for audit, but not the primary authority source.

## See Also

- [Query Pipeline](../query-pipeline.md) — canonical query contract
- [PECS-LITE](pecs-lite.md) — stateless projection protocol
- [Continue](continue.md), [Copilot](copilot.md), [Kimi](kimi.md), [CommandCode](commandcode.md) — consumer integrations
