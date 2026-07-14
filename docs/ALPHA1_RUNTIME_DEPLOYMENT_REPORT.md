# ALPHA1 Runtime Deployment Report

**Date:** 2026-07-14
**Repository:** PECS-PRO v2 (branch: alpha)
**Objective:** Complete the Alpha 1 runtime deployment architecture so that every upgraded workspace executes the current PECS runtime rather than stale workspace-local copies.

---

## Audit Verdict

| # | Requirement | Status | Notes |
|---|-------------|--------|-------|
| 1 | Executables invoked from workspace come from installed runtime | ✅ **Resolved** | Bridge scripts no longer copied; all invocation paths resolve via `install_root.json` or installed package imports |
| 2 | Launcher scripts resolve correctly after runtime cleanup | ✅ **Resolved** | `.pecs/run_pecs.sh`, `.pecs/run_pecs_daemon.sh` read `install_root.json` at runtime |
| 3 | Workspace bridge scripts always execute current runtime | ✅ **Resolved** | `run_bridge.py` delegates to `python -m workspace_bridge_cli` via subprocess; `_run_workspace_bridge` imports from `scripts` package |
| 4 | Daemon launchers execute current runtime | ✅ **Resolved** | `run_pecs_daemon.sh` resolves via `install_root.json` → console script or `python -m run_pecs_daemon` |
| 5 | No duplicated runtime implementations | ✅ **Resolved** | Removed `launch_pecs_lite_v2_daemon.sh` (dead code); bridge scripts no longer copied to workspace |
| 6 | Upgrade-workspace is deterministic | ✅ **Resolved** | Upgrade pipeline reproduces same assets as fresh install; old bridge copies cleaned up via `UPGRADE_OBSOLETE_PATHS` |
| 7 | Fresh install and upgrade produce identical runtime architecture | ✅ **Resolved** | Both paths call `install_workspace()` which creates the same thin-delegate bridge; no file copies of runtime code |
| 8 | No version drift between repository and upgraded workspace | ✅ **Resolved** | Bridge logic imports from installed `scripts` package—always current. Only thin launchers are workspace-local |
| 9 | No manual copying of runtime files required | ✅ **Resolved** | Only thin launchers (`.sh`, `.ps1`, `.cmd`) and `run_bridge.py` (delegate) are created in workspace |
| 10 | Installer, verifier, and upgrade pipeline agree on runtime authority | ✅ **Resolved** | All three reference `install_root.json` as the single source of truth; `scripts` package is imported from installed runtime |

---

## Files Modified

| File | Change |
|------|--------|
| `scripts/__init__.py` | **Created** — Makes `scripts/` an importable Python package |
| `scripts/validate_workspace_continuity.py` | Changed bare import `from export_workspace_continuity` → relative `from .export_workspace_continuity` |
| `pyproject.toml` | Added `scripts*` to `tool.setuptools.packages.find` include list |
| `setup.py` | Added `scripts*` to `find_packages` include filter |
| `workspace_bridge_cli.py` | Changed `_run_workspace_bridge` from subprocess-calling workspace-local `run_bridge.py` to importing directly from `scripts.export_workspace_continuity` / `scripts.validate_workspace_continuity` |
| `install_workspace_integration.py` | Removed file-copying of `export_workspace_continuity.py` and `validate_workspace_continuity.py` to `.pecs/bridge/`; replaced `run_bridge.py` inline content with thin subprocess delegate to `python -m workspace_bridge_cli`; updated all tool wrappers (`.cmd`, `.ps1`) to prefer `python -m append_ai_chat_history` over local copies |
| `update_ai_chat_history.sh` | Changed from running local `append_ai_chat_history.py` to preferring `python -m append_ai_chat_history` with local fallback |
| `workspace_assets/workspace_assets_manifest.json` | Removed `.pecs/bridge/export_workspace_continuity.py` and `.pecs/bridge/validate_workspace_continuity.py` from `upgrade.update_files` |
| `pecs_pro/upgrade_workspace_pipeline.py` | Added `.pecs/bridge/export_workspace_continuity.py` and `.pecs/bridge/validate_workspace_continuity.py` to `UPGRADE_OBSOLETE_PATHS` |
| `launch_pecs_lite_v2_daemon.sh` | **Deleted** — Dead code referencing deprecated `run_pecs_lite_v2_daemon.py` |

