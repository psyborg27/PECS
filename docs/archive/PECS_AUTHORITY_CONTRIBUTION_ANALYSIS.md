# PECS Authority Contribution Analysis

## Query 1: Clipboard paste not working in Notes Module.

### Evidence fusion weight configuration

```json
{
  "tier_0_static": 0.2,
  "tier_1_runtime": 0.35,
  "tier_2_continuity": 0.25,
  "tier_3_validation": 0.2
}
```

### Top 10 ranked files and score contributions

#### Rank 1: `install_workspace_integration.py`

- fused_score: `0.228`
- tier_scores: `{'tier_0_static': 0.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.38, 'tier_3_validation': 0.667}`
- tier_sources: `{'tier_0_static': [], 'tier_1_runtime': [], 'tier_2_continuity': ['continuity_hotspots', 'engineering_continuity_chain'], 'tier_3_validation': ['accepted_rejected_fix_validation', 'error_to_object_correlation']}`
- provenance: `['accepted_rejected_fix_validation', 'continuity_hotspots', 'engineering_continuity_chain', 'error_to_object_correlation']`

Score contributions by evidence type:

- `tier_0_static`: `0.0` * `0.2` = `0.0`
- `tier_1_runtime`: `0.0` * `0.35` = `0.0`
- `tier_2_continuity`: `0.38` * `0.25` = `0.095`
- `tier_3_validation`: `0.667` * `0.2` = `0.133`

#### Rank 2: `workspace_bridge_cli.py`

- fused_score: `0.228`
- tier_scores: `{'tier_0_static': 0.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.38, 'tier_3_validation': 0.667}`
- tier_sources: `{'tier_0_static': [], 'tier_1_runtime': [], 'tier_2_continuity': ['continuity_hotspots', 'engineering_continuity_chain'], 'tier_3_validation': ['accepted_rejected_fix_validation', 'error_to_object_correlation']}`
- provenance: `['accepted_rejected_fix_validation', 'continuity_hotspots', 'engineering_continuity_chain', 'error_to_object_correlation']`

Score contributions by evidence type:

- `tier_0_static`: `0.0` * `0.2` = `0.0`
- `tier_1_runtime`: `0.0` * `0.35` = `0.0`
- `tier_2_continuity`: `0.38` * `0.25` = `0.095`
- `tier_3_validation`: `0.667` * `0.2` = `0.133`

#### Rank 3: `Qt/auto_toc_dialog_rewrite.py`

- fused_score: `0.212`
- tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.048, 'tier_3_validation': 0.0}`
- tier_sources: `{'tier_0_static': ['dependency_topology', 'filesystem_structure', 'import_topology'], 'tier_1_runtime': [], 'tier_2_continuity': ['canonical_authority_cluster'], 'tier_3_validation': []}`
- provenance: `['canonical_authority_cluster', 'dependency_topology', 'filesystem_structure', 'import_topology']`

Score contributions by evidence type:

- `tier_0_static`: `1.0` * `0.2` = `0.2`
- `tier_1_runtime`: `0.0` * `0.35` = `0.0`
- `tier_2_continuity`: `0.048` * `0.25` = `0.012`
- `tier_3_validation`: `0.0` * `0.2` = `0.0`

#### Rank 4: `EnhancedPDFViewer.py`

- fused_score: `0.2`
- tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}`
- tier_sources: `{'tier_0_static': ['dependency_topology', 'filesystem_structure', 'import_topology'], 'tier_1_runtime': [], 'tier_2_continuity': [], 'tier_3_validation': []}`
- provenance: `['dependency_topology', 'filesystem_structure', 'import_topology']`

Score contributions by evidence type:

- `tier_0_static`: `1.0` * `0.2` = `0.2`
- `tier_1_runtime`: `0.0` * `0.35` = `0.0`
- `tier_2_continuity`: `0.0` * `0.25` = `0.0`
- `tier_3_validation`: `0.0` * `0.2` = `0.0`

#### Rank 5: `Qt/__init__.py`

