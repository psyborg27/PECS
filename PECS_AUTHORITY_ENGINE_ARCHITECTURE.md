# PECS Authority Engine Architecture

## Part 1 — Current components contributing to authority generation

### `integrations/pecs_pro_query_adapter.py`

- `evidence_fusion_lookup()`
  - Responsibility: aggregate and fuse all available PECS evidence into deterministic, file-level tier scores.
  - Implementation evidence:
    - reads `.pecs/locality_index.json`, `.pecs/compact_bundle.json`, `.pecs/continuity/locality_state.json`, `.pecs/continuity/engineering_continuity_state.json`, and `.pecs/topology_compact.json`.
    - builds `tier_scores` for each file from:
      - `tier_0_static` (import topology, dependency topology, filesystem structure)
      - `tier_1_runtime` (active object activation, touched-file counts, runtime neighborhood)
      - `tier_2_continuity` (ownership continuity, continuity hotspots, engineering continuity chain, canonical cluster influence)
      - `tier_3_validation` (runtime confirmed locality, error-object correlation, fix validation, unresolved/rejection penalties)
    - outputs `ranked_files`, `weights`, `tier_sources`, and `provenance`.
  - Current role: rich evidence fusion in PECS-PRO, but not final authority output.

- `runtime_target_candidates()`
  - Responsibility: generate a candidate list of runtime-locality files for projection.
  - Implementation evidence:
    - seeds with runtime interaction neighborhood targets derived from `active_context` and `locality_state`.
    - then appends ranked files from `evidence_fusion_lookup()`.
    - sets candidate metadata such as `evidence`, `base_confidence`, `tier_scores`, and `provenance`.
  - Current role: candidate supplier for PECS-LITE hardening.

- `engineering_continuity_lookup()`
  - Responsibility: expose compact engineering continuity signals derived from accepted/rejected locality chains.
  - Implementation evidence:
    - reads `.pecs/continuity/engineering_continuity_state.json`.
    - filters chains by `issue_query` tokens.
    - returns `accepted_locality_scores`, `rejected_locality_scores`, `runtime_confirmed_locality_scores`, `continuity_survivability_scores`, and per-chain continuity confidence metadata.
  - Current role: bounded continuity signal provider for hardener scoring.

### `integrations/pecs_lite_projection_hardener.py`

- `ProjectionHardener._score_candidates()`
  - Responsibility: convert candidate evidence into local hardener confidence scores.
  - Implementation evidence:
    - inputs: `targets` from `runtime_target_candidates()` and `continuity_signals` from `engineering_continuity_lookup()`.
    - creates `ConfidenceScore` based on `evidence_type`, `base_confidence`, evidence order, and proximity.
    - blends in `accepted_locality_scores` and applies rejected penalties.
    - downranks inactive localities and lightly boosts query token hits.
  - Current role: simplified authority approximator inside PECS-LITE.

- `ProjectionExporter` in `integrations/pecs_lite_projection_hardener.py`
  - Responsibility: build final projection payload, attach diagnostics, and surface metadata.
  - Implementation evidence:
    - calls `adapter.evidence_fusion_lookup(max_files=128)` to enrich final targets.
    - builds `runtime_targets` with `probable_file`, `confidence`, `evidence_tiers`, `evidence_sources`, continuity metadata, and `search_budget`.
    - emits `pecs_lite_status`, `evidence_fusion`, `engineering_continuity_summary`, `active_engineering_continuity`, and `pecs_runtime_report`.
  - Current role: projection formatter and metadata aggregator, not primary authority computation.

### Observed seam in current architecture

- Evidence fusion and continuity scoring are computed in `PECSProQueryAdapter`.
- `ProjectionHardener._score_candidates()` re-synthesizes a much smaller confidence signal from `base_confidence`, `evidence_type`, and positional ordering.
- `ProjectionExporter` adds metadata and transparency after selection, but does not alter core target ranking.
- Therefore the current authority path is:
  - Evidence collection → evidence fusion → simplified hardener scoring → projection output.

## Part 2 — Architecture comparison

### Option A — Existing architecture

Evidence
↓
ProjectionHardener
↓
Projection

#### separation of concerns
- weak: `ProjectionHardener` must both interpret fused evidence and perform target selection.
- evidence fusion is separated, but authority reasoning is duplicated in hardener.

