"""PECS Workspace Assets Manager

Manages installation, verification, and repair of PECS workspace assets
using a manifest-driven approach.
"""

from __future__ import annotations

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
        logger.info(
            f"Loaded workspace assets manifest (v{self.manifest.get('version', '?')})"
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
                    asset_id, source, target, merge_strategy, upgrade
                )
                deployed.append(target_path)
                logger.info(f"Deployed asset {asset_id} to {target_path}")

            except Exception as e:
                logger.error(f"Failed to deploy asset {asset_id}: {e}")
                raise

        return deployed

    def _apply_merge_strategy(
        self, asset_id: str, source: Path, target: Path, strategy: str, upgrade: bool
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
            if target.exists() and target.suffix == ".md":
                source_content = source.read_text(encoding="utf-8")
                try:
                    target_content = target.read_text(encoding="utf-8")
                except Exception:
                    # Unable to safely read existing markdown; preserve original and provide manual merge guidance.
                    manual_merge = self.workspace_root / "PECS_COPILOT_APPEND.md"
                    manual_merge.write_text(source_content, encoding="utf-8")
                    logger.warning(
                        f"Unable to merge markdown asset {asset_id}; created manual merge file {manual_merge}"
                    )
                    return

                if source_content.strip() in target_content:
                    return

                marker = f"<!-- ASSET:{asset_id} -->"
                if marker in target_content:
                    return

                target.write_text(
                    target_content + "\n\n" + marker + "\n" + source_content,
                    encoding="utf-8",
                )
            else:
                shutil.copy2(source, target)

        elif strategy == "merge_yaml":
            if target.exists() and upgrade:
                # Preserve existing YAML content when a parseable merge is unavailable.
                logger.info(
                    f"YAML merge strategy is not supported in this environment for asset {asset_id}; preserving existing target"
                )
                return
            else:
                shutil.copy2(source, target)

        elif strategy == "merge_markdown":
            if target.exists() and upgrade:
                source_content = source.read_text(encoding="utf-8")
                target_content = target.read_text(encoding="utf-8")
                if source_content not in target_content:
                    target.write_text(
                        target_content + "\n\n" + source_content, encoding="utf-8"
                    )
            else:
                shutil.copy2(source, target)

        elif strategy == "preserve_existing":
            if not target.exists():
                shutil.copy2(source, target)

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
                # For lists, extend if not already present
                for item in value:
                    if item not in target[key]:
                        target[key].append(item)
            else:
                target[key] = value

    def verify_installation(self) -> Dict[str, Any]:
        """Verify PECS workspace assets are properly installed."""
        result = {
            "valid": True,
            "timestamp": datetime.now().isoformat(),
            "workspace": str(self.workspace_root),
            "checks": {},
            "errors": [],
            "warnings": [],
        }

        verification_config = self.manifest.get("verification", {})
        required_assets = verification_config.get("required_assets", [])
        required_daemon_files = verification_config.get("required_daemon_files", [])
        required_daemon_dirs = verification_config.get(
            "required_daemon_directories", []
        )

        # Check required assets
        for asset_path in required_assets:
            full_path = self.workspace_root / asset_path
            exists = full_path.exists()
            result["checks"][asset_path] = exists
            if not exists:
                result["errors"].append(f"Missing required asset: {asset_path}")
                result["valid"] = False
                logger.error(f"Missing required asset: {asset_path}")

        # Check daemon infrastructure
        for daemon_file in required_daemon_files:
            full_path = self.workspace_root / daemon_file
            if not full_path.exists():
                result["errors"].append(f"Missing daemon file: {daemon_file}")
                result["valid"] = False
                logger.error(f"Missing daemon file: {daemon_file}")

        for daemon_dir in required_daemon_dirs:
            full_path = self.workspace_root / daemon_dir
            if not full_path.exists():
                result["errors"].append(f"Missing daemon directory: {daemon_dir}")
                result["valid"] = False
                logger.error(f"Missing daemon directory: {daemon_dir}")

        self._verify_install_root_references(result)
        return result

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
