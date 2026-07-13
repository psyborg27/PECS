# PECS Architecture

PECS-PRO v2 is a deterministic, topology-first continuity infrastructure for AI-assisted engineering workspaces. It produces a single canonical model of a workspace—the **Workspace Graph**—and derives from it a **Workspace Registry**, an **Evidence Correlation Engine**, a **Navigation Builder**, and a **Query Pipeline**.

No AI, embeddings, or semantic search are used. All evidence is structural: package layout, module files, imports/exports, class/method names, ownership, runtime zones, and graph topology.

## Core Components

| Component | Purpose | Document |
|-----------|---------|----------|
| Workspace Graph | Single in-memory canonical graph of the workspace | [workspace-graph.md](workspace-graph.md) |
| Workspace Registry | Classify and index features versus infrastructure units | [workspace-registry.md](workspace-registry.md) |
| Evidence Correlation | Rank nodes against query terms using deterministic evidence | [evidence-correlation.md](evidence-correlation.md) |
| Navigation Builder | Build bounded projected subgraphs for consumers | [navigation-builder.md](navigation-builder.md) |
| Query Pipeline | Expose the full flow through the CLI | [query-pipeline.md](query-pipeline.md) |

## Data Flow

```
Workspace source files
        ↓
Daemon refresh cycle
        ↓
Runtime locality payload + topology edges
        ↓
WorkspaceGraphBuilder ──→ Workspace Graph (in-memory, optional dump)
        ↓
WorkspaceRegistryBuilder ──→ Workspace Registry (in-memory, optional dump)
        ↓
EvidenceCorrelator ──→ Evidence Clusters (in-memory only)
        ↓
NavigationGraphBuilder ──→ Navigation Graph (in-memory only)
        ↓
query-pipeline CLI ──→ JSON response
```

The daemon builds the Workspace Graph, Workspace Registry, and Evidence Correlation index once per refresh cycle. The Navigation Graph is built on demand per query.

## Deterministic Guarantees

- **Workspace Graph**: `graph_hash` is stable for identical inputs; timestamps excluded.
- **Workspace Registry**: `registry_hash` is stable for identical graphs.
- **Evidence Correlation**: fixed weights, sorted iteration, stable cluster IDs derived from root package and content hash.
- **Navigation Graph**: identical query terms, graph, and budget parameters produce identical node/edge sets and line ranges for unchanged files.
- **Query Pipeline response**: JSON is serialized with `sort_keys=True` and deterministic ordering of nested objects.

## Refresh and Update Strategy

- The daemon performs all graph/registry/correlation construction during its existing refresh cycle (`pecs refresh`).
- No new background loops were added.
- New components are additive: legacy indexes and consumers remain unchanged.
- Optional serialization is controlled by daemon flags `--dump-workspace-graph` and `--dump-workspace-registry`.
- The CLI `query-pipeline` can rebuild graph/registry from `.pecs/locality_index.json` and `.pecs/topology_compact.json` if dumps are absent, so queries do not strictly require a running daemon.

## Artifact Generation Strategy

**Produced by the daemon (refresh cycle)**

- `.pecs/locality_index.json` — runtime locality payload
- `.pecs/topology_compact.json` — topology edges and entrypoints
- `.pecs/active_context.json`
- `.pecs/session_context.json`
- `.pecs/compact_bundle.json`
- `.pecs/daemon_state.json`
- `.pecs/daemon_health.json`

**Optional dumps**

- `.pecs/workspace_graph.json` — only with `--dump-workspace-graph`
- `.pecs/workspace_graph_validation.json` — only with `--dump-workspace-graph`
- `.pecs/workspace_registry.json` — only with `--dump-workspace-registry`
- `.pecs/workspace_registry_validation.json` — only with `--dump-workspace-registry`

**Generated on demand by query-pipeline**

- Navigation Graph JSON (stdout or `--output` file)
- Lifecycle records in `.pecs/logs/lifecycle_commands.jsonl`

**Not persisted**

- Evidence Clusters
- Navigation Graph
- Line ranges

See [artifacts.md](artifacts.md) for a complete catalog of PECS-generated files.

## Current Limitations

- The Query Pipeline rebuilds the graph/registry from legacy artifacts when daemon dumps are unavailable; this may produce a slightly different registry than the daemon because entrypoint handling depends on actual file existence.
- Evidence Correlation uses substring matching on normalized tokens; multi-word query terms are split on whitespace at the CLI layer.
- Line ranges are resolved from Python source only via `ast`; non-Python files fall back to whole-file ranges.
- The daemon does not expose an IPC/query endpoint; queries are CLI-driven and rebuild components as needed.
- Legacy parallel graph/index structures still exist and are the authority for legacy consumers.

## Future Work

- Migrate legacy consumers to query the Workspace Graph and Workspace Registry directly.
- Implement concrete `ProjectionEngine` subclasses that consume the registry.
- Remove legacy parallel graph/index structures after all consumers are migrated.
- Add an IPC or file-watch request/response path so the daemon can answer queries without CLI-side rebuilding.
- Extend line-range resolution to additional languages.
- Add optional semantic enrichment while preserving deterministic structural correlation as the primary signal.

## Integration Points

- **CLI**: `pecs query-pipeline` in `workspace_bridge_cli.py`
- **Daemon**: `runtime/daemon/workspace_continuity_daemon.py` owns graph/registry/correlator lifecycle
- **Session**: `runtime/session/workspace_runtime_session.py` stores the canonical graph, registry, and correlator
- **Validators**: `validation/workspace_graph_validator.py`, `validation/workspace_registry_validator.py`
- **Consumers** (target): PECS Lite, Copilot, Continue, Kimi, Command Code, VS Code Extension, Localhost Viewer

See the [integrations/](integrations/) directory for consumer-specific integration contracts.
