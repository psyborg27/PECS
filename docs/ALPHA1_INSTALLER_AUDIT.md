# ALPHA1 Installer Audit

## Scope

Investigated:
- `install_workspace_integration.py`
- `workspace_assets_manager.py`
- `workspace_assets/workspace_assets_manifest.json`

This audit covers the complete installer lifecycle, backup/merge/preserve/replace/cleanup/verification behaviors, and obsolete runtime file handling.

---

## 1. Installer architecture and flow

### Two-layer installation flow

The workspace installer has two distinct layers:

1. **Manifest-driven asset manager**
   - `workspace_assets_manager.py::WorkspaceAssetsManager.install_assets()`
   - Reads `workspace_assets/workspace_assets_manifest.json`
   - Validates target, backups certain existing files on upgrade, deploys managed assets, optionally verifies installation

2. **Legacy workspace installer**
   - `install_workspace_integration.py::install_workspace()`
   - Performs bridge/runtime/launcher installation and managed asset writing using explicit helper functions
   - Includes remediation such as `_cleanup_stale_local_runtime_copy()` and `register_workspace()`

The CLI in `install_workspace_integration.py::main()` attempts to use the manifest-based manager if available, but always runs the legacy `install_workspace(...)` path as fallback/supplementary.

### Upgrade/preserve option

- CLI option `--upgrade` / `--preserve` is parsed and passed into `install_workspace(..., preserve_existing=True)`.
- In the legacy `install_workspace()` implementation, the `preserve_existing` parameter is accepted but not used.
- In the manifest manager, `upgrade=True` affects backup behavior and some merge strategies.

---

## 2. Complete asset lifecycle

### Manifest assets

The manifest defines 21 managed assets. For each asset, the installer lifecycle is:

- Load manifest via `WorkspaceAssetsManager._load_manifest()`
- Validate required policy fields
- For each asset:
  - resolve `source` inside `workspace_assets/`
  - resolve `target` inside workspace root
  - create target directories if `create_dirs` is true
  - apply `merge_strategy`
  - add `target_path` to deployed list

### Legacy installer assets

The legacy installer installs workspace assets with explicit helper methods:

- `_install_chat_tools()` writes `.pecs/tools/*`
- `_install_bridge_runtime()` writes `.pecs/bridge/run_bridge.py`, shell/cmd/ps1 delegates, `.pecs/config/continuity_bridge.json`, and `.pecs/continuity/*` scaffolding
- `_merge_tasks()` updates `.vscode/tasks.json`
- `_merge_json_dict()` updates `.vscode/settings.json`
- `_write_continue_config()` updates `.continue/config.yaml`
- `_write_continue_rules()` installs `.continue/rules/*`
- `_write_copilot_instructions()` writes or preserves `.github/copilot-instructions.md`
- `_install_consumer_guidance_assets()` writes `.pecs/PECS_CONSUMER_PROTOCOL.md`, `.kimi/instructions.md`, `.commandcode/instructions.md`
- `_copy_manual_setup_guide()` writes `.pecs/README_MANUAL_SETUP.md`
- `_write_readme()` writes `.pecs/README_WORKSPACE_INTEGRATION.md`
- `_write_workspace_install_root()` writes `.pecs/config/install_root.json`
- `_install_workspace_local_launchers()` writes `.pecs/run_pecs*` and `.pecs/run_pecs_daemon*`

### Asset lifecycle phases in manifest manager

`WorkspaceAssetsManager.install_assets()` executes:

1. `_validate_installation_target()`
2. `_backup_existing_files(upgrade)`
3. `_deploy_assets(upgrade)`
4. optional `verify_installation()`

---

## 3. Backup lifecycle

### Manifest-driven backup

`WorkspaceAssetsManager._backup_existing_files(upgrade=True)` creates backups only when `upgrade=True`.

Backed up file set:
- `.github/copilot-instructions.md`
- `.continue/config.yaml`
- `.vscode/tasks.json`
- `.vscode/settings.json`
- `.pecs/PECS_CONSUMER_PROTOCOL.md`
- `.kimi/instructions.md`
- `.commandcode/instructions.md`

Backup directory:
- `workspace_root/.pecs/backups`

Backup naming:
- `<path_with_underscores>__<timestamp>.bak`

This backup phase is global for asset manager upgrades, not per-asset.

### Legacy installer backup

The legacy installer uses `_write_managed_text_asset()` and related helpers that back up individual files before replacing or modifying them.