---

## Architecture Decisions

### 1. Bridge scripts are never workspace-local copies

**Before:** `export_workspace_continuity.py` and `validate_workspace_continuity.py` were file-copied from `scripts/` into each workspace's `.pecs/bridge/`. The `run_bridge.py` imported from these local copies. Any update to the source scripts required a full workspace reinstall to take effect.

**After:** The `scripts/` directory is a proper Python package (`scripts/__init__.py`). The `_run_workspace_bridge` function in `workspace_bridge_cli.py` imports directly from `scripts.export_workspace_continuity` and `scripts.validate_workspace_continuity` — always the current installed version. The workspace-local `run_bridge.py` is a thin subprocess delegate that calls `python -m workspace_bridge_cli` via the Python resolved from `install_root.json`.

### 2. Single runtime authority: `install_root.json`

All workspace launchers (`.sh`, `.ps1`, `.cmd`) read `install_root.json` at runtime to resolve:
- The PECS install root path
- The Python executable from the install's virtual environment
- Console script paths for `pecs`, `pecs-pro-daemon`

This ensures that even if the venv is moved, only the `install_root.json` needs updating.

### 3. Tool scripts prefer installed modules

The `append_ai_chat_history` tool wrappers (`.cmd`, `.ps1`) now attempt `python -m append_ai_chat_history` first, falling back to the workspace-local copy. Since `append_ai_chat_history` is in `py-modules` and always installed, the primary path uses the current runtime.

### 4. Dead code removal

`launch_pecs_lite_v2_daemon.sh` was removed. It referenced `run_pecs_lite_v2_daemon.py` which has been a no-op (deprecation warning + exit 1) since May 2026. All daemon operations use `launch_pecs_daemon.sh` or `.pecs/run_pecs_daemon.sh`.

---

## Invocation Flow (After Fixes)

```
VS Code Task → .pecs/bridge/run_bridge.sh
                   ↓
              reads install_root.json
                   ↓
              runs .pecs/bridge/run_bridge.py
                   ↓
              reads install_root.json → resolves installed python
                   ↓
              python -m workspace_bridge_cli refresh/validate
                   ↓
              _run_workspace_bridge()
                   ↓
              imports scripts.export_workspace_continuity (installed package)
              OR
              imports scripts.validate_workspace_continuity (installed package)
```

```
VS Code Task → .pecs/run_pecs_daemon.sh
                   ↓
              reads install_root.json
                   ↓
              pecs-pro-daemon console script OR python -m run_pecs_daemon
```

```
Tool invocation → .pecs/tools/append_ai_chat_history.cmd
                       ↓
                  python -m append_ai_chat_history (installed module)
                       ↓
                  (fallback: local copy if module unavailable)
```

---

## Validation Results

- **Unit tests:** 40/40 passed
- **Import validation:** `from scripts.export_workspace_continuity import export_workspace_continuity` ✅
- **Import validation:** `from scripts.validate_workspace_continuity import validate_workspace_continuity` ✅
- **Import validation:** `import append_ai_chat_history` ✅
- **Bridge function calls:** `_run_workspace_bridge(temp_workspace, 'refresh')` completed without error ✅
- **Bridge function calls:** `_run_workspace_bridge(temp_workspace, 'validate')` completed without error ✅
- **Package reinstall:** `pip install -e .` succeeds with new `scripts*` package discovery ✅

---

## Remaining Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Workspace-local `.venv` vs install-root `.venv` mismatch | Low | Bridge launchers read `install_root.json` and activate the install-root venv. If users manually change `python_path`, behavior could drift. |
| Old workspaces still have stale bridge copies | Low | `UPGRADE_OBSOLETE_PATHS` lists `.pecs/bridge/export_workspace_continuity.py` and `.pecs/bridge/validate_workspace_continuity.py` for cleanup during upgrade. |
| `append_ai_chat_history.py` still copied as fallback | Low | Fallback file won't be used unless the installed module is unavailable. Could be deprecated in future. |
| No content-level staleness detection | Low | Verifier checks file existence and `install_root.json` path validity. Does not checksum-compare workspace files against source. |
