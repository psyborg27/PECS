# REMAINING_PROPAGATION_GAPS

## Root gap

A successful continuity refresh does not guarantee fresh core runtime projection artifacts.
The bridge export path is downstream from the runtime artifact generator and does not rebuild `topology_compact.json`, `compact_bundle.json`, or `active_context.json`.

## Exact missing propagation links

1. `ai_chat_history.json` ingestion is not a daemon-generated artifact.
   - It must be written by external chat append actions.
   - If Copilot/Continue activity is not actually appending to `.pecs/ai_chat_history.json`, the daemon never receives the signal.
   - This is the most likely source of stale `ai_chat_history.json`.

2. `compact_bundle.json` / `active_context.json` rebuild is only executed when:
   - topology is rebuilt
   - chat history update is detected
   - runtime activation events update

   If incoming activity is not materialized in one of those paths, projection regeneration is skipped.

3. `topology_compact.json` is rebuilt only on `.py` change or startup scan.
   - It is not refreshed on chat/history or activation alone.
   - If workspace activity changes topology without a corresponding `.py` modification visible to the watcher, the topology projection is stale.

4. `locality_authority_state.json` evidence is generated but not consumed.
   - `_refresh_locality_authority_state()` writes chat-derived authority evidence.
   - That evidence does not feed back into `_build_compact_bundle()` or `_build_active_context_payload()`.
   - This makes the extraction path narrower than intended.

5. Core artifact write suppression can hide timestamp updates.
   - `_write_json_path()` avoids rewriting identical JSON payloads.
   - If the computed state does not differ from the existing file, modification time stays unchanged.
   - This can make a fresh cycle appear stale if the content is semantically identical.

6. `bridge refresh` success is not sufficient freshness evidence.
   - `continuity_refresh_state.json` can show `success` even when upstream core artifacts were already stale.
   - The bridge does not validate that `topology_compact.json` / `compact_bundle.json` / `active_context.json` were regenerated as part of the refresh.

## Likely missing propagation path in practice

- Copilot/Continue activity → `.pecs/ai_chat_history.json` append may not happen
- or `.pecs/ai_chat_history.json` update may not lead to a meaningful focus change
- or `.pecs/runtime_activation.jsonl` updates may not be present or may not contain matching object IDs
- yet the daemon still writes `continuity_refresh_state.json` because refresh is triggered

The remaining bug is therefore a combination of:
- missing or out-of-band chat ingestion
- upstream core artifact regeneration not being explicitly enforced during bridge refresh
- extracted authority evidence not being integrated into compact/active context builds
