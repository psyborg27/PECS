# PECS Retrieval Effectiveness

## Evidence fusion ranking effectiveness

### Query 1

- runtime_targets returned: `50 `
- runtime_neighbors returned: `0 `
- evidence_fusion ranked_files: `50 `
- engineering continuity chains: `0 `

Top-ranked file and score breakdown:
- top file: `install_workspace_integration.py`
- fused_score: `0.228`
- tier_scores: `{'tier_0_static': 0.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.38, 'tier_3_validation': 0.667}`
- tier_sources: `{'tier_0_static': [], 'tier_1_runtime': [], 'tier_2_continuity': ['continuity_hotspots', 'engineering_continuity_chain'], 'tier_3_validation': ['accepted_rejected_fix_validation', 'error_to_object_correlation']}`

Continuity evidence flags:
- ownership_locality: `PECS_ID:Qt.main_app_UI_rewrite`
- active_continuity size: `14`
- runtime_confirmation_density: `0.0`

Runtime activation evidence:
- active_runtime_zones: `['locality', 'overlay_pipeline', 'topology']`

Diagnostics:
- wrapper_warning: `False`
- execution_depth: `deep`

### Query 2

- runtime_targets returned: `50 `
- runtime_neighbors returned: `0 `
- evidence_fusion ranked_files: `50 `
- engineering continuity chains: `0 `

Top-ranked file and score breakdown:
- top file: `install_workspace_integration.py`
- fused_score: `0.228`
- tier_scores: `{'tier_0_static': 0.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.38, 'tier_3_validation': 0.667}`
- tier_sources: `{'tier_0_static': [], 'tier_1_runtime': [], 'tier_2_continuity': ['continuity_hotspots', 'engineering_continuity_chain'], 'tier_3_validation': ['accepted_rejected_fix_validation', 'error_to_object_correlation']}`

Continuity evidence flags:
- ownership_locality: `PECS_ID:Qt.main_app_UI_rewrite`
- active_continuity size: `14`
- runtime_confirmation_density: `0.0`

Runtime activation evidence:
- active_runtime_zones: `['locality', 'overlay_pipeline', 'topology']`

Diagnostics:
- wrapper_warning: `False`
- execution_depth: `deep`

### Query 3

- runtime_targets returned: `50 `
- runtime_neighbors returned: `0 `
- evidence_fusion ranked_files: `50 `
- engineering continuity chains: `0 `

Top-ranked file and score breakdown:
- top file: `install_workspace_integration.py`
- fused_score: `0.228`
- tier_scores: `{'tier_0_static': 0.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.38, 'tier_3_validation': 0.667}`
- tier_sources: `{'tier_0_static': [], 'tier_1_runtime': [], 'tier_2_continuity': ['continuity_hotspots', 'engineering_continuity_chain'], 'tier_3_validation': ['accepted_rejected_fix_validation', 'error_to_object_correlation']}`

Continuity evidence flags:
- ownership_locality: `PECS_ID:Qt.main_app_UI_rewrite`
- active_continuity size: `14`
- runtime_confirmation_density: `0.0`

Runtime activation evidence:
- active_runtime_zones: `['locality', 'overlay_pipeline', 'topology']`

Diagnostics:
- wrapper_warning: `False`
- execution_depth: `deep`

---

## Source evidence summary

- runtime authority contributions are present when `tier_1_runtime` is non-zero.
- continuity contributions are present when `tier_2_continuity` is non-zero or continuity-provenance values exist.
- validation contributions are present when `tier_3_validation` is non-zero.
- topology/ownership evidence is visible in the `tier_0_static` and `tier_2_continuity` provenance values.
