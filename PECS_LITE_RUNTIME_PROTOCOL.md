# PECS-LITE Runtime Protocol

## Protocol Summary

1. `RuntimeContextResolver` resolves workspace runtime context in read-only mode.
2. `PECSLiteRuntimeV2` invokes the resolver before building a projection.
3. `PECSProQueryAdapter` reads only `.pecs` artifacts and never reconstructs topology or scans workspace files.
4. `ProjectionExporter` builds a structured projection with a deterministic `pecs_runtime_report` section.

## Deterministic Runtime Interface

- `runtime_interface`: `stateless_query`
- `validation_state`: `read_only`
- `runtime_mode`: `read_only`
- `artifact_writes`: `0`
- `authority_source`: `PECS-PRO artifacts`
- `inferred`: `false`

## Output Sections

- `PECS STATUS`
- `PECS ARTIFACTS`
- `LOCALITY RESOLUTION`
- `SEARCH PLAN`
- `EXECUTION SCOPE`
- `UNRESOLVED`

## Read-only Context Resolution

- The resolver loads `.pecs/active_context.json`, `.pecs/locality_index.json`, `.pecs/compact_bundle.json`, `.pecs/topology_compact.json`, and continuity artifacts.
- It returns deterministic artifact state and runtime zone context without mutating the workspace.
- Validation and context resolution are explicitly separated from refresh and repair.

## Evidence chain

- `integration/pecs_pro_query_adapter.py` supplies artifact-based locality and continuity signals.
- `integrations/pecs_lite_projection_hardener.py` hardens projection and records query diagnostics.
- `PECSLiteRuntimeV2` now exposes runtime context and projection output in a deterministic structure.