Relevant backup helpers:
- `_backup_target_file(workspace_root, target, suffix)`
- `_write_managed_text_asset()` backs up existing target if it exists and content differs (unless `only_if_missing=True`)
- `_copy_canonical_asset()` backs up existing target when source and target differ
- `_write_continue_config()` backs up before writing merged configuration
- `_write_copilot_instructions()` backs up the existing `.github/copilot-instructions.md` before writing a separate manual merge file

Backup directory for legacy installer is also:
- `workspace_root/.pecs/backups`

Thus backup lifecycle exists both at manifest level (coarse upgrade backup of selected files) and legacy install level (per-file content-difference backup).

---

## 4. Merge lifecycle

### Manifest-driven merge strategies

The manifest declares `merge_strategy` for each asset. `WorkspaceAssetsManager._apply_merge_strategy()` implements:

- `overwrite`
  - always `shutil.copy2(source, target)`
- `create_if_missing`
  - copy only when target does not exist
- `append` / `append_or_merge`
  - if target exists and is `.md`, append source text unless already present
  - otherwise copy source
- `merge_yaml`
  - if target exists and `upgrade=True`, preserve existing target (no change)
  - else copy source
- `merge_markdown`
  - if target exists and `upgrade=True`, append source if not present
  - else copy source
- `preserve_existing`
  - copy only if target does not exist

### Legacy installer merge behavior

The legacy installer performs merges via helper functions:

- `_merge_tasks()` merges or replaces VS Code tasks dictionary entries
- `_merge_json_dict()` updates `.vscode/settings.json` with `pecs.contextPath`
- `_write_continue_config()` preserves existing YAML and appends managed config if it cannot replace via managed block
- `_write_continue_rules()` copies canonical `.continue/rules` assets, replacing existing files if they differ
- `_write_copilot_instructions()` does not overwrite an existing `.github/copilot-instructions.md`; it preserves the existing file and writes a manual append file instead
- `_write_managed_text_asset()` replaces existing target if content differs, with backup

### Manifest asset merge lifecycle by asset

| asset id | source | target | merge_strategy | effective behavior |
|---|---|---|---|---|
| workspace_bootstrap | WORKSPACE_BOOTSTRAP.md | .pecs/WORKSPACE_BOOTSTRAP.md | create_if_missing | create if absent, preserve existing |
| readme_workspace_preparation | README_WORKSPACE_PREPARATION.md | .pecs/README_WORKSPACE_PREPARATION.md | overwrite | always replace target |
| copilot_instructions | .github/copilot-instructions.md | .github/copilot-instructions.md | append_or_merge | append markdown if not already present; preserve existing content |
| continue_config | .continue/config.yaml | .continue/config.yaml | merge_yaml | if upgrade preserves existing target; else replace |
| pecs_first_routing_rule | .continue/rules/pecs-first-routing.yaml | .continue/rules/pecs-first-routing.yaml | create_if_missing | create if absent, preserve existing |
| pecs_context_rule | .continue/rules/PECS_CONTEXT_RULE.md | .continue/rules/PECS_CONTEXT_RULE.md | create_if_missing | create if absent, preserve existing |
| pecs_append_rule | .continue/rules/PECS_APPEND_RULE.md | .continue/rules/PECS_APPEND_RULE.md | create_if_missing | create if absent, preserve existing |
| continuity_map | .continue/rules/CONTINUITY_MAP.md | .continue/rules/CONTINUITY_MAP.md | create_if_missing | create if absent, preserve existing |
| pecs_coding_protocol | .continue/rules/PECS_CODING_PROTOCOL.md | .continue/rules/PECS_CODING_PROTOCOL.md | create_if_missing | create if absent, preserve existing |
| pecs_prompt | .continue/rules/PECS_PROMPT.md | .continue/rules/PECS_PROMPT.md | create_if_missing | create if absent, preserve existing |
| live_context | .continue/rules/live-context.md | .continue/rules/live-context.md | create_if_missing | create if absent, preserve existing |
| pecs_readme | .pecs/README.md | .pecs/README.md | overwrite | always replace target |
| pecs_consumer_protocol | .pecs/PECS_CONSUMER_PROTOCOL.md | .pecs/PECS_CONSUMER_PROTOCOL.md | create_if_missing | create if absent, preserve existing |
| consumer_consultation_policy | .pecs/config/consumer_consultation.json | .pecs/config/consumer_consultation.json | create_if_missing | create if absent, preserve existing |
| kimi_instructions | .kimi/instructions.md | .kimi/instructions.md | create_if_missing | create if absent, preserve existing |
| commandcode_instructions | .commandcode/instructions.md | .commandcode/instructions.md | create_if_missing | create if absent, preserve existing |
| readme_workspace_integration | README_WORKSPACE_INTEGRATION.md | .pecs/README_WORKSPACE_INTEGRATION.md | overwrite | always replace target |

