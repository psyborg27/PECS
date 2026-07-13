# Backward Compatibility Report

Date: 2026-05-20

## Compatibility Goals
- Preserve existing PECS workspace behavior.
- Preserve non-PECS workspace operation with graceful degradation.
- Avoid breaking existing launch/bootstrap paths.

## Validation Summary
- Existing workspace-local artifacts remained intact:
  - .pecs/active_context.json
  - .pecs/locality_index.json
  - .pecs/topology_compact.json
- Workspace install-root bridging remained intact via .pecs/config/install_root.json.
- Global runtime registry overlays were added without replacing workspace-local continuity artifacts.

## Non-Destructive Guarantees
- Global config/registry updates use merge/set-default behavior.
- Governance/Modes overlays are created only if absent.
- No destructive overwrite of existing governance overlay files.

## Runtime Compatibility Notes
- Existing daemon launch path unchanged.
- Existing runtime session/topology engines unchanged.
- Existing PECS retrieval pipeline remains advisory and topology-first.

## Additional Stability Fix
- Fixed a latent installer issue: missing _read_workspace_install_root helper used by health_check.
- Health-check now executes correctly and reports governance hydration observability fields.
