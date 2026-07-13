# Governance Hydration Report

Date: 2026-05-20

## Hydration Sequence
1. Resolve workspace root.
2. Resolve global PECS home (~/.pecs) and config/runtime registry locations.
3. Resolve PECS root from config.json; fallback to workspace .pecs/config/install_root.json when config is missing.
4. Detect runtime_registry.json and export path.
5. Resolve governance_runtime and modes paths dynamically from registry values.
6. Validate presence of overlays and export active/inactive flags.
7. Export retrieval priority when present.
8. Continue into workspace PECS detection and daemon/retrieval readiness checks.
9. Export degraded continuity mode when artifacts are unavailable.

## Observability Emitted
Loader now emits:
- runtime registry detected/missing
- governance runtime detected/missing
- operational modes detected/missing
- governance hydration active/inactive
- degraded continuity mode active/inactive

## Hard-Failure Avoidance
Confirmed behavior:
- No hard fail when runtime_registry.json is missing.
- No hard fail when governance runtime file is missing.
- No hard fail when modes file is missing.
- No hard fail solely due to absent governance overlays.

## Deterministic Governance Retrieval
- Retrieval order remains deterministic via runtime registry retrieval_priority values.
- Hydration is dynamic, registry-driven, and path-resolved at runtime.
- Governance and mode overlays are treated as advisory runtime context.
