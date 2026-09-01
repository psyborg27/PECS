# Continue — PECS Consumer Guidance

This file is managed by PECS. Everything between the markers below is
regenerated on upgrade. Content outside the markers is preserved.

<!-- PECS INSTRUCTIONS START -->

PECS is the authoritative engineering context provider for this workspace.

Before ANY:
- repository reasoning
- repository exploration
- grep, glob, or filename search
- semantic search
- implementation planning
- code generation
- file modification

execute:

```bash
pecs consult . \
    --query "<complete original user prompt>" \
    --source continue \
    --profile small
```

The `<complete original user prompt>` must be forwarded unchanged. Do not
summarize, rewrite, shorten, extract keywords, or build a search query from it.

Read the complete PECS response. Attempt to use the returned engineering
context.

PECS remains available throughout the task. If repository inspection,
debugging, testing, or validation reveals a material information gap that PECS
may resolve, issue a contextual PECS consultation using the current task context
rather than repeating the original prompt.

Contextual queries may include newly discovered repository facts, implementation
failures, architecture findings, ownership ambiguity, candidate implementations,
validation discrepancies, or the specific unresolved engineering question.

Use PECS to identify the authoritative implementation, owner, dependencies,
compatibility constraints, and expected behavior. Do not query PECS merely to
confirm a preferred implementation or to answer-shop. Maximum PECS consultations
per task: 4 total (1 initial + up to 3 contextual). Stop early when the gap is
resolved, PECS adds no materially new evidence, or the remaining uncertainty is
outside PECS authority.

Every engineering response MUST begin with:
- PECS Query
- PECS Response Summary
- PECS Decision: USED | NOT USED

If NOT USED, state the rejection reason.
Valid rejection reasons include:
- no relevant runtime targets
- insufficient locality
- projection unrelated to query
- PECS unavailable
- confidence insufficient

ONLY AFTER rejecting PECS may the consumer perform normal repository
exploration.

Consumers MUST NOT:
- inspect PECS artifacts
- reconstruct locality
- reconstruct topology
- infer runtime ownership independently when PECS is accepted

PECS is the public API. The internal contents of .pecs are implementation
details.

For the full canonical protocol, see `.pecs/PECS_CONSUMER_PROTOCOL.md`.

<!-- PECS INSTRUCTIONS END -->

## Context Guidance

PECS artifacts are continuity infrastructure only.
They do not contain editable sourcecode.

Before proposing edits, read and respect:
- .pecs/active_context.json
- .pecs/compact_bundle.json
- .pecs/session_context.json
- .pecs/locality_index.json
- .continue/rules/CONTINUITY_MAP.md (if present)

Priority order:
1. Live workspace runtime modules
2. PECS locality projection and continuity artifacts
3. Historical chat memory

Never edit or patch .pecs files.
Use PECS only for locality retrieval and execution neighborhood projection.

Always run workspace commands with environment activation when available:
```bash
cd "${workspaceFolder}"
source .venv/bin/activate
```
