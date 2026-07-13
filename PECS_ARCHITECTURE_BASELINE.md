# PECS Architecture Baseline

> Document version: 1.0.0
> Scope: describes the implemented PECS-PRO v2 architecture exactly as it exists today.
> This document captures the state after the Query Pipeline was wired into `workspace_bridge_cli.py`.

## 1. Overview

PECS-PRO v2 (Project Execution Continuity System) is a deterministic, topology-first continuity infrastructure for AI-assisted engineering workspaces. It produces a single canonical model of a workspace—the **Workspace Graph**—and derives from it a **Workspace Registry**, an **Evidence Correlation Engine**, and a **Navigation Builder**. The **Query Pipeline** exposes these components through the CLI, returning a deterministic Navigation Graph response for a set of architectural query terms.

No AI, embeddings, or semantic search are used. All evidence is structural: package layout, module files, imports/exports, class/method names, ownership, runtime zones, and graph topology.

## 2. Components

### 2.1 Workspace Graph

**Responsibilities**

- Provide the single in-memory canonical graph of the workspace.
- Replace the parallel RuntimeGraph/ExecutionGraph/OwnershipGraph and GraphIndex/ExecutionIndex/OwnershipIndex families.
- Store language-agnostic nodes and edges with deterministic identity, hashing, and serialization.

**Implementation**

- File: `execution_graph/graph/workspace_graph.py`
- Core classes: `Graph`, `Node`, `Edge`, `GraphMetadata`
- Node types (`NodeType`): `workspace`, `module`, `class`, `method`, `function`, `signal`, `slot`, `callback`, `dispatch`, `execution`, `qaction`, `toolbar`, `menu`, `dialog`, `viewer`, `overlay`, `subprocess`, `unknown`
- Edge types (`EdgeType`): `import`, `method_call`, `signal_slot`, `callback_execution`, `qaction_register`, `qaction_factory_register`, `shortcut_register`, `qaction_ownership`, `shortcut_ownership`, `dialog_launch`, `subprocess_launch`, `overlay_propagation`, `viewer_propagation`, `state_propagation`, `execution_chain`, `dispatch_chain`, `ownership`
- Authority levels (`AuthorityLevel`): `live_runtime`, `execution_graph`, `workspace_state`, `registry_state`, `historical`
- Edge directions (`EdgeDirection`): `directed`, `bidirectional`, `self`

**Construction**

- File: `execution_graph/builders/workspace_graph_builder.py`
- `WorkspaceGraphBuilder.build(...)` takes:
  - `reachable_files`: set of `Path` objects discovered by the daemon
  - `runtime_locality_payload`: mapping from `PECS_ID:*` anchors to locality metadata
  - `runtime_topology_edges`: list of `{from, to, type}` edge records
  - optional `entrypoints`: list of `Path` objects
  - optional legacy indexes for validation comparison only
- Nodes are derived from `runtime_locality_payload`.
- Edges are derived from `runtime_topology_edges`.
- Zones are registered per `execution_zone`.
- A deterministic SHA-256 `graph_hash` is computed over stable content, excluding mutable timestamps.

**Deterministic guarantees**

- Identical inputs produce identical `graph_hash`.
- `Graph.to_dict()` and `Graph.from_dict()` are stable and round-trip preserving.
- Timestamps are excluded from the content hash.

### 2.2 Workspace Registry

**Responsibilities**

- Identify user-facing **Features** versus **Infrastructure Units** from deterministic evidence.
- Provide a stable, hashed registry that future projection engines can consume.
- Index nodes by their containing feature/unit membership.

**Implementation**

- File: `workspace_registry/models.py`
- Core classes: `WorkspaceRegistry`, `WorkspaceFeature`, `WorkspaceInfrastructureUnit`, `WorkspaceEvidence`, `WorkspaceRegistryMetadata`
- Classification values: `user_facing`, `infrastructure`
- Evidence fields:
  - Boolean flags: `package_locality`, `module_naming_locality`, `public_ui_registration`, `controller_ownership`, `import_export_locality`, `runtime_evidence`, `graph_topology_validated`
  - Counts: `package_depth`, `ui_anchor_count`, `controller_count`, `support_module_count`, `observed_activation_count`, `inbound_feature_count`

**Construction**

