# ALPHA1 Upgrade Pipeline Audit

## Scope

Investigated:
- `pecs_pro/upgrade_workspace_pipeline.py`
- `install_workspace_integration.py`
- `workspace_assets_manager.py`
- `workspace_assets/workspace_assets_manifest.json`

This audit tracks the `pecs upgrade-workspace` CLI path end-to-end, with explicit evidence for backup, obsolete asset detection, cleanup, reporting, and success conditions.

---

## 1. Complete call graph for `pecs upgrade-workspace`

1. `pyproject.toml` registers `pecs = "workspace_bridge_cli:main"`.
2. `workspace_bridge_cli.py::main()` parses CLI args.
3. `workspace_bridge_cli.py::_cmd_upgrade_workspace(args)` is invoked for `upgrade-workspace`.
4. In `_cmd_upgrade_workspace`:
   - `workspace_root` and `repo_root` are resolved.
   - `print_install_root_guidance(repo_root)` may warn on unstable install roots.
   - `validate_dependencies()` is used to ensure `watchdog` is present.
   - `_append_lifecycle_record(..., "upgrade_workspace_started", ...)` writes lifecycle metadata.
   - `pipeline = UpgradeWorkspacePipeline(workspace_root, repo_root)` constructs the pipeline.
   - `report = pipeline.run()` executes the upgrade pipeline.
5. `UpgradeWorkspacePipeline.run()` in `pecs_pro/upgrade_workspace_pipeline.py`:
   - `inspect_workspace()` inspects current workspace state.
   - `classify_artifacts(plan)` classifies managed/generated/legacy assets.
   - `self.manager.install_assets(upgrade=True, verify=False)` deploys workspace assets.
   - `self._perform_obsolete_cleanup()` removes obsolete legacy assets before `install_workspace`.
   - `install_workspace(self.workspace_root, self.repo_root, preserve_existing=True)` runs the legacy installer.
   - `self._capture_deployment_report(report, self.plan)` records deployment-related warnings.
   - `regenerate_artifacts()` refreshes continuity state and rebuilds graph/registry/query artifacts.
   - `restart_daemon_if_required()` may start the workspace daemon if health is bad.
   - `validate_workspace_installation()` performs verify/doctor/validate/canonical checks.
   - `report.after_versions`, `preserved_files`, `merged_files`, `replaced_files`, `elapsed_seconds`, `success` are computed.
6. After return to `_cmd_upgrade_workspace`:
   - warnings are emitted.
   - `_append_lifecycle_record(..., "upgrade_workspace_completed", ...)` is appended.
   - report is printed as JSON.
   - `_cmd_upgrade_workspace` exits with failure if `report.success` is false.

### Internal pipeline branches

- `regenerate_artifacts()` performs:
  - `_run_workspace_bridge("refresh")`
  - `_ensure_workspace_graph_and_registry()`
  - `_exercise_query_pipeline()`
- `validate_workspace_installation()` performs:
  - `_run_verify_workspace()` => `workspace_bridge_cli.py::_cmd_verify_workspace` => `WorkspaceAssetsManager.verify_installation()`
  - `_run_doctor()` => `workspace_bridge_cli.py::_cmd_doctor`
  - `_run_validate_workspace()` => bridge validate via `_run_workspace_bridge("validate")`
  - `_run_canonical_verification()` => `validation.canonical_workspace_validator.run_canonical_workspace_validation()`

---

## 2. Exactly where backups occur

Backups occur in three distinct places:

1. `workspace_assets_manager.py::WorkspaceAssetsManager._backup_existing_files(upgrade=True)`
   - Called from `WorkspaceAssetsManager.install_assets(upgrade=True, verify=False)`.
   - Backs up existing user-managed files to `workspace_root / .pecs / backups`.
   - Files backed up:
     - `.github/copilot-instructions.md`
     - `.continue/config.yaml`
     - `.vscode/tasks.json`
     - `.vscode/settings.json`
     - `.pecs/PECS_CONSUMER_PROTOCOL.md`
     - `.kimi/instructions.md`
     - `.commandcode/instructions.md`
   - Backup filenames are timestamped, e.g. `copilot-instructions.md__20260714_123456.bak`.

2. `pecs_pro/upgrade_workspace_pipeline.py::UpgradeWorkspacePipeline._perform_obsolete_cleanup()`
   - Called immediately after `manager.install_assets(...)` and before `install_workspace(...)`.
   - Backs up obsolete paths being removed to `workspace_root / .pecs / backups`.
   - Backup filenames are prefixed with `stale_obsolete_`.

