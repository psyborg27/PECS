# PECS Design Principles

These principles govern the architecture and operation of PECS-PRO v2.

## 1. Continuity Is Execution-Topological

Continuity in complex engineering systems is derived from runtime composition and execution paths, not from file hierarchy alone. PECS reconstructs:

- signal-slot chains
- dispatch propagation
- QAction and menu ownership
- overlay and viewer propagation
- subprocess orchestration
- callback and execution chains

This makes locality retrieval grounded in how the system actually runs.

## 2. PECS-PRO Is the Single Continuity Authority

PECS-PRO owns all runtime topology and continuity state. PECS-LITE is a stateless projection adapter that queries PECS-PRO artifacts. No consumer independently scans the workspace or reconstructs topology.

## 3. Deterministic Artifacts

Given identical inputs, PECS produces identical outputs:

- `graph_hash` and `registry_hash` are stable across rebuilds.
- Timestamps are excluded from content hashes.
- JSON outputs use `sort_keys=True` and deterministic ordering.
- Evidence weights and correlation scoring are fixed and explicit.

## 4. Structural Evidence Only

PECS does not use AI, embeddings, or semantic search. Evidence is structural:

- package layout
- module and file names
- imports and exports
- class, method, and function names
- ownership and runtime zones
- graph topology

## 5. Generated Infrastructure Is Not Sourcecode

Files under `.pecs/` are generated continuity infrastructure. They must never be edited as engineering sourcecode. Models use `.pecs/` artifacts to locate live workspace modules, then edit those modules.

## 6. Authority-Driven Decomposition

Components are organized around authority boundaries, not feature areas. There is one graph authority, one registry authority, one evidence authority, one query authority, and one export authority. Parallel or duplicate authorities are avoided.

## 7. Stateless Projection Layer

PECS-LITE is intentionally stateless, lean, query-driven, and projection-only. It reads PECS-PRO artifacts and returns compact runtime target projections without mutating the workspace.

## 8. Preserve-First Operational Lifecycle

Bootstrap, refresh, rebind, and rebuild operations preserve existing continuity state, chat history, and telemetry history. Destructive reset remains an explicit manual action only.

## 9. Consumer-Agnostic Canonical Contract

All consumers use the same canonical query and projection contract. Consumer adapters translate consumer-specific payloads into the canonical form and translate projections back, but the underlying authority and scoring are consumer-independent.

## 10. Observability Without Orchestration

Daemon observability is lightweight and local: small JSONL logs under `.pecs/logs/`, no external telemetry services, and no orchestration state machine. Events reflect actual runtime steps and are useful for operational diagnosis.