- File: `workspace_registry/builders/workspace_registry_builder.py`
- `WorkspaceRegistryBuilder.build(graph)`:
  1. Uses `FeatureIdentifier` to derive candidates from the graph.
  2. Classifies each candidate as `user_facing` or `infrastructure`.
  3. Computes confidence via weighted evidence + tanh normalization.
  4. Generates aliases.
  5. Links infrastructure units to the features they support based on shared node membership.
  6. Computes a deterministic `registry_hash`.

**Feature classification rules**

A candidate is user-facing if it has at least one of:
- `public_ui_registration` evidence
- both `controller_ownership` and `runtime_evidence`
- its root node is in `graph.entrypoints`
- its root node name matches user-facing naming patterns (e.g., `dialog`, `viewer`, `workflow`)

Otherwise it is infrastructure.

**Deterministic guarantees**

- `registry_hash` is stable across repeated builds from the same graph.
- `WorkspaceRegistry.to_dict()` and `from_dict()` preserve the hash.

### 2.3 Evidence Correlation Engine

**Responsibilities**

- Correlate a list of query terms against deterministic workspace evidence.
- Return ranked Evidence Clusters without semantic search or AI.

**Implementation**

- File: `evidence_correlation/engines/evidence_correlator.py`
- Helper: `evidence_correlation/engines/evidence_extractor.py`
- Models: `evidence_correlation/models.py`

**Evidence sources (14)**

Each source is scored independently and weighted:

| Source | Weight |
|--------|--------|
| `package_name` | 1.0 |
| `folder_hierarchy` | 0.9 |
| `module_file_name` | 0.9 |
| `import_locality` | 0.7 |
| `export_locality` | 0.6 |
| `class_name` | 0.8 |
| `function_method_name` | 0.7 |
| `decorator` | 0.5 |
| `controller_ownership` | 0.6 |
| `runtime_ownership` | 0.6 |
| `ui_registration` | 0.8 |
| `execution_graph_locality` | 0.5 |
| `graph_topology` | 0.4 |
| `continuity_artifact` | 0.5 |

**Correlation algorithm**

1. `EvidenceExtractor.extract()` builds per-node evidence sets from the graph, registry, and locality payload.
2. `EvidenceCorrelator.correlate(query_terms)`:
   - Normalizes each query term (lowercase, strip, remove `_` and `-`).
   - For each node, scores each evidence source by substring match of any normalized query term in any normalized evidence term.
   - Computes a weighted sum normalized by the total weight sum, producing a score in `[0, 1]`.
   - Drops nodes below `_MIN_CLUSTER_SCORE = 0.01`.
   - Groups surviving nodes into clusters by root package (first segment of the `PECS_ID`).
   - Sorts clusters by cumulative score descending, then by namespace lexicographically.
   - Returns up to `max_clusters` clusters.

**Deterministic guarantees**

- Fixed weights.
- Sorted iteration over nodes, edges, and evidence terms.
- Identical query terms and graph produce identical cluster ranking and cluster IDs.

### 2.4 Navigation Builder

**Responsibilities**

- Transform selected Evidence Clusters into a bounded projected subgraph.
- Resolve current line ranges immediately before projection.
- Never persist line ranges.

**Implementation**

- File: `navigation_builder/builders/navigation_graph_builder.py`
- Models: `navigation_builder/models.py`
- Line range resolver: `navigation_builder/line_range_resolver.py`

**Construction**

`NavigationGraphBuilder.build(clusters, query_terms)`:

1. Collects seed node IDs from `graph_nodes`, `imports`, and `exports` of the input clusters.
2. Caps the seed set to `max_nodes`.
3. Expands the boundary via outgoing/incoming edges up to `max_depth` while respecting `max_nodes`.
4. Creates a `NavigationNode` for each selected graph node, resolving `start`/`end` line numbers through `LineRangeResolver`.
5. Creates a `NavigationEdge` for each graph edge whose source and target are both selected.
6. Wires parent/child relationships based on `module_path` prefix nesting.

**Line range resolution**

- `LineRangeResolver` parses the source file with `ast`.
- Caches results only for the duration of one build, keyed by `(absolute_path, mtime)`.
- If a file is modified, the next build re-parses it.
- Falls back to `(1, line_count)` or `(1, 1)` when the entity cannot be found.

**Budget defaults**

- `max_nodes = 40`
- `max_depth = 2`

### 2.5 Query Pipeline

**Responsibilities**

- Expose the full flow `query terms → Evidence Correlation → Cluster Selection → Navigation Graph → JSON response` via the CLI.
- Load or build required artifacts deterministically.