- fused_score: `0.2`
- tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}`
- tier_sources: `{'tier_0_static': ['dependency_topology', 'filesystem_structure', 'import_topology'], 'tier_1_runtime': [], 'tier_2_continuity': [], 'tier_3_validation': []}`
- provenance: `['dependency_topology', 'filesystem_structure', 'import_topology']`

Score contributions by evidence type:

- `tier_0_static`: `1.0` * `0.2` = `0.2`
- `tier_1_runtime`: `0.0` * `0.35` = `0.0`
- `tier_2_continuity`: `0.0` * `0.25` = `0.0`
- `tier_3_validation`: `0.0` * `0.2` = `0.0`

#### Rank 6: `Qt/auto_toc_dialog_rewrite_next.py`

- fused_score: `0.2`
- tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}`
- tier_sources: `{'tier_0_static': ['dependency_topology', 'filesystem_structure', 'import_topology'], 'tier_1_runtime': [], 'tier_2_continuity': [], 'tier_3_validation': []}`
- provenance: `['dependency_topology', 'filesystem_structure', 'import_topology']`

Score contributions by evidence type:

- `tier_0_static`: `1.0` * `0.2` = `0.2`
- `tier_1_runtime`: `0.0` * `0.35` = `0.0`
- `tier_2_continuity`: `0.0` * `0.25` = `0.0`
- `tier_3_validation`: `0.0` * `0.2` = `0.0`

#### Rank 7: `Qt/auto_toc_logic.py`

- fused_score: `0.2`
- tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}`
- tier_sources: `{'tier_0_static': ['dependency_topology', 'filesystem_structure', 'import_topology'], 'tier_1_runtime': [], 'tier_2_continuity': [], 'tier_3_validation': []}`
- provenance: `['dependency_topology', 'filesystem_structure', 'import_topology']`

Score contributions by evidence type:

- `tier_0_static`: `1.0` * `0.2` = `0.2`
- `tier_1_runtime`: `0.0` * `0.35` = `0.0`
- `tier_2_continuity`: `0.0` * `0.25` = `0.0`
- `tier_3_validation`: `0.0` * `0.2` = `0.0`

#### Rank 8: `Qt/bulk_ocr_mapping_dialog.py`

- fused_score: `0.2`
- tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}`
- tier_sources: `{'tier_0_static': ['dependency_topology', 'filesystem_structure', 'import_topology'], 'tier_1_runtime': [], 'tier_2_continuity': [], 'tier_3_validation': []}`
- provenance: `['dependency_topology', 'filesystem_structure', 'import_topology']`

Score contributions by evidence type:

- `tier_0_static`: `1.0` * `0.2` = `0.2`
- `tier_1_runtime`: `0.0` * `0.35` = `0.0`
- `tier_2_continuity`: `0.0` * `0.25` = `0.0`
- `tier_3_validation`: `0.0` * `0.2` = `0.0`

#### Rank 9: `Qt/bulk_page_mapping_dialog.py`

- fused_score: `0.2`
- tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}`
- tier_sources: `{'tier_0_static': ['dependency_topology', 'filesystem_structure', 'import_topology'], 'tier_1_runtime': [], 'tier_2_continuity': [], 'tier_3_validation': []}`
- provenance: `['dependency_topology', 'filesystem_structure', 'import_topology']`

Score contributions by evidence type:

- `tier_0_static`: `1.0` * `0.2` = `0.2`
- `tier_1_runtime`: `0.0` * `0.35` = `0.0`
- `tier_2_continuity`: `0.0` * `0.25` = `0.0`
- `tier_3_validation`: `0.0` * `0.2` = `0.0`

#### Rank 10: `Qt/clipboard_harness.py`

- fused_score: `0.2`
- tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}`
- tier_sources: `{'tier_0_static': ['dependency_topology', 'filesystem_structure', 'import_topology'], 'tier_1_runtime': [], 'tier_2_continuity': [], 'tier_3_validation': []}`
- provenance: `['dependency_topology', 'filesystem_structure', 'import_topology']`

Score contributions by evidence type:

- `tier_0_static`: `1.0` * `0.2` = `0.2`
- `tier_1_runtime`: `0.0` * `0.35` = `0.0`
- `tier_2_continuity`: `0.0` * `0.25` = `0.0`
- `tier_3_validation`: `0.0` * `0.2` = `0.0`

