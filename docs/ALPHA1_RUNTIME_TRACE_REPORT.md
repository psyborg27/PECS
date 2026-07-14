# ALPHA1 Runtime Trace Report

## Summary

This trace records the actual execution of the `pecs upgrade-workspace` code path in the current repo environment, using a temporary reproduction workspace containing a stale `.pecs/pecs_pro` directory.

The observed behaviour was:
- `.pecs/pecs_pro` was detected by the upgrade pipeline
- It was inserted into both `plan.legacy_artifacts` and `plan.stale_workspace_runtime_paths`
- `_perform_obsolete_cleanup()` iterated over it and removed it using `shutil.copytree()` and `shutil.rmtree()`
- Verification then passed because the stale path had already been removed
- The final reported pipeline status in this trace was `success=False` due to canonical validation failure, not because of `.pecs/pecs_pro`

This report is based on instrumented execution, not inferred intent.

---

## Environment and instrumentation

- Repo root: `/Users/raj/Developer/PECS`
- Python runtime: `/Users/raj/Developer/PECS/.venv/bin/python`
- `pecs` entrypoint: `/Users/raj/Developer/PECS/.venv/bin/pecs`
- `pecs_pro` package loaded from `/Users/raj/Developer/PECS/pecs_pro/__init__.py`
- Reproduction workspace created at `/tmp/pecs_runtime_trace_workspace`
- Stale directory created: `/tmp/pecs_runtime_trace_workspace/.pecs/pecs_pro`
- Instrumentation logged to `/tmp/pecs_runtime_trace.log`

The actual execution traced the same code paths in `pecs_pro/upgrade_workspace_pipeline.py`, `workspace_assets_manager.py`, and `install_workspace_integration.py`.

---

## Exact execution trace

### 1. Detection of `.pecs/pecs_pro`

The stale runtime path was detected by two functions:

- `pecs_pro/upgrade_workspace_pipeline.py::UpgradeWorkspacePipeline._detect_stale_workspace_runtime_paths()`
  - Observed log: `_detect_stale_workspace_runtime_paths returned ['.pecs/pecs_pro']`
  - Actual value: `['.pecs/pecs_pro']`

- `pecs_pro/upgrade_workspace_pipeline.py::UpgradeWorkspacePipeline._detect_legacy_artifacts()`
  - Observed log: `_detect_legacy_artifacts returned ['.pecs/pecs_pro']`
  - Actual value: `['.pecs/pecs_pro']`

So yes: `.pecs/pecs_pro` was actually detected.

### 2. Insertion into plan fields

Observed values immediately before cleanup:
- `plan.legacy_artifacts=['.pecs/pecs_pro']`
- `plan.stale_workspace_runtime_paths=['.pecs/pecs_pro']`

Therefore `.pecs/pecs_pro` was inserted into both lists.

### 3. Contents of `plan.legacy_artifacts` before cleanup

The trace shows:

- `BEFORE _perform_obsolete_cleanup plan.legacy_artifacts=['.pecs/pecs_pro'] plan.stale_workspace_runtime_paths=['.pecs/pecs_pro']`

Exact contents:
- `['.pecs/pecs_pro']`

### 4. Iteration in `_perform_obsolete_cleanup()`

The trace shows `_perform_obsolete_cleanup()` iterated over `.pecs/pecs_pro`.

No exclusion branch prevented it.

The exact loop branch taken was:
- `for path_name in self.plan.legacy_artifacts if self.plan else []:`
- `path_name` value: `'.pecs/pecs_pro'`
- `target = self.workspace_root / path_name`
- `target.exists()` was true

### 5. Exact execution path for `.pecs/pecs_pro`

The executed path in `_perform_obsolete_cleanup()` was:

1. `target = workspace_root / '.pecs/pecs_pro'`
2. `if not target.exists(): continue` — skipped because it existed
3. `backup_dir = workspace_root / '.pecs/backups'`
4. `backup_dir.mkdir(parents=True, exist_ok=True)`
5. `timestamp = ...`
6. `backup_path = backup_dir / f'stale_obsolete_{path_name.replace('/', '_')}_{timestamp}'`
7. `if target.is_dir():` took the directory branch
8. `shutil.copytree(target, backup_path, ignore=shutil.ignore_patterns('.git'))`
9. `shutil.rmtree(target, ignore_errors=True)`
10. appended `path_name` to `removed`

### 6. Execution of `shutil.rmtree()` / `shutil.move()`

Observed instrumentation:
- `shutil.copytree called args=(PosixPath('/private/tmp/pecs_runtime_trace_workspace/.pecs/pecs_pro'), PosixPath('/private/tmp/pecs_runtime_trace_workspace/.pecs/backups/stale_obsolete_.pecs_pecs_pro_20260714_160450')) kwargs={'ignore': <function ignore_patterns.<locals>._ignore_patterns at 0x109f741f0>}`
- `shutil.rmtree called args=(PosixPath('/private/tmp/pecs_runtime_trace_workspace/.pecs/pecs_pro'),) kwargs={'ignore_errors': True}`

