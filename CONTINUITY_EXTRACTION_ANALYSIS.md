# CONTINUITY_EXTRACTION_ANALYSIS

## Extraction sources

### Runtime topology extraction

- `WorkspaceContinuityDaemon._resolve_runtime_reachable_files()` follows imports from discovered entrypoints.
- `_populate_runtime_indexes()` extracts:
  - objects from file paths
  - runtime zones by path heuristics
  - QActions, signal-slot links, dialog launches, subprocess launches
- Runtime topology edges are written to `.pecs/topology_compact.json`.

### Runtime-locality payload extraction

- Each reachable file becomes a `pecs_id` entry in `runtime_locality_payload`.
- Anchors are generated from:
  - `pecs_id`
  - `pecs_id.class`
  - `pecs_id.method`
- Locality indices are registered in `self.runtime_session.locality_index`.

### Chat semantics extraction

- `_infer_active_focus_from_chat()` reads the last 30 entries from `.pecs/ai_chat_history.json`.
- It sets:
  - `current_issue` from the latest message
  - `active_topology_zone` via simple keyword matching
  - `dissatisfaction_signals` from known negative tokens
  - `rejected_edits` from reject-pattern tokens
  - `focus_terms` and `issue_terms` from regexed terms

### Runtime activation extraction

- `RuntimeActivationLogger` writes normalized runtime events to `.pecs/runtime_activation.jsonl`.
- `LocalityActivationEngine.infer_locality()` processes recent runtime events and builds:
  - activated objects
  - active runtime zones
  - activation confidence
  - observed edges
  - activation reasons and diagnostics

### Locality authority extraction

- `_refresh_locality_authority_state()` derives evidence from chat correlation fields, including:
  - `attempted_locality`
  - `runtime_authority_candidate`
  - `runtime_effect_confirmed`
  - topology mismatch suspicion
  - duplicate shadow suspicion
  - dead execution path suspicion
  - ownership ambiguity
  - wrapper-only mutation
- It writes `.pecs/continuity/locality_authority_state.json`.

## What is actually extracted

- `locality_index.json` from runtime-locality payload
- `topology_compact.json` from runtime topology edges
- `compact_bundle.json` from activation and continuity traversal
- `active_context.json` from compact bundle and runtime session state
- `session_context.json` from active objects and issue state
- `locality_authority_state.json` from chat-derived authority evidence
- `.pecs/continuity/*` exports from the bridge

## Continuity signal coverage

### Present signals

- runtime-local issue semantics via chat issue inference
- dissatisfaction via token patterns
- rejected edits via chat token patterns
- runtime activation evidence via `runtime_activation.jsonl`
- observed runtime edges for activation reinforcement
- active topology zone heuristics
- connectivity-based compact bundle selection

### Weak or missing signals

- successful stabilization signals are not explicitly extracted beyond persistence token count.
- rejected locality signals are only inferred from chat tokens and elapsed correlation fields.
- reinforcement deltas are limited to observed activation edges and not surfaced as explicit continuity weights in the compact bundle.
- object-group reinforcement is not explicit; only activated objects and active locality clusters are surfaced.
- topology adjacency reinforcement exists in `RuntimeEdgeReinforcement`, but must be driven by `observed_edges` from activation.

## Weakened continuity extraction points

- `compact_bundle` is rebuilt from activation seeds, active zone, and focus terms, but it does not directly consume `locality_authority_state.json`.
- The chat-derived authority evidence written to `locality_authority_state.json` is decoupled from the downstream export pipeline.
- `LocalityActivationEngine` only processes runtime events and chat issue terms; it does not ingest explicit success/validation outcomes from the broader chat corpus.

## Conclusion

The current implementation still performs runtime-local continuity extraction, but the extraction is narrow: it favors topology and activation evidence over richer chat-based authority signals. The main weakness is that authority evidence is generated, but not fully integrated into the continuity / projection export path.