---

## Query 2: Cmd+A selects all notes instead of all text in active frame.

### Evidence fusion weight configuration

```json
{
  "tier_0_static": 0.2,
  "tier_1_runtime": 0.35,
  "tier_2_continuity": 0.25,
  "tier_3_validation": 0.2
}
```

### Top 10 ranked files and score contributions

#### Rank 1: `install_workspace_integration.py`

- fused_score: `0.228`
- tier_scores: `{'tier_0_static': 0.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.38, 'tier_3_validation': 0.667}`
- tier_sources: `{'tier_0_static': [], 'tier_1_runtime': [], 'tier_2_continuity': ['continuity_hotspots', 'engineering_continuity_chain'], 'tier_3_validation': ['accepted_rejected_fix_validation', 'error_to_object_correlation']}`
- provenance: `['accepted_rejected_fix_validation', 'continuity_hotspots', 'engineering_continuity_chain', 'error_to_object_correlation']`

Score contributions by evidence type:

- `tier_0_static`: `0.0` * `0.2` = `0.0`
- `tier_1_runtime`: `0.0` * `0.35` = `0.0`
- `tier_2_continuity`: `0.38` * `0.25` = `0.095`
- `tier_3_validation`: `0.667` * `0.2` = `0.133`

#### Rank 2: `workspace_bridge_cli.py`

- fused_score: `0.228`
- tier_scores: `{'tier_0_static': 0.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.38, 'tier_3_validation': 0.667}`
- tier_sources: `{'tier_0_static': [], 'tier_1_runtime': [], 'tier_2_continuity': ['continuity_hotspots', 'engineering_continuity_chain'], 'tier_3_validation': ['accepted_rejected_fix_validation', 'error_to_object_correlation']}`
- provenance: `['accepted_rejected_fix_validation', 'continuity_hotspots', 'engineering_continuity_chain', 'error_to_object_correlation']`

Score contributions by evidence type:

- `tier_0_static`: `0.0` * `0.2` = `0.0`
- `tier_1_runtime`: `0.0` * `0.35` = `0.0`
- `tier_2_continuity`: `0.38` * `0.25` = `0.095`
- `tier_3_validation`: `0.667` * `0.2` = `0.133`

#### Rank 3: `Qt/auto_toc_dialog_rewrite.py`

- fused_score: `0.212`
- tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.048, 'tier_3_validation': 0.0}`
- tier_sources: `{'tier_0_static': ['dependency_topology', 'filesystem_structure', 'import_topology'], 'tier_1_runtime': [], 'tier_2_continuity': ['canonical_authority_cluster'], 'tier_3_validation': []}`
- provenance: `['canonical_authority_cluster', 'dependency_topology', 'filesystem_structure', 'import_topology']`

Score contributions by evidence type:

- `tier_0_static`: `1.0` * `0.2` = `0.2`
- `tier_1_runtime`: `0.0` * `0.35` = `0.0`
- `tier_2_continuity`: `0.048` * `0.25` = `0.012`
- `tier_3_validation`: `0.0` * `0.2` = `0.0`

#### Rank 4: `EnhancedPDFViewer.py`

- fused_score: `0.2`
- tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}`
- tier_sources: `{'tier_0_static': ['dependency_topology', 'filesystem_structure', 'import_topology'], 'tier_1_runtime': [], 'tier_2_continuity': [], 'tier_3_validation': []}`
- provenance: `['dependency_topology', 'filesystem_structure', 'import_topology']`

Score contributions by evidence type:

- `tier_0_static`: `1.0` * `0.2` = `0.2`
- `tier_1_runtime`: `0.0` * `0.35` = `0.0`
- `tier_2_continuity`: `0.0` * `0.25` = `0.0`
- `tier_3_validation`: `0.0` * `0.2` = `0.0`

#### Rank 5: `Qt/__init__.py`

