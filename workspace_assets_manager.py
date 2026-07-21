"""PECS Workspace Assets Manager

Manages installation, verification, and repair of PECS workspace assets
using a manifest-driven approach.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class WorkspaceAssetsManager:
    """Manages PECS workspace asset deployment and verification."""

    def __init__(self, repo_root: Path, workspace_root: Path):
        self.repo_root = repo_root.resolve()
        self.workspace_root = workspace_root.resolve()
        self.assets_dir = self.repo_root / "workspace_assets"
        self.manifest_path = self.assets_dir / "workspace_assets_manifest.json"
        self.manifest: Dict[str, Any] = {}
        self._load_manifest()

    def _load_manifest(self) -> None:
        """Load workspace assets manifest."""
        if not self.manifest_path.exists():
            raise FileNotFoundError(
                f"Workspace assets manifest not found: {self.manifest_path}"
            )
        self.manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self._validate_manifest_policy_fields()
        logger.info(
            f"Loaded workspace assets manifest (v{self.manifest.get('version', '?')})"
        )

    def _validate_manifest_policy_fields(self) -> None:
        required_fields = {
            "asset_version",
            "ownership",
            "replacement_policy",
            "merge_policy",
            "upgrade_behavior",
        }
        missing_by_asset: Dict[str, List[str]] = {}
        for asset in self.manifest.get("assets", []):
            asset_id = str(asset.get("id", "unknown"))
            missing = sorted(
                field for field in required_fields if field not in asset
            )
            if missing:
                missing_by_asset[asset_id] = missing

        if missing_by_asset:
            raise ValueError(
                "Workspace asset manifest missing required policy fields: "
                + json.dumps(missing_by_asset, sort_keys=True)
            )

    def install_assets(
        self, upgrade: bool = False, verify: bool = True
    ) -> Dict[str, Any]:
        """Install workspace assets into target workspace.

        Args:
            upgrade: If True, preserve user customizations
            verify: If True, verify installation after completion

        Returns:
            Installation result dictionary
        """
        logger.info(f"Installing PECS workspace assets into {self.workspace_root}")

        result = {
            "status": "started",
            "timestamp": datetime.now().isoformat(),
            "workspace": str(self.workspace_root),
            "upgrade": upgrade,
            "installed_assets": [],
            "errors": [],
            "warnings": [],
        }

        try:
            # Phase 1: Validation
            self._validate_installation_target()
            logger.info("Phase 1: Validation passed")

            # Phase 2: Backup
            backups = self._backup_existing_files(upgrade)
            result["backups"] = backups
            logger.info(f"Phase 2: Created {len(backups)} backup(s)")

            # Phase 3: Asset deployment
            installed = self._deploy_assets(upgrade)
            result["installed_assets"] = installed
            logger.info(f"Phase 3: Deployed {len(installed)} asset(s)")

            # Phase 4: Verification
            if verify:
                verification = self.verify_installation()
                result["verification"] = verification
                if not verification["valid"]:
                    result["errors"].extend(verification.get("errors", []))
                logger.info(
                    f"Phase 4: Verification {'passed' if verification['valid'] else 'failed'}"
                )

            result["status"] = "success"
            logger.info("Asset installation completed successfully")

        except Exception as e:
            result["status"] = "failed"
            result["errors"].append(str(e))
            logger.error(f"Asset installation failed: {e}")
            raise

        return result

    def _validate_installation_target(self) -> None:
        """Validate that workspace is suitable for installation."""
        if not self.workspace_root.exists():
            raise FileNotFoundError(f"Workspace does not exist: {self.workspace_root}")

        # Ensure we're not installing into PECS repository itself
        try:
            if (self.workspace_root / "pecs_pro.egg-info").exists():
                raise ValueError(
                    "Cannot install into PECS-PRO repository itself. "
                    "PECS-PRO must remain external to target workspace."
                )
        except Exception:
            pass

        logger.debug(f"Validation passed for workspace: {self.workspace_root}")

    def _backup_existing_files(self, upgrade: bool = False) -> Dict[str, str]:
        """Backup existing configuration files before modification."""
        backups = {}

        if not upgrade:
            return backups

        backup_dir = self.workspace_root / ".pecs" / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)

        files_to_backup = [
            ".github/copilot-instructions.md",
            ".continue/config.yaml",
            ".vscode/tasks.json",
            ".vscode/settings.json",
            ".pecs/PECS_CONSUMER_PROTOCOL.md",
            ".kimi/instructions.md",
            ".commandcode/instructions.md",
        ]

        for file_path in files_to_backup:
            source = self.workspace_root / file_path
            if source.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"{file_path.replace('/', '_')}__{timestamp}.bak"
                backup_target = backup_dir / backup_name
                backup_target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, backup_target)
                backups[file_path] = str(backup_target)
                logger.info(f"Backed up {file_path} to {backup_target}")

        return backups

    def _deploy_assets(self, upgrade: bool = False) -> List[str]:
        """Deploy workspace assets according to manifest."""
        deployed = []

        for asset in self.manifest.get("assets", []):
            try:
                asset_id = asset.get("id", "unknown")
                source_file = asset.get("source")
                target_path = asset.get("target")
                merge_strategy = asset.get("merge_strategy", "overwrite")
                required = asset.get("required", False)
                create_dirs = asset.get("create_dirs", True)

                if not source_file or not target_path:
                    logger.warning(f"Asset {asset_id} missing source or target")
                    continue

                source = self.assets_dir / source_file
                target = self.workspace_root / target_path
                merge_options = asset.get("merge_options", {})

                if not source.exists():
                    msg = f"Asset source not found: {source}"
                    if required:
                        raise FileNotFoundError(msg)
                    else:
                        logger.warning(msg)
                        continue

                # Create target directories
                if create_dirs:
                    target.parent.mkdir(parents=True, exist_ok=True)

                # Apply merge strategy
                self._apply_merge_strategy(
                    asset_id,
                    source,
                    target,
                    merge_strategy,
                    upgrade,
                    merge_options,
                )
                deployed.append(target_path)
                logger.info(f"Deployed asset {asset_id} to {target_path}")

            except Exception as e:
                logger.error(f"Failed to deploy asset {asset_id}: {e}")
                raise

        return deployed

    def _apply_merge_strategy(
        self,
        asset_id: str,
        source: Path,
        target: Path,
        strategy: str,
        upgrade: bool,
        merge_options: Dict[str, Any],
    ) -> None:
        """Apply merge strategy for asset deployment."""
        if strategy == "overwrite":
            shutil.copy2(source, target)

        elif strategy == "create_if_missing":
            if not target.exists():
                shutil.copy2(source, target)
            else:
                logger.info(f"Asset {asset_id} already exists, skipping")

        elif strategy == "append" or strategy == "append_or_merge":
            if target.exists():
                if target.suffix in {".md", ".markdown"}:
                    self._append_markdown(asset_id, source, target, merge_options)
                    return
                if target.suffix == ".json" or source.suffix == ".json":
                    self._merge_json(asset_id, source, target)
                    return
                if target.suffix in {".yaml", ".yml"} or source.suffix in {".yaml", ".yml"}:
                    self._merge_yaml(asset_id, source, target, merge_options, upgrade)
                    return
                raise ValueError(
                    f"append_or_merge does not support asset type: {target.suffix}"
                )
            shutil.copy2(source, target)

        elif strategy == "merge_yaml":
            self._merge_yaml(asset_id, source, target, merge_options, upgrade)

        elif strategy == "merge_json":
            self._merge_json(asset_id, source, target)

        elif strategy == "merge_vscode_tasks":
            if target.exists():
                self._merge_vscode_tasks(target, source)
                return
            shutil.copy2(source, target)

        elif strategy == "merge_markdown":
            if target.exists() and upgrade:
                self._append_markdown(asset_id, source, target, merge_options)
            else:
                shutil.copy2(source, target)

        elif strategy == "preserve_existing":
            if not target.exists():
                shutil.copy2(source, target)
        else:
            raise ValueError(f"Unsupported merge strategy: {strategy}")

    def _deep_merge(self, target: Dict, source: Dict) -> None:
        """Deep merge source dictionary into target dictionary."""
        for key, value in source.items():
            if (
                key in target
                and isinstance(target[key], dict)
                and isinstance(value, dict)
            ):
                self._deep_merge(target[key], value)
            elif (
                key in target
                and isinstance(target[key], list)
                and isinstance(value, list)
            ):
                for item in value:
                    if item not in target[key]:
                        target[key].append(item)
            else:
                target[key] = value

    def _append_markdown(
        self,
        asset_id: str,
        source: Path,
        target: Path,
        merge_options: Dict[str, Any],
    ) -> None:
        source_content = source.read_text(encoding="utf-8")
        target_content = target.read_text(encoding="utf-8")

        if source_content.strip() in target_content:
            return

        marker = merge_options.get("append_section_marker") or f"<!-- ASSET:{asset_id} -->"
        if marker in target_content:
            return

        separator = "\n\n" if target_content.strip() else ""
        target.write_text(
            target_content.rstrip() + separator + marker + "\n" + source_content.strip() + "\n",
            encoding="utf-8",
        )

    def _merge_json(self, asset_id: str, source: Path, target: Path) -> None:
        source_data = json.loads(source.read_text(encoding="utf-8"))
        if not target.exists():
            json_text = json.dumps(source_data, indent=2, ensure_ascii=True)
            target.write_text(json_text, encoding="utf-8")
            return

        target_data = json.loads(target.read_text(encoding="utf-8"))
        if not isinstance(source_data, dict) or not isinstance(target_data, dict):
            raise ValueError(f"JSON merge requires object payloads for asset {asset_id}")

        self._deep_merge(target_data, source_data)
        target.write_text(
            json.dumps(target_data, indent=2, ensure_ascii=True), encoding="utf-8"
        )

    def _merge_yaml(
        self,
        asset_id: str,
        source: Path,
        target: Path,
        merge_options: Dict[str, Any],
        upgrade: bool,
    ) -> None:
        source_content = source.read_text(encoding="utf-8")
        if not target.exists():
            target.write_text(source_content, encoding="utf-8")
            return

        key_paths = merge_options.get("key_paths", [])
        if not isinstance(key_paths, list):
            raise ValueError(
                f"merge_yaml requires key_paths list for asset {asset_id}"
            )

        if not key_paths:
            raise ValueError(
                f"merge_yaml requires at least one key_path for asset {asset_id}"
            )

        target_lines = target.read_text(encoding="utf-8").splitlines()
        source_lines = source_content.splitlines()
        merged_lines = list(target_lines)

        for key_path in key_paths:
            key_name = str(key_path).split(".")[-1]
            source_block = self._extract_yaml_block(source_lines, key_name)
            if source_block is None:
                continue

            target_block = self._extract_yaml_block(merged_lines, key_name)
            if target_block is None:
                if merge_options.get("create_if_missing_top_level", False):
                    insertion_index = self._find_yaml_insert_index(merged_lines)
                    merged_lines[insertion_index:insertion_index] = ["", *source_block]
                else:
                    raise ValueError(
                        f"Key path '{key_path}' missing in target for asset {asset_id}"
                    )
            else:
                merged_block = self._merge_yaml_blocks(
                    target_block,
                    source_block,
                    merge_options.get("merge_mode", "extend"),
                )
                merged_lines = self._replace_yaml_block(
                    merged_lines, key_name, merged_block
                )

        target.write_text("\n".join(merged_lines).rstrip() + "\n", encoding="utf-8")

    def _extract_yaml_block(self, lines: List[str], key_name: str) -> Optional[List[str]]:
        start = None
        indent = None
        for idx, line in enumerate(lines):
            stripped = line.lstrip()
            if stripped.startswith(f"{key_name}:") and not stripped.startswith(f"{key_name}::"):
                start = idx
                indent = len(line) - len(stripped)
                break

        if start is None:
            return None

        block = [lines[start]]
        for line in lines[start + 1 :]:
            current_indent = len(line) - len(line.lstrip())
            if line.strip() == "":
                block.append(line)
                continue
            if current_indent <= indent:
                break
            block.append(line)

        return block

    def _find_yaml_insert_index(self, lines: List[str]) -> int:
        for idx in range(len(lines) - 1, -1, -1):
            if lines[idx].strip() == "":
                continue
            return idx + 1
        return len(lines)

    def _merge_yaml_blocks(
        self,
        target_block: List[str],
        source_block: List[str],
        merge_mode: str,
    ) -> List[str]:
        if merge_mode != "extend":
            return source_block

        target_items = self._extract_yaml_list_items(target_block)
        source_items = self._extract_yaml_list_items(source_block)
        existing = [item.strip() for item in target_items]

        merged = list(target_block)
        for source_item in source_items:
            normalized = source_item.strip()
            if normalized and normalized not in existing:
                merged.append(source_item)
                existing.append(normalized)

        return merged

    def _extract_yaml_list_items(self, block: List[str]) -> List[str]:
        items = []
        in_item = False
        current = []
        for line in block[1:]:
            if line.lstrip().startswith("-"):
                if in_item:
                    items.append("\n".join(current))
                current = [line]
                in_item = True
            elif in_item:
                if line.strip() == "":
                    current.append(line)
                else:
                    current.append(line)
        if in_item:
            items.append("\n".join(current))
        return items

    def _replace_yaml_block(
        self,
        lines: List[str],
        key_name: str,
        new_block: List[str],
    ) -> List[str]:
        start = None
        indent = None
        for idx, line in enumerate(lines):
            stripped = line.lstrip()
            if stripped.startswith(f"{key_name}:") and not stripped.startswith(f"{key_name}::"):
                start = idx
                indent = len(line) - len(stripped)
                break

        if start is None:
            return lines

        end = start + 1
        for line in lines[start + 1 :]:
            current_indent = len(line) - len(line.lstrip())
            if line.strip() == "":
                end += 1
                continue
            if current_indent <= indent:
                break
            end += 1

        return lines[:start] + new_block + lines[end:]

    def _merge_vscode_tasks(self, target: Path, source: Path) -> None:
        """Merge workspace tasks and inputs from source into an existing tasks.json."""
        target_data = json.loads(target.read_text(encoding="utf-8"))
        source_data = json.loads(source.read_text(encoding="utf-8"))

        if not isinstance(target_data, dict) or not isinstance(source_data, dict):
            raise ValueError("VS Code tasks merge requires JSON objects")

        merged = dict(target_data)
        merged_tasks = self._merge_vscode_task_entries(
            target_data.get("tasks", []), source_data.get("tasks", [])
        )
        merged_inputs = self._merge_vscode_input_entries(
            target_data.get("inputs", []), source_data.get("inputs", [])
        )

        if merged_tasks is not None:
            merged["tasks"] = merged_tasks
        if merged_inputs is not None:
            merged["inputs"] = merged_inputs

        merged.update({k: v for k, v in source_data.items() if k not in {"tasks", "inputs"}})

        target.write_text(
            json.dumps(merged, indent=2, ensure_ascii=True), encoding="utf-8"
        )

    def _merge_vscode_task_entries(
        self, existing: List[Any], source: List[Any]
    ) -> List[Any]:
        if not isinstance(existing, list) or not isinstance(source, list):
            return source if isinstance(source, list) else []

        existing_by_label = {
            str(task.get("label", "")): task
            for task in existing
            if isinstance(task, dict) and task.get("label")
        }
        merged_tasks: List[Any] = list(existing)

        for task in source:
            if not isinstance(task, dict) or not task.get("label"):
                if task not in merged_tasks:
                    merged_tasks.append(task)
                continue

            label = str(task["label"])
            if label in existing_by_label:
                existing_task = existing_by_label[label]
                merged_task = dict(existing_task)
                for key, value in task.items():
                    if key not in merged_task:
                        merged_task[key] = value
                for index, element in enumerate(merged_tasks):
                    if isinstance(element, dict) and element.get("label") == label:
                        merged_tasks[index] = merged_task
                        break
            else:
                merged_tasks.append(task)

        return merged_tasks

    def _merge_vscode_input_entries(
        self, existing: List[Any], source: List[Any]
    ) -> List[Any]:
        if not isinstance(existing, list) or not isinstance(source, list):
            return source if isinstance(source, list) else []

        existing_by_id = {
            str(input_item.get("id", "")): input_item
            for input_item in existing
            if isinstance(input_item, dict) and input_item.get("id")
        }
        merged_inputs: List[Any] = list(existing)

        for input_item in source:
            if not isinstance(input_item, dict) or not input_item.get("id"):
                if input_item not in merged_inputs:
                    merged_inputs.append(input_item)
                continue

            input_id = str(input_item["id"])
            if input_id in existing_by_id:
                merged_item = dict(existing_by_id[input_id])
                for key, value in input_item.items():
                    if key not in merged_item:
                        merged_item[key] = value
                for index, element in enumerate(merged_inputs):
                    if isinstance(element, dict) and element.get("id") == input_id:
                        merged_inputs[index] = merged_item
                        break
            else:
                merged_inputs.append(input_item)

        return merged_inputs

    def verify_installation(self) -> Dict[str, Any]:
        """Verify PECS workspace assets are properly installed."""
        result = {
            "valid": True,
            "timestamp": datetime.now().isoformat(),
            "workspace": str(self.workspace_root),
            "checks": {},
            "asset_reports": {},
            "orphaned_files": [],
            "summary": {
                "missing": 0,
                "partial": 0,
                "outdated": 0,
                "complete": 0,
                "orphaned": 0,
            },
            "errors": [],
            "warnings": [],
        }

        manifest_targets = set()
        for asset in self.manifest.get("assets", []):
            report = self._verify_manifest_asset(asset)
            target_path = asset.get("target", "")
            result["asset_reports"][target_path] = report
            result["checks"][target_path] = report["exists"]
            manifest_targets.add(target_path)

            if report["missing"]:
                result["summary"]["missing"] += 1
                if asset.get("required", False):
                    result["valid"] = False
                    result["errors"].append(
                        f"Missing required asset: {target_path}"
                    )
            elif report["partial"]:
                result["summary"]["partial"] += 1
                result["valid"] = False
                result["errors"].append(
                    f"Partial asset installation: {target_path}"
                )
            elif report["outdated"]:
                result["summary"]["outdated"] += 1
                result["valid"] = False
                result["errors"].append(
                    f"Outdated asset content: {target_path}"
                )
            else:
                result["summary"]["complete"] += 1

        orphaned_files = self._find_orphaned_files(manifest_targets)
        result["orphaned_files"] = orphaned_files
        result["summary"]["orphaned"] = len(orphaned_files)
        if orphaned_files:
            result["warnings"].append(
                f"Found orphaned workspace files: {len(orphaned_files)}"
            )

        verification_config = self.manifest.get("verification", {})
        required_daemon_files = verification_config.get("required_daemon_files", [])
        required_daemon_dirs = verification_config.get(
            "required_daemon_directories", []
        )

        for daemon_file in required_daemon_files:
            full_path = self.workspace_root / daemon_file
            if not full_path.exists():
                result["errors"].append(f"Missing daemon file: {daemon_file}")
                result["valid"] = False

        for daemon_dir in required_daemon_dirs:
            full_path = self.workspace_root / daemon_dir
            if not full_path.exists():
                result["errors"].append(f"Missing daemon directory: {daemon_dir}")
                result["valid"] = False

        self._verify_install_root_references(result)
        return result

    def _verify_manifest_asset(self, asset: Dict[str, Any]) -> Dict[str, Any]:
        target_path = asset.get("target", "")
        merge_strategy = asset.get("merge_strategy", "overwrite")
        required = asset.get("required", False)
        merge_options = asset.get("merge_options", {}) or {}

        full_path = self.workspace_root / target_path
        category = self._classify_asset(asset)
        report = {
            "target": target_path,
            "exists": full_path.exists(),
            "required": required,
            "policy": merge_strategy,
            "category": category,
            "merge_status": None,
            "hash": None,
            "expected_hash": None,
            "outdated": False,
            "missing": False,
            "partial": False,
            "orphaned": False,
            "details": [],
        }

        if not report["exists"]:
            report["missing"] = True
            report["details"].append("Asset file missing")
            return report

        report["hash"] = self._file_hash(full_path)

        source_path = self.assets_dir / asset.get("source", "")
        if source_path.exists():
            report["expected_hash"] = self._file_hash(source_path)
            if report["hash"] != report["expected_hash"]:
                if category in {"runtime_generated", "scaffold", "preserved_asset"}:
                    report["merge_status"] = "content_preserved"
                    report["details"].append(
                        "Asset content differs from source but is allowed by its category"
                    )
                elif merge_strategy == "overwrite":
                    report["outdated"] = True
                    report["details"].append("Target content differs from source")
                else:
                    report["merge_status"] = self._assess_merge_status(
                        merge_strategy,
                        source_path,
                        full_path,
                        merge_options,
                        asset.get("id", "unknown"),
                    )
                    if report["merge_status"] != "merged":
                        report["partial"] = True
                        report["details"].append(
                            f"Merge status: {report['merge_status']}"
                        )
        else:
            report["details"].append("Source asset missing from manifest")
            report["partial"] = True

        return report

    def _classify_asset(self, asset: Dict[str, Any]) -> str:
        target_path = asset.get("target", "")
        merge_strategy = asset.get("merge_strategy", "overwrite")

        if target_path.endswith(".pecs/ai_chat_history.json"):
            return "runtime_generated"
        if target_path.endswith(".gitkeep"):
            return "scaffold"
        if merge_strategy == "create_if_missing":
            return "preserved_asset"
        return "canonical_managed"

    def _assess_merge_status(
        self,
        strategy: str,
        source: Path,
        target: Path,
        merge_options: Dict[str, Any],
        asset_id: str,
    ) -> str:
        if strategy in {"merge_json", "append_or_merge"} and target.suffix == ".json":
            try:
                source_data = json.loads(source.read_text(encoding="utf-8"))
                target_data = json.loads(target.read_text(encoding="utf-8"))
                if isinstance(source_data, dict) and isinstance(target_data, dict):
                    return "merged" if self._is_json_subset(source_data, target_data) else "partial"
            except Exception:
                return "partial"
        if strategy == "merge_vscode_tasks":
            try:
                source_data = json.loads(source.read_text(encoding="utf-8"))
                target_data = json.loads(target.read_text(encoding="utf-8"))
                if isinstance(source_data, dict) and isinstance(target_data, dict):
                    merged_tasks = self._merge_vscode_task_entries(
                        target_data.get("tasks", []), source_data.get("tasks", [])
                    )
                    merged_inputs = self._merge_vscode_input_entries(
                        target_data.get("inputs", []), source_data.get("inputs", [])
                    )
                    if merged_tasks == target_data.get("tasks", []) and merged_inputs == target_data.get("inputs", []):
                        return "merged"
                    return "partial"
            except Exception:
                return "partial"
        if strategy == "merge_yaml":
            try:
                source_lines = source.read_text(encoding="utf-8").splitlines()
                target_lines = target.read_text(encoding="utf-8").splitlines()
                key_paths = merge_options.get("key_paths", [])
                if key_paths:
                    for key_path in key_paths:
                        key_name = str(key_path).split(".")[-1]
                        source_block = self._extract_yaml_block(source_lines, key_name)
                        target_block = self._extract_yaml_block(target_lines, key_name)
                        if source_block and target_block:
                            return "merged"
                    return "partial"
            except Exception:
                return "partial"
        if strategy in {"merge_markdown", "append_or_merge"} and target.suffix in {".md", ".markdown"}:
            content = target.read_text(encoding="utf-8")
            marker = merge_options.get("append_section_marker") or f"<!-- ASSET:{asset_id} -->"
            return "merged" if marker in content else "partial"
        if strategy == "merge_markdown":
            content = target.read_text(encoding="utf-8")
            marker = merge_options.get("append_section_marker") or f"<!-- ASSET:{asset_id} -->"
            return "merged" if marker in content else "partial"
        return "unknown"

    def _is_json_subset(self, subset: Dict[str, Any], superset: Dict[str, Any]) -> bool:
        for key, value in subset.items():
            if key not in superset:
                return False
            if isinstance(value, dict) and isinstance(superset[key], dict):
                if not self._is_json_subset(value, superset[key]):
                    return False
            elif isinstance(value, list) and isinstance(superset[key], list):
                for item in value:
                    if item not in superset[key]:
                        return False
            elif superset[key] != value:
                return False
        return True

    def _file_hash(self, path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(8192), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def _find_orphaned_files(self, manifest_targets: set) -> List[str]:
        orphans = []
        for path in self.workspace_root.rglob("*"):
            if path.is_file():
                relative = str(path.relative_to(self.workspace_root))
                if relative.startswith(".git"):
                    continue
                if relative not in manifest_targets:
                    orphans.append(relative)
        return sorted(orphans)

    def _verify_install_root_references(self, result: Dict[str, Any]) -> None:
        """Verify workspace asset references point to the current PECS install root."""
        install_root_config = self.workspace_root / ".pecs" / "config" / "install_root.json"
        if install_root_config.exists():
            try:
                config = json.loads(install_root_config.read_text(encoding="utf-8"))
                if not isinstance(config, dict):
                    raise ValueError("install_root.json root element is not an object")

                install_root = Path(config.get("install_root", ""))
                if install_root.exists():
                    install_root = install_root.resolve()
                    if install_root != self.repo_root:
                        result["errors"].append(
                            "Workspace install root is stale: install_root.json points to a different PECS root"
                        )
                        result["valid"] = False
                else:
                    result["errors"].append(
                        "Workspace install root config references a missing PECS install root"
                    )
                    result["valid"] = False

                python_path = config.get("python_path", "")
                if not python_path or not Path(python_path).exists():
                    result["errors"].append(
                        "Workspace install root runtime is incomplete: python_path is missing or invalid"
                    )
                    result["valid"] = False

                console_scripts = config.get("console_scripts", {})
                if not isinstance(console_scripts, dict):
                    console_scripts = {}
                for name in ["pecs", "pecs-pro-daemon"]:
                    script_path = console_scripts.get(name, "")
                    if not script_path or not Path(script_path).exists():
                        result["warnings"].append(
                            f"Workspace install root is missing expected console script: {name}"
                        )
            except Exception:
                result["errors"].append(
                    "Workspace install root config is invalid or unreadable"
                )
                result["valid"] = False
        else:
            result["errors"].append(
                "Workspace install root config missing: .pecs/config/install_root.json"
            )
            result["valid"] = False

        for launcher_path in [
            ".pecs/run_pecs.sh",
            ".pecs/run_pecs.cmd",
            ".pecs/run_pecs.ps1",
            ".pecs/run_pecs_daemon.sh",
            ".pecs/run_pecs_daemon.cmd",
            ".pecs/run_pecs_daemon.ps1",
        ]:
            full_path = self.workspace_root / launcher_path
            if not full_path.exists():
                result["errors"].append(f"Workspace launcher missing: {launcher_path}")
                result["valid"] = False
            elif full_path.suffix == ".sh" and not os.access(full_path, os.X_OK):
                result["warnings"].append(
                    f"Workspace launcher exists but is not executable: {launcher_path}"
                )

        stale_runtime_paths = [
            ".pecs/pecs_pro",
            ".pecs/pecs_pro.egg-info",
            ".pecs/pecs_pro.dist-info",
        ]
        for stale_path in stale_runtime_paths:
            full_path = self.workspace_root / stale_path
            if full_path.exists():
                result["errors"].append(
                    f"Stale workspace-local PECS runtime copy detected: {stale_path}"
                )
                result["valid"] = False

        tasks_path = self.workspace_root / ".vscode" / "tasks.json"
        if tasks_path.exists():
            task_data = tasks_path.read_text(encoding="utf-8")
            matches = re.findall(r'PECS_PRO_REPO="([^"]+)"', task_data)
            for match in matches:
                try:
                    referenced_root = Path(match).resolve()
                    if referenced_root != self.repo_root:
                        result["errors"].append(
                            f"Stale PECS install root reference in tasks: {referenced_root}"
                        )
                        result["valid"] = False
                except Exception:
                    result["warnings"].append(
                        f"Could not resolve referenced PECS root in tasks: {match}"
                    )

    def repair_installation(self) -> Dict[str, Any]:
        """Repair broken PECS workspace installation."""
        logger.info(f"Repairing PECS installation in {self.workspace_root}")

        result = {
            "status": "started",
            "timestamp": datetime.now().isoformat(),
            "workspace": str(self.workspace_root),
            "repairs": [],
            "errors": [],
        }

        try:
            # Reinstall missing assets
            repair_config = self.manifest.get("repair", {})

            # Re-deploy all assets
            for asset in self.manifest.get("assets", []):
                if asset.get("required", False):
                    try:
                        source_file = asset.get("source")
                        target_path = asset.get("target")
                        source = self.assets_dir / source_file
                        target = self.workspace_root / target_path

                        if (
                            not target.exists()
                            or source.stat().st_mtime > target.stat().st_mtime
                        ):
                            target.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(source, target)
                            result["repairs"].append(f"Repaired {target_path}")
                            logger.info(f"Repaired {target_path}")
                    except Exception as e:
                        logger.error(f"Failed to repair {asset.get('id')}: {e}")
                        result["errors"].append(str(e))

            # Verify after repair
            verification = self.verify_installation()
            result["verification"] = verification
            result["status"] = "success" if verification["valid"] else "partial"

        except Exception as e:
            result["status"] = "failed"
            result["errors"].append(str(e))
            logger.error(f"Repair failed: {e}")
            raise

        return result


def setup_logging(verbose: bool = False) -> None:
    """Setup logging for workspace assets manager."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
