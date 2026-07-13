# PECS Notes/Clipboard Authority Trace

This file traces a real Notes/Clipboard example end-to-end through PECS evidence collection, continuity processing, export, and retrieval.

## Example 1: `Qt/notes_module_v2.py`

### 1. Origin

Evidence originated from Auto-TOC runtime/session state:

- `.pecs/daemon_state.json.changed_files` contains `Qt/notes_module_v2.py`
- `.pecs/session_context.json.active_paths` contains `Qt.notes_module_v2`

This is the primary place where Notes/Clipboard edit history enters PECS.

### 2. PECS collection

The continuity export code collects it via:

- `.pecs/bridge/export_workspace_continuity.py::export_workspace_continuity()`
- `changed_files = daemon_state.get('changed_files', [])`
- `active_paths = session_context.get('active_paths', [])`
- `recent_edit_clusters = _cluster_paths([*changed_files, *active_paths])`

Therefore, Notes/Clipboard evidence was successfully collected.

### 3. Artifact storage

Evidence stored in export artifacts:

- `.pecs/continuity/locality_state.json.active_locality_clusters` includes `{'cluster': 'Qt.clipboard_harness', 'count': 1}`
- `.pecs/continuity/locality_state.json.ownership_hotspots` includes `{'edge_count': 34, 'id': 'PECS_ID:Qt.notes_module_v2'}`

Evidence did not store as:

- `.pecs/continuity/engineering_continuity_state.json` Notes/Clipboard chain
- `.pecs/active_context.json` Notes/Clipboard active objects
- `.pecs/compact_bundle.json` Notes/Clipboard bundle entries

### 4. Daemon process consumption

The export daemon consumed the evidence in:

- `.pecs/bridge/export_workspace_continuity.py` (bridge export script)
- It read `daemon_state.json` and `session_context.json`.
- It built `recent_edit_clusters` and `ownership_hotspots` from those values.

### 5. Continuity stage processing

Processed stages:

- Data ingestion from session/daemon files
- Cluster creation via `_cluster_paths()`
- Hotspot scoring via `_collect_hotspots()`

Not processed stages:

- `engineering_continuity_state` chain creation for Notes/Clipboard because `ai_chat_history.json` contains no related entries.

### 6. Export survival

Survived as:

- `locality_state.json` hotspot and cluster metadata

Did not survive as:

- `engineering_continuity_state.json` continuity chain
- `active_context.json` runtime activation for Notes/Clipboard

### 7. Retrieval survival

`PECSProQueryAdapter.runtime_target_candidates()` returns Notes/Clipboard files including `Qt/notes_module_v2.py`.

However, the retrieved evidence is weak:

- `evidence = 'evidence_fusion'`
- `tier_1_runtime = 0.0`
- `tier_2_continuity = 0.0`
- `tier_3_validation = 0.0`

That means retrieval recognizes a Notes/Clipboard file, but only because of static topology, not because of active runtime or continuity authority.

---

## Example 2: `Qt/notes_clipboard.py`

### 1. Origin

Evidence originated from:

- `.pecs/daemon_state.json.changed_files` contains `Qt/notes_clipboard.py`
- `.pecs/session_context.json.active_paths` contains `Qt.notes_clipboard`

### 2. Collection

Collected by `export_workspace_continuity()` through the same session/daemon ingestion path.

### 3. Artifact storage

Evidence appears indirectly as part of `active_locality_clusters` and `ownership_hotspots`.

However:

- `ownership_hotspots` lists only `PECS_ID:Qt.notes_module_v2`, not `Qt/notes_clipboard.py`.
- `canonical_authority_clusters` is unrelated and contains only `Qt/auto_toc_dialog_rewrite.py`.

### 4. Daemon consumption

Same as Example 1: `_cluster_paths()` and `_collect_hotspots()`.

### 5. Continuity processing

Notes/Clipboard evidence is present in cluster/hotspot formation, but is not promoted into top-level engineering continuity.

### 6. Export survival

Survives in `locality_state.json` as weak locality cluster/hotspot evidence.

Fails to survive as:

- `engineering_continuity_state.json`
- `active_context.json`

### 7. Retrieval survival

`PECSProQueryAdapter.runtime_target_candidates()` returns `Qt/notes_clipboard.py` with only static evidence.

---

## Example 3: `Qt/clipboard_harness.py`

### 1. Origin

Evidence originates in:

- `.pecs/session_context.json.active_paths` contains `Qt.clipboard_harness`

No explicit changed file entry is required because active path state is sufficient.

### 2. Collection

Collected in `recent_edit_clusters` via the same export path.

### 3. Artifact storage

It is visible in `locality_state.json.active_locality_clusters`.

### 4. Daemon consumption

Same export daemon code path as previous examples.

### 5. Continuity processing

No `engineering_continuity_state` chain or runtime activation in `active_context.json` is built for it.

### 6. Export survival

Survives only as locality cluster evidence.

### 7. Retrieval survival

It appears in `runtime_target_candidates()` with static evidence only.

---

## Core evidence loss location

The exact loss is not at the file-change/session ingestion layer. It is at the boundary between two continuity stages:

1. Evidence is collected from `daemon_state.json` and `session_context.json`.
2. It is exported into `locality_state.json` cluster/hotspot fields.
3. It is not promoted into:
   - `engineering_continuity_state.json`
   - `active_context.json`
   - `compact_bundle.json`
4. Retrieval uses it only as static topology evidence.

This identifies the loss as: evidence is collected and exported, but not promoted into higher-authority continuity payloads.

---

## Specific code paths where loss occurs

### Collected evidence path

- `.pecs/bridge/export_workspace_continuity.py::export_workspace_continuity()`
- `_cluster_paths()`
- `_collect_hotspots()`
- `_build_validation_metrics()`

### Lost promotion path

- `_build_engineering_continuity_state()` relies on `ai_chat_history.json`, which contains no Notes/Clipboard evidence.
- `active_context.json` is generated from runtime activation/compact bundle, neither of which has Notes/Clipboard runtime activation evidence.

### Retrieval path

- `integrations/pecs_pro_query_adapter.py::runtime_target_candidates()`
- `integrations/pecs_pro_query_adapter.py::evidence_fusion_lookup()`

Notes/Clipboard evidence only contributes via static topology and import/dependency scoring.

---

## Evidence loss classification

For Notes/Clipboard:

- A. Evidence never entered PECS: NO
- B. Evidence entered ai_chat_history but was never promoted: NOT APPLICABLE (zero Notes/Clipboard history entries)
- C. Evidence entered continuity but was compacted/pruned: PARTIAL
- D. Evidence exists in continuity but retrieval ignores it: PARTIAL
- E. Evidence exists but export artifacts do not surface it: PARTIAL

The primary root cause is that Notes/Clipboard evidence is not present in the chat-history-driven engineering continuity stage, so it never reaches high-authority continuity payloads.