- fused_score: `0.2`
- tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}`
- tier_sources: `{'tier_0_static': ['dependency_topology', 'filesystem_structure', 'import_topology'], 'tier_1_runtime': [], 'tier_2_continuity': [], 'tier_3_validation': []}`
- provenance: `['dependency_topology', 'filesystem_structure', 'import_topology']`

Score contributions by evidence type:

- `tier_0_static`: `1.0` * `0.2` = `0.2`
- `tier_1_runtime`: `0.0` * `0.35` = `0.0`
- `tier_2_continuity`: `0.0` * `0.25` = `0.0`
- `tier_3_validation`: `0.0` * `0.2` = `0.0`

#### Rank 6: `Qt/auto_toc_dialog_rewrite_next.py`

- fused_score: `0.2`
- tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}`
- tier_sources: `{'tier_0_static': ['dependency_topology', 'filesystem_structure', 'import_topology'], 'tier_1_runtime': [], 'tier_2_continuity': [], 'tier_3_validation': []}`
- provenance: `['dependency_topology', 'filesystem_structure', 'import_topology']`

Score contributions by evidence type:

- `tier_0_static`: `1.0` * `0.2` = `0.2`
- `tier_1_runtime`: `0.0` * `0.35` = `0.0`
- `tier_2_continuity`: `0.0` * `0.25` = `0.0`
- `tier_3_validation`: `0.0` * `0.2` = `0.0`

#### Rank 7: `Qt/auto_toc_logic.py`

- fused_score: `0.2`
- tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}`
- tier_sources: `{'tier_0_static': ['dependency_topology', 'filesystem_structure', 'import_topology'], 'tier_1_runtime': [], 'tier_2_continuity': [], 'tier_3_validation': []}`
- provenance: `['dependency_topology', 'filesystem_structure', 'import_topology']`

Score contributions by evidence type:

- `tier_0_static`: `1.0` * `0.2` = `0.2`
- `tier_1_runtime`: `0.0` * `0.35` = `0.0`
- `tier_2_continuity`: `0.0` * `0.25` = `0.0`
- `tier_3_validation`: `0.0` * `0.2` = `0.0`

#### Rank 8: `Qt/bulk_ocr_mapping_dialog.py`

- fused_score: `0.2`
- tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}`
- tier_sources: `{'tier_0_static': ['dependency_topology', 'filesystem_structure', 'import_topology'], 'tier_1_runtime': [], 'tier_2_continuity': [], 'tier_3_validation': []}`
- provenance: `['dependency_topology', 'filesystem_structure', 'import_topology']`

Score contributions by evidence type:

- `tier_0_static`: `1.0` * `0.2` = `0.2`
- `tier_1_runtime`: `0.0` * `0.35` = `0.0`
- `tier_2_continuity`: `0.0` * `0.25` = `0.0`
- `tier_3_validation`: `0.0` * `0.2` = `0.0`

#### Rank 9: `Qt/bulk_page_mapping_dialog.py`

- fused_score: `0.2`
- tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}`
- tier_sources: `{'tier_0_static': ['dependency_topology', 'filesystem_structure', 'import_topology'], 'tier_1_runtime': [], 'tier_2_continuity': [], 'tier_3_validation': []}`
- provenance: `['dependency_topology', 'filesystem_structure', 'import_topology']`

Score contributions by evidence type:

- `tier_0_static`: `1.0` * `0.2` = `0.2`
- `tier_1_runtime`: `0.0` * `0.35` = `0.0`
- `tier_2_continuity`: `0.0` * `0.25` = `0.0`
- `tier_3_validation`: `0.0` * `0.2` = `0.0`

#### Rank 10: `Qt/clipboard_harness.py`

- fused_score: `0.2`
- tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}`
- tier_sources: `{'tier_0_static': ['dependency_topology', 'filesystem_structure', 'import_topology'], 'tier_1_runtime': [], 'tier_2_continuity': [], 'tier_3_validation': []}`
- provenance: `['dependency_topology', 'filesystem_structure', 'import_topology']`

Score contributions by evidence type:

- `tier_0_static`: `1.0` * `0.2` = `0.2`
- `tier_1_runtime`: `0.0` * `0.35` = `0.0`
- `tier_2_continuity`: `0.0` * `0.25` = `0.0`
- `tier_3_validation`: `0.0` * `0.2` = `0.0`

