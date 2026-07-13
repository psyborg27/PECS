# PECS Authority Fusion Final Report

## Summary

This audit confirms that current PECS authority generation for `engineering_continuity_state.json` is driven from `ai_chat_history.json` only.

The following artifacts are not directly ingested into authority generation:
- `.pecs/continuity/locality_state.json`
- `.pecs/active_context.json`
- runtime evidence artifacts (e.g. `runtime_activation.jsonl` sources)
- validation evidence from evidence fusion ranking
- ownership hotspot summaries

## Trace of `_build_engineering_continuity_state()`

The core authority construction is in `scripts/export_workspace_continuity.py`:
- `_build_engineering_continuity_state(workspace_root: Path)`
- reads only `workspace_root / ".pecs" / "ai_chat_history.json"`
- normalizes chat entries via `_normalize_chat_history_entries()`
- builds a `chains` dictionary from chat history entries alone
- derives authority and confidence using `ContinuityArchaeology` or fallback archaeology
- returns only a continuity state object built from chat entries and historical summary

No other artifact read is used in this function.

## Authority-generation code paths

### Primary path

- `ai_chat_history.json` → `_normalize_chat_history_entries()`
- each chat entry is turned into an engineering continuity chain
- chain fields are initialized from message text and chat correlation metadata
- evidence derivation is performed from chat correlation values such as:
  - `runtime_effect_confirmed`
  - `runtime_confirmation_signal`
  - `persistence_signal`
  - `unresolved_persistence`
  - `duplicate_shadow_suspicion`
  - `dead_execution_path_suspicion`
  - `topology_mismatch_suspicion`
  - `ownership_ambiguity`
  - `locality_authority_confidence`
  - `continuity_survivability_confidence`

### Derived confidence path

- `archaeology.derive_locality_authority_evidence(...)`
- `confidence_model.derive_locality_authority_confidence(...)`

These derive numeric authority/confidence values, but only from chat correlation inputs.

## Evidence sources used vs not used

### Used

- `ai_chat_history.json`
- chat entry `correlation` fields
- chat message text for `topic` and `accepted_locality`
- optionally runtime-confirmed flags if present in chat correlation

### Not directly used

- `.pecs/continuity/locality_state.json`
- `.pecs/active_context.json`
- `.pecs/topology_compact.json`
- `.pecs/locality_index.json`
- evidence fusion outputs from `PECSProQueryAdapter.evidence_fusion_lookup()`
- runtime activation artifacts / runtime event logs
- ownership hotspot summaries in locality state

## Intentionality assessment

### Was this behavior intentional?

The code structure strongly suggests yes. Authority construction is intentionally encapsulated in `_build_engineering_continuity_state()` and the function explicitly reads only chat history.

There is no fallback or alternate branch that merges locality or runtime artifacts into the continuity state.

### Is authority fusion incomplete?

Yes. The current implementation is incomplete relative to the intended evidence surface described elsewhere in repository artifacts.

There are multiple evidence artifacts available (`locality_state`, `active_context`, runtime validation, ownership hotspots) that are not incorporated into authority state generation.

### Was authority fusion planned but never implemented?

Yes. Evidence for planning but missing implementation includes:
- existence of locality and continuity artifact exporters
- explicit collection of runtime and ownership evidence in `.pecs/continuity/locality_state.json`
- evidence fusion ranking in `PECSProQueryAdapter` that uses those artifacts
- absence of any bridging code that feeds those artifacts back into `_build_engineering_continuity_state()`

That pattern indicates the design intended broader evidence fusion, but current authority generation remains chat-only.

### Was authority fusion disabled?

No. There is no code path showing a disabled or feature-flagged authority fusion layer.

The current state is not a disabled feature; it is a missing integration.

### Was authority fusion present but not exported?

No. If authority fusion from locality/runtime evidence existed, it would be visible in `engineering_continuity_state.json` chains or in the exported continuity hydration reports.

The exported continuity state contains only talk-derived chains and any evidence encoded into chat correlation.

## Behavior classification

### Current PECS authority behavior

`Chat -> Authority`

The evidence chain is:
- chat history entries are read
- chat correlation fields are interpreted
- authority/confidence is derived from those fields
- `engineering_continuity_state.json` is written from this derived state

While PECS retrieval and runtime ranking may use locality and evidence fusion artifacts, the canonical authority payload is built from chat history only.

## Supporting evidence from code

### Direct chat-only source

- `_build_engineering_continuity_state()` reads `ai_chat_history.json`
- it does not read `.pecs/continuity/locality_state.json`
- it does not read `.pecs/active_context.json`
- it does not read `runtime_activation.jsonl`

### Evidence fusion is separate

- `PECSProQueryAdapter.evidence_fusion_lookup()` uses `active_context`, `locality_state`, and `topology_compact`
- but that function is not part of authority generation for `engineering_continuity_state.json`

### Ownership hotspot evidence is not fused

- locality ownership hotspots are collected into `locality_state.json`
- those hotspot IDs are not referenced by `_build_engineering_continuity_state()`

## Conclusion

- Authority generation is currently intentional as a chat-driven pipeline.
- Authority fusion is incomplete with respect to broader runtime/locality evidence.
- The design appears to have planned evidence fusion, but the integration was not implemented in the authority export path.
- There is no evidence that the missing fusion is merely disabled.
- There is no evidence that unexported authority fusion exists.

PECS is currently: **Chat -> Authority**.
