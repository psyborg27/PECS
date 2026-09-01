# PECS Consumer Protocol

This document defines the shared canonical contract for all supported PECS
consumer agents: Copilot, Continue, Kimi, and Command Code.

## What is PECS?

PECS (Persistent Engineering Continuity System) is the authoritative workspace
discovery and continuity mechanism for this workspace. PECS is **not** a text
search engine.

PECS maintains and reconstructs:

- workspace topology
- feature ownership
- canonical implementation locations
- execution paths
- architectural relationships
- implementation history
- workspace continuity
- previous engineering decisions

PECS exists to tell the implementation agent **where work belongs** before
repository exploration begins.

## Contract

PECS is the authoritative engineering context provider for the workspace.

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
    --source <consumer> \
    --profile <profile>
```

The `<complete original user prompt>` is the user's request **exactly as
received**. Do not:

- summarize it
- rewrite it
- shorten it
- extract keywords from it
- build a search query from it

PECS is responsible for interpreting the request, constructing its retrieval
strategy, identifying relevant workspace objects, and generating the workspace
projection.

## Why PECS must execute before repository search

Repository search tools (grep, glob, text search, semantic search) only discover
text. They do **not** determine:

- which implementation is authoritative
- which module owns the feature
- which copy is active
- which code is obsolete
- architectural boundaries
- previous implementation decisions
- execution topology

Searching first frequently causes:

- duplicated implementations
- modifications to non-authoritative modules
- scattered logic
- architectural drift
- unnecessary context consumption

PECS reconstructs the workspace topology first so repository exploration can be
targeted and limited to the authoritative implementation.

## Why the original prompt must remain unchanged

PECS performs its own interpretation, decomposition, and retrieval planning.
Pre-processing the prompt removes information required for accurate workspace
projection. The consumer's responsibility is only to forward the user's request
unchanged.

## Do NOT begin with repository search

Do NOT start by:

- grep
- glob
- semantic search
- filename search
- workspace indexing
- repository exploration
- opening likely files

These activities should only begin after the PECS projection has been received.

PECS is the authoritative workspace discovery mechanism.
Repository search is a secondary verification mechanism.

## Repository discovery order

For every engineering task:

```text
User Prompt
    ↓
PECS Query
    ↓
Workspace Projection
    ↓
Targeted Repository Inspection
    ↓
Implementation
```

Repository-wide grep, glob, semantic search or file inspection should only begin
after PECS has returned the workspace projection.

## After PECS returns

Every consumer must:

1. Report that PECS was consulted.
2. Report the projection received (or that PECS was unavailable).
3. Explain whether the projection influenced the implementation.
4. Then continue repository inspection.

Read the complete PECS response. Attempt to use the returned engineering
context.

If PECS is accepted, the consumer may use repository search only for targeted
verification of projected targets.

## PECS unavailable

If PECS cannot be executed or is unavailable, the consumer must explicitly
report this before proceeding without PECS. Proceeding without PECS is the
exception, not the default.

## PECS Decision

Every engineering response MUST begin with:

- PECS Query
- PECS Response Summary
- PECS Decision: USED | NOT USED

If NOT USED, state the rejection reason. Valid rejection reasons include:

- no relevant runtime targets
- insufficient locality
- projection unrelated to query
- PECS unavailable
- confidence insufficient

## Consumer Profiles

| Consumer     | --source     | --profile |
|-------------|-------------|-----------|
| Continue    | continue    | small     |
| CommandCode | commandcode | medium    |
| Copilot     | copilot     | medium    |
| Kimi        | kimi        | large     |

## What consumers MUST NOT do

- inspect PECS artifacts directly
- reconstruct locality independently
- reconstruct topology independently
- infer runtime ownership independently when PECS is accepted

PECS is the public API. The internal contents of `.pecs/` are implementation
details.

## AGENTS.md is a repository reference only

`AGENTS.md` describes repository facts, architecture, build commands, and
code conventions. It is **not** the implementation workflow.

Implementation workflow, reasoning order, discovery workflow, continuity,
ownership discovery, and implementation discipline are delegated exclusively
to this file: `.pecs/PECS_CONSUMER_PROTOCOL.md`.

There must be no duplication or contradiction between `AGENTS.md` and
`.pecs/PECS_CONSUMER_PROTOCOL.md`. If a conflict appears, this protocol file
takes precedence.

## Installation

This file is installed into the target workspace at
`.pecs/PECS_CONSUMER_PROTOCOL.md`. Consumer instruction files reference this
path for the canonical protocol definition.
