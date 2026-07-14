# PECS Alpha 1 Manual

PECS is intended to help developers discover execution locality and workspace continuity in Python-based workspaces. The current implementation provides deterministic runtime topology reconstruction, a workspace graph, a registry, evidence correlation, a navigation builder, and a query pipeline.

## Purpose

This manual describes how PECS works, what it indexes, how to use the CLI, and how to interpret outputs.

## Concepts

- **Workspace Graph** — a canonical graph of the workspace derived from runtime topology and locality.
- **Workspace Registry** — a classification of workspace features and infrastructure units.
- **Evidence Correlation** — a deterministic ranking engine for query terms.
- **Navigation Graph** — a bounded projected view used for AI guidance.
- **PECS-LITE** — a stateless projection wrapper around PECS-PRO artifacts.
- **Daemon** — watches Python workspace files and refreshes `.pecs` artifacts.

## How PECS Works

1. The daemon observes Python source changes and rebuilds runtime topology.
2. Runtime locality and topology artifacts are written to `.pecs/`.
3. The workspace graph and registry are derived from those artifacts.
4. A query is processed through Evidence Correlation and Navigation Builder.
5. The projection result is returned as deterministic JSON.

## Indexing

The daemon uses AST, import resolution, and entrypoint discovery to build runtime locality.

- It collects reachable `.py` files from workspace entrypoints.
- It resolves imports and local module dependencies.
- It writes `.pecs/locality_index.json` and `.pecs/topology_compact.json`.

## Querying

Use `pecs query-pipeline` to run a query against the current workspace.

- The query pipeline loads graph and registry artifacts.
- It builds evidence clusters and a navigation graph.
- The result is serialized as deterministic JSON.

## Profiles

PECS-LITE supports profile shaping through its wrapper, but the current CLI exposes only the query pipeline. Projections are generated on demand and shaped by the consumer adapter.

## Runtime Discovery

Runtime topology is discovered from Python sources only. The daemon searches for entrypoint candidates and fallback Python modules.

## Troubleshooting

If a workspace appears unhealthy:

- Run `pecs status` and `pecs health`
- Run `pecs refresh` and `pecs validate`
- Inspect `.pecs/logs/daemon_activity.log` and `.pecs/logs/daemon_errors.log`

## Examples

Bootstrap a workspace:

```bash
pecs bootstrap-workspace "/path/to/workspace" --repo-root "$(pwd)"
```

Run a query:

```bash
pecs query-pipeline "/path/to/workspace" --terms "runtime locality reconciliation"
```

Capture a projection snapshot:

```bash
pecs observe-projection-snapshot "/path/to/workspace" --query "runtime locality reconciliation" --query-source test --model-name test-model --profile-class local --local-vs-frontier local
```