3. `install_workspace_integration.py::_cleanup_stale_local_runtime_copy(workspace_root)`
   - Called at the end of legacy install flow in `install_workspace(...)`.
   - Backs up stale runtime copy directories under `workspace_root / .pecs / backups`.
   - Backup filenames are prefixed with `stale_local_runtime_`.

These are the only explicit backup sites in the upgrade/install flow.

---

## 3. Exactly where obsolete assets are detected

Obsolete paths are detected in the upgrade pipeline and later verified in asset verification.

### Detection in upgrade pipeline

1. `pecs_pro/upgrade_workspace_pipeline.py::UpgradeWorkspacePipeline._detect_legacy_artifacts()`
   - Uses `UPGRADE_OBSOLETE_PATHS` to detect workspace artifacts that should be removed during upgrade.
   - `UPGRADE_OBSOLETE_PATHS` includes:
     - `pecs_lite`
     - `run_pecs_lite.sh`
     - `runtime_observability_daemon`
     - `runtime_observability_daemon.py`
     - `start_pecs_daemon.sh`
     - `.pecs/pecs_lite_runtime_projection.json`
     - `.pecs/daemon_lite_v2.pid`
     - `.pecs/daemon_lite_v2_state.json`
     - `.pecs/bridge/run_runtime_topology_build.py`
     - `.pecs/bridge/export_workspace_continuity.py`
     - `.pecs/bridge/validate_workspace_continuity.py`
     - `.pecs/pecs_pro`
     - `.pecs/pecs_pro.egg-info`
     - `.pecs/pecs_pro.dist-info`
     - `docs/README_ALPHA1.md`
   - This returns `plan.legacy_artifacts`.

2. `pecs_pro/upgrade_workspace_pipeline.py::UpgradeWorkspacePipeline._detect_stale_workspace_runtime_paths()`
   - Explicitly detects existing stale runtime copies:
     - `.pecs/pecs_pro`
     - `.pecs/pecs_pro.egg-info`
     - `.pecs/pecs_pro.dist-info`
   - This returns `plan.stale_workspace_runtime_paths`.

### Detection in verification

1. `workspace_assets_manager.py::WorkspaceAssetsManager.verify_installation()`
   - In `_verify_install_root_references()`, it checks for stale workspace-local PECS runtime copies:
     - `.pecs/pecs_pro`
     - `.pecs/pecs_pro.egg-info`
     - `.pecs/pecs_pro.dist-info`
   - If any exist, it appends an error:
     - `Stale workspace-local PECS runtime copy detected: {stale_path}`
   - This makes the asset verification path fail when stale runtime copies remain.

---

## 4. Exactly where obsolete assets are scheduled for removal

Obsolete assets are scheduled for removal in:

- `pecs_pro/upgrade_workspace_pipeline.py::UpgradeWorkspacePipeline._perform_obsolete_cleanup()`
  - Iterates `self.plan.legacy_artifacts` and removes matching files/dirs.
  - Called by `UpgradeWorkspacePipeline.run()` immediately after `manager.install_assets()`.

- `install_workspace_integration.py::_cleanup_stale_local_runtime_copy(workspace_root)`
  - Called by `install_workspace()` near the end of the legacy install.
  - Intended to clean stale `.pecs/pecs_pro*` paths.

The first is the upgrade pipeline’s explicit obsolete-removal phase; the second is legacy remediation during install.

---

## 5. Exactly where obsolete assets are actually removed

Actual removal happens in:

- `pecs_pro/upgrade_workspace_pipeline.py::UpgradeWorkspacePipeline._perform_obsolete_cleanup()`
  - For directories: `shutil.copytree(...); shutil.rmtree(target, ignore_errors=True)`.
  - For files: `shutil.copy2(target, backup_path); target.unlink()`.

- `install_workspace_integration.py::_cleanup_stale_local_runtime_copy(workspace_root)`
  - For directories: `shutil.move(str(path), str(target_backup))`.
  - For files: `shutil.copy2(str(path), str(target_backup)); path.unlink()`.

These are the two concrete removal sites for the stale runtime copy paths.

---

## 6. Exactly where removal failures are handled

Removal failures are handled by swallowing exceptions:

- `pecs_pro/upgrade_workspace_pipeline.py::UpgradeWorkspacePipeline._perform_obsolete_cleanup()`
  - `except Exception as e: logging.getLogger(__name__).error("Failed to remove obsolete path %s: %s", path_name, e); continue`
  - Failure does not propagate; other obsolete paths continue.

- `install_workspace_integration.py::_cleanup_stale_local_runtime_copy(workspace_root)`
  - `except Exception: continue`
  - Errors are ignored entirely; install does not fail because of cleanup.

