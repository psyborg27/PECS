# Kimi PECS Integration Plan

## Purpose
Design the final PECS integration architecture for Kimi.

Requirements:
- large-context model
- architecture-aware
- continuity-aware
- capable of broader reasoning

## Response Format
Kimi should return a PECS-aware response with these sections:

PECS Status:
- consultation and artifact availability
- runtime/continuity usage
- validation state
- fallback reason

PECS Query:
- source = `kimi`
- issue_query
- profile = `large`
- projection_profile
- requested_fields
- metadata

PECS Response:
- runtime_targets
- secondary_neighbors
- continuity_evidence
- validation_evidence
- locality_evidence
- divergence_evidence
- advisory_cognition
- diagnostics

PECS Confidence:
- authority_confidence
- authority_confidence_band
- tier_contributions
- evidence_balance
- continuity_survivability

Relying On PECS:
- runtime_projection_primary
- continuity_export_secondary
- audit_enabled

Reason:
- explanation of the chosen balance of projection and continuity authority

## Retrieval Flow

1. Kimi invokes its integration adapter.
2. Kimi emits a query event tagged `source=kimi`.
3. `PECSLiteRuntimeAdapter.build_projection_safe(..., query_source="kimi")` is called.
4. `PECS-LITE` loads runtime and continuity artifacts via `PECSProQueryAdapter`.
5. `ProjectionHardener.harden_projection()` uses a large-context profile.
6. `ProjectionExporter.export_projection()` constructs the response.
7. Kimi also performs a lightweight continuity export audit by loading `engineering_continuity_state.json` and `active_topology.json` when available.
8. The response merges projection evidence with selected continuity summaries.

## Implementation

The canonical Kimi runtime adapter is implemented in `integrations/kimi_adapter.py`.
It consumes PECS context only through `PECSLiteRuntimeAdapter.build_projection_safe(..., query_source="kimi")` and preserves the returned projection schema without altering semantic content.

## Exact Projection Profile

For Kimi, use a large profile:
- `profile`: `large`
- `projection_profile.reasoning_budget`: `high`
- `projection_profile.exploration_constraints`: `expanded`
- `projection_profile.target_count`: `20`
- `projection_profile.continuity_depth`: `deep`
- `projection_profile.include_advisories`: `true`
- `max_related_files`: 10
- `max_symbol_expansions`: 20
- `max_new_files_before_validation`: 6

This profile supports broad reasoning and architecture-aware locality while remaining grounded in runtime evidence.

## Runtime Authority Exposure

Kimi should expose runtime authority prominently:
- `runtime_targets` with `fused_score`
- `tier_1_runtime` values
- `evidence_sources` containing runtime evidence names
- `supporting_symbols` and `related_files`
- `wrapper_warning` and `execution_depth`

The projection should surface enough runtime authority to allow Kimi to reason about which files are executable and immediately relevant.

## Validation Authority Exposure

Kimi should also expose validation evidence:
- `tier_3_validation`
- `engineering_chain_count`
- `runtime_confirmation_density`
- `accepted_rejected_fix_validation`
- `validation_flags`

Use validation evidence to qualify certainty and help Kimi avoid stale or unsupported targets.

## Ownership Authority Exposure

Ownership data should be a first-class signal:
- `ownership_hotspots`
- `possible_mutation_owner`
- `ownership_locality_lookup()` result
- `locality_authority_scores`

Prioritize targets that align with ownership hotspots, but do not exclude strong runtime targets outside ownership focus.

## Divergence Authority Exposure

Kimi must see divergence evidence explicitly:
- `divergence_indicators` with topology/historical mismatch metrics
- `continuity_concentration`
- `topology_authority_divergence`
- `runtime_historical_match`
- `wrapper_inflation`
- `convergence_opportunities`

If divergence is detected, Kimi should be able to reason about potential authority mismatch and uncertainty.

## Continuity Exposure

Kimi should consume both projection and continuity:
- `active_engineering_continuity.chains` (selected)
- `engineering_continuity_summary`
- `continuity_supporting_artifacts`
- `canonical_authority_clusters`
- `continuity_reconstruction_confidence`
- `continuity_survivability_confidence`

Continuity export should be used for architectural authority and audit, not as the only source.

## How Much Projection Should Be Surfaced

Kimi should surface:
- top 12 runtime targets in detail
- up to 8 secondary neighbors
- up to 5 top evidence fusion ranked files
- concise continuity chains with accepted/rejected locality context
- ownership hotspot summary
- divergence indicator summary

The response should be broad enough for architecture-level reasoning but not unbounded.

## Design Summary

Kimi should be a hybrid consumer:
- primary evidence from runtime projection
- secondary authority from continuity export
- broad evidence exposure for runtime, validation, ownership, and divergence
- large-context profile tuned for architecture-aware reasoning
- projection surface limited to the most meaningful targets and summaries

This design gives Kimi the best of both worlds: the practical runtime/locality evidence already available today, and the canonical continuity authority needed for long-term audit and architectural correctness.

## See Also

- [Query Pipeline](../query-pipeline.md) — canonical query contract
- [PECS-LITE](pecs-lite.md) — stateless projection protocol
- [Continue](continue.md), [Copilot](copilot.md), [Kimi](kimi.md), [CommandCode](commandcode.md) — consumer integrations