### Effective merge lifecycle summary

- `overwrite` assets are replaced unconditionally.
- `create_if_missing` assets are preserved when present.
- `append_or_merge` uses append semantics for markdown, preserving existing content and not duplicating.
- `merge_yaml` attempts preservation on upgrade.
- `preserve_existing` is supported in code but not present in this manifest.

---

## 5. Preserve lifecycle

Preserve behavior is implemented by the following policies:

### In manifest manager

- `create_if_missing` preserves file if it already exists.
- `preserve_existing` would preserve only if the target exists.
- `merge_yaml` preserves existing target when `upgrade=True`.
- `append_or_merge` and `merge_markdown` preserve existing content by appending only if necessary.

### In legacy installer

- `_write_continue_config()` preserves existing YAML unless a managed block is present or appended canonical content.
- `_write_copilot_instructions()` preserves the existing GitHub Copilot instructions file and does not overwrite it.
- `_write_managed_text_asset()` preserves target if content is identical or `only_if_missing=True`.
- `_copy_canonical_asset()` preserves target if identical.

### Preserve lifecycle conclusions

- Existing `.continue` config and `.github/copilot-instructions.md` are preserved by legacy installer logic.
- Most other managed assets are either overwritten or created-if-missing depending on strategy.

---

## 6. Replace lifecycle

Replace behavior occurs in:

### Manifest manager

- `overwrite` assets are always replaced with `shutil.copy2(source, target)`.
- `merge_yaml` assets are replaced when not in upgrade mode.
- `merge_markdown` assets are replaced when not in upgrade mode.

### Legacy installer

- `_write_managed_text_asset()` replaces existing targets if their content differs.
- `_copy_canonical_asset()` replaces existing targets if their content differs.
- `_write_continue_config()` may replace the managed block or entire config when canonical blocks are reapplied.
- `_write_continue_rules()` replaces existing `.continue/rules/*` files if content differs.
- `_write_workspace_install_root()` replaces `.pecs/config/install_root.json` if content differs.
- `_install_workspace_local_launchers()` replaces `.pecs/run_pecs*` and `.pecs/run_pecs_daemon*` if content differs.

### Replace lifecycle conclusions

- The installer may overwrite managed assets under explicit `overwrite` strategy or when canonical content differs.
- The legacy installer uses content-diff backups before replacing changed files.

---

## 7. Cleanup lifecycle

Cleanup behavior is not manifest-driven. It is implemented only in legacy installer code.

### Stale runtime cleanup

- `install_workspace_integration.py::_cleanup_stale_local_runtime_copy(workspace_root)`
  - Detects stale runtime paths:
    - `.pecs/pecs_pro`
    - `.pecs/pecs_pro.egg-info`
    - `.pecs/pecs_pro.dist-info`
  - For directories, moves them into `.pecs/backups/stale_local_runtime_<name>_<timestamp>`.
  - For files, copies them to backup and unlinks the target.
  - Exceptions are caught and ignored.

### Other cleanup

- The manifest manager itself does not remove obsolete assets.
- Legacy installer cleanup is limited to stale runtime copies, not general obsolete paths.

### Cleanup lifecycle conclusions

- The installer can clean up stale local runtime copies during `install_workspace()`.
- There is no manifest asset cleanup policy for obsolete files.
- Cleanup is remediation-only and errors are ignored.

---

## 8. Verification lifecycle

### Manifest asset verification

`WorkspaceAssetsManager.verify_installation()` performs:

1. Reads `verification_config = self.manifest.get("verification", {})`
2. Checks `required_assets` listed there
3. Checks `required_daemon_files` and `required_daemon_directories`
4. Runs `_verify_install_root_references(result)` to verify:
   - `.pecs/config/install_root.json` exists and points to current repo root
   - `python_path` exists
   - optional console scripts exist and warns if missing
   - workspace launchers exist and are executable for `.sh`
   - stale runtime copies `.pecs/pecs_pro*` are absent
   - stale PECS root references in `.vscode/tasks.json` are absent

### Verification policy in current manifest

