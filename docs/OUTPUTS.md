# PECS Output Artifacts

This document describes the current generated artifacts produced by PECS Alpha 1, their purpose, generation stage, and ownership.

## Generated Artifact Categories

PECS outputs are grouped into:

- workspace continuity artifacts
- runtime artifacts
- projection outputs
- logs
- validation reports
- exports
- indexes
- JSON schemas

## Workspace Continuity Artifacts

These artifacts are written under `.pecs/` in the target workspace during the daemon refresh cycle.

### `.pecs/locality_index.json`
- Purpose: runtime locality payload mapping code objects to workspace files and execution zones.
- Generation step: daemon refresh.
- Consumer: PECS-PRO graph builders and PECS-LITE projection adapters.
- Ownership: PECS-PRO.

### `.pecs/topology_compact.json`
- Purpose: compact topology edges and entrypoint information.
- Generation step: daemon refresh.
- Consumer: graph rebuild and query pipeline when dumps are absent.
- Ownership: PECS-PRO.

### `.pecs/active_context.json`
- Purpose: current active continuity context.
- Generation step: daemon refresh.
- Consumer: diagnostic and projection layers.
- Ownership: PECS-PRO.

### `.pecs/session_context.json`
- Purpose: session continuity and workspace refresh context.
- Generation step: daemon refresh.
- Consumer: continuity validators and observers.
- Ownership: PECS-PRO.

### `.pecs/compact_bundle.json`
- Purpose: compact continuity context bundle.
- Generation step: daemon refresh.
- Consumer: runtime session rebuild and serialized continuity delivery.
- Ownership: PECS-PRO.

### `.pecs/daemon_state.json`
- Purpose: daemon lifecycle and refresh state snapshot.
- Generation step: daemon refresh.
- Consumer: `pecs status` and daemon health checks.
- Ownership: PECS-PRO.

### `.pecs/daemon_health.json`
- Purpose: authoritative daemon readiness and health status.
- Generation step: daemon refresh.
- Consumer: `pecs health` and system diagnostics.
- Ownership: PECS-PRO.

## Optional Dumps

These artifacts are produced if the daemon is configured to emit graph and registry dumps.

### `.pecs/workspace_graph.json`
- Purpose: full Workspace Graph dump.
- Generation step: optional daemon dump after refresh.
- Consumer: query pipeline and offline analysis.
- Ownership: PECS-PRO.

### `.pecs/workspace_graph_validation.json`
- Purpose: validation report for the Workspace Graph dump.
- Generation step: optional dump validation.
- Consumer: diagnostic and validation tooling.
- Ownership: PECS-PRO.

### `.pecs/workspace_registry.json`
- Purpose: Workspace Registry dump.
- Generation step: optional daemon dump.
- Consumer: query pipeline and registry consumers.
- Ownership: PECS-PRO.

### `.pecs/workspace_registry_validation.json`
- Purpose: validation report for the registry dump.
- Generation step: optional validation.
- Consumer: diagnostic tooling.
- Ownership: PECS-PRO.

## Continuity Reports

### `.pecs/continuity/engineering_continuity_state.json`
- Purpose: detailed engineering continuity state.
- Generation step: continuity export or bridge operation.
- Consumer: audit and continuity review.
- Ownership: bridge/export authority.

### `.pecs/continuity/continuity_hydration_report.json`
- Purpose: hydration and continuity reconstruction report.
- Generation step: continuity export.
- Consumer: audit and diagnostic tooling.
- Ownership: bridge/export authority.

### `.pecs/continuity/active_topology.json`
- Purpose: active topology snapshot for continuity.
- Generation step: continuity export.
- Consumer: audit and topology review.
- Ownership: bridge/export authority.

### `.pecs/continuity/locality_state.json`
- Purpose: continuity locality state.
- Generation step: continuity export.
- Consumer: audit tooling and continuity analysis.
- Ownership: bridge/export authority.

## Runtime Outputs

### `.pecs/ai_chat_history.json`
- Purpose: workspace chat history metadata.
- Generation step: chat append tools or CLI operations.
- Consumer: continuity and provenance tracing.
- Ownership: workspace bridge tools.

### `.pecs/logs/lifecycle_commands.jsonl`
- Purpose: recorded lifecycle events and CLI command operations.
- Generation step: bridge and daemon operations.
- Consumer: audit and observability.
- Ownership: PECS-PRO.

## Projection Outputs

The query pipeline emits JSON responses to stdout or to a file when `--output` is provided.

### Query output
- Purpose: navigation graph and evidence projection for a query.
- Generation step: `pecs query-pipeline`.
- Consumer: AI assistant integrations and user-facing workflows.
- Ownership: query pipeline.

### Observation snapshots
- Purpose: opt-in projection emission snapshots for analysis.
- Generation step: `pecs observe-projection-snapshot` and `pecs observe-projection-daemon`.
- Consumer: diagnostics and projection observability.
- Ownership: observation tooling.

## Logs

PECS logs are written under `.pecs/logs/`:

- `daemon_activity.log` — daemon lifecycle and refresh events.
- `daemon_errors.log` — errors and retry events.
- `continuity_sync.log` — continuity sync and refresh details.
- `lifecycle_commands.jsonl` — command execution records.

## Validation Reports

PECS produces validation outputs in `.pecs/` for workspace and continuity validation.

Key validation artifacts:

- `.pecs/workspace_graph_validation.json`
- `.pecs/workspace_registry_validation.json`
- `.pecs/daemon_cycle_validation.json`
- `.pecs/workspace_graph_validation.json`

## Exported Artifacts

The bridge and exporter scripts produce artifacts used for continuity review and workspace export.

Common exported items:

- `export_workspace_continuity.py` output
- continuity JSON reports for audit and reconciliation

## Indexes

PECS creates topology and locality indexes used by runtime and query flows.

Key index files:

- `.pecs/locality_index.json`
- `.pecs/topology_compact.json`

## JSON Schemas

PECS does not ship a separate schema registry in Alpha 1. Current JSON outputs are implicitly defined by the CLI and module implementations.

## Ownership Summary

- **PECS-PRO** owns all workspace continuity and runtime artifact generation.
- **PECS-LITE** owns ephemeral projection shaping but not file output.
- **Bridge and export tooling** own continuity export and observation artifacts.

## Notes

This document describes the current Alpha 1 artifacts. It does not describe future schema stabilization or external data contracts.
