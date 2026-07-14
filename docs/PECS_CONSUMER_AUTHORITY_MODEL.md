# PECS Consumer Authority Model

## Purpose
Define the optimal PECS authority source for the three downstream consumers in this architecture:
- Copilot
- Continue
- Kimi

The model must reflect the current state of evidence availability:
- exported continuity authority is currently `Chat -> Authority`
- runtime projection is richer and already consumes runtime/locality/ownership evidence
- the best future architecture must balance practical retrieval with long-term canonical authority

## Authority Source Candidates

### continuity export
Source: `.pecs/continuity/engineering_continuity_state.json`
- strongest formal continuity authority
- currently chat-derived and under-fused
- valuable for audit, accepted/rejected locality, and canonical provenance

### runtime projection
Source: `PECS-LITE` projection output
- richest current evidence path
- includes runtime targets, evidence fusion, ownership, diagnostics
- consumer-facing and query-driven

### hybrid
- primary consumer evidence from runtime projection
- supplementary canonical authority from continuity export
- supports audit, validation, and continuity context

## Optimal Choices

### A. Copilot
Recommendation: `hybrid`

Rationale:
- Copilot is an interactive, external-facing assistant that benefits most from runtime projection evidence.
- It must see rich runtime authority, ownership hotspots, and diagnostics quickly.
- At the same time, Copilot should still consult continuity export for auditability, accepted locality, and chain summaries.
- This avoids over-reliance on the current under-fused continuity export while preserving future authority convergence.

### B. Continue
Recommendation: `runtime projection` with continuity audit support

Rationale:
- Continue is a local-model, locality-first workflow with tight token and context budgets.
- It should use runtime projection as the primary authority source because that path is already optimized for local execution and projection diagnostics.
- Continuity export may be consulted in a lightweight audit mode only when available, not as the primary authority source.
- This keeps retrieval fast and compact while preserving PECS accountability.

### C. Kimi
Recommendation: `hybrid`

Rationale:
- Kimi is intended for large-context architecture-aware reasoning.
- It should receive both runtime projection evidence and continuity export insights.
- Runtime projection supplies file-locality targets, ownership hints, and evidence fusion.
- Continuity export supplies canonical continuity chains, divergence authority, and accepted/rejected locality summaries.
- Kimi should be the most continuity-aware consumer, but it still should not ignore the runtime projection layer.

## Decision Criteria

Each consumer should choose authority sources based on:
- model profile and token budget
- need for auditability versus execution locality
- available evidence richness
- fallback safety requirements

| Consumer | Recommended Source | Why |
|---|---|---|
| Copilot | hybrid | best balance of practical richness and canonical accountability |
| Continue | runtime projection (+ lightweight continuity audit) | local-model budget, locality-first, low token, strong ownership guidance |
| Kimi | hybrid | large-context reasoning needs both projection detail and continuity authority |

## Justification

### Why not continuity export only?
- Current export is effectively `Chat -> Authority` and misses runtime/locality fusion.
- Consumers that rely solely on it will lose the richer evidence already available in projection.

### Why not runtime projection only?
- Runtime projection is the practical consumer interface, but it is intentionally stateless and advisory.
- A purely projection-only model can miss accepted locality audit, continuity chain provenance, and long-term authority state.

### Why hybrid?
- Hybrid allows downstream consumers to use the strongest available evidence for their primary task while preserving canonical continuity accountability.
- The architecture can evolve by standardizing projection output first and then improving continuity export over time.

## Implementation Guidance (Design Only)

- Always issue a PECS query for all consumers.
- Use runtime projection as the primary evidence path for local model and interactive assistance.
- Use continuity export as a secondary authority source for audit, accepted/rejected locality, and divergence context.
- Expose clear pipe semantics: `RuntimeProjectionPrimary`, `ContinuityExportSecondary`, and `EvidenceAudit`.

## Recommended Authority Model Summary

- Copilot: Hybrid
- Continue: Runtime projection primary, continuity export secondary
- Kimi: Hybrid

This model preserves current strengths and future-proofs the architecture without treating the under-fused continuity export as the only authority source.
