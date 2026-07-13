# New Workspace Bootstrap Report

## Current bootstrap flow

### Primary install/update commands
- `python3 install_workspace_integration.py <workspace_root>`
- `python3 install_workspace_integration.py <workspace_root> --upgrade`
- `python3 workspace_bridge_cli.py bootstrap-workspace --workspace <workspace_root>`

### Refresh and validation
- `bash .pecs/bridge/run_bridge.sh <workspace_root> refresh`
- `bash .pecs/bridge/run_bridge.sh <workspace_root> validate`

## Cold-start initialization

### Import graph construction
- `export_workspace_continuity.py` reads `.pecs/topology_compact.json` and `.pecs/locality_index.json`.
- Topology edges are used to build `active_topology.json` and ownership density.
- `PECS-LITE` uses this topology evidence in `related_files_for()` and `entrypoint_chain_for()`.

### Ownership bootstrapping
- Ownership evidence is bootstrapped from runtime artifacts and curated edges.
- `locality_state.json` includes `ownership_hotspots` derived from topology edge counts.
- `PECS-LITE` uses `ownership_locality_lookup()` to expose a candidate mutation owner.

### Dependency topology mapping
- `topology_compact.json` is the canonical dependency graph source.
- `related_files_for()` and `entrypoint_chain_for()` perform topology-based neighborhood resolution.
- `export_workspace_continuity.py` also computes `continuity_hotspots` from `compact_bundle` and runtime touched files.

### Locality initialization
- `active_context.json` and `compact_bundle.json` seed runtime locality.
- Runtime touched files and active clusters are extracted from runtime event streams.
- `runtime_validation` score measures alignment between runtime evidence and topology.

## Evidence of cold-start functionality

- The system still uses import topology as a first-class signal.
- Runtime evidence is layered on top of static topology through continuity artifacts.
- A workspace with no runtime evidence will still produce unresolved tension markers.

## Degradation analysis

- Current code does not show import-based topology degradation; it remains integral.
- Runtime evidence is additive and used for validation, not sole authority.
- If runtime evidence is absent, the system still maintains topology-first continuity state.

## Conclusion

Current new-workspace bootstrap behavior remains import- and topology-based.
Runtime evidence is incorporated as validation and continuity support, not as a replacement for topology initialization.
