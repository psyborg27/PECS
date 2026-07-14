# Workflow

This document describes the current PECS Alpha 1 workflows for developers, daemons, queries, and projections.

## Developer Workflow

1. install PECS in a stable location.
2. bootstrap a workspace with `pecs bootstrap-workspace`.
3. use `pecs query-pipeline` or a supported consumer adapter for queries.
4. edit live workspace source files.
5. refresh continuity with `pecs refresh`.
6. validate with `pecs validate`.

## Daemon Workflow

The workspace daemon watches the target workspace and refreshes continuity artifacts.

- start the daemon with `.pecs/run_pecs_daemon.sh` or via the workspace bridge.
- stop the daemon with `pecs stop-daemon`.
- restart the daemon with `pecs restart-daemon`.
- check daemon status with `pecs status`.
- inspect health with `pecs health`.

The daemon writes deterministic `.pecs/` artifacts during refresh cycles.

## Query Workflow

1. issue a query term set to `pecs query-pipeline`.
2. the pipeline loads workspace artifacts or optional daemon dumps.
3. Evidence Correlation scores structural evidence.
4. Navigation Builder creates a bounded projection.
5. results are emitted as deterministic JSON.

For on-demand observation, use `pecs observe-projection-snapshot`.

## Consumer Workflow

Consumer adapters translate external models into the canonical PECS query contract.

- `integrations/copilot_adapter.py`
- `integrations/continue_adapter.py`
- `integrations/kimi_adapter.py`
- `integrations/commandcode_adapter.py`

Adapters preserve the canonical projection contract and return bounded, safe projections.

## AI Interaction Workflow

1. AI assistant sends query terms to a PECS adapter.
2. adapter normalizes query metadata.
3. PECS-LITE requests a projection from PECS-PRO artifacts.
4. the projection is returned to the AI assistant.
5. developer reviews and edits the source.

## Workspace Refresh Workflow

- `pecs refresh` regenerates continuity artifacts from current workspace state.
- `pecs rebuild-topology` refreshes runtime and topology artifacts without destroying continuity.
- `pecs rebuild-continuity` regenerates derived continuity outputs.
- `pecs validate` checks continuity integrity.

## Incremental Update Workflow

The daemon observes file changes and refreshes continuity as source files change. This workflow is intended to keep `.pecs/` derived artifacts aligned with workspace modifications.

## Artifact Generation Workflow

1. workspace scanner identifies entrypoints and imports.
2. runtime locality and topology payloads are built.
3. the workspace graph and registry are derived.
4. continuity artifacts are emitted under `.pecs/`.
5. optional dumps are written when configured.

## Recommended Daily Workflow

- verify installation with `pecs doctor`.
- query continuity with `pecs query-pipeline` or a supported adapter.
- edit live source files.
- refresh with `pecs refresh`.
- validate with `pecs validate`.
- run `pecs status` or `pecs health` if the daemon appears unhealthy.

## Notes

- PECS does not modify workspace source files.
- `.pecs/` files are generated infrastructure only.
- use version control for workspace rollback and upgrade safety.
