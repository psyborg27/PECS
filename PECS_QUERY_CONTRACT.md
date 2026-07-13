# PECS Query Contract

This document defines a deterministic PECS query/response contract for Copilot, Continue, Kimi, and future consumers.

Goals:
- PECS remains evidence-only.
- PECS does not make coding decisions.
- PECS provides authority evidence.
- PECS output is human-readable, LLM-readable, machine-readable, and auditable.
- PECS consultation must be observable.

## Contract Overview

### PECS Status
`PECS Status` reports the consultation state and artifact availability.

Fields:
- `queried_pegs`: boolean
- `workspace_id`: string
- `workspace`: string
- `runtime_mode`: string
- `projection_mode`: string
- `runtime_observability_used`: boolean
- `engineering_continuity_used`: boolean
- `consulted_artifacts`: string[]
- `missing_artifacts`: string[]
- `artifact_writes`: integer
- `validation_state`: string
- `fallback_reason`: string
- `reason`: string

Example:
```json
{
  "queried_pegs": true,
  "workspace_id": "sha256-...",
  "workspace": "/path/to/workspace",
  "runtime_mode": "read_only",
  "projection_mode": "query_driven",
  "runtime_observability_used": true,
  "engineering_continuity_used": true,
  "consulted_artifacts": [
    ".pecs/active_context.json",
    ".pecs/compact_bundle.json",
    ".pecs/continuity/locality_state.json"
  ],
  "missing_artifacts": [],
  "artifact_writes": 0,
  "validation_state": "read_only",
  "fallback_reason": "",
  "reason": "PECS consulted for evidence retrieval"
}
```

## PECS Query Schema

PECS Query is the consumer request message.

Fields:
- `query_id`: string
- `source`: string
- `issue_query`: string
- `workspace_id`: string
- `profile`: string
- `projection_profile`: object
- `requested_fields`: string[]
- `timestamp`: string
- `metadata`: object

### Exact Query Schema
```json
{
  "query_id": "string",
  "source": "copilot|continue|kimi|other",
  "issue_query": "string",
  "workspace_id": "string",
  "profile": "small|medium|large",
  "projection_profile": {
    "profile": "small|medium|large",
    "reasoning_budget": "low|medium|high|very_high",
    "exploration_constraints": "strict|bounded|expanded",
    "target_count": integer,
    "continuity_depth": "minimal|balanced|deep",
    "include_advisories": boolean
  },
  "requested_fields": [
    "runtime_targets",
    "secondary_neighbors",
    "continuity_evidence",
    "validation_evidence",
    "locality_evidence",
    "divergence_evidence",
    "advisory_cognition",
    "diagnostics"
  ],
  "timestamp": "ISO8601 string",
  "metadata": {
    "user_intent": "string",
    "reasoning_capability_class": "small|medium|large|frontier|unknown"
  }
}
```

### Profile Fields

#### Small profile fields
- `profile`: `small`
- `projection_profile.reasoning_budget`: `low`
- `projection_profile.exploration_constraints`: `strict`
- `projection_profile.target_count`: `6`
- `projection_profile.continuity_depth`: `minimal`
- `projection_profile.include_advisories`: `false`

#### Medium profile fields
- `profile`: `medium`
- `projection_profile.reasoning_budget`: `medium`
- `projection_profile.exploration_constraints`: `bounded`
- `projection_profile.target_count`: `12`
- `projection_profile.continuity_depth`: `balanced`
- `projection_profile.include_advisories`: `true`

#### Large profile fields
- `profile`: `large`
- `projection_profile.reasoning_budget`: `high`
- `projection_profile.exploration_constraints`: `expanded`
- `projection_profile.target_count`: `20`
- `projection_profile.continuity_depth`: `deep`
- `projection_profile.include_advisories`: `true`

## PECS Response Schema

PECS Response is the evidence payload returned to the consumer.

Top-level fields:
- `schema`: string
- `query_id`: string
- `workspace_id`: string
- `status`: string
- `PECS_Status`: object
- `PECS_Query`: object
- `PECS_Response`: object
- `PECS_Confidence`: object
- `Relying_On_PECS`: object
- `Reason`: string