---

## Query 3: Notes Module modularization and ownership extraction.

### Evidence fusion weight configuration

```json
{
  "tier_0_static": 0.2,
  "tier_1_runtime": 0.35,
  "tier_2_continuity": 0.25,
  "tier_3_validation": 0.2
}
```

### Top 10 ranked files and score contributions

#### Rank 1: `install_workspace_integration.py`

- fused_score: `0.228`
- tier_scores: `{'tier_0_static': 0.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.38, 'tier_3_validation': 0.667}`
- tier_sources: `{'tier_0_static': [], 'tier_1_runtime': [], 'tier_2_continuity': ['continuity_hotspots', 'engineering_continuity_chain'], 'tier_3_validation': ['accepted_rejected_fix_validation', 'error_to_object_correlation']}`
- provenance: `['accepted_rejected_fix_validation', 'continuity_hotspots', 'engineering_continuity_chain', 'error_to_object_correlation']`

Score contributions by evidence type:

- `tier_0_static`: `0.0` * `0.2` = `0.0`
- `tier_1_runtime`: `0.0` * `0.35` = `0.0`
- `tier_2_continuity`: `0.38` * `0.25` = `0.095`
- `tier_3_validation`: `0.667` * `0.2` = `0.133`

#### Rank 2: `workspace_bridge_cli.py`

- fused_score: `0.228`
- tier_scores: `{'tier_0_static': 0.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.38, 'tier_3_validation': 0.667}`
- tier_sources: `{'tier_0_static': [], 'tier_1_runtime': [], 'tier_2_continuity': ['continuity_hotspots', 'engineering_continuity_chain'], 'tier_3_validation': ['accepted_rejected_fix_validation', 'error_to_object_correlation']}`
- provenance: `['accepted_rejected_fix_validation', 'continuity_hotspots', 'engineering_continuity_chain', 'error_to_object_correlation']`

Score contributions by evidence type:

- `tier_0_static`: `0.0` * `0.2` = `0.0`
- `tier_1_runtime`: `0.0` * `0.35` = `0.0`
- `tier_2_continuity`: `0.38` * `0.25` = `0.095`
- `tier_3_validation`: `0.667` * `0.2` = `0.133`

#### Rank 3: `Qt/auto_toc_dialog_rewrite.py`

- fused_score: `0.212`
- tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.048, 'tier_3_validation': 0.0}`
- tier_sources: `{'tier_0_static': ['dependency_topology', 'filesystem_structure', 'import_topology'], 'tier_1_runtime': [], 'tier_2_continuity': ['canonical_authority_cluster'], 'tier_3_validation': []}`
- provenance: `['canonical_authority_cluster', 'dependency_topology', 'filesystem_structure', 'import_topology']`

Score contributions by evidence type:

- `tier_0_static`: `1.0` * `0.2` = `0.2`
- `tier_1_runtime`: `0.0` * `0.35` = `0.0`
- `tier_2_continuity`: `0.048` * `0.25` = `0.012`
- `tier_3_validation`: `0.0` * `0.2` = `0.0`

#### Rank 4: `EnhancedPDFViewer.py`

- fused_score: `0.2`
- tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}`
- tier_sources: `{'tier_0_static': ['dependency_topology', 'filesystem_structure', 'import_topology'], 'tier_1_runtime': [], 'tier_2_continuity': [], 'tier_3_validation': []}`
- provenance: `['dependency_topology', 'filesystem_structure', 'import_topology']`

Score contributions by evidence type:

- `tier_0_static`: `1.0` * `0.2` = `0.2`
- `tier_1_runtime`: `0.0` * `0.35` = `0.0`
- `tier_2_continuity`: `0.0` * `0.25` = `0.0`
- `tier_3_validation`: `0.0` * `0.2` = `0.0`

#### Rank 5: `Qt/__init__.py`

