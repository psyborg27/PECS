# PECS Roadmap

## Purpose
Determine whether the future PECS architecture should emphasize:
- improving `engineering_continuity_state.json`
- or standardizing all consumers around the runtime projection layer

## Most Important Question
Would modifying `engineering_continuity_state.json` provide greater benefit, or would standardizing all consumers around the runtime projection layer provide greater benefit?

## Recommendation
**Standardizing all consumers around the runtime projection layer provides greater benefit today.**

## Evidence

### 1. Current authority fusion state
`PECS_AUTHORITY_FUSION_FINAL_REPORT.md` shows:
- `engineering_continuity_state.json` is currently built from `ai_chat_history.json` only
- runtime/locality evidence artifacts are not directly ingested into canonical authority export
- the existing authority export is effectively `Chat -> Authority`

That means continuity export is not yet the robust evidence source required to support full consumer reliance.

### 2. Current projection richness
`COPILOT_PECS_INTEGRATION_GAP_REPORT.md` shows runtime projection already consumes:
- runtime authority
- accepted locality
- ownership hotspots
- evidence fusion
- runtime targets
- projection diagnostics

This path is already richer and more complete than the current continuity export.

### 3. Consumer design goals
The design for Continue and Kimi favors:
- Continue: local-model, low token, locality-first
- Kimi: large-context, architecture-aware, continuity-aware

For both, the runtime projection layer is the practical interface today. It can deliver the evidence consumers need without waiting for authority export fusion to mature.

### 4. Audit and policy alignment
The recommended policy in `PECS_CONSULTATION_POLICY.md` is:
- mandatory query
- optional reliance

This policy is best supported by a strong runtime projection layer and a separate continuity audit path.
If continuity export were treated as mandatory today, it would force consumers onto an under-fused evidence source.

## Benefit Comparison

| Option | Benefit Today | Risk | Notes |
|---|---|---|---|
| Modify `engineering_continuity_state.json` | moderate | high | requires deep integration of runtime/locality/validation evidence into the canonical continuity pipeline; valuable long-term, but currently under-implemented |
| Standardize runtime projection | high | low | uses the existing richer evidence path; easier to deploy; supports all consumers now |

## Recommended Future Direction

1. **Standardize consumers on the runtime projection layer first.**
   - Use `PECS-LITE` projection as the primary authority interface.
   - Ensure all consumers issue PECS queries and report on query success.
   - Make the projection response the main evidence source for runtime targets, ownership, and diagnostics.

2. **Improve continuity export as a secondary audit source.**
   - Enhance `engineering_continuity_state.json` over time to ingest runtime/locality evidence.
   - Use it for accepted/rejected locality provenance, continuity chains, divergence summaries, and audit.

3. **Adopt a hybrid model in the future.**
   - Keep runtime projection primary.
   - Use continuity export for secondary authority, especially for Kimi and audit scenarios.

## Concrete Direction

- Short term: build around runtime projection and keep continuity export as audit/support.
- Medium term: integrate runtime/locality evidence into `engineering_continuity_state.json` so the hybrid model becomes stronger.
- Long term: aim for a true hybrid architecture where runtime projection and fused continuity export reinforce each other.

## Conclusion

Standardizing all consumers around the runtime projection layer will provide the greater immediate benefit.
Modifying `engineering_continuity_state.json` is still important, but it is a longer-term improvement that should follow after consumers are aligned on the projection interface.

## Continuity Export and TOC Upgrades

Planned work includes incremental upgrades to the auto-TOC / continuity export pipeline:

- Isolate markdown/TOC generation in the bridge export pipeline.
- Preserve existing `.pecs/ai_chat_history.json` and `.pecs/continuity/*` artifacts across upgrades.
- Extend bridge validation to cover generated markdown structure.
- Add regression snapshots for `.pecs/continuity/*` artifacts.
- Roll out changes in a feature branch before promoting to Kimi integration.

The goal is to keep formatting changes separate from core continuity ingestion and retrieval flows.

## Architecture Evolution Notes

- Remove legacy parallel graph/index structures after all consumers are migrated to the Workspace Graph and Workspace Registry.
- Extend line-range resolution to additional languages.
- Consider optional semantic enrichment while preserving deterministic structural correlation as the primary signal.

## Release History

See `CHANGELOG.md` for the canonical project changelog.

**PECS Core v1 Alpha 1** completes the deterministic architectural retrieval pipeline. It delivers the Workspace Graph, Workspace Registry, Evidence Correlation Engine, Navigation Builder, and Query Pipeline as the unified foundation for PECS-PRO. This release marks the transition from continuity-first, file-hierarchical retrieval to navigation-first, deterministic architectural correlation. The next phase, **PECS Validation**, will harden consumer integrations and projection quality against this base.
