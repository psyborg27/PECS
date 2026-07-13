# PECS Accepted Engineering Continuity Refactor Accountability

Date: 2026-05-15
Scope: Structured accepted engineering continuity linkage for small, medium, and large profiles.

## 1) Files Touched

1. integrations/pecs_pro_query_adapter.py
2. integrations/pecs_lite_projection_hardener.py
3. PECS_LITE v2/pecs_lite v2/runtime/pecs_lite_runtime_v2.py
4. PECS_LITE v2/pecs_lite v2/runtime/run_lite.py
5. install_workspace_integration.py
6. README.md
7. PECS_ACCEPTED_ENGINEERING_CONTINUITY_ACCOUNTABILITY.md (this report)

## 2) Methods Added

1. PECSProQueryAdapter.engineering_continuity_lookup()
2. ProjectionHardener._continuity_anchor_candidates()
3. ProjectionHardener._capture_confidence_summary()
4. ProjectionExporter._build_confidence_projection()
5. ProjectionExporter._build_active_engineering_continuity()

## 3) Methods Modified

1. PECSProQueryAdapter._load_artifacts()
2. PECSProQueryAdapter.active_continuity_lookup()
3. PECSProQueryAdapter.get_query_diagnostics()
4. PECSProQueryAdapter.get_health_metrics()
5. ProjectionHardener.__init__()
6. ProjectionHardener.harden_projection()
7. ProjectionHardener._score_candidates()
8. ProjectionHardener._calculate_metrics()
9. ProjectionHardener.validate_small_model_safety()
10. ProjectionExporter.export_projection()
11. PECSLiteRuntimeV2.build_projection()
12. run_lite CLI profile parsing
13. install_workspace_integration._write_continue_rules()
14. install_workspace_integration._write_copilot_instructions()
15. install_workspace_integration._install_bridge_runtime()
16. install_workspace_integration._write_readme()

## 4) Methods Removed

None.

## 5) Continuity Model Changes

Added compact structured continuity state consumption from:
.pecs/continuity/engineering_continuity_state.json

New continuity structure consumed by PECS-LITE:
- issue
- accepted_locality
- rejected_locality
- continuity_strength
- accepted_followup
- locality_stability
- repeat_success_count
- rollback_count
- abandoned_count
- contradictory_followups
- unresolved_locality
- runtime_ambiguity

Derived projection-side continuity confidence (0.0-1.0):
- Upranked by accepted followups, locality stability, repeated successful usage, no rollback.
- Downranked by rollback, abandonment, contradictory followups.

No raw chat transcript or narrative reasoning is used for projection shaping.

## 6) Accepted Continuity Changes

Accepted locality is now preserved as a compact signal and can influence projection via:

1. accepted_locality_scores map from adapter
2. continuity anchor candidate injection (accepted_continuity evidence)
3. direct confidence boost in hardener scoring
4. profile-specific active_engineering_continuity projection payloads

High-confidence accepted continuity chains (>= 0.75) become eligible for projection output.

## 7) Rejected Locality Changes

Rejected locality now has explicit downranking:

1. rejected_locality_scores map from adapter
2. hardener applies multiplicative confidence penalty per rejected locality
3. repeated rollback increases rejection strength
4. rejected chains included as bounded hints in continuity payload

Effect:
- repeatedly failed or rolled-back locality is deprioritized
- accepted followup chains dominate when conflict exists

## 8) Profile-Specific Continuity Changes

SMALL profile:
- mode: small_anchor
- includes only one high-confidence chain
- includes accepted_locality, continuity_confidence, accepted_followup
- includes at most one rejected locality
- no narrative continuity

MEDIUM profile:
- mode: bounded_chain
- includes up to two high-confidence chains
- includes accepted/rejected locality and locality_stability
- bounded neighborhood linkage

LARGE profile:
- mode: rich_bounded_chain
- includes up to four high-confidence chains
- includes accepted/rejected locality evolution
- includes unresolved_locality and runtime_ambiguity
- still structured and bounded (no raw continuity dump)

## 9) Negative Assertions

Confirmed true:

1. PECS-PRO remains model-agnostic.
2. PECS-LITE does not scan workspace.
3. PECS-LITE does not reconstruct topology.
4. PECS-LITE does not own continuity state.
5. PECS-LITE does not consume raw chat transcripts as projection context.
6. Projection includes forbidden mutation prefixes for .pecs.
7. Safety validation rejects .pecs continuity anchors if present.

## 10) Validation Results

Syntax checks:
- integrations/pecs_pro_query_adapter.py: pass
- integrations/pecs_lite_projection_hardener.py: pass
- PECS_LITE v2/pecs_lite v2/runtime/pecs_lite_runtime_v2.py: pass
- PECS_LITE v2/pecs_lite v2/runtime/run_lite.py: pass
- install_workspace_integration.py: pass

Diagnostics checks:
- No editor errors in touched files.
- Query diagnostics include engineering_continuity_state artifact reads.
- Health metrics include engineering_chain_count.

Middleware update validation in target workspace:
- .continue/rules/PECS_CONTEXT_RULE.md includes Engineering Continuity Principle.
- .github/copilot-instructions.md includes Engineering Continuity Principle.

Slicemypdf continuity case validation:
- Seeded structured chain:
  issue: obsolete slicemypdf dependency cleanup
  accepted_locality: dependency_manager.py
  rejected_locality: viewer_pipeline.py
  continuity_strength: 0.92

Observed behavior across profiles:
- active_engineering_continuity present for small/medium/large
- accepted locality anchor includes dependency_manager.py
- rejected locality includes viewer_pipeline.py
- runtime_targets include dependency_manager.py for small/medium/large
- has_pecs_runtime_target = false
- forbidden_mutation_prefixes includes .pecs/

## 11) Before/After Projection Examples

Before (no structured engineering continuity payload):
{
  "profile": "small",
  "runtime_targets": ["..."],
  "secondary_neighbors": ["..."],
  "metrics": {"...": "..."}
}

After SMALL:
{
  "profile": "small",
  "runtime_targets": ["..."],
  "forbidden_mutation_prefixes": [".pecs/"],
  "confidence_projection": {
    "primary": [{"file": "...", "confidence": 0.92, "evidence_type": "..."}],
    "uncertainty": {"projection_uncertainty": 0.08, "ambiguity_hint": "locality_confidence_high"}
  },
  "active_engineering_continuity": {
    "mode": "small_anchor",
    "chains": [{
      "issue": "obsolete slicemypdf dependency cleanup",
      "accepted_locality": "dependency_manager.py",
      "rejected_locality": ["viewer_pipeline.py"],
      "continuity_confidence": 1.0,
      "accepted_followup": true
    }]
  }
}

After MEDIUM:
{
  "profile": "medium",
  "execution_enrichment": {"execution_neighborhood": {"...": "..."}},
  "active_engineering_continuity": {
    "mode": "bounded_chain",
    "chains": [{"accepted_locality": "dependency_manager.py", "locality_stability": 0.9, "...": "..."}]
  }
}

After LARGE:
{
  "profile": "large",
  "execution_enrichment": {
    "execution_continuity": {"...": "..."},
    "continuity_context": {"...": "..."}
  },
  "active_engineering_continuity": {
    "mode": "rich_bounded_chain",
    "chains": [{"accepted_locality": "dependency_manager.py", "unresolved_locality": [], "runtime_ambiguity": false, "...": "..."}]
  }
}

## Final Outcome

PECS now preserves accepted engineering continuity as structured, compact, confidence-aware locality linkage.

PECS does not become raw conversational memory infrastructure.