- fused_score: `0.2`
- tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}`
- tier_sources: `{'tier_0_static': ['dependency_topology', 'filesystem_structure', 'import_topology'], 'tier_1_runtime': [], 'tier_2_continuity': [], 'tier_3_validation': []}`
- provenance: `['dependency_topology', 'filesystem_structure', 'import_topology']`

Score contributions by evidence type:

- `tier_0_static`: `1.0` * `0.2` = `0.2`
- `tier_1_runtime`: `0.0` * `0.35` = `0.0`
- `tier_2_continuity`: `0.0` * `0.25` = `0.0`
- `tier_3_validation`: `0.0` * `0.2` = `0.0`

#### Rank 6: `Qt/auto_toc_dialog_rewrite_next.py`

- fused_score: `0.2`
- tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}`
- tier_sources: `{'tier_0_static': ['dependency_topology', 'filesystem_structure', 'import_topology'], 'tier_1_runtime': [], 'tier_2_continuity': [], 'tier_3_validation': []}`
- provenance: `['dependency_topology', 'filesystem_structure', 'import_topology']`

Score contributions by evidence type:

- `tier_0_static`: `1.0` * `0.2` = `0.2`
- `tier_1_runtime`: `0.0` * `0.35` = `0.0`
- `tier_2_continuity`: `0.0` * `0.25` = `0.0`
- `tier_3_validation`: `0.0` * `0.2` = `0.0`

#### Rank 7: `Qt/auto_toc_logic.py`

- fused_score: `0.2`
- tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}`
- tier_sources: `{'tier_0_static': ['dependency_topology', 'filesystem_structure', 'import_topology'], 'tier_1_runtime': [], 'tier_2_continuity': [], 'tier_3_validation': []}`
- provenance: `['dependency_topology', 'filesystem_structure', 'import_topology']`

Score contributions by evidence type:

- `tier_0_static`: `1.0` * `0.2` = `0.2`
- `tier_1_runtime`: `0.0` * `0.35` = `0.0`
- `tier_2_continuity`: `0.0` * `0.25` = `0.0`
- `tier_3_validation`: `0.0` * `0.2` = `0.0`

#### Rank 8: `Qt/bulk_ocr_mapping_dialog.py`

- fused_score: `0.2`
- tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}`
- tier_sources: `{'tier_0_static': ['dependency_topology', 'filesystem_structure', 'import_topology'], 'tier_1_runtime': [], 'tier_2_continuity': [], 'tier_3_validation': []}`
- provenance: `['dependency_topology', 'filesystem_structure', 'import_topology']`

Score contributions by evidence type:

- `tier_0_static`: `1.0` * `0.2` = `0.2`
- `tier_1_runtime`: `0.0` * `0.35` = `0.0`
- `tier_2_continuity`: `0.0` * `0.25` = `0.0`
- `tier_3_validation`: `0.0` * `0.2` = `0.0`

#### Rank 9: `Qt/bulk_page_mapping_dialog.py`

- fused_score: `0.2`
- tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}`
- tier_sources: `{'tier_0_static': ['dependency_topology', 'filesystem_structure', 'import_topology'], 'tier_1_runtime': [], 'tier_2_continuity': [], 'tier_3_validation': []}`
- provenance: `['dependency_topology', 'filesystem_structure', 'import_topology']`

Score contributions by evidence type:

- `tier_0_static`: `1.0` * `0.2` = `0.2`
- `tier_1_runtime`: `0.0` * `0.35` = `0.0`
- `tier_2_continuity`: `0.0` * `0.25` = `0.0`
- `tier_3_validation`: `0.0` * `0.2` = `0.0`

#### Rank 10: `Qt/clipboard_harness.py`

- fused_score: `0.2`
- tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}`
- tier_sources: `{'tier_0_static': ['dependency_topology', 'filesystem_structure', 'import_topology'], 'tier_1_runtime': [], 'tier_2_continuity': [], 'tier_3_validation': []}`
- provenance: `['dependency_topology', 'filesystem_structure', 'import_topology']`

Score contributions by evidence type:

- `tier_0_static`: `1.0` * `0.2` = `0.2`
- `tier_1_runtime`: `0.0` * `0.35` = `0.0`
- `tier_2_continuity`: `0.0` * `0.25` = `0.0`
- `tier_3_validation`: `0.0` * `0.2` = `0.0`

---