- The current manifest contains no `verification` section.
- Therefore `verify_installation()` does not check managed assets from the manifest by default.
- It only checks assets if they are explicitly listed in `verification.required_assets`.

### Additional verification

`_verify_install_root_references()` adds important checks beyond `verification.required_assets`:
- `install_root.json` validity and matching repo root
- launcher presence
- stale local runtime copy absence
- stale `.vscode/tasks.json` install-root references

### Verification lifecycle conclusions

- The manifest-based verification does not automatically verify all managed assets.
- It verifies only required assets if configured, plus install-root/launcher/runtime-copy invariants.
- Obsolete asset absence is not generally verified by manifest verification, except for stale runtime copies and stale task references.

---

## 9. Per-managed-asset policy matrix

| asset id | source | target | merge_strategy | replacement_policy | merge_policy | upgrade_behavior | backup policy | cleanup policy | verification policy |
|---|---|---|---|---|---|---|---|---|---|
| workspace_bootstrap | WORKSPACE_BOOTSTRAP.md | .pecs/WORKSPACE_BOOTSTRAP.md | create_if_missing | manifest_controlled | create_if_missing | preserve_if_present | no per-asset backup in manifest manager; only global upgrade selected-files backup | none | not checked unless configured in manifest verification |
| readme_workspace_preparation | README_WORKSPACE_PREPARATION.md | .pecs/README_WORKSPACE_PREPARATION.md | overwrite | manifest_controlled | overwrite | replace | same as above | none | same as above |
| copilot_instructions | .github/copilot-instructions.md | .github/copilot-instructions.md | append_or_merge | manifest_controlled | append_or_merge | merge | same as above | none | same as above |
| continue_config | .continue/config.yaml | .continue/config.yaml | merge_yaml | manifest_controlled | merge_yaml | merge | same as above | none | same as above |
| pecs_first_routing_rule | .continue/rules/pecs-first-routing.yaml | .continue/rules/pecs-first-routing.yaml | create_if_missing | manifest_controlled | create_if_missing | preserve_if_present | same as above | none | same as above |
| pecs_context_rule | .continue/rules/PECS_CONTEXT_RULE.md | .continue/rules/PECS_CONTEXT_RULE.md | create_if_missing | manifest_controlled | create_if_missing | preserve_if_present | same as above | none | same as above |
| pecs_append_rule | .continue/rules/PECS_APPEND_RULE.md | .continue/rules/PECS_APPEND_RULE.md | create_if_missing | manifest_controlled | create_if_missing | preserve_if_present | same as above | none | same as above |
| continuity_map | .continue/rules/CONTINUITY_MAP.md | .continue/rules/CONTINUITY_MAP.md | create_if_missing | manifest_controlled | create_if_missing | preserve_if_present | same as above | none | same as above |
| pecs_coding_protocol | .continue/rules/PECS_CODING_PROTOCOL.md | .continue/rules/PECS_CODING_PROTOCOL.md | create_if_missing | manifest_controlled | create_if_missing | preserve_if_present | same as above | none | same as above |
| pecs_prompt | .continue/rules/PECS_PROMPT.md | .continue/rules/PECS_PROMPT.md | create_if_missing | manifest_controlled | create_if_missing | preserve_if_present | same as above | none | same as above |
| live_context | .continue/rules/live-context.md | .continue/rules/live-context.md | create_if_missing | manifest_controlled | create_if_missing | preserve_if_present | same as above | none | same as above |
| pecs_readme | .pecs/README.md | .pecs/README.md | overwrite | manifest_controlled | overwrite | replace | same as above | none | same as above |
| pecs_consumer_protocol | .pecs/PECS_CONSUMER_PROTOCOL.md | .pecs/PECS_CONSUMER_PROTOCOL.md | create_if_missing | manifest_controlled | create_if_missing | preserve_if_present | same as above | none | same as above |
| consumer_consultation_policy | .pecs/config/consumer_consultation.json | .pecs/config/consumer_consultation.json | create_if_missing | manifest_controlled | create_if_missing | preserve_if_present | same as above | none | same as above |
| kimi_instructions | .kimi/instructions.md | .kimi/instructions.md | create_if_missing | manifest_controlled | create_if_missing | preserve_if_present | same as above | none | same as above |
| commandcode_instructions | .commandcode/instructions.md | .commandcode/instructions.md | create_if_missing | manifest_controlled | create_if_missing | preserve_if_present | same as above | none | same as above |
| readme_workspace_integration | README_WORKSPACE_INTEGRATION.md | .pecs/README_WORKSPACE_INTEGRATION.md | overwrite | manifest_controlled | overwrite | replace | same as above | none | same as above |

