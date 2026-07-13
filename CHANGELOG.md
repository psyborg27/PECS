# PECS Changelog

## PECS Core v1 Alpha 1

### Overview

PECS Core v1 Alpha 1 completes the deterministic, topology-first architectural retrieval pipeline. It establishes the canonical in-memory models and CLI interface through which PECS-PRO exposes workspace locality to AI consumers without relying on semantic search, embeddings, or non-deterministic reasoning.

### Major Architectural Additions

- **Workspace Graph** — A single in-memory canonical graph of the workspace. Replaces parallel RuntimeGraph/ExecutionGraph/OwnershipGraph families with unified nodes, edges, authority levels, and deterministic hashing.
- **Workspace Registry** — A deterministic registry that classifies workspace components as user-facing **Features** or **Infrastructure Units** and links support modules to the features they serve.
- **Evidence Correlation Engine** — Ranks workspace nodes against query terms using explicit weighted evidence sources and tier-based evidence fusion, producing deterministic Evidence Clusters.
- **Navigation Builder** — Transforms selected Evidence Clusters into a bounded projected subgraph with live AST-based line-range resolution.
- **Query Pipeline** — Exposes the full retrieval flow through the CLI as `pecs query-pipeline`, emitting deterministic JSON responses with canonical schema `pecs.query_pipeline.v1`.

### Documentation

- **Architecture Baseline** (`PECS_ARCHITECTURE_BASELINE.md`) — Canonical specification of the implemented PECS-PRO v2 architecture.
- **Architectural Projection Specification** (`PECS_ARCHITECTURAL_PROJECTION_SPEC.md`) — Canonical projection and consumer contract specification.
- **Documentation Hierarchy** (`docs/`) — Structured guides covering getting started, installation, architecture, components, integrations, troubleshooting, roadmap, design principles, and glossary.
- **Design Principles** (`docs/design-principles.md`) — Core deterministic principles governing topology, authority, stateless projection, and preserve-first operations.
- **Glossary** (`docs/glossary.md`) — Definitions of primary PECS terminology.

### Architectural Changes

PECS Core v1 Alpha 1 transitions the system from a continuity-first, file-hierarchical retrieval model to a deterministic architectural correlation and navigation model. Retrieval is now navigation-first: query terms are correlated against structural evidence, clusters are selected, and a bounded Navigation Graph is projected for the consumer. Continuity evidence remains a weighted tier in evidence fusion, but the primary retrieval path is structural and deterministic.

### Deterministic Guarantees

- Identical workspace inputs produce identical Workspace Graph `graph_hash` values; timestamps are excluded from content hashes.
- Identical graphs produce identical Workspace Registry `registry_hash` values.
- Evidence Correlation uses fixed weights, sorted iteration, and stable cluster IDs derived from root package and content hash.
- Navigation Graph output is stable for identical query terms, graph, and budget parameters against unchanged files.
- Query Pipeline JSON responses are serialized with `sort_keys=True` and deterministic nested object ordering.

### Known Limitations

- Method-level and class-level navigation expansion is still evolving.
- Extension-point inference is pending.
- Impact graph construction is pending.
- Consumer integrations remain advisory and are not fully enforced at runtime.
- Auto-TOC validation is pending.

### Validation Status

| Area | Status |
|------|--------|
| Architecture | Complete |
| Implementation | Complete |
| Documentation | Complete |
| Integration | In Progress |
| Auto-TOC Validation | Pending |

**Consumer Validation**

- Copilot: Pending
- Continue: Pending
- Kimi: Pending
- Command Code: Pending

### Next Milestone

**PECS Validation**

The next engineering phase focuses on validating and hardening the Core v1 architecture through integrations and benchmarks:

- Auto-TOC validation
- Copilot integration
- Continue integration
- Kimi integration
- Command Code integration
- Projection quality benchmarking
