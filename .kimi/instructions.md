# Kimi — PECS Consumer Guidance

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

    pecs consult . \
        --query "<complete original user prompt>" \
        --source kimi \
        --profile large

The `<complete original user prompt>` must be forwarded unchanged. Do not
summarize, rewrite, shorten, extract keywords, or build a search query from it.

Read the complete PECS response. Attempt to use the returned engineering
context.

PECS remains available throughout the whole task. When implementation,
repository inspection, debugging, testing, or validation reveals a material
information gap that PECS may resolve, issue a contextual PECS consultation
using the current engineering context instead of repeating the original prompt.

Contextual PECS queries may include newly discovered repository facts,
implementation findings, ownership ambiguity, architecture findings, candidate
modules, runtime failures, validation discrepancies, or the specific unresolved
engineering question. Use PECS to identify the authoritative implementation,
owner, dependencies, compatibility rules, and expected behavior.

Do not use PECS merely to confirm a preferred implementation or to answer-shop.
The maximum PECS consultation budget is 4 total per task: 1 initial plus up to 3
contextual consultations. Stop early when the gap is resolved, PECS adds no
materially new evidence, or the uncertainty is outside PECS authority.

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