#### compatibility
- existing: fits current `PECS-LITE` runtime because hardener remains downstream and query-only.
- no new contract required.

#### extensibility
- limited: adding new evidence types requires hardener changes, since authority is still computed there.
- evidence fusion improvements may not fully affect selection if hardener does not consume them.

#### object authority integration
- weak: object-level evidence is available in `PECSProQueryAdapter`, but not centrally scored as authority.
- hardener only sees candidate-level `base_confidence`, not a dedicated object authority model.

#### performance
- reasonable: no extra subsystem, fewer layers.
- but authority computation is duplicated between adapter and hardener.

#### maintainability
- moderate: authority logic is split across `pecs_pro_query_adapter.py` and `ProjectionHardener`.
- risk of drift between fused evidence semantics and hardener confidence semantics.

### Option B — Proposed architecture

Evidence
↓
Authority Engine
↓
ProjectionHardener
↓
Projection

#### separation of concerns
- strong: centralize authority score generation in a dedicated PECS-PRO subsystem.
- `ProjectionHardener` becomes a pure selection/narrowing layer.

#### compatibility
- good: can preserve current projection schema by mapping authority engine outputs into existing `evidence_fusion` / `confidence_projection` / `pecs_lite_status`.
- `ProjectionExporter` can continue to build the same outer payload.

#### extensibility
- high: new evidence types and object authority rules can be added in one place.
- better support for object-level and group-level scoring without changing hardener internals.

#### object authority integration
- clean: object authority can be incorporated as first-class input to the Authority Engine.
- object IDs, object groups, and episode evidence become direct authority signals.

#### performance
- slightly higher subsystem overhead, but likely negligible compared to value.
- authoritative scoring can still be deterministic and cached in PECS-PRO.

#### maintainability
- improved: authoritative scoring is no longer split between PECS-PRO fusion and PECS-LITE hardener.
- reduces the current bottleneck by centralizing evidence interpretation.

## Part 3 — Recommended Authority Engine responsibilities

### It should consume

- `tier_0_static`
  - import topology, dependency topology, filesystem existence.
- `tier_1_runtime`
  - active object activations, touched file counts, runtime neighborhood, runtime interaction evidence.
- `tier_2_continuity`
  - ownership continuity, continuity hotspots, canonical clusters, accepted/rejected locality scores, engineering continuity metrics.
- `tier_3_validation`
  - user-confirmed runtime validation, error-object correlation, fix validation, unresolved/rejected indicators.
- `canonical_authority_clusters`
  - historical cluster share, continuity emergence bonus, cluster-based authority reinforcement.
- `accepted_locality_scores`
  - explicit accepted locality anchors from engineering continuity.
- ownership evidence
  - active runtime ownership, touched-file ownership, object-to-file canonical ownership.
- runtime evidence
  - active context, runtime interaction topology, runtime zone confirmation.
- validation evidence
  - runtime confirmation, validation accept/reject/regression, error linkage.
- historical evidence
  - continuity chain stability, persistence signals, historical retention.
- object authority
  - object IDs, object groups, object-based locality signals, object error correlations.
- episode evidence
  - temporal persistence from repeated activations or repeated validation outcomes.

### It should produce

- per-target/file `authority_score`
- per-target `authority_breakdown` by evidence tier
- `evidence_breakdown` with contributing artifact categories
- `contributing_artifacts` list or identifiers
- `contributing_object_groups` and/or object authority groups
- `contributing_runtime_targets` or target candidate provenance
- `contributing_continuity` signals and accepted/rejected locality anchors
- `confidence_band` or `authority_confidence_class`

### Recommended minimal Authority Engine output

- `authority_score` (0.0–1.0) per candidate file
- `authority_breakdown` containing `tier_0_static`, `tier_1_runtime`, `tier_2_continuity`, `tier_3_validation`
- `evidence_breakdown` listing `provenance` and `contributing_artifacts`
- `confidence_band` (`high`, `medium`, `low`, etc.)
- `target_file` or normalized candidate identifier
- optional `authority_type` / `failure_mode` metadata

## Part 4 — Exact Authority Engine output contract

A minimum canonical contract should include:

