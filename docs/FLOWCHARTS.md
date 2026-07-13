# PECS Alpha 1 Flowcharts

These text diagrams describe the implemented flow in the current repository.

## Workspace Indexing

```
Source files
    ├─ file watcher
    ├─ import resolver
    ├─ entrypoint discovery
    └─ runtime locality extractor
          ↓
   Topology builder
          ↓
   .pecs/locality_index.json
   .pecs/topology_compact.json
```

## Runtime Discovery

```
WorkspaceContinuityDaemon
    ├─ Start
    ├─ Full scan or incremental scan
    ├─ Discover entrypoints
    ├─ Resolve imports and local modules
    ├─ Build reachable file set
    ├─ Populate runtime indexes
    ├─ Build workspace graph + registry
    ├─ Write core artifacts
    ├─ Write daemon state / health
    └─ Observe file changes
```

## Incremental Update

```
File change event
    ├─ is Python file? → yes
    ├─ record changed file
    ├─ run cycle lock
    ├─ rebuild runtime topology
    ├─ update locality payload
    ├─ refresh compact bundle and active context
    └─ write artifacts
```

## Query Processing

```
User query
    ├─ normalize query terms
    ├─ load Workspace Graph + Registry (daemon dumps or rebuild)
    ├─ EvidenceCorrelator.build_index()
    ├─ correlate query terms
    ├─ select clusters
    ├─ NavigationGraphBuilder.build()
    ├─ serialize JSON
    └─ return projection
```

## Projection Generation

```
PECS-LITE wrapper
    ├─ read .pecs artifacts
    ├─ shape runtime targets
    ├─ attach diagnostics
    ├─ enforce profile limits
    └─ return bounded projection
```

## Agent Interaction Cycle

```
AI assistant request
    ├─ consumer adapter normalizes query
    ├─ invoke PECS query pipeline or projection wrapper
    ├─ receive projection JSON
    ├─ render targets and evidence
    └─ developer reviews / edits files
```