No explicit failure is returned from either cleanup path.

---

## 7. Exactly where `removed_files` is populated

- `pecs_pro/upgrade_workspace_pipeline.py::UpgradeWorkspacePipeline.run()`
  - `report.removed_files = self._perform_obsolete_cleanup()`

- `_perform_obsolete_cleanup()` returns the list of obsolete paths successfully removed.

---

## 8. Exactly where `success = true` is decided

- `pecs_pro/upgrade_workspace_pipeline.py::UpgradeWorkspacePipeline.run()` computes:

```python
report.success = (
    validation_results.get("verify", False)
    and validation_results.get("doctor", False)
    and bool(report.canonical_verification.get("valid", False))
)
```

- Success depends on three boolean values:
  - `verify` from `_run_verify_workspace()`
  - `doctor` from `_run_doctor()`
  - `canonical_verification.valid` from `_run_canonical_verification()`

- The `validate` bridge result is not directly used in the final `success` boolean.

---

## 9. Whether cleanup failures can still result in success

Yes, cleanup failures can still result in `success=true` if they do not prevent later validation from passing.

- `_perform_obsolete_cleanup()` swallows exceptions and does not affect `report.success` directly.
- `_cleanup_stale_local_runtime_copy()` also swallows exceptions and does not raise.
- However, if stale path remnants remain, `WorkspaceAssetsManager.verify_installation()` will add errors for stale runtime copies and likely cause `verify` to fail, which would make `report.success` false.
- Thus cleanup failures are not automatically fatal, but surviving stale runtime copies are detected by verification and can prevent success.

---

## 10. Whether cleanup occurs before or after deployment

Cleanup occurs in two places relative to deployment:

- Before legacy install:
  - `UpgradeWorkspacePipeline.run()` calls `manager.install_assets(upgrade=True, verify=False)` first, then `self._perform_obsolete_cleanup()`, then `install_workspace(...)`.
  - The code comment explicitly says obsolete cleanup is performed before `install_workspace` so removal is detected and reported.

- After the legacy bridge/launcher deployment inside install:
  - `install_workspace_integration.py::install_workspace()` calls `_cleanup_stale_local_runtime_copy(workspace_root)` at the end.

So the upgrade flow performs cleanup both before and after deployment.

---

## 11. Whether deployment can recreate removed assets

No, deployment does not recreate the obsolete assets listed in `UPGRADE_OBSOLETE_PATHS`.

Evidence:
- `workspace_assets_manager.py::WorkspaceAssetsManager._deploy_assets()` deploys only assets in `workspace_assets/workspace_assets_manifest.json`.
- The manifest does not include any obsolete paths such as `.pecs/bridge/export_workspace_continuity.py`, `.pecs/bridge/validate_workspace_continuity.py`, `.pecs/pecs_pro`, `.pecs/pecs_pro.egg-info`, or `.pecs/pecs_pro.dist-info`.
- `install_workspace_integration.py::_install_bridge_runtime()` writes a thin bridge delegate into `.pecs/bridge/run_bridge.py` and related delegates, but it does not recreate the obsolete runtime copy directories.
- `install_workspace()` then runs `_cleanup_stale_local_runtime_copy()` again, removing stale `.pecs/pecs_pro*` if still present.

Therefore removed obsolete assets are not intentionally recreated by either the manifest-based install or legacy install.

---

## 12. Whether stale workspace runtime copies are actually removed

Yes, stale workspace runtime copies are explicitly removed by the code.

Paths involved:
- `.pecs/pecs_pro`
- `.pecs/pecs_pro.egg-info`
- `.pecs/pecs_pro.dist-info`

Removal mechanisms:
- `UpgradeWorkspacePipeline._detect_stale_workspace_runtime_paths()` discovers these paths.
- `UpgradeWorkspacePipeline._perform_obsolete_cleanup()` removes legacy artifacts from `plan.legacy_artifacts`, including those three paths if present.
- `install_workspace_integration.py::_cleanup_stale_local_runtime_copy(workspace_root)` also removes these same paths during legacy install.
- `WorkspaceAssetsManager.verify_installation()` flags them as errors if they remain.

So stale runtime copies are actually removed by both upgrade-specific cleanup and legacy install cleanup.

---

## 13. Audit for `.pecs/pecs_pro`, `.pecs/pecs_pro.egg-info`, `.pecs/pecs_pro.dist-info`

### Detection functions

