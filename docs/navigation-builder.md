# Navigation Builder

The Navigation Builder transforms selected Evidence Clusters into a bounded projected subgraph. It resolves current line ranges immediately before projection and never persists line ranges.

## Implementation

- File: `navigation_builder/builders/navigation_graph_builder.py`
- Models: `navigation_builder/models.py`
- Line range resolver: `navigation_builder/line_range_resolver.py`

## Construction

`NavigationGraphBuilder.build(clusters, query_terms)`:

1. Collects seed node IDs from `graph_nodes`, `imports`, and `exports` of the input clusters.
2. Caps the seed set to `max_nodes`.
3. Expands the boundary via outgoing/incoming edges up to `max_depth` while respecting `max_nodes`.
4. Creates a `NavigationNode` for each selected graph node, resolving `start`/`end` line numbers through `LineRangeResolver`.
5. Creates a `NavigationEdge` for each graph edge whose source and target are both selected.
6. Wires parent/child relationships based on `module_path` prefix nesting.

## Line Range Resolution

- `LineRangeResolver` parses the source file with `ast`.
- Caches results only for the duration of one build, keyed by `(absolute_path, mtime)`.
- If a file is modified, the next build re-parses it.
- Falls back to `(1, line_count)` or `(1, 1)` when the entity cannot be found.

## Budget Defaults

- `max_nodes = 40`
- `max_depth = 2`

## Relationship to Other Components

- Input clusters are produced by the [Evidence Correlation Engine](evidence-correlation.md).
- Selected nodes and edges come from the [Workspace Graph](workspace-graph.md).
- The [Query Pipeline](query-pipeline.md) emits the Navigation Graph as JSON.
