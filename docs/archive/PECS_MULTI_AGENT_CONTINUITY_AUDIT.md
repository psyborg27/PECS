# PECS Multi-Agent Continuity Audit

## Objective

Audit the current PECS continuity ingestion model for multi-agent scenarios and clarify whether the system should merge chat histories or preserve independent sources with later correlation.

This document is based on the current implementation in:
- `.pecs/tools/append_ai_chat_history.py`
- `scripts/export_workspace_continuity.py`
- `integrations/copilot_adapter.py`
- `integrations/continue_adapter.py`
- `integrations/pecs_lite_runtime_adapter.py`
- `PECS_QUERY_CONTRACT.md`
- `PECS_KIMI_CONTINUITY_INGESTION.md`

---

## Current Implementation

### Canonical ingestion path

- All chat continuity events are written to a single sink: `.pecs/ai_chat_history.json`.
- The ingestion utility is `.pecs/tools/append_ai_chat_history.py`.
- Each event is normalized with:
  - `workspace_root`
  - `workspace_id`
  - `continuity_namespace`
  - `source`
  - `event_type`
  - `message`
  - `ts`
  - `correlation`
  - `event_id`
- `source` is used to distinguish origin values such as `copilot`, `continue`, `kimi`, or `manual`.

### Continuity export path

- The daemon watches `.pecs/ai_chat_history.json` and triggers bridge refreshes.
- `scripts/export_workspace_continuity.py` reads `.pecs/ai_chat_history.json` and normalizes entries via `_normalize_chat_history_entries()`.
- The continuity export is written to `.pecs/continuity/engineering_continuity_state.json`.
- Exported chains are inferred from:
  - `source`
  - `event_type`
  - `message`
  - `correlation.{object_ids,error_ids,result_ids}`
  - `validation_outcome`
  - `runtime_effect_confirmed`

### Runtime query source preservation

- `integrations/copilot_adapter.py` calls `PECSLiteRuntimeAdapter.build_projection_safe()` with `query_source="copilot"`.
- `integrations/continue_adapter.py` does the same with `query_source="continue"`.
- The query contract supports `source`/`query_source` values of `copilot|continue|kimi|other`.

---

## What the current design preserves

### Provenance

- The core implementation preserves agent provenance as an explicit `source` field in chat events.
- Runtime projections also preserve the query source separately as `query_source`.

### Independent source metadata

- Each event keeps its own source identity.
- No code path currently collapses `source` into a generic unified origin before export.

### Correlation fields

- `append_ai_chat_history.py` normalizes correlation metadata into `correlation`.
- Supported fields include:
  - `object_ids`
  - `error_ids`
  - `result_ids`
  - `runtime_effect_confirmed`
  - `validation_outcome`
  - `accepted_fix`
  - `rejected_fix`
  - `regression_confirmed`
  - `runtime_confirmation_signal`
- These fields are preserved for later continuity analysis.

---

## Current multi-agent limitations and gaps

### No explicit multi-agent chain fusion

- Continuity export treats `.pecs/ai_chat_history.json` as a single flattened event stream.
- The export logic infers topics and locality from message text and generic correlation, not from agent-specific ownership models.
- There is no dedicated per-agent chain or per-source consensus/disagreement scoring.

### Limited explicit metadata beyond `source`

- Although documentation suggests `component` and richer `metadata`, the actual ingestion code normalizes only `source`, `event_type`, `message`, `correlation`, and timestamps.
- This means source provenance exists, but agent-specific context is limited.

### Source-independent inference

- `_infer_engineering_continuity_topic()` and `_infer_engineering_continuity_locality()` use message keywords, not explicit source or agent semantics.
- This increases risk that separate agents working on the same issue may be merged without explicit cross-agent correlation.

### No explicit divergence evidence aggregation

- The export pipeline can carry `validation_outcome` and runtime signal fields, but it does not currently compute multi-agent divergence metrics such as:
  - same issue different agent conclusions
  - conflicting `accepted_fix` vs `rejected_fix`
  - disagreement between `copilot` and `kimi`

---

## Should PECS merge all chats or preserve independent sources?

### Recommendation

PECS should preserve independent sources and correlate later, not merge all chats blindly.

### Why preserve independent sources?

- Provenance enables:
  - agent ownership and auditability
  - source-specific trust policies
  - later detection of divergence between agents
- Preserving `source` prevents loss of attribution when multiple agents contribute to the same workspace.
- A single sink with provenance metadata is the correct model for the current codebase.

### How to correlate later

- Use shared correlation keys such as `object_ids`, `error_ids`, and `result_ids`.
- Use `validation_outcome` and `runtime_effect_confirmed` to identify agreement or disagreement across events.
- Maintain event ordering by `ts` and use `source` as an additional axis.

---

## Does provenance improve authority, ownership, validation, and divergence evidence?

### Authority and ownership

- Yes. Provenance allows continuity consumers to know which agent produced each event.
- This is especially important when the same issue is touched by `copilot`, `continue`, and `kimi`.
- It enables future authority models to weight or trust one source differently from another.

### Validation evidence

- Preserving `validation_outcome` across sources supports cross-agent validation.
- When multiple agents report `accepted`, `rejected`, or `regression`, the system can surface stronger or weaker evidence.

### Divergence evidence

- Source metadata is essential to detect divergence.
- Without it, two agents could appear as a single blended history and divergence would be invisible.
- Explicit provenance makes it possible to say: "copilot reported accepted fix, kimi reported unresolved".

---

## Practical findings from the current implementation

- The current system already supports multi-agent provenance at a mechanical level via `source`.
- The actual event normalization pipeline does not yet enforce richer agent-specific fields such as `component` or `metadata`.
- The continuity export logic is intentionally downstream of the chat history sink and therefore can preserve provenance if source metadata is provided.
- Current exported chain inference is still coarse and relies on message content plus generic correlation fields rather than explicit per-agent ownership semantics.
- For the existing code, the safest strategy is to preserve `source` at ingestion and enhance later correlation rules, rather than flattening events before export.

---

## Conclusion

- Keep multi-agent events together in `.pecs/ai_chat_history.json` but preserve explicit `source` and correlation fields.
- Do not merge sources blindly; preserve independent provenance for later audit, divergence analysis, and authority weighting.
- The current codebase already implements the single-sink model with source metadata, but it should be extended with richer agent-specific fields and explicit divergence scoring.
- This audit recommends treating `.pecs/ai_chat_history.json` as canonical event storage and `engineering_continuity_state.json` as a derived, source-aware summary.