- `pecs_pro/upgrade_workspace_pipeline.py::UpgradeWorkspacePipeline._detect_legacy_artifacts()`
  - Detects these paths because they are included in `UPGRADE_OBSOLETE_PATHS`.

- `pecs_pro/upgrade_workspace_pipeline.py::UpgradeWorkspacePipeline._detect_stale_workspace_runtime_paths()`
  - Explicitly reports these three paths in `plan.stale_workspace_runtime_paths`.

- `workspace_assets_manager.py::WorkspaceAssetsManager.verify_installation()`
  - In `_verify_install_root_references()`, it checks these three paths and appends errors if any exist.

### Cleanup functions

- `pecs_pro/upgrade_workspace_pipeline.py::UpgradeWorkspacePipeline._perform_obsolete_cleanup()`
  - Removes any path in `plan.legacy_artifacts`, including these three.

- `install_workspace_integration.py::_cleanup_stale_local_runtime_copy(workspace_root)`
  - Removes these three paths after legacy install.

### Verification functions

- `workspace_assets_manager.py::WorkspaceAssetsManager.verify_installation()`
  - Performs verification and reports stale runtime copies as errors.

- `validation.canonical_workspace_validator.run_canonical_workspace_validation()`
  - Runs the canonical Alpha 1 validation after upgrade; stale runtime copy checks originate in `WorkspaceAssetsManager.verify_installation()`.

### Reporting functions

- `pecs_pro/upgrade_workspace_pipeline.py::UpgradeWorkspacePipeline.run()`
  - Populates `report.removed_files` from `_perform_obsolete_cleanup()`.
  - Populates `report.warnings` from plan workspace health and `install_assets` warnings.

- `workspace_assets_manager.py::WorkspaceAssetsManager.verify_installation()`
  - Appends errors and warnings for verification failures.

- `workspace_bridge_cli.py::_cmd_upgrade_workspace()`
  - Appends lifecycle records for `upgrade_workspace_started`, `upgrade_workspace_completed`, and `upgrade_workspace_failed`.

### Surviving an upgrade

If any of these paths survive an upgrade, the likely reason is one of the cleanup calls raised an exception while removing them and swallowed it.

- `_perform_obsolete_cleanup()` logs the failure and continues.
- `_cleanup_stale_local_runtime_copy()` catches all exceptions and continues.

Those exception paths do not directly mark upgrade failure, but surviving stale runtime copies are later detected by `verify_installation()` and may cause `report.success` to be false.

---

## 14. Role of `workspace_assets_manifest.json`

- The manifest is the authoritative list of managed workspace assets installed by `WorkspaceAssetsManager.install_assets()`.
- It does not include obsolete runtime-copy paths.
- It defines install behavior for current assets, not cleanup behavior.
- Therefore obsolete cleanup is controlled by `pecs_pro/upgrade_workspace_pipeline.py` and `install_workspace_integration.py`, not by the manifest.

---

## Conclusions

- `pecs upgrade-workspace` starts in `workspace_bridge_cli.py::_cmd_upgrade_workspace` and delegates to `UpgradeWorkspacePipeline.run()`.
- Backups occur in asset manager upgrade backup, upgrader obsolete cleanup backup, and legacy install runtime cleanup backup.
- Obsolete asset detection is performed by `UPGRADE_OBSOLETE_PATHS`, stale runtime path detection, and verification logic.
- Obsolete assets are scheduled for removal in `_perform_obsolete_cleanup()` and `_cleanup_stale_local_runtime_copy()`.
- Actual removal is done by `shutil.rmtree`/`unlink` in `_perform_obsolete_cleanup()` and `shutil.move`/`unlink` in `_cleanup_stale_local_runtime_copy()`.
- Removal failures are swallowed and logged; they do not directly stop the upgrade.
- `removed_files` is populated only in the upgrade pipeline from `_perform_obsolete_cleanup()`.
- `success=true` is based on `verify`, `doctor`, and canonical validation, not on cleanup results directly.
- Cleanup failures can still result in success if validation does not fail, but stale runtime copy remnants are independently detected and can make success false.
- Cleanup occurs both before and after installation.
- Deployment does not recreate removed obsolete assets.
- Stale workspace runtime copies are explicitly targeted for removal.

This audit is evidence-only. No code changes were made.

---

**File references:**
- `pyproject.toml`
- `workspace_bridge_cli.py`
- `pecs_pro/upgrade_workspace_pipeline.py`
- `install_workspace_integration.py`
- `workspace_assets_manager.py`
- `workspace_assets/workspace_assets_manifest.json`

**Published:** July 14, 2026

---

If you want, I can also extract exact source-line references to the same audit file for even more direct traceability.
