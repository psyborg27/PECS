# Copilot Integration Recommendations

## Purpose
Evaluate whether the current Copilot PECS integration should be modified, and recommend required and optional changes.

## Current Behavior Summary
- Copilot uses `integrations/copilot_adapter.py` to query PECS.
- The integration calls `PECSLiteRuntimeAdapter.build_projection_safe()` with `query_source="copilot"`.
- The projection output includes runtime targets, diagnostics, and advisory evidence.
- A fallback path to `TopologyRetriever.build_minimal_context(object_id)` exists if projection fails.
- `.github/copilot-instructions.md` provides advisory PECS-first guidance, but is not enforced by runtime code.
- The canonical continuity export remains `Chat -> Authority` and is not fully fused with runtime/locality evidence.

## Copilot vs Contract

### Matches
- Copilot queries PECS-LITE and emits PECS-related telemetry.
- The projection payload contains observable status and diagnostics.
- Projection profiles are selected based on model metadata and profile class.
- The integration is advisory and consistent with the PECS projection-first design.

### Gaps
- The integration is not fully aligned with `PECS_QUERY_CONTRACT.md` schema.
- `engineering_continuity_state.json` is not a fully fused authority source.
- Continuity evidence is under-represented relative to the contract’s expected continuity/locality/divergence objects.
- Copilot can bypass PECS via fallback, which is acceptable but reduces enforcement strength.
- `.github/copilot-instructions.md` is advisory only and may be ignored by external agents.

## Evaluation of Specific Behaviors

### Advisory-only instructions
- Current status: advisory.
- Implication: Copilot may choose non-PECS guidance if the external service does not honor workspace instructions.
- Recommendation: retain advisory guidance, but add stronger audit and query enforcement at the integration layer.

### Fallback behavior
- Current status: present and intentional.
- Implication: fallback improves resilience, but it also enables PECS bypass.
- Recommendation: keep fallback, but require explicit fallback logging and a `fallback_reason` in the returned response.

### Ability to bypass PECS
- Current status: yes.
- Implication: acceptable under policy B, but it should be observable.
- Recommendation: maintain bypass capability but make it explicit in `PECS Status` and `Relying On PECS`.

### Ability to read artifacts directly
- Current status: indirect through projection adapter.
- Implication: good; Copilot should not manually read `.pecs` files as source, only via the PECS query layer.
- Recommendation: preserve adapter-based artifact access and avoid direct `.pecs` parsing in Copilot adapter code.

## Recommended Changes

### Required Changes
1. **Add explicit query obligation**
   - Ensure Copilot always issues a PECS query and records `queried_pegs: true`.
   - This enforces policy B and preserves auditability.

2. **Record fallback reasons explicitly**
   - If `TopologyRetriever.build_minimal_context()` is used, populate `fallback_reason`.
   - Include `projection_delivered` and `fallback_triggered` clearly in `PECS Status`.

3. **Expose evidence usage in response**
   - Add `Relying On PECS` section indicating whether the returned advice relied on PECS evidence.
   - Include `runtime_projection_used`, `continuity_export_audited`, and `fallback_used`.

4. **Avoid over-reliance on continuity export until fused**
   - Do not change Copilot to treat `engineering_continuity_state.json` as the only authority source.
   - Continue using the projection layer as the primary evidence path.

### Optional Changes
1. **Add lightweight continuity audit**
   - Have Copilot optionally load a shallow summary of `engineering_continuity_state.json` for provenance checks.
   - This should be audit-only, not primary authority.

2. **Expose more evidence fields selectively**
   - Surface `tier_2_continuity` and `tier_3_validation` only when they add value.
   - Hide verbose chain data unless the model requests deeper continuity context.

3. **Strengthen instruction guidance**
   - Update `.github/copilot-instructions.md` to document specific PECS query response fields expected by Copilot.
   - This improves future external compliance.

### No-change Areas
1. **Fallback path itself**
   - Retain fallback capability for reliability.

2. **Advisory instruction model**
   - Maintain advisory guidance rather than hard enforcement, because current continuity export is under-fused.

3. **Adapter-based `.pecs` access**
   - Keep artifact access through `PECSLiteRuntimeAdapter` and avoid direct `.pecs` file parsing in Copilot code.

## Recommendation Summary

- Required: add explicit query obligation, fallback tracing, and reliance reporting.
- Optional: add lightweight continuity audit and selective evidence exposure.
- No-change: preserve fallback behavior, advisory guidance, and adapter-based artifact access.

This recommendation keeps Copilot practical and resilient while improving PECS observability and alignment with the contract.

## See Also

- [Query Pipeline](../query-pipeline.md) — canonical query contract
- [PECS-LITE](pecs-lite.md) — stateless projection protocol
- [Continue](continue.md), [Copilot](copilot.md), [Kimi](kimi.md), [CommandCode](commandcode.md) — consumer integrations
