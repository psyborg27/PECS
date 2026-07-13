# PECS Evidence Loss Root Cause

This document identifies exactly where Notes/Clipboard authority evidence is lost in the Auto-TOC PECS pipeline.

## Root cause summary

For Notes/Clipboard authority, the evidence loss occurs at the boundary between locality-state export and engineering-continuity promotion.

### Evidence that is present

- `.pecs/daemon_state.json.changed_files` contains `Qt/notes_clipboard.py` and `Qt/notes_module_v2.py`.
- `.pecs/session_context.json.active_paths` contains `Qt.clipboard_harness`, `Qt.notes_clipboard`, `Qt.notes_module`, `Qt.notes_module_v2`, and `Qt.session_clipboard_history`.
- `.pecs/continuity/locality_state.json` contains:
  - `active_locality_clusters` with `Qt.clipboard_harness`
  - `ownership_hotspots` with `PECS_ID:Qt.notes_module_v2`

This proves Notes/Clipboard evidence successfully enters the PECS pipeline.

### Evidence that is missing

- `.pecs/ai_chat_history.json` contains zero Notes/Clipboard-related entries.
- `.pecs/continuity/engineering_continuity_state.json` contains no Notes/Clipboard chains.
- `.pecs/active_context.json` contains zero Notes/Clipboard activated objects.
- `.pecs/compact_bundle.json` is empty, so Notes/Clipboard bundle evidence is absent.

These missing items prove the evidence is not promoted into higher-authority continuity structures.

## Exact loss points

### Loss point 1: Chat-history continuity promotion

Code path:

- `.pecs/bridge/export_workspace_continuity.py::_build_engineering_continuity_state()`
- `_normalize_chat_history_entries()` reads `.pecs/ai_chat_history.json`
- It infers `topic` and `accepted_locality` from message text
- It builds chains only from chat entries

Observation:

- Auto-TOC `ai_chat_history.json` has no Notes/Clipboard-specific messages.
- Therefore no Notes/Clipboard continuity chains are generated.

Result:

- Notes/Clipboard evidence is not promoted into `engineering_continuity_state.json`.

### Loss point 2: Active runtime context attachment

Code path:

- `integrations/pecs_pro_query_adapter.py` loads `.pecs/active_context.json`
- `runtime_target_candidates()` and `evidence_fusion_lookup()` use `active_context` activation data

Observation:

- Auto-TOC `active_context.json` contains no Notes/Clipboard activated objects.
- `active_runtime_touched_files` is empty in `locality_state.json`.

Result:

- Notes/Clipboard evidence cannot become runtime authority evidence.

### Loss point 3: Continuity export vs retrieval mismatch

Code path:

- `.pecs/bridge/export_workspace_continuity.py::_collect_hotspots()` writes `continuity_hotspots`
- `integrations/pecs_pro_query_adapter.py::evidence_fusion_lookup()` uses the resulting `active_context`, `locality_state`, and `compact_bundle`

Observation:

- Notes/Clipboard files appear in `ownership_hotspots` and `active_locality_clusters`.
- Retrieval sees these files, but only with static evidence scores.

Result:

- Evidence survives export, but retrieval downgrades it to topology-only evidence.

## Evidence flow failure categories

Based on actual code and artifacts, the loss is best classified as:

- C. Evidence entered continuity and was partially pruned from high-authority structures.
- D. Evidence exists in continuity state but retrieval only uses it as static evidence.
- E. Evidence exists in export artifacts, but not in `engineering_continuity_state.json` or `active_context.json`.

## Why this happens

### Notes/Clipboard work enters only session/daemon state

- `daemon_state.json.changed_files` and `session_context.json.active_paths` contain Notes/Clipboard evidence.

### But continuity promotion depends on chat history

- `engineering_continuity_state.json` is built from AI/chat history, not from file changes or active paths.
- Because `ai_chat_history.json` contains no Notes/Clipboard evidence, promotion fails.

### Runtime authority is absent because active runtime activations are absent

- `active_context.json` lacks Notes/Clipboard activations.
- `locality_state.json.active_runtime_touched_files` is empty.
- Thus runtime authority cannot support Notes/Clipboard retrieval.

## Concrete tracing conclusion

For Notes/Clipboard authority evidence:

- Evidence entered PECS: yes.
- Evidence survived basic continuity export: yes, as clusters/hotspots.
- Evidence failed to reach authoritative continuity payloads: yes.
- Evidence was retrieved only as static topology: yes.

This is the exact evidence-loss root cause.
