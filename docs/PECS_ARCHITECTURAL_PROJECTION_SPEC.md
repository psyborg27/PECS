# PECS Architectural Projection Specification

> Version: 1.0.0
> Status: canonical contract for all PECS consumers
> Authority: PECS-PRO v2 Query Pipeline

This document defines the authoritative contract between PECS and its consumers. All future integrations—PECS Lite, Copilot, Continue, Kimi, Command Code, VS Code Extension, and Localhost Viewer—must consume projections through this contract.

## 1. Scope

This specification covers:

- Query input schema
- Evidence correlation contract
- Evidence cluster schema
- Navigation graph schema
- Node and edge schemas
- Navigation metadata
- Live line range resolution
- Deterministic guarantees
- Versioning policy
- Artifact budget policy
- Backward compatibility policy

## 2. Query Input Schema

### 2.1 CLI Invocation

```bash
pecs query-pipeline <workspace_root> \
  --terms <term> \
  [--terms <term> ...] \
  [--max-clusters <int>] \
  [--max-nodes <int>] \
  [--max-depth <int>] \
  [--output <path>] \
  [--use-dumps]
```

### 2.2 Arguments

| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `workspace_root` | string | no | `.` | Absolute or relative path to the workspace root. Must contain `.pecs/locality_index.json` and `.pecs/topology_compact.json`. |
| `--terms` | string | yes | — | Repeatable. Each value is split on whitespace into individual query tokens. Tokens are correlated independently. |
| `--max-clusters` | integer | no | `3` | Upper bound on the number of Evidence Clusters returned. |
| `--max-nodes` | integer | no | `40` | Upper bound on the number of NavigationNodes in the projected graph. |
| `--max-depth` | integer | no | `2` | Maximum graph-locality expansion depth from cluster seeds. |
| `--output` | string | no | stdout | File path to write the JSON response. When omitted, the response is printed to stdout. |
| `--use-dumps` | boolean | no | `false` | If true, PECS loads `workspace_graph.json` and `workspace_registry.json` when available instead of rebuilding them. |

### 2.3 Tokenization rule

Each `--terms` value is tokenized on ASCII whitespace (`split()`). The resulting tokens are lowercased, stripped, and have `_` and `-` removed before correlation. Consumers must not rely on phrase-level matching; correlation is per-token substring matching.

### 2.4 Error contract

- Missing workspace root: exit code `1`, error logged to stderr.
- Missing query terms: exit code `1`, error logged to stderr.
- Missing required artifacts: exit code `1`, message indicates `pecs refresh` is required.
- Any runtime failure: exit code `1`, `query_pipeline_failed` lifecycle record written.

## 3. Response Envelope

The top-level response is a JSON object.