- `schema`: `pecs.authority_engine.v1`
- `authority_targets`: array of objects with:
  - `file`: normalized path
  - `authority_score`: float
  - `confidence_band`: string
  - `authority_breakdown`: {
    - `tier_0_static`: float,
    - `tier_1_runtime`: float,
    - `tier_2_continuity`: float,
    - `tier_3_validation`: float,
    - `canonical_cluster_bonus`: float,
  }
  - `evidence_breakdown`: {
    - `contributing_artifacts`: [string],
    - `contributing_object_groups`: [string],
    - `contributing_continuity`: [string],
    - `contributing_runtime_targets`: [string],
  }
  - `provenance`: [string]
  - `authority_type`: string
  - `predicted_failure_mode`: string

- `summary`: {
  - `authority_engine_version`: string,
  - `deterministic`: bool,
  - `authority_score_mean`: float,
  - `authority_score_uncertainty`: float,
  - `top_ranked_targets`: [string],
}

This contract is intentionally additive. Existing projection fields may remain unchanged while the authority engine output is surfaced in a contained section.

## Part 5 — Recommended change to ProjectionHardener

### Preferred architecture

- `ProjectionHardener` should consume authority produced elsewhere.
- It should not be the primary authority generator.

### Why

- The current implementation flattens rich evidence into simplified confidence in `_score_candidates()`.
- That flattening is the bottleneck: `ProjectionHardener` sees only `base_confidence`, `evidence_type`, and positional ordering, rather than the full fused authority signal.
- Moving authority generation to PECS-PRO keeps PECS-LITE focused on selection, token budgeting, and small-model narrowing.

### Recommended role for `ProjectionHardener`

- accept `authority_targets` or equivalent authority payload from PECS-PRO.
- select `primary_targets` and `secondary_neighbors` based on authority ranking plus locality proximity rules.
- apply profile-specific hard limits, token budgets, and progressive disclosure.
- preserve small-model safety and projection diagnostics.

## Part 6 — Compatibility analysis

### Consumer Observability
- compatible: `ProjectionExporter` currently already reports `pecs_lite_status`, `evidence_fusion`, and diagnostic metadata.
- a dedicated Authority Engine can be surfaced as an additional provenance layer without breaking observability.

### Object ID Producer
- compatible: object IDs are an input source for PECS-PRO evidence, not a projection output.
- centralizing authority in PECS-PRO would likely improve object ID signal usage.

### Object Evidence Capture
- compatible: captured evidence remains upstream of the Authority Engine.
- the Authority Engine is the natural consumer of object evidence.

### Object Correlation
- compatible and improved: authority can explicitly represent correlated object groups and object-to-file authority.

### Object Groups
- compatible: object groups can be encoded as `contributing_object_groups`.
- supports richer group-level authority without changing PECS-LITE semantics.

### PECS-LITE Query Agent
- compatible: `PECS-LITE` remains a downstream, query-only consumer.
- it would still preserve the existing no-workspace-scan and read-only model.

### existing projection format
- compatible if the new output is additive, not disruptive.
- `ProjectionExporter` can keep current fields and add an `authority_engine` section.
- existing clients can continue to use `runtime_targets`, `confidence_projection`, and `pecs_lite_status`.

## Most important question

### Does introducing a dedicated Authority Engine eliminate the current evidence-consumption bottleneck?

**Answer: PARTIAL**

#### justification
- The current bottleneck is real and visible in code: `ProjectionHardener._score_candidates()` flattens rich `evidence_fusion_lookup()` output into a simplified score model.
- A dedicated Authority Engine would remove the architectural seam by centralizing authority computation in PECS-PRO and passing a richer, canonical authority contract downstream.
- However, elimination is only partial until `ProjectionHardener` is changed to consume that authority output instead of recomputing or re-synthesizing it.
- In its current form, the bottleneck would still persist if the hardener continues to use raw candidate scoring logic.

## Recommendation

- Introduce a dedicated Authority Engine in PECS-PRO.
- Keep `ProjectionHardener` as the downstream selector/narrower.
- Preserve existing `ProjectionExporter` output and add an optional `authority_engine` section.
- Use the Authority Engine to materialize the canonical contract documented above.
- This is the best architectural path to preserve PECS-LITE while fixing the evidence-consumption seam.
