# Determinism Audit Report

## Validation behavior

- `scripts/validate_workspace_continuity.py` now performs a read-only determinism check.
- It no longer calls `export_workspace_continuity()` on the validated workspace.
- `validation_mode` is explicitly returned as `read_only`.
- `artifact_writes` is explicitly returned as `0`.

## Bridge refresh behavior

- `bash .pecs/bridge/run_bridge.sh <workspace> refresh` continues to write `.pecs/continuity/*` artifacts.
- Refresh is the explicit write path; validate is the explicit read-only path.
- The current bridge CLI returns JSON results from refresh/validate.

## Artifact rewrites

- Continuity exports create `active_topology.json`, `locality_state.json`, `engineering_continuity_state.json`, and markdown summaries.
- The validation script now compares stable hashes and mtimes without introducing new writes.

## Serialization stability

- JSON output is written with `sort_keys=True` in `export_workspace_continuity.py` and validation helpers.
- Markdown output is normalized before write, preserving stable text content.

## Timestamp churn

- Validation does not update continuity mtimes.
- Chat event appends still generate `ts` values, but these are expected for new event records.
- Continuity export writes `updated_at` only for engineering continuity state.

## Hidden mutation paths

- No hidden artifact mutation is present in validation.
- `PECSProQueryAdapter` and `RuntimeContextResolver` are read-only.
- Runtime observability reads daemon health artifacts but does not write them.

## Runtime observability behavior

- `PECSProQueryAdapter._runtime_observability_available()` only reads `.pecs/daemon_health.json`.
- The runtime projection path is deliberately separated from artifact mutation.

## Conclusion

The current code base supports deterministic validation as a read-only operation and explicit refresh as the write operation.
The main risk to determinism is refresh-generated continuity state, not validation or runtime projection.
