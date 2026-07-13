# PECS Evidence Flow Audit

## Purpose

This audit traces Notes/Clipboard evidence through the PECS evidence pipeline in the Auto-TOC workspace and identifies where that evidence is lost.

## Evidence Flow Summary

Source evidence for Notes/Clipboard authority exists in Auto-TOC at:

- `.pecs/daemon_state.json` `changed_files`
- `.pecs/session_context.json` `active_paths`

The evidence is consumed by:

- `.pecs/bridge/export_workspace_continuity.py`
  - `_cluster_paths()`
  - `_build_locality_file_map()`
  - `_resolve_runtime_touched_files()`
  - `_collect_hotspots()`
  - `_build_engineering_continuity_state()`

Export artifacts are:

- `.pecs/continuity/locality_state.json`
- `.pecs/continuity/active_topology.json`
- `.pecs/continuity/engineering_continuity_state.json`

Retrieval consumes those artifacts through:

- `integrations/pecs_pro_query_adapter.py`
  - `runtime_target_candidates()`
  - `evidence_fusion_lookup()`
  - `engineering_continuity_lookup()`

---

## Example trace: `Qt/notes_module_v2.py`

### 1. Origin

Evidence originated from file-change/session state:

- `.pecs/daemon_state.json` changed_files includes `Qt/notes_module_v2.py`
- `.pecs/session_context.json` active_paths includes `Qt.notes_module_v2`

### 2. Was it collected by PECS?

Yes, evidence entered PECS as recent edit/session path state.

- `export_workspace_continuity()` reads both `daemon_state.json` and `session_context.json`.
- `recent_edit_clusters = _cluster_paths([*changed_files, *active_paths])`

This confirms that Notes/Clipboard evidence was collected in the continuity export stage.

### 3. Which artifact stored it?

Evidence survived into:

- `.pecs/continuity/locality_state.json`:
  - `active_locality_clusters` contains `Qt.clipboard_harness`
  - `ownership_hotspots` contains `PECS_ID:Qt.notes_module_v2`

Evidence did not survive into:

- `.pecs/continuity/engineering_continuity_state.json` for Notes-specific chains
- `.pecs/active_context.json` for Notes/Clipboard activated objects
- `.pecs/compact_bundle.json` (bundle is empty)

### 4. Which daemon process consumed it?

The continuity export daemon process consumed it via:

- `.pecs/bridge/export_workspace_continuity.py::export_workspace_continuity()`
- It reads `daemon_state.json` and `session_context.json` directly.

The evidence is not created by the runtime activation daemon path alone.

### 5. Which continuity stage processed it?

Processed stages:

- `recent_edit_clusters` formation in `_cluster_paths()`
- hotspot generation in `_collect_hotspots()`
- `ownership_hotspots` computed from topology edges in `topology_compact`

Not processed for Notes-specific engineering continuity because:

- `_build_engineering_continuity_state()` depends on `ai_chat_history.json`
- `ai_chat_history.json` contains zero Notes/Clipboard events

### 6. Did it survive export?

Partially.

Survived:

- `.pecs/continuity/locality_state.json.active_locality_clusters` includes a Notes/Clipboard cluster.
- `.pecs/continuity/locality_state.json.ownership_hotspots` includes `PECS_ID:Qt.notes_module_v2`.

Lost before export/surface:

- `.pecs/continuity/engineering_continuity_state.json` contains no Notes/Clipboard chain.
- `.pecs/active_context.json` contains no Notes/Clipboard activated objects.

### 7. Did it survive retrieval?

Yes, but only as weak static topology evidence.

Retrieval evidence in `PECSProQueryAdapter.runtime_target_candidates()`:

- `Qt/clipboard_harness.py`
- `Qt/notes_clipboard.py`
- `Qt/notes_module.py`
- `Qt/notes_module_v2.py`
- `Qt/session_clipboard_history.py`

However, all Notes/Clipboard retrieval entries are:

- `evidence = 'evidence_fusion'`
- `tier_1_runtime = 0.0`
- `tier_2_continuity = 0.0`
- `tier_3_validation = 0.0`

This indicates retrieval sees only static topology evidence, not runtime or historical authority.

---

## Loss point classification for Notes/Clipboard

A. Evidence never entered PECS: NO

- Evidence entered PECS via `daemon_state.json` and `session_context.json`.

B. Evidence entered ai_chat_history but was never promoted into continuity: NO

- `ai_chat_history.json` contains zero Notes/Clipboard entries.

C. Evidence entered continuity but was compacted or pruned: PARTIAL

- Notes/Clipboard evidence survived into `locality_state.json` at the hotspot/cluster level.
- It was pruned from `engineering_continuity_state.json` because the chat-history-driven chain builder had no Notes signals.

D. Evidence exists in continuity but retrieval ignores it: PARTIAL

- Retrieval does see Notes/Clipboard files, but only as static topology evidence.
- Runtime/continuity weights are absent.

E. Evidence exists but export artifacts do not surface it: PARTIAL

- `locality_state.json` surfaces it.
- `engineering_continuity_state.json` and `active_context.json` do not.

---

## Additional trace: `Qt/notes_clipboard.py`

### Source

- `daemon_state.json.changed_files` includes `Qt/notes_clipboard.py`
- `session_context.json.active_paths` includes `Qt.notes_clipboard`

### Artifact outcome

- `locality_state.json` does not show a Notes-specific continuity chain.
- `ownership_hotspots` contains only `PECS_ID:Qt.notes_module_v2`, not `Qt/notes_clipboard.py`.
- That means static file-change evidence entered the pipeline but was not converted into a stronger Notes/Clipboard authority anchor.

### Retrieval outcome

- `Qt/notes_clipboard.py` appears as an evidence fusion target, but only with static tier scores.

---

## Notes modularization and clipboard consolidation flow

Evidence exists at the file-change/session state boundary, but not in the chat-history-driven engineering continuity boundary.

Specifically:

- `session_context.active_paths` contains Notes and Clipboard object IDs.
- `active_context.json` contains no Notes/Clipboard activated objects.
- `engineering_continuity_state.json` has no Notes/Clipboard chain entries.

This means the flow is broken at the transition from session/runtime activity into historical continuity chains.

---

## Bottom line

For Notes/Clipboard authority, the evidence loss occurs in two places:

1. `ai_chat_history.json` does not contain Notes/Clipboard evidence, so no engineering continuity chains are generated.
2. `active_context.json` does not include Notes/Clipboard activation evidence, so runtime authority is not attached.

The surviving evidence is only low-authority static topology and ownership hotspot signal.
