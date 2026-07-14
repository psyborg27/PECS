# PECS Alpha 1 Overview

PECS Alpha 1 is the first implementation of the Project Execution Continuity System. It focuses on discovering runtime topology and making workspace continuity available to AI-enabled tooling.

## What is included

- Runtime topology reconstruction for Python workspaces.
- A workspace continuity daemon that refreshes `.pecs` artifacts.
- A `pecs` CLI for bootstrap, status, refresh, validate, query, and observation.
- Deterministic `.pecs` artifacts for continuity and projection.
- A query pipeline with evidence correlation and navigation builder support.

## Core features

- `bootstrap-workspace` installs workspace integration assets.
- `refresh` rebuilds `.pecs` runtime artifacts from the current workspace.
- `validate` checks continuity artifact integrity.
- `query-pipeline` runs a search over workspace continuity and evidence.
- `observe-projection-snapshot` logs projection state for opt-in observability.

## Implementation footprint

- `runtime/` contains the file watcher, topology builder, and runtime session logic.
- `execution_graph/`, `topology/`, and `continuity/` contain graph and continuity engines.
- `integrations/` contains the PECS-LITE and adapter layers.
- `workspace_assets/` contains installable workspace guidance assets.

## Usage

```bash
# Bootstrap the target workspace
pecs bootstrap-workspace "/path/to/workspace" --repo-root "$(pwd)"

# Refresh continuity artifacts
pecs refresh "/path/to/workspace"

# Validate artifacts
pecs validate "/path/to/workspace"

# Query workspace continuity
pecs query-pipeline "/path/to/workspace" --terms "find entrypoints"
```

## Notes

This Alpha 1 release is intended for early experimentation. The current system is not yet optimized for production-scale multi-repo analysis.
