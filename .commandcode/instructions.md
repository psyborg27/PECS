# CommandCode — PECS Consumer Guidance

This file is managed by PECS. Everything between the markers below is
regenerated on upgrade. Content outside the markers is preserved.

<!-- PECS INSTRUCTIONS START -->

## Mandatory PECS-First Workflow

PECS is the authoritative engineering context provider for this workspace.
It reconstructs workspace topology, feature ownership, canonical implementation
locations, execution paths, architectural relationships, and prior engineering
decisions. PECS is **not** a text search engine.

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
        --source commandcode \
        --profile medium

## Forward the Complete Original Prompt Unchanged

The `<complete original user prompt>` is the user's request exactly as
received. Do **not**:

- summarize it
- rewrite it
- shorten it
- extract keywords from it
- build a search query from it

**WHY**: PECS performs its own interpretation, decomposition, and retrieval
planning. Pre-processing the prompt removes information required for accurate
workspace projection. Your only responsibility is to forward the request
unchanged.

## Discovery Order

For every engineering task:

    User Prompt
        ↓
    PECS Query
        ↓
    Workspace Projection
        ↓
    Targeted Repository Inspection
        ↓
    Implementation

Do **not** reorder these steps. Do not start inspection before projection.

## Do NOT Begin with Repository Search

Do NOT start by:

- grep
- glob
- semantic search
- filename search
- workspace indexing
- repository exploration
- opening likely files

These activities must only begin after the PECS projection has been received.

**WHY search-first causes problems**: Repository search tools (grep, glob,
text search) discover text, not architecture. They cannot determine:

- which implementation is authoritative
- which module owns the feature
- which copy is active and which is obsolete
- architectural boundaries or execution topology
- prior implementation decisions

Searching first frequently causes:

- duplicated implementations
- modifications to non-authoritative modules
- scattered logic across the codebase
- architectural drift
- unnecessary context consumption

PECS is the authoritative workspace discovery mechanism. Repository search is
a secondary verification tool, not the primary discovery mechanism.

## After PECS Returns

Every engineering response MUST begin with:

- **PECS Query**: the exact query submitted
- **PECS Response Summary**: what the projection contained
- **PECS Decision**: `USED` or `NOT USED`

If `NOT USED`, state the rejection reason. Valid reasons include:

- no relevant runtime targets
- insufficient locality
- projection unrelated to query
- PECS unavailable
- confidence insufficient

If PECS is accepted, use repository search only for targeted verification of
projected targets. Read the complete PECS response and attempt to use the
returned engineering context. Explain whether the projection influenced the
implementation.

## Iterative PECS Consultation

PECS remains available throughout the entire engineering task. If repository
inspection, debugging, testing, or validation reveals a material information
gap that PECS may resolve, issue a contextual PECS consultation using the
current engineering context rather than repeating the original user prompt.

Contextual queries may include newly discovered repository facts, candidate
implementations, architecture findings, ownership ambiguity, dependency
relationships, runtime failures, validation discrepancies, or the specific
unresolved engineering question. This is an evidence-discovery and
uncertainty-resolution step, not answer-shopping.

Use PECS to identify the authoritative implementation, owner, compatibility
constraints, and expected behavior. The maximum consultation budget is 4 total
per task: 1 initial plus up to 3 contextual. Stop early when the gap is
resolved, PECS produces no materially new evidence, or the remaining uncertainty
is outside PECS authority.

## PECS Unavailable

If PECS cannot be executed or is unavailable, explicitly report this before
proceeding without PECS. Proceeding without PECS is the exception, not the
default.

## Engineering Discipline

These principles apply to every implementation task:

**Minimal change**: Prefer the smallest possible change that satisfies the
requirement. Do not refactor surrounding code, add extra features, or make
improvements beyond what was asked.

**Preserve architecture**: Treat existing code as potentially active unless
proven otherwise. Do not redesign unless explicitly instructed. Avoid
introducing parallel logic, duplicate authorities, or orchestration forests.

**Architecture-first modifications**: Before making architectural changes
(changing data flow, adding new patterns, modifying core subsystems), read
the relevant architecture documentation first. Determine the intended
design before deciding to deviate from it.

**Deterministic implementation**: Prefer predictable, testable code. Avoid
non-deterministic behaviour, time-dependent logic, and implicit state.

**Verification**: After changes, run the test suite. Fix regressions before
considering the task complete. Do not leave broken code.

**Reporting**: Every response should explain what was changed and why. If
PECS guided the decision, state that explicitly.

## Project Conventions

For project-specific facts — technology stack, repository structure, build
commands, test commands, entry points, protected files, code style, and
useful reference documents — consult `AGENTS.md` in the repository root.

`AGENTS.md` is the authoritative repository reference. These instruction
files are the workflow authority. There must be no duplication or
contradiction between them.

## Quick Reference

```text
# PECS query (always first)
pecs consult . --query "<prompt>" --source commandcode --profile medium

# Verify PECS is running
pecs status .

# Refresh workspace projection
pecs refresh .

# Validate workspace
pecs validate .

# Run tests
python3 -m unittest discover -s tests -v
```

## What Consumers MUST NOT Do

- inspect PECS artifacts directly
- reconstruct locality independently
- reconstruct topology independently
- infer runtime ownership independently when PECS is accepted

PECS is the public API. The internal contents of `.pecs/` are implementation
details.

For the full canonical protocol, see `.pecs/PECS_CONSUMER_PROTOCOL.md`.

<!-- PECS INSTRUCTIONS END -->