```json
{
  "schema": "pecs.query_pipeline.v1",
  "workspace_root": "/absolute/path/to/workspace",
  "query_terms": ["sorted", "tokens"],
  "deterministic": true,
  "correlation": { /* CorrelationResult */ },
  "navigation_graph": { /* NavigationGraph */ }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `schema` | string | Constant value `pecs.query_pipeline.v1`. |
| `workspace_root` | string | Absolute workspace root path. |
| `query_terms` | array of string | Sorted list of query tokens actually used. |
| `deterministic` | boolean | Constant value `true`; indicates the response is produced by deterministic structural correlation. |
| `correlation` | object | `CorrelationResult` object. |
| `navigation_graph` | object | `NavigationGraph` object. |

Keys are sorted alphabetically. Arrays of objects preserve deterministic order (by score, then by stable identifier).

## 4. Evidence Correlation Contract

### 4.1 Purpose

Map query tokens to ranked Evidence Clusters using only deterministic structural evidence. No semantic similarity, embeddings, or LLM inference are used.

### 4.2 Evidence sources

Each graph node is annotated with evidence from exactly these sources:

| Source | Description |
|--------|-------------|
| `package_name` | First segment of the node's `PECS_ID`. |
| `folder_hierarchy` | All prefix paths of the `PECS_ID` body. |
| `module_file_name` | Source file stem and relative path. |
| `import_locality` | Outgoing `import` edge targets and their source files. |
| `export_locality` | Incoming `import` edge sources and their source files. |
| `class_name` | Class name when the node represents a class. |
| `function_method_name` | Method/function name when the node represents one. |
| `decorator` | Decorator evidence (currently reserved). |
| `controller_ownership` | Outgoing `signal_slot` edge targets. |
| `runtime_ownership` | Outgoing UI ownership/registration edge targets. |
| `ui_registration` | Same targets as `runtime_ownership` plus UI-anchor node identities. |
| `execution_graph_locality` | Runtime zone of the node. |
| `graph_topology` | Node type and canonical name. |
| `continuity_artifact` | Raw locality payload fields: file, class, method, runtime_zone. |

### 4.3 Scoring contract

For each evidence source `s` with fixed weight `w_s`:

1. Normalize every evidence term: lowercase, strip whitespace, remove `_` and `-`.
2. Normalize every query token: lowercase, strip whitespace, remove `_` and `-`.
3. For source `s`, count how many distinct query tokens are substrings of at least one normalized evidence term. Call this `matches`.
4. Source contribution: `min(1.0, matches / |query_tokens|) * w_s`.
5. Node cumulative score: `Σ_s (contribution_s * w_s) / Σ_s w_s`.

Nodes with cumulative score `< 0.01` are discarded.

### 4.4 Weights (fixed)

```json
{
  "package_name": 1.0,
  "folder_hierarchy": 0.9,
  "module_file_name": 0.9,
  "import_locality": 0.7,
  "export_locality": 0.6,
  "class_name": 0.8,
  "function_method_name": 0.7,
  "decorator": 0.5,
  "controller_ownership": 0.6,
  "runtime_ownership": 0.6,
  "ui_registration": 0.8,
  "execution_graph_locality": 0.5,
  "graph_topology": 0.4,
  "continuity_artifact": 0.5
}
```

Consumers must treat these weights as immutable for schema version `pecs.query_pipeline.v1`.

### 4.5 Clustering contract

Surviving nodes are grouped by root package: the first dot-separated segment of the `PECS_ID` body. Each group becomes one `EvidenceCluster`. Clusters are sorted by cumulative score descending, then by `primary_namespace` ascending. The top `--max-clusters` clusters are returned.

## 5. CorrelationResult Schema

```json
{
  "query_terms": ["token1", "token2"],
  "cluster_count": 2,
  "clusters": [ /* EvidenceCluster */ ],
  "metadata": {
    "workspace_root": "/absolute/path",
    "indexed_nodes": 42,
    "matched_nodes": 12,
    "evidence_source_count": 14
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `query_terms` | array of string | Sorted query tokens. |
| `cluster_count` | integer | Number of clusters in `clusters`. |
| `clusters` | array of `EvidenceCluster` | Ranked clusters. |
| `metadata.workspace_root` | string | Absolute workspace root. |
| `metadata.indexed_nodes` | integer | Total graph nodes indexed. |
| `metadata.matched_nodes` | integer | Nodes with score >= 0.01. |
| `metadata.evidence_source_count` | integer | Number of evidence sources (14). |

## 6. EvidenceCluster Schema

```json
{
  "cluster_id": "ec-<root_package>-<hash>",
  "primary_namespace": "root_package",
  "root_package": "root_package",
  "participating_files": ["relative/path.py"],
  "imports": ["PECS_ID:..."],
  "exports": ["PECS_ID:..."],
  "classes": ["ClassName"],
  "methods_functions": ["method_name"],
  "runtime_nodes": ["PECS_ID:..."],
  "ownership_nodes": ["PECS_ID:..."],
  "graph_nodes": ["PECS_ID:..."],
  "evidence_breakdown": { /* EvidenceBreakdown */ },
  "cumulative_correlation_score": 0.25,
  "metadata": {
    "node_count": 3
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `cluster_id` | string | Stable identifier `ec-<root_package>-<sha256_short>`. |
| `primary_namespace` | string | Root package used for grouping. |
| `root_package` | string | Same as `primary_namespace`. |
| `participating_files` | array of string | Sorted relative source files of member nodes. |
| `imports` | array of string | Sorted outgoing import targets outside the cluster. |
| `exports` | array of string | Sorted incoming import sources outside the cluster. |
| `classes` | array of string | Sorted class names of member nodes. |
| `methods_functions` | array of string | Sorted method/function names of member nodes. |
| `runtime_nodes` | array of string | Sorted UI/anchor node IDs in the cluster. |
| `ownership_nodes` | array of string | Same as `runtime_nodes` in current implementation. |
| `graph_nodes` | array of string | Sorted member node IDs. |
| `evidence_breakdown` | object | Per-source contribution scores. |
| `cumulative_correlation_score` | number | Weighted sum in `[0, 1]`. |
| `metadata.node_count` | integer | Number of member nodes. |

### 6.1 EvidenceBreakdown Schema

```json
{
  "package_name": 0.0,
  "folder_hierarchy": 0.0,
  "module_file_name": 0.0,
  "import_locality": 0.0,
  "export_locality": 0.0,
  "class_name": 0.0,
  "function_method_name": 0.0,
  "decorator": 0.0,
  "controller_ownership": 0.0,
  "runtime_ownership": 0.0,
  "ui_registration": 0.0,
  "execution_graph_locality": 0.0,
  "graph_topology": 0.0,
  "continuity_artifact": 0.0
}
```

Each value is `min(1.0, matches / |query_tokens|) * weight` for that source.

## 7. NavigationGraph Schema

```json
{
  "query_terms": ["token1", "token2"],
  "node_count": 25,
  "edge_count": 58,
  "nodes": { "PECS_ID:...": { /* NavigationNode */ } },
  "edges": { "<edge_id>": { /* NavigationEdge */ } },
  "metadata": {
    "workspace_root": "/absolute/path",
    "max_nodes": 40,
    "max_depth": 2
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `query_terms` | array of string | Sorted query tokens. |
| `node_count` | integer | Number of entries in `nodes`. |
| `edge_count` | integer | Number of entries in `edges`. |
| `nodes` | object | Map from node ID to `NavigationNode`. Keys sorted in JSON output. |
| `edges` | object | Map from edge ID to `NavigationEdge`. Keys sorted in JSON output. |
| `metadata.workspace_root` | string | Absolute workspace root. |
| `metadata.max_nodes` | integer | Node budget used. |
| `metadata.max_depth` | integer | Depth budget used. |

## 8. NavigationNode Schema

```json
{
  "node_id": "PECS_ID:module.path.file",
  "node_type": "module",
  "file_path": "relative/path/file.py",
  "line_range": { "start": 10, "end": 50 },
  "parent_node_id": "PECS_ID:module.path",
  "child_node_ids": ["PECS_ID:module.path.file.Class"],
  "incoming_edges": ["<edge_id>"],
  "outgoing_edges": ["<edge_id>"],
  "metadata": {
    "canonical_name": "file",
    "module_path": "module.path.file",
    "execution_zone": "general_runtime",
    "authority_level": "workspace_state",
    "confidence": 1.0
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `node_id` | string | Same `PECS_ID` as the Workspace Graph node. |
| `node_type` | string | Value from `NodeType` enum. |
| `file_path` | string \| null | Workspace-relative source file path. |
| `line_range` | object | `{start, end}` resolved immediately before projection. |
| `parent_node_id` | string \| null | Closest enclosing module/class node by `module_path` prefix. |
| `child_node_ids` | array of string | Sorted child node IDs. |
| `incoming_edges` | array of string | Sorted edge IDs pointing to this node. |
| `outgoing_edges` | array of string | Sorted edge IDs leaving this node. |
| `metadata.canonical_name` | string | Short name of the entity. |
| `metadata.module_path` | string \| null | Python-style dotted module path. |
| `metadata.execution_zone` | string \| null | Runtime zone from the graph. |
| `metadata.authority_level` | string | Authority level from the graph. |
| `metadata.confidence` | number | Confidence from the graph. |

## 9. NavigationEdge Schema

```json
{
  "edge_id": "PECS_ID:source--import--PECS_ID:target",
  "source_id": "PECS_ID:source",
  "target_id": "PECS_ID:target",
  "edge_type": "import",
  "metadata": {
    "execution_zone": null
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `edge_id` | string | Stable identifier: `<source>--<edge_type>--<target>`. |
| `source_id` | string | Source node ID. |
| `target_id` | string | Target node ID. |
| `edge_type` | string | Value from `EdgeType` enum. |
| `metadata.execution_zone` | string \| null | Runtime zone when available. |

## 10. Live Line Range Resolution

### 10.1 Contract

- Line ranges are resolved per projection, never persisted.
- The resolver re-parses a source file only if its `mtime` has changed since the start of the current build.
- Resolution uses Python `ast`.

### 10.2 Resolution precedence

Given `file_path`, optional `class_name`, optional `method_name`:

1. If `class_name` and `method_name` are provided, return the range of `class_name.method_name`.
2. If only `class_name` is provided, return the class range.
3. If only `method_name` is provided, return the function/method range.
4. Otherwise return `(1, line_count_of_file)`.
5. If the file does not exist or cannot be parsed, return `(1, 1)`.

### 10.3 Consumer obligation

Consumers must treat `line_range` as advisory and current only at the moment of projection. For stale checks, consumers must compare file `mtime` or re-invoke the pipeline.

## 11. Deterministic Guarantees

For schema version `pecs.query_pipeline.v1`:

1. **Input determinism**: Identical workspace state, identical query tokens, and identical budget parameters produce identical JSON output.
2. **Hash stability**: `graph_hash` and `registry_hash` are stable across repeated builds of the same inputs.
3. **Cluster stability**: Cluster IDs and ordering are stable for identical inputs.
4. **Navigation stability**: For unchanged files, navigation node/edge sets and line ranges are stable across repeated queries.
5. **Serialization stability**: JSON output uses sorted keys and deterministic collection ordering.

## 12. Versioning Policy

- The response envelope contains `schema: "pecs.query_pipeline.v1"`.
- A new schema version is introduced only when:
  - A required field is removed or re-typed.
  - The correlation scoring contract changes.
  - Fixed weights change.
  - The cluster ID format changes.
- Additive field additions within the same schema version do not require a version bump.
- Consumers must inspect `schema` and reject unknown major versions.

## 13. Artifact Budget Policy

| Artifact | Budget default | Consumer expectation |
|----------|----------------|----------------------|
| Evidence clusters per response | `--max-clusters` (default 3) | Consumers must handle zero clusters gracefully. |
| Navigation nodes per response | `--max-clusters` × seeds expanded to `--max-nodes` (default 40) | Consumers must paginate or truncate if they impose tighter UI limits. |
| Navigation expansion depth | `--max-depth` (default 2) | Consumers may request depth 0 for seed-only projection. |
| Line range resolution | Per build, per file, mtime-bounded | No persistent cache is exposed. |

Consumers may request tighter budgets but cannot exceed the implementation's hard-coded defaults through the CLI.

## 14. Backward Compatibility Policy

- Schema version `pecs.query_pipeline.v1` is guaranteed to retain all fields documented in this specification.
- New optional fields may be added without a version bump.
- Consumers must ignore unknown fields (tolerant reader).
- Legacy `.pecs` artifacts and legacy consumers remain unchanged; the Query Pipeline is additive.
- `deterministic: true` is a permanent guarantee for this schema version.

## 15. Consumer Compliance Checklist

- [ ] Invoke `pecs query-pipeline` with `--terms` split into individual tokens (or rely on CLI whitespace splitting).
- [ ] Parse `schema` and validate it is `pecs.query_pipeline.v1`.
- [ ] Handle `cluster_count == 0` and `node_count == 0` gracefully.
- [ ] Use `file_path` and `line_range` for source navigation; re-invoke the pipeline when files change.
- [ ] Treat `evidence_breakdown` as advisory diagnostic data, not as a ranking API.
- [ ] Ignore unknown JSON fields.
- [ ] Do not cache Navigation Graphs across file modifications.
