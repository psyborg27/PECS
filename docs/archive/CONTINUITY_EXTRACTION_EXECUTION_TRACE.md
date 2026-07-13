# CONTINUITY_EXTRACTION_EXECUTION_TRACE

## Extraction workflow

### Runtime topology extraction

Extracted by `WorkspaceContinuityDaemon._rebuild_runtime_topology()`:
- discover entrypoints in the workspace
- resolve runtime-reachable Python files
- parse imports and runtime constructs
- build `self.runtime_topology_edges`
- build runtime locality payload for each reachable file

This writes:
- `.pecs/topology_compact.json`
- `.pecs/locality_index.json`

### Runtime-locality payload extraction

Within `_populate_runtime_indexes()`:
- each reachable file is normalized into `runtime_locality_payload`
- object anchors are registered in `self.runtime_session.locality_index`
- active object sets and execution indices are populated

This data is the source for:
- `compact_bundle.json`
- `active_context.json`

### Chat-derived authority extraction

Triggered by `WorkspaceContinuityDaemon._on_chat_history_update_unlocked()`:
- reads `.pecs/ai_chat_history.json`
- writes `chat_history_state.json`
- calls `_refresh_locality_authority_state(chat_data)`
- `_refresh_locality_authority_state()` derives evidence from chat correlation fields
- writes `.pecs/continuity/locality_authority_state.json`

Important note:
- extracted authority evidence is written, but downstream builders do not currently consume it directly
- `compact_bundle` and `active_context` are built from focus, activation, and topology, not from `locality_authority_state.json`

### Runtime activation extraction

Triggered by changes to `runtime_activation.jsonl`:
- `_process_changes_unlocked()` detects `self.runtime_activation_logger.event_path`
- `_on_activation_update()` infers locality from activation and rebuilds compact/context
- this path also triggers `_run_continuity_refresh()`

## Execution trace for each artifact

### `ai_chat_history.json`

- created/updated by external appenders
- watched by `WorkspaceContinuityDaemon._poll_chat_history()`
- on update triggers `_on_chat_history_update_unlocked()`

### `compact_bundle.json`

- rebuilt in `_rebuild_runtime_topology()`
- rebuilt on chat updates in `_on_chat_history_update_unlocked()`
- rebuilt on runtime activation updates in `_on_activation_update()`

### `active_context.json`

- rebuilt in `_rebuild_runtime_topology()`
- rebuilt on chat updates in `_on_chat_history_update_unlocked()`
- rebuilt on runtime activation updates in `_on_activation_update()`

### `topology_compact.json`

- rebuilt only in `_rebuild_runtime_topology()`
- NOT rebuilt on chat updates or runtime activation updates

## Extraction vs. export

- `WorkspaceContinuityDaemon` is responsible for extraction and core runtime artifact generation.
- `.pecs/bridge/export_workspace_continuity.py` is responsible only for reading artifacts and writing continuity export files.
- therefore, if extraction is incomplete, bridge refresh can still report `success` without fixing stale `compact_bundle.json`, `active_context.json`, or `topology_compact.json`.

## Additional findings

- `_write_json_path()` avoids rewriting identical canonical JSON. This preserves file stability but can hide timestamp changes when the computed state is unchanged.
- `_infer_active_focus_from_chat()` returns a default focus if chat history is empty or invalid, which can lead to compact/context rebuilds using generic defaults instead of fresh workspace issue signals.
- `locality_authority_state.json` is derived from chat evidence, but it is not incorporated back into the compact or active context build pipeline.
