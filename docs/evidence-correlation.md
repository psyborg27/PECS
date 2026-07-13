# Evidence Correlation

The Evidence Correlation Engine correlates a list of query terms against deterministic workspace evidence and returns ranked Evidence Clusters without semantic search or AI.

## Implementation

- File: `evidence_correlation/engines/evidence_correlator.py`
- Helper: `evidence_correlation/engines/evidence_extractor.py`
- Models: `evidence_correlation/models.py`

## Evidence Sources (14)

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

## Correlation Algorithm

1. `EvidenceExtractor.extract()` builds per-node evidence sets from the graph, registry, and locality payload.
2. `EvidenceCorrelator.correlate(query_terms)`:
   - Normalizes each query term (lowercase, strip, remove `_` and `-`).
   - For each node, scores each evidence source by substring match of any normalized query term in any normalized evidence term.
   - Computes a weighted sum normalized by the total weight sum, producing a score in `[0, 1]`.
   - Drops nodes below `_MIN_CLUSTER_SCORE = 0.01`.
   - Groups surviving nodes into clusters by root package (first segment of the `PECS_ID`).
   - Sorts clusters by cumulative score descending, then by namespace lexicographically.
   - Returns up to `max_clusters` clusters.

## Evidence Fusion

Runtime target candidates are ranked using explicit tier-based evidence fusion in `integrations/pecs_pro_query_adapter.py`:

| Tier | Weight | Evidence |
|------|--------|----------|
| `tier_0_static` | 0.20 | import topology, dependency topology, filesystem structure |
| `tier_1_runtime` | 0.35 | runtime activation evidence, touched files, chain neighborhood |
| `tier_2_continuity` | 0.25 | ownership continuity, hotspots, engineering continuity chains |
| `tier_3_validation` | 0.20 | user-confirmed validation, error-to-object correlation, accepted/rejected fix validation |

Formula: `fused_score = sum(weight[tier] * tier_score[tier])`

Each ranked file includes `tier_scores`, `tier_sources`, `provenance`, and `fused_score`.

## Deterministic Guarantees

- Fixed weights.
- Sorted iteration over nodes, edges, and evidence terms.
- Identical query terms and graph produce identical cluster ranking and cluster IDs.

## Relationship to Other Components

- Evidence sets are extracted from the [Workspace Graph](workspace-graph.md) and [Workspace Registry](workspace-registry.md).
- Selected clusters feed the [Navigation Builder](navigation-builder.md).
- The [Query Pipeline](query-pipeline.md) orchestrates the full correlation flow.
