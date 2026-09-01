# Copilot — PECS Workspace Integration

This file is managed by PECS. Everything between the markers below is
regenerated on upgrade. Content outside the markers is preserved.

Runtime bootstrap and environment instructions above the start marker are
preserved across upgrades. The PECS consumer contract below is authoritative.

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
    --source copilot \
    --profile medium
```

The `<complete original user prompt>` must be forwarded unchanged. Do not
summarize, rewrite, shorten, extract keywords, or build a search query from it.

Read the complete PECS response. Attempt to use the returned engineering
context.

PECS remains available throughout the entire engineering task. If repository
investigation, debugging, testing, or validation reveals a material information
gap that PECS may resolve, issue a contextual consultation using the current
engineering context instead of repeating the original prompt.

Contextual queries may include newly discovered repository facts, ownership
ambiguities, implementation findings, candidate modules, runtime failures,
validation discrepancies, or the specific unresolved engineering question.

The maximum PECS consultation budget is 4 total per task: 1 initial consultation
plus up to 3 contextual ones. Stop early when the gap is resolved, PECS adds no
materially new evidence, or the remaining uncertainty is outside PECS authority.
Do not use PECS merely to confirm a preferred implementation or to answer-shop.

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

## Environment

```bash
cd "${workspaceFolder}"
if [[ -f .venv/bin/activate ]]; then source .venv/bin/activate; fi
```

## Chat Continuity

```bash
python3 .pecs/tools/append_ai_chat_history.py "${workspaceFolder}" \
  --source copilot --message "Summary of changes"
```