**Implementation**

- Entry point: `workspace_bridge_cli.py`, subcommand `query-pipeline`
- Command: `pecs query-pipeline [workspace_root] --terms TERM ...`

**Options**

| Option | Default | Description |
|--------|---------|-------------|
| `workspace_root` | `.` | Target workspace |
| `--terms` | required | Query term, repeatable; multi-word values are split on whitespace |
| `--max-clusters` | 3 | Maximum evidence clusters to select |
| `--max-nodes` | 40 | Maximum navigation graph nodes |
| `--max-depth` | 2 | Maximum graph expansion depth |
| `--output` | stdout | File to write JSON result |
| `--use-dumps` | false | Prefer daemon-written `workspace_graph.json` / `workspace_registry.json` |

**Artifact loading strategy**

1. Requires `.pecs/locality_index.json` and `.pecs/topology_compact.json`.
2. If `--use-dumps` and `.pecs/workspace_graph.json` exist, load it; otherwise rebuild the graph from locality/topology.
3. If `--use-dumps` and `.pecs/workspace_registry.json` exist, load it; otherwise rebuild the registry from the graph.
4. Build the evidence index, correlate, select clusters, build navigation graph.
5. Emit JSON with schema `pecs.query_pipeline.v1`.

**Lifecycle records**

The command appends `query_pipeline_started`, `query_pipeline_completed`, and `query_pipeline_failed` events to `.pecs/logs/lifecycle_commands.jsonl`.

## 3. Data Flow

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

## 4. Deterministic Guarantees

- **Workspace Graph**: `graph_hash` is stable for identical inputs; timestamps excluded.
- **Workspace Registry**: `registry_hash` is stable for identical graphs.
- **Evidence Correlation**: fixed weights, sorted iteration, stable cluster IDs derived from root package and content hash.
- **Navigation Graph**: identical query terms, graph, and budget parameters produce identical node/edge sets and line ranges for unchanged files.
- **Query Pipeline response**: JSON is serialized with `sort_keys=True` and deterministic ordering of nested objects.

## 5. Incremental Update Strategy

- The daemon performs all graph/registry/correlation construction during its existing refresh cycle (`pecs refresh`).
- No new background loops were added.
- New components are additive: legacy indexes and consumers remain unchanged.
- Optional serialization is controlled by daemon flags `--dump-workspace-graph` and `--dump-workspace-registry`.
- The CLI query-pipeline can rebuild graph/registry from `.pecs/locality_index.json` and `.pecs/topology_compact.json` if dumps are absent, so queries do not strictly require a running daemon.

## 6. Artifact Generation Strategy

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

## 7. Current Limitations

- The Query Pipeline rebuilds the graph/registry from legacy artifacts when daemon dumps are unavailable; this may produce a slightly different registry than the daemon because entrypoint handling depends on actual file existence.
- Evidence Correlation uses substring matching on normalized tokens; multi-word query terms are split on whitespace at the CLI layer.
- Line ranges are resolved from Python source only via `ast`; non-Python files fall back to whole-file ranges.
- The daemon does not expose an IPC/query endpoint; queries are CLI-driven and rebuild components as needed.
- Legacy parallel graph/index structures still exist and are the authority for legacy consumers.
- `integrations/pecs_lite_runtime_adapter.py` has a pre-existing syntax error that blocks `test_pecs_lite_runtime_validation`; it is unrelated to the query pipeline.

## 8. Future Work

- Migrate legacy consumers to query the Workspace Graph and Workspace Registry directly.
- Implement concrete `ProjectionEngine` subclasses that consume the registry.
- Remove legacy parallel graph/index structures after all consumers are migrated.
- Add an IPC or file-watch request/response path so the daemon can answer queries without CLI-side rebuilding.
- Extend line-range resolution to additional languages.
- Add optional semantic enrichment while preserving deterministic structural correlation as the primary signal.

## 9. Integration Points

- **CLI**: `pecs query-pipeline` in `workspace_bridge_cli.py`
- **Daemon**: `runtime/daemon/workspace_continuity_daemon.py` owns graph/registry/correlator lifecycle
- **Session**: `runtime/session/workspace_runtime_session.py` stores the canonical graph, registry, and correlator
- **Validators**: `validation/workspace_graph_validator.py`, `validation/workspace_registry_validator.py`
- **Consumers** (target): PECS Lite, Copilot, Continue, Kimi, Command Code, VS Code Extension, Localhost Viewer