### Exact Response Schema
```json
{
  "schema": "pecs.query_response.v1",
  "query_id": "string",
  "workspace_id": "string",
  "status": "success|partial|failed",
  "PECS_Status": {
    "queried_pegs": true,
    "runtime_mode": "read_only",
    "projection_mode": "query_driven",
    "runtime_observability_used": true,
    "engineering_continuity_used": true,
    "consulted_artifacts": ["string"],
    "missing_artifacts": ["string"],
    "artifact_writes": 0,
    "validation_state": "read_only",
    "fallback_reason": "string"
  },
  "PECS_Query": {
    "source": "string",
    "issue_query": "string",
    "profile": "small|medium|large",
    "projection_profile": {
      "profile": "string",
      "reasoning_budget": "string",
      "exploration_constraints": "string",
      "target_count": integer,
      "continuity_depth": "string",
      "include_advisories": boolean
    },
    "requested_fields": ["string"],
    "timestamp": "ISO8601 string",
    "metadata": {"string": "any"}
  },
  "PECS_Response": {
    "runtime_targets": [
      {
        "file": "string",
        "fused_score": number,
        "tier_scores": {
          "tier_0_static": number,
          "tier_1_runtime": number,
          "tier_2_continuity": number,
          "tier_3_validation": number
        },
        "evidence_sources": {
          "tier_0_static": ["string"],
          "tier_1_runtime": ["string"],
          "tier_2_continuity": ["string"],
          "tier_3_validation": ["string"]
        },
        "provenance": ["string"],
        "is_active": boolean,
        "authority_type": "primary|secondary|legacy|wrapper|deprecated"
      }
    ],
    "secondary_neighbors": ["string"],
    "continuity_evidence": {
      "schema": "pecs.engineering_continuity_projection.v1",
      "active_engineering_chains": [object],
      "accepted_locality_scores": {"string": number},
      "locality_authority_scores": {"string": number},
      "runtime_confirmed_locality_scores": {"string": number},
      "locality_authority_confidence": number,
      "continuity_survivability_confidence": number
    },
    "validation_evidence": {
      "runtime_confirmation_density": number,
      "engineering_chain_count": integer,
      "validation_flags": ["string"]
    },
    "locality_evidence": {
      "active_locality_clusters": [object],
      "ownership_hotspots": [object],
      "active_runtime_touched_files": [object],
      "runtime_validation": {"string": number}
    },
    "divergence_evidence": {
      "divergence_indicators": {
        "scattering_index": number,
        "continuity_concentration": number,
        "topology_authority_divergence": number,
        "runtime_historical_match": number,
        "wrapper_inflation": number
      },
      "convergence_opportunities": [object]
    },
    "advisory_cognition": {
      "comprehension": "string",
      "observations": ["string"],
      "recommendations": ["string"]
    },
    "diagnostics": {
      "queried_pecs_pro": boolean,
      "workspace_scan_performed": boolean,
      "topology_reconstructed": boolean,
      "consulted_pecs_artifacts": ["string"],
      "projection_profile": object,
      "failure_modes": ["string"]
    }
  },
  "PECS_Confidence": {
    "authority_confidence": number,
    "authority_confidence_band": "low|medium|high",
    "tier_contributions": {
      "runtime": number,
      "continuity": number,
      "validation": number,
      "topology": number,
      "ownership": number
    },
    "evidence_balance": {
      "runtime": number,
      "continuity": number,
      "validation": number,
      "topology": number,
      "ownership": number
    }
  },
  "Relying_On_PECS": {
    "pegs_used": boolean,
    "pegs_observed": boolean,
    "pegs_influence": "strong|moderate|weak|none",
    "fallback_reason": "string"
  },
  "Reason": "string"
}
```

### Field semantics
- `PECS_Status`: shows whether PECS was consulted and which artifacts were read.
- `PECS_Query`: echoes the incoming query and profile.
- `PECS_Response`: contains evidence-only outputs.
- `PECS_Confidence`: quantifies how much authority evidence exists.
- `Relying_On_PECS`: records whether the consumer relied on PECS and why.
- `Reason`: plain language explanation of the response status.

## Evidence fields

### runtime_targets
Current retrieval output maps to `runtime_targets`.
- Source: `runtime_target_candidates()` and `runtime_target_lookup()`.
- Evidence: `tier_scores` from runtime activation, touched files, and neighborhood.
- Provenance: `runtime_interaction_graph`, `evidence_fusion`.

### secondary_neighbors
Current retrieval output maps to `secondary_neighbors`.
- Source: `runtime_interaction_neighborhood_lookup()`.

### continuity_evidence
Current retrieval output maps to `engineering_continuity_lookup()`.
- Source: `.pecs/continuity/engineering_continuity_state.json`.
- Includes: accepted and rejected locality scores, runtime-confirmed locality, authority/confidence summaries.