So yes, `shutil.rmtree()` executed for `.pecs/pecs_pro`.

### 7. Branches preventing execution

No branch prevented execution in `_perform_obsolete_cleanup()` for `.pecs/pecs_pro`.

The path was not excluded by any conditional; it satisfied all conditions to be removed.

### 8. Exception handlers that could swallow failure

The actual cleanup path contains two exception handlers that could swallow failure:

- `pecs_pro/upgrade_workspace_pipeline.py::UpgradeWorkspacePipeline._perform_obsolete_cleanup()`
  - `except Exception as e:`
  - logs `Failed to remove obsolete path %s: %s`
  - continues to next path

- `install_workspace_integration.py::_cleanup_stale_local_runtime_copy()`
  - `except Exception:`
  - `continue`
  - `# Do not fail install because of cleanup; this is remediation only.`

In this trace, neither exception handler was triggered for `.pecs/pecs_pro`.

### 9. If cleanup failed: `removed_files` empty?

Not applicable. In this trace cleanup succeeded and `removed_files` was `['.pecs/pecs_pro']`.

### 10. If cleanup succeeded, why would the directory still exist?

In this actual trace, it did not exist afterwards.

Final state log:
- `final .pecs/pecs_pro exists=False`
- final `.pecs` entries did not include `pecs_pro`

So the traced code path removed the directory successfully.

### 11. Recreation of `.pecs/pecs_pro`

No later stage recreated `.pecs/pecs_pro` in this trace.

The main post-cleanup stages were:
- `_cleanup_stale_local_runtime_copy()` called after legacy install, but `.pecs/pecs_pro` was already absent
- `_run_workspace_bridge('refresh')`
- `_run_verify_workspace()` / `_run_doctor()` / `_run_workspace_bridge('validate')`
- `_run_canonical_verification()`

None of these create `.pecs/pecs_pro`.

### 12. Why did `verify_installation()` not fail?

Actual verification path:
- `WorkspaceAssetsManager.verify_installation()` executed after cleanup
- It checked manifest-required asset paths from `verification_config` (empty in current manifest) and launchers/install-root invariants
- The stale runtime path `.pecs/pecs_pro` was absent at verification time
- The instrumentation logged:
  - `verify_installation result valid=True errors=[] warnings=[] checks={...}`

Therefore verification passed because the stale path had already been removed.

### 13. Which validation result ultimately allowed success?

In this trace, `report.success` was `False`.

The pipeline final success value is computed as:

```python
report.success = (
    validation_results.get("verify", False)
    and validation_results.get("doctor", False)
    and bool(report.canonical_verification.get("valid", False))
)
```

Observed values:
- `_run_verify_workspace returned True`
- `_run_doctor returned True`
- `report.canonical_verification['valid']` = `False`

So the pipeline did not reach `success=true` in this execution because canonical validation failed.

### 14. Could doctor/canonical validation pass while `.pecs/pecs_pro` still exists?

In this trace, `.pecs/pecs_pro` did not exist during verification because it was removed earlier.

If `.pecs/pecs_pro` had still existed at verification, `WorkspaceAssetsManager._verify_install_root_references()` contains a hardcoded check that would append an error:
- `Stale workspace-local PECS runtime copy detected: .pecs/pecs_pro`
- and set `result['valid'] = False`

So on the actual verification path, a remaining `.pecs/pecs_pro` would cause `verify_installation()` to fail.

However, the pipeline’s final `success` also depends on canonical validation; in this trace the canonical stage was already failing independently.

---

## Root cause and responsible function

### Root cause in this trace

The actual execution path removed `.pecs/pecs_pro` before verification.

The responsible function for removing `.pecs/pecs_pro` was:
- `pecs_pro/upgrade_workspace_pipeline.py::UpgradeWorkspacePipeline._perform_obsolete_cleanup()`

This function executed `shutil.copytree()` to back up the directory and `shutil.rmtree()` to remove it.

### Responsible cleanup function

- Primary cleanup: `_perform_obsolete_cleanup()`
- Secondary cleanup attempt: `install_workspace_integration.py::_cleanup_stale_local_runtime_copy()` (executed but no longer needed)

### Actual failure point in this trace

There was no failure removing `.pecs/pecs_pro` in this run.

The trace indicates the observed final `success=False` came from canonical validation, not from stale runtime cleanup.

---

## Code location references

- `pecs_pro/upgrade_workspace_pipeline.py:304` — `_detect_legacy_artifacts`
- `pecs_pro/upgrade_workspace_pipeline.py:334` — `_detect_stale_workspace_runtime_paths`
- `pecs_pro/upgrade_workspace_pipeline.py:481` — `_perform_obsolete_cleanup`
- `install_workspace_integration.py:1765` — `_cleanup_stale_local_runtime_copy`
- `install_workspace_integration.py:1790` — `install_workspace`
- `workspace_assets_manager.py:309` — `verify_installation`
- `workspace_assets_manager.py:355` — `_verify_install_root_references`

---

## Note

This report reflects the actual executed code path and logged runtime values from the traced upgrade run. No code was modified permanently.
