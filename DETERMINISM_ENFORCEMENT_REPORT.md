# Determinism Enforcement Report

## Enforcement changes

- Validation now operates in read-only mode.
- `validate_workspace_continuity()` no longer exports or rewrites the target workspace continuity artifacts.
- Bridge validation reports now include:
  - `validation_mode: "read_only"`
  - `artifact_writes: 0`
- `PECSLiteRuntimeV2` runtime output now includes deterministic metadata for runtime mode and artifact behavior.

## Observed validation results

- `bash .pecs/bridge/run_bridge.sh "/Users/raj/Developer/PECS" validate` returned:
  - `deterministic: true`
  - `noop_zero_writes: true`
  - `artifact_writes: 0`
  - `validation_mode: "read_only"`

- `bash .pecs/bridge/run_bridge.sh '/Users/raj/Downloads/auto OCR app' validate` returned the same deterministic and read-only indicators.

## Determinism guarantees

- Read-only validation keeps existing `.pecs` artifact mtimes unchanged.
- Runtime report sections are assembled in insertion order to preserve deterministic JSON output ordering.
- Search plan, locality resolution, and execution scope are all derived from explicit artifact evidence rather than prompt heuristics.