### validation_evidence
Current retrieval output maps to evidence fusion tier 3 and active continuity.
- Source: evidence fusion ranking and active continuity snapshot.
- Includes: confirmed runtime locality, error-object correlations, fix validation, unresolved penalties.

### locality_evidence
Current retrieval output maps to `.pecs/continuity/locality_state.json` and `.pecs/continuity/active_topology.json`.
- Includes: active locality clusters, ownership hotspots, touched runtime files, runtime validation.

### divergence_evidence
Current retrieval output maps to locality state divergence indicators.
- Includes scattering index, continuity concentration, topology authority divergence, runtime-historical match, wrapper inflation.

### advisory_cognition
Current retrieval output is derived from projection hardener / advisory envelope builders.
- Includes advisory observations and recommendations.
- Should be evidence commentary, not decision instructions.

### diagnostics
- Source: `get_query_diagnostics()`, `get_health_metrics()`, and response builder metadata.
- Must include whether PECS was consulted, fallback reasons, and exact artifact list.

## Profile field mappings

Current adapter conventions suggest the following profile mappings:

- `small`: low reasoning budget, strict exploration, limited runtime targets, no expanded advisory detail.
- `medium`: balanced reasoning budget, bounded exploration, moderate target count, advisory detail enabled.
- `large`: high reasoning budget, expanded exploration, larger target set, deep continuity evidence, advisory detail enabled.

## Mapping from current artifacts

| Contract field | Current artifact | Source code / function |
|---|---|---|
| `consulted_artifacts` | `.pecs/*.json`, `.pecs/continuity/*.json` | `ProjectionHardener._build_pecs_runtime_report()` |
| `runtime_targets` | `.pecs/active_context.json`, `.pecs/locality_index.json`, `.pecs/topology_compact.json` | `PECSProQueryAdapter.runtime_target_candidates()` |
| `secondary_neighbors` | `.pecs/topology_compact.json` | `PECSProQueryAdapter.runtime_interaction_neighborhood_lookup()` |
| `continuity_evidence` | `.pecs/continuity/engineering_continuity_state.json` | `PECSProQueryAdapter.engineering_continuity_lookup()` |
| `validation_evidence` | evidence fusion outputs | `PECSProQueryAdapter.evidence_fusion_lookup()` |
| `locality_evidence` | `.pecs/continuity/locality_state.json` | `PECSProQueryAdapter.evidence_fusion_lookup()` and `active_continuity_lookup()` |
| `divergence_evidence` | `.pecs/continuity/locality_state.json` | `PECSProQueryAdapter.evidence_fusion_lookup()` |
| `advisory_cognition` | projection hardener | `ProjectionHardener._build_pecs_runtime_report()` |
| `diagnostics` | query diagnostics | `PECSProQueryAdapter.get_query_diagnostics()` |

## Mapping from current retrieval outputs

- `runtime_targets` → `PECSProQueryAdapter.runtime_target_candidates()` results.
- `secondary_neighbors` → `runtime_interaction_neighborhood_lookup()` results.
- `continuity_evidence` → `engineering_continuity_lookup()` results.
- `validation_evidence` → evidence fusion `tier_3_validation` and active continuity lookup.
- `locality_evidence` → `locality_state` clusters and active topology runtime validation.
- `divergence_evidence` → `locality_state.divergence_indicators` and convergence opportunities.
- `advisory_cognition` → packaged advisory summary from hardener/runner.
- `diagnostics` → `get_query_diagnostics()` and `get_health_metrics()`.

## Accountability and observability

To make consultation observable, every response MUST include:
- `queried_pegs`: true/false
- `consulted_artifacts`: exact artifact list
- `missing_artifacts`: exact missing manifest list
- `fallback_reason`: if any
- `Relying_On_PECS.pegs_used`: boolean
- `Relying_On_PECS.pegs_observed`: boolean
- `Reason`: human-readable explanation

Consumers MUST NOT:
- treat PECS output as a coding decision
- infer code changes directly from evidence weights
- hide whether PECS was consulted

## Human / LLM / Machine readability

This schema is intentionally:
- human-readable: field names are plain language and sections are labeled.
- LLM-readable: nested structures and repeated field names are explicit.
- machine-readable: JSON schema shape is deterministic and fully typed.
- auditable: consultation metadata, artifact lists, and fallback reasons are explicit.

## Notes

- The contract is evidence-only: no code path, fix, or patch is prescribed.
- `PECS_Confidence` is a summary of evidence strength, not a decision signal.
- `Relying_On_PECS.Reason` is required when fallback or bypass occurs.
- `Reason` should be a concise explanation of the response state.
