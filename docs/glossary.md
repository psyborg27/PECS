# PECS Glossary

## PECS-PRO

The continuity authority. Reconstructs runtime topology, ownership, and workspace structure, and writes deterministic continuity artifacts under `.pecs/`.

## PECS-LITE

A stateless projection adapter. Queries PECS-PRO artifacts and returns compact, model-shaped locality guidance. Does not scan the workspace or own continuity state.

## Workspace Graph

The single in-memory canonical graph of a workspace. Contains language-agnostic nodes and edges with deterministic identity, hashing, and serialization.

## Workspace Registry

A deterministic registry derived from the Workspace Graph. Classifies workspace components as user-facing **Features** or **Infrastructure Units** and indexes nodes by membership.

## Evidence Correlation Engine

Ranks workspace nodes against query terms using deterministic structural evidence. Returns ranked **Evidence Clusters** without AI or semantic search.

## Navigation Builder

Transforms selected Evidence Clusters into a bounded projected subgraph with resolved line ranges. Built on demand per query and never persisted.

## Query Pipeline

The CLI flow `query terms → Evidence Correlation → Cluster Selection → Navigation Graph → JSON response`. Entry point: `pecs query-pipeline`.

## Locality

The set of runtime-relevant files, classes, functions, and execution neighborhoods associated with a task or query term.

## Topology

The execution structure of the workspace: nodes, edges, signals, slots, dispatch chains, ownership relationships, and runtime zones.

## Continuity

Preserved engineering memory linking issues, localities, outcomes, and validations across sessions. Used to ground AI reasoning in prior confirmed work.

## Authority

The definitive source for a given kind of information. PECS-PRO is the authority for runtime topology and continuity; workspace modules are the authority for engineering sourcecode.

## Projection

A bounded, consumer-shaped response produced by PECS-LITE from PECS-PRO artifacts. Includes runtime targets, ownership hotspots, evidence fusion scores, and diagnostics.

## Artifact

A generated file under `.pecs/`, such as `active_context.json`, `locality_index.json`, `topology_compact.json`, or `compact_bundle.json`. Artifacts are infrastructure, not sourcecode.

## Daemon

The `workspace_continuity_daemon.py` process that watches the workspace, rebuilds topology and continuity artifacts on change, and emits structured logs.

## Bridge

Workspace-local scripts under `.pecs/bridge/` that execute refresh, export, and validation commands without requiring direct PECS-PRO invocation.

## Feature

A user-facing workspace component identified by the Workspace Registry, typically with public UI registration, controller ownership, runtime evidence, or entrypoint membership.

## Infrastructure Unit

A workspace component that supports Features but is not itself user-facing, such as utility modules, data models, or internal services.

## Evidence Cluster

A group of workspace nodes ranked by the Evidence Correlation Engine for a set of query terms. Clusters are grouped by root package and sorted by cumulative score.

## Evidence Fusion

The tier-based scoring of runtime target candidates from static, runtime, continuity, and validation evidence sources.

## Entrypoint

A file or module that launches executable workspace behavior, used by the daemon and graph builder to seed runtime-reachable topology.

## Runtime Zone

A logical runtime region or activation area identified during topology reconstruction, used to group related runtime activity.
