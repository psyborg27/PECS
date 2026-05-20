# Evidence Pipeline Analysis

## Evidence sources in current PECS

### A. Import/dependency topology evidence
- `PECSProQueryAdapter.related_files_for()` uses `.pecs/topology_compact.json` edges.
- `PECSProQueryAdapter.entrypoint_chain_for()` walks entrypoint graph from compact topology.
- `ProjectionExporter._build_structured_runtime_targets()` includes `related_files` and `entrypoint_chain` fields.
- `export_workspace_continuity.py` computes ownership density from topology edges.

### B. Runtime behavioral evidence
- Runtime activation events are read from `.pecs/runtime_activation.jsonl`.
- `export_workspace_continuity.py` resolves `active_runtime_touched_files` and runtime validation metrics.
- `PECSProQueryAdapter.runtime_target_candidates()` uses `active_context` and touched files as runtime evidence.

### C. User-confirmed validation evidence
- `.pecs/ai_chat_history.json` is normalized by `append_ai_chat_history.py`.
- `export_workspace_continuity.py` uses chat history in `_build_engineering_continuity_state()`.
- The system extracts correlation fields such as `attempted_locality`, `runtime_effect_confirmed`, and `unresolved_persistence`.

### D. Error-to-object correlation evidence
- `append_ai_chat_history.py` normalizes correlation fields into the `correlation` payload.
- The continuity export fallback archaeology derives locality confidence from those correlation signals.

### E. Ownership continuity evidence
- `PECSProQueryAdapter.ownership_locality_lookup()` exposes top ownership files.
- `locality_state.json` includes `ownership_hotspots` and `continuity_hotspots`.
- `engineering_continuity_state.json` carries accepted/rejected locality chains.

### F. Historical implementation continuity
- `Export_workspace_continuity.py` builds continuity chains and unresolved tension summaries.
- `.continue` rules and `.github/copilot-instructions.md` preserve continuity principles over time.

## Implemented vs degraded evidence

Implemented and active:
- import topology evidence
- runtime behavioral evidence
- ownership continuity evidence
- historical continuity state
- structured chat correlation fields

Potentially degraded or underused:
- raw chat narrative is intentionally not used directly; only correlation fields are used.
- issue-based prompt heuristics may outweigh static evidence in symbol selection.

## Chat/history consolidation status

- Chat events are normalized by `append_ai_chat_history.py`.
- Full chat transcripts are not preserved as authoritative locality input.
- History enters the pipeline only as structured continuity/correlation evidence.

## Runtime validation feedback

- Runtime confirmation and evidence density are used in `export_workspace_continuity.py` to compute `runtime_validation`.
- Low confirmation density generates `unresolved_tensions`.
- This feedback is available to `PECS-LITE` through continuity artifacts.

## User-confirmed fixes and continuity confidence

- `append_ai_chat_history.py` supports explicit `correlation-json` fields for fix/outcome signals.
- These signals can strengthen locality confidence via `manual` continuity evidence.
- The current pipeline preserves this as engineered evidence, not raw conversation.
