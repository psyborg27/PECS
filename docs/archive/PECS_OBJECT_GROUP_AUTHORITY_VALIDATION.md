# PECS Object Group Authority Validation

## Objective

Validate whether Object Groups should be the primary authority unit instead of Engineering Episodes for PECS.

Assumptions:
- `locality_index.json` becomes the canonical object registry
- `ai_chat_history.json` remains the canonical event sink
- `object_ids` become the primary linkage mechanism

This document uses the actual PECS architecture and implementation evidence in the current workspace.

---

## 1. Object Group versus Episode as Primary Authority Unit

### Actual architecture evidence

- `.pecs/locality_index.json` already contains canonical object metadata including `file`, `class`, and `method` fields.
- `append_ai_chat_history.py` supports capturing `object_ids` in event correlation.
- `scripts/export_workspace_continuity.py` consumes `object_ids`, `validation_outcome`, and `runtime_effect_confirmed`.
- There is no current evidence of episode IDs in stored event history or continuity exports.

### Evaluation

- Episode authority would require a new primary identity layer (`episode_id`) that is not currently present in stored artifacts.
- Object Group authority can reuse existing object registry semantics and extend current event correlation fields.
- Because current architecture already supports object IDs and object metadata, Object Groups are a more natural primary authority unit.

### Conclusion

**Object Group should be the primary authority unit.**

Rationale: the existing code and artifact model already align with object-based evidence, while episode-based authority would require introducing a new primary key layer that is absent from current storage.

---

## 2. Long-Term Modularization Continuity

### Object Groups

- Object Groups map directly to code artifacts in `locality_index.json`.
- They can persist through modularization because object IDs remain attached to file/class/function entities.
- For Notes module modularization history, object groups can record evidence for the same `Notes` object IDs across refactors.

### Episodes

- Episodes represent temporal or intent boundaries.
- They do not inherently preserve artifact modularization history.
- If `Notes` code migrates or splits, episode boundaries do not provide stable artifact continuity.

### Verdict

Object Groups better support long-term modularization continuity.

---

## 3. Cross-Conversation Continuity

### Object Groups

- Object Groups use shared `object_ids` to link events across conversations.
- The canonical event sink can record repeating object IDs for separate sessions.
- Continuity can be recovered by object references even when episode context is absent.

### Episodes

- Cross-conversation continuity requires propagation of the same `episode_id` across sessions.
- The current architecture has no episode propagation mechanism in stored events.

### Verdict

Object Groups are stronger for cross-conversation continuity given the current PECS architecture.

---

## 4. Cross-Agent Continuity

### Object Groups

- The event sink already stores `source` values such as `copilot`, `continue`, `kimi`, and `manual`.
- If events carry shared `object_ids`, cross-agent evidence can aggregate on the same object groups.
- This supports independent agent contributions to the same code artifact.

### Episodes

- Cross-agent continuity over episodes requires agents to share episode context and IDs.
- That is brittle in a multi-agent environment unless a robust episode-sharing protocol is built.

### Verdict

Object Groups better enable cross-agent continuity in the current object-centric architecture.

---

## 5. Ownership Authority

### Object Groups

- Ownership can attach to artifacts referenced by object IDs.
- `source_counts` in continuity chains and `object_error_links` can be used to infer object-level ownership strength.
- Existing architecture already has the machinery to combine source metadata with object linkage.

### Episodes

- Ownership on episodes is ownership of an intent or workflow, not a code artifact.
- It does not naturally express who owns a specific file/class/function.

### Verdict

Object Groups are the better basis for ownership authority.

---

## 6. Runtime Authority

### Object Groups

- Runtime validation signals such as `runtime_effect_confirmed` can be attached to `object_ids` in event correlation.
- This lets runtime authority accumulate against concrete code objects.

### Episodes

- Runtime authority on episodes is broader and less precise.
- It can report that a workflow executed, but not which object received the runtime validation.

### Verdict

Object Groups provide stronger runtime authority support.

---

## 7. Validation Authority

### Object Groups

- Validation outcomes (`accepted`, `rejected`, `regression`, `unresolved`) can be counted per object group.
- This allows the system to track object-specific validation history over time.

### Episodes

- Validation authority for episodes captures the result of a particular instructional interaction, not object-specific validation history.
- It is useful for session-level correctness, but not for persistent object trust.

### Verdict

Object Groups better support validation authority for artifact-level evidence.

---

## 8. Historical Authority

### Object Groups

- Historical authority is strongest when attached to persistent artifact identities.
- `locality_index.json` provides a stable registry for objects across time.
- Historical evidence can accumulate on object groups even if episode context disappears.

### Episodes

- Historical authority on episodes is inherently bounded by episode lifespan.
- It requires replaying or linking episodes to derive long-term artifact history.

### Verdict

Object Groups are better aligned with historical authority.

---

## Use Case Evaluation

### Clipboard Extraction History

- Clipboard extraction is a code artifact workflow tied to specific module objects.
- Object Groups can accumulate evidence on clipboard-related object IDs.
- Episodes would only capture the temporal extraction episode, not the persistent clipboard object.

### Notes Module Modularization History

- Modularization requires tracking the Notes module across refactorings.
- Object Groups can follow object IDs through file/class/function boundaries.
- Episodes are insufficient to capture modularization lineage directly.

### OCR Stabilization History

- OCR stabilization is a behavior applied to OCR-related objects and code paths.
- Object Groups can link runtime validation and acceptance events to OCR object IDs.
- Episode authority would capture the stabilization attempt but not the underlying OCR artifact history.

### Verdict

For all three use cases, Object Groups better support the required authority history.

---

## Most Important Question

### Should authority accumulate primarily on:

- A. Episode IDs
- B. Object Groups

### Decision

**B. Object Groups**

### Justification

- Actual PECS architecture already contains object registry metadata in `locality_index.json`.
- The event sink `ai_chat_history.json` already supports `object_ids` and source provenance.
- Episode IDs are absent from current stored artifacts and would require adding a new primary authority layer.
- Object Groups better support modularization continuity, cross-conversation continuity, cross-agent continuity, ownership authority, runtime authority, validation authority, and historical authority.

---

## Conclusion

Given the actual PECS architecture and stored artifacts, Object Groups should be the primary authority unit rather than Engineering Episodes.

This aligns with the canonical object registry assumption and preserves the current event sink while enabling persistent, artifact-centric authority.
