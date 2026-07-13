# PECS-LITE Runtime Protocol

PECS-LITE is the compatibility layer between AI consumers and the canonical PECS Query Pipeline. It preserves the existing public `PECSLiteRuntimeAdapter.build_projection_safe(...)` interface while internally routing requests through `PECSQueryPipeline.query(...)`.

## Protocol Summary

1. A consumer invokes `PECSLiteRuntimeAdapter.build_projection_safe(...)`.
2. The adapter normalizes model identity and classifies capability profile.
3. The adapter calls `PECSQueryPipeline.query(...)` with the consumer's query terms.
4. The Query Pipeline reads `.pecs/locality_index.json` and `.pecs/topology_compact.json`, builds the Workspace Graph and Workspace Registry, correlates evidence, and returns a bounded Navigation Graph.
5. The adapter maps the Navigation Graph back into the PECS-LITE projection schema (`runtime_targets`, `secondary_neighbors`, `pecs_lite_status`, `pecs_lite_telemetry`, etc.).
6. If the Query Pipeline is unavailable, the adapter falls back to the legacy `PECSLiteRuntimeV2` continuity retrieval path.

## Deterministic Runtime Interface

- `runtime_interface`: `stateless_query`
- `validation_state`: `read_only`
- `runtime_mode`: `read_only`
- `artifact_writes`: `0`
- `authority_source`: `PECS-PRO Query Pipeline`
- `inferred`: `false`

## Output Sections

- `schema`
- `profile`
- `projection_profile`
- `runtime_targets`
- `secondary_neighbors`
- `pecs_lite_status`
- `pecs_lite_telemetry`
- `final_emission_observability`
- `query_pipeline` (correlation and navigation graph metadata)
- `diagnostics`

## Read-only Context Resolution

- The Query Pipeline loads `.pecs/locality_index.json` and `.pecs/topology_compact.json`.
- It reconstructs the Workspace Graph and Workspace Registry in memory without mutating the workspace.
- The Navigation Graph is built on demand and never persisted.

## Evidence Chain

- `integrations/pecs_lite_runtime_adapter.py` receives consumer requests and preserves the public interface.
- `pecs_query/pipeline.py` executes the canonical Query Pipeline.
- `integrations/pecs_lite_projection_hardener.py` supplies profile limits and capability classification for mapping the Navigation Graph into the PECS-LITE schema.
- Legacy `PECSLiteRuntimeV2` is retained only as a fallback when the Query Pipeline cannot be used.

## See Also

- [Query Pipeline](../query-pipeline.md) — canonical query contract
- [Architecture](../architecture.md) — high-level components and data flow
- [Continue](continue.md), [Copilot](copilot.md), [Kimi](kimi.md), [CommandCode](commandcode.md) — consumer integrations
