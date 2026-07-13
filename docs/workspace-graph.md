# Workspace Graph

The Workspace Graph is the single in-memory canonical graph of the workspace. It replaces the parallel RuntimeGraph/ExecutionGraph/OwnershipGraph and GraphIndex/ExecutionIndex/OwnershipIndex families, and stores language-agnostic nodes and edges with deterministic identity, hashing, and serialization.

## Implementation

- File: `execution_graph/graph/workspace_graph.py`
- Core classes: `Graph`, `Node`, `Edge`, `GraphMetadata`

### Node types (`NodeType`)

`workspace`, `module`, `class`, `method`, `function`, `signal`, `slot`, `callback`, `dispatch`, `execution`, `qaction`, `toolbar`, `menu`, `dialog`, `viewer`, `overlay`, `subprocess`, `unknown`

### Edge types (`EdgeType`)

`import`, `method_call`, `signal_slot`, `callback_execution`, `qaction_register`, `qaction_factory_register`, `shortcut_register`, `qaction_ownership`, `shortcut_ownership`, `dialog_launch`, `subprocess_launch`, `overlay_propagation`, `viewer_propagation`, `state_propagation`, `execution_chain`, `dispatch_chain`, `ownership`

### Authority levels (`AuthorityLevel`)

`live_runtime`, `execution_graph`, `workspace_state`, `registry_state`, `historical`

### Edge directions (`EdgeDirection`)

`directed`, `bidirectional`, `self`

## Construction

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

## Deterministic Guarantees

- Identical inputs produce identical `graph_hash`.
- `Graph.to_dict()` and `Graph.from_dict()` are stable and round-trip preserving.
- Timestamps are excluded from the content hash.

## Relationship to Other Components

- The [Workspace Registry](workspace-registry.md) is derived from the Workspace Graph.
- The [Evidence Correlation Engine](evidence-correlation.md) consumes graph nodes, edges, and evidence sets.
- The [Navigation Builder](navigation-builder.md) selects graph nodes and expands across edges.
- The [Query Pipeline](query-pipeline.md) rebuilds the graph from `.pecs/locality_index.json` and `.pecs/topology_compact.json` when daemon dumps are not available.
