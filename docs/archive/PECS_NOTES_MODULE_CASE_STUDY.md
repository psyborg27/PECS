# PECS Notes Module Case Study

## Notes Module Case Study

This case study extracts notes-related file evidence from live retrieval output. All values are from actual PECS projections.

### Query 1: Clipboard paste not working in Notes Module.

- ownership_locality: `PECS_ID:Qt.main_app_UI_rewrite`
- top runtime neighbor count: `0`
- notes-related runtime targets:
  - `Qt/clipboard_harness.py` tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}` provenance: `['dependency_topology', 'filesystem_structure', 'import_topology']`
  - `Qt/notes_clipboard.py` tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}` provenance: `['dependency_topology', 'filesystem_structure', 'import_topology']`
  - `Qt/notes_module.py` tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}` provenance: `['dependency_topology', 'filesystem_structure', 'import_topology']`
  - `Qt/notes_module_v2.py` tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}` provenance: `['dependency_topology', 'filesystem_structure', 'import_topology']`
  - `Qt/session_clipboard_history.py` tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}` provenance: `['dependency_topology', 'filesystem_structure', 'import_topology']`
- notes-related evidence fusion files:
  - `Qt/clipboard_harness.py` fused_score: `0.2` tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}` tier_sources: `{'tier_0_static': ['dependency_topology', 'filesystem_structure', 'import_topology'], 'tier_1_runtime': [], 'tier_2_continuity': [], 'tier_3_validation': []}`
  - `Qt/notes_clipboard.py` fused_score: `0.2` tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}` tier_sources: `{'tier_0_static': ['dependency_topology', 'filesystem_structure', 'import_topology'], 'tier_1_runtime': [], 'tier_2_continuity': [], 'tier_3_validation': []}`
  - `Qt/notes_module.py` fused_score: `0.2` tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}` tier_sources: `{'tier_0_static': ['dependency_topology', 'filesystem_structure', 'import_topology'], 'tier_1_runtime': [], 'tier_2_continuity': [], 'tier_3_validation': []}`
  - `Qt/notes_module_v2.py` fused_score: `0.2` tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}` tier_sources: `{'tier_0_static': ['dependency_topology', 'filesystem_structure', 'import_topology'], 'tier_1_runtime': [], 'tier_2_continuity': [], 'tier_3_validation': []}`
  - `Qt/session_clipboard_history.py` fused_score: `0.2` tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}` tier_sources: `{'tier_0_static': ['dependency_topology', 'filesystem_structure', 'import_topology'], 'tier_1_runtime': [], 'tier_2_continuity': [], 'tier_3_validation': []}`

---

### Query 2: Cmd+A selects all notes instead of all text in active frame.

- ownership_locality: `PECS_ID:Qt.main_app_UI_rewrite`
- top runtime neighbor count: `0`
- notes-related runtime targets:
  - `Qt/clipboard_harness.py` tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}` provenance: `['dependency_topology', 'filesystem_structure', 'import_topology']`
  - `Qt/notes_clipboard.py` tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}` provenance: `['dependency_topology', 'filesystem_structure', 'import_topology']`
  - `Qt/notes_module.py` tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}` provenance: `['dependency_topology', 'filesystem_structure', 'import_topology']`
  - `Qt/notes_module_v2.py` tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}` provenance: `['dependency_topology', 'filesystem_structure', 'import_topology']`
  - `Qt/session_clipboard_history.py` tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}` provenance: `['dependency_topology', 'filesystem_structure', 'import_topology']`
- notes-related evidence fusion files:
  - `Qt/clipboard_harness.py` fused_score: `0.2` tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}` tier_sources: `{'tier_0_static': ['dependency_topology', 'filesystem_structure', 'import_topology'], 'tier_1_runtime': [], 'tier_2_continuity': [], 'tier_3_validation': []}`
  - `Qt/notes_clipboard.py` fused_score: `0.2` tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}` tier_sources: `{'tier_0_static': ['dependency_topology', 'filesystem_structure', 'import_topology'], 'tier_1_runtime': [], 'tier_2_continuity': [], 'tier_3_validation': []}`
  - `Qt/notes_module.py` fused_score: `0.2` tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}` tier_sources: `{'tier_0_static': ['dependency_topology', 'filesystem_structure', 'import_topology'], 'tier_1_runtime': [], 'tier_2_continuity': [], 'tier_3_validation': []}`
  - `Qt/notes_module_v2.py` fused_score: `0.2` tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}` tier_sources: `{'tier_0_static': ['dependency_topology', 'filesystem_structure', 'import_topology'], 'tier_1_runtime': [], 'tier_2_continuity': [], 'tier_3_validation': []}`
  - `Qt/session_clipboard_history.py` fused_score: `0.2` tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}` tier_sources: `{'tier_0_static': ['dependency_topology', 'filesystem_structure', 'import_topology'], 'tier_1_runtime': [], 'tier_2_continuity': [], 'tier_3_validation': []}`

---

### Query 3: Notes Module modularization and ownership extraction.

- ownership_locality: `PECS_ID:Qt.main_app_UI_rewrite`
- top runtime neighbor count: `0`
- notes-related runtime targets:
  - `Qt/clipboard_harness.py` tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}` provenance: `['dependency_topology', 'filesystem_structure', 'import_topology']`
  - `Qt/notes_clipboard.py` tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}` provenance: `['dependency_topology', 'filesystem_structure', 'import_topology']`
  - `Qt/notes_module.py` tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}` provenance: `['dependency_topology', 'filesystem_structure', 'import_topology']`
  - `Qt/notes_module_v2.py` tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}` provenance: `['dependency_topology', 'filesystem_structure', 'import_topology']`
  - `Qt/session_clipboard_history.py` tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}` provenance: `['dependency_topology', 'filesystem_structure', 'import_topology']`
- notes-related evidence fusion files:
  - `Qt/clipboard_harness.py` fused_score: `0.2` tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}` tier_sources: `{'tier_0_static': ['dependency_topology', 'filesystem_structure', 'import_topology'], 'tier_1_runtime': [], 'tier_2_continuity': [], 'tier_3_validation': []}`
  - `Qt/notes_clipboard.py` fused_score: `0.2` tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}` tier_sources: `{'tier_0_static': ['dependency_topology', 'filesystem_structure', 'import_topology'], 'tier_1_runtime': [], 'tier_2_continuity': [], 'tier_3_validation': []}`
  - `Qt/notes_module.py` fused_score: `0.2` tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}` tier_sources: `{'tier_0_static': ['dependency_topology', 'filesystem_structure', 'import_topology'], 'tier_1_runtime': [], 'tier_2_continuity': [], 'tier_3_validation': []}`
  - `Qt/notes_module_v2.py` fused_score: `0.2` tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}` tier_sources: `{'tier_0_static': ['dependency_topology', 'filesystem_structure', 'import_topology'], 'tier_1_runtime': [], 'tier_2_continuity': [], 'tier_3_validation': []}`
  - `Qt/session_clipboard_history.py` fused_score: `0.2` tier_scores: `{'tier_0_static': 1.0, 'tier_1_runtime': 0.0, 'tier_2_continuity': 0.0, 'tier_3_validation': 0.0}` tier_sources: `{'tier_0_static': ['dependency_topology', 'filesystem_structure', 'import_topology'], 'tier_1_runtime': [], 'tier_2_continuity': [], 'tier_3_validation': []}`

---