Note: all backup policy entries are global upgrade backups; manifest manager does not provide per-asset backup policies in the manifest itself.

---

## 10. Obsolete runtime file handling

### Can installer overwrite obsolete runtime files?

- The manifest manager does not deploy obsolete runtime files.
- The legacy installer does not explicitly overwrite stale runtime files; it removes them via `_cleanup_stale_local_runtime_copy(workspace_root)`.
- Therefore the installer does not treat obsolete runtime files as managed assets to overwrite; it only removes them if present.

### Can installer leave obsolete files untouched?

- Yes, if `_cleanup_stale_local_runtime_copy()` encounters an exception, it catches and continues.
- The manifest manager has no cleanup step for obsolete runtime copies, so if the legacy cleanup is not executed or fails, obsolete files can remain.
- In the CLI, legacy `install_workspace()` is always executed after the manifest manager, so cleanup is normally attempted.
- For manifest manager only use, obsolete files are not removed by `WorkspaceAssetsManager` itself.

### Does verification check obsolete absence?

- `WorkspaceAssetsManager.verify_installation()` reads `manifest.verification` if present.
- The current manifest has no `verification` section.
- Therefore required asset checking does not cover all manifest assets.
- Verification does include hardcoded checks in `_verify_install_root_references()` for:
  - `.pecs/config/install_root.json`
  - workspace launcher scripts
  - stale runtime copies `.pecs/pecs_pro*`
  - stale `.vscode/tasks.json` install-root references
- Obsolete assets beyond stale runtime copies are not otherwise checked by verification.

### Verification-only summary

- The installer does not verify the full manifest asset set by default.
- It verifies only explicitly configured required assets plus runtime/launcher/install-root invariants.
- It does not verify that all obsolete runtime or bridge artifacts are absent except the hardcoded stale runtime copy check.

---

## 11. Specific evidence for policy behaviors

### Manifest manager policies

- `WorkspaceAssetsManager._validate_installation_target()` ensures the workspace exists and is not the PECS repository itself.
- `WorkspaceAssetsManager._backup_existing_files(upgrade=True)` backs up selected existing files before manifest asset deployment.
- `WorkspaceAssetsManager._deploy_assets()` iterates manifest assets, creates directories, and delegates to `_apply_merge_strategy()`.
- `WorkspaceAssetsManager._apply_merge_strategy()` implements all merge/replacement behaviors.
- `WorkspaceAssetsManager.verify_installation()` validates required assets only if `manifest.verification` provides them, then checks install root and stale runtime files.

### Legacy installer policies

- `_write_managed_text_asset()` performs file replacement with backup when content differs.
- `_copy_canonical_asset()` performs content replacement with backup.
- `_write_continue_config()` preserves existing YAML and appends managed content when necessary.
- `_write_copilot_instructions()` preserves existing target and writes a manual merge artifact instead of overwriting it.
- `_install_bridge_runtime()` writes workspace bridge delegates and `.pecs` runtime/continuity scaffolding.
- `_install_workspace_local_launchers()` writes launchers with backup support.
- `_cleanup_stale_local_runtime_copy()` removes stale `.pecs/pecs_pro*` runtime copies, with backup, and ignores failures.

---

## 12. Conclusions

- The installer lifecycle is split between manifest-driven deployment and legacy explicit asset writes.
- Backup behavior is available on manifest upgrade for selected config files, and more broadly in legacy helpers on per-file replace.
- Merge lifecycle is policy-driven by `merge_strategy`; `overwrite` and `create_if_missing` are primary behaviors.
- Preserve lifecycle is implemented via `create_if_missing`, `preserve_existing`, `merge_yaml` on upgrade, and explicit legacy helpers.
- Replace lifecycle occurs via `overwrite`, content-diff replacement helpers, and launchers/bridge delegates.
- Cleanup is not manifest-managed; it is limited to stale runtime copies in `_cleanup_stale_local_runtime_copy()`.
- Verification does not verify all manifest assets by default; it only checks `verification.required_assets` if configured, plus install root/launcher/stale-runtime invariants.
- The installer can leave obsolete runtime files untouched if legacy cleanup fails, because failures are swallowed.
- The installer does not overwrite obsolete runtime files as managed assets; it only removes them if present.

No code changes were made as part of this audit.
