# Installer Update Report

Date: 2026-05-20

## Installer Changes Implemented
File updated:
- install_workspace_integration.py

### Added Global Runtime Registry Provisioning
- Added constants and helpers to manage:
  - ~/.pecs/config.json
  - ~/.pecs/runtime_registry.json
  - ~/.pecs/GOVERNANCE_RUNTIME.md
  - ~/.pecs/MODES.md
- Added _ensure_global_runtime_registry(repo_root) and invoked it in install_workspace(...).

### Health Check Observability Enhancements
health_check(...) now reports:
- runtime_registry_path
- runtime_registry_exists
- governance_runtime_path
- governance_runtime_exists
- modes_path
- modes_exists

### Safety and Upgrade Semantics
- Existing config keys preserved.
- Missing canonical keys added to runtime_registry.json.
- Overlay markdown files created only when missing.
- Installer remains upgrade-safe and backward compatible.

### Latent Bug Remediation
- Added _read_workspace_install_root(workspace_root) to satisfy existing health_check usage.

## Determinism and Scope
- No new framework layers introduced.
- No duplicate bootstrap/registry systems introduced.
- Changes are confined to authoritative installer path.
