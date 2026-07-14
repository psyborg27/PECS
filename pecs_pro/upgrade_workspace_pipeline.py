from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from pecs_pro.install_workspace_integration import install_workspace
from pecs_pro.workspace_assets_manager import WorkspaceAssetsManager
from validation.canonical_workspace_validator import run_canonical_workspace_validation

UPGRADE_OBSOLETE_PATHS = [
    "pecs_lite",
    "run_pecs_lite.sh",
    "runtime_observability_daemon",
    "runtime_observability_daemon.py",
    "start_pecs_daemon.sh",
    ".pecs/pecs_lite_runtime_projection.json",
    ".pecs/daemon_lite_v2.pid",
    ".pecs/daemon_lite_v2_state.json",
    ".pecs/bridge/run_runtime_topology_build.py",
    ".pecs/bridge/export_workspace_continuity.py",
    ".pecs/bridge/validate_workspace_continuity.py",
    ".pecs/pecs_pro",
    ".pecs/pecs_pro.egg-info",
    ".pecs/pecs_pro.dist-info",
    "docs/README_ALPHA1.md",
]

ManagedArtifactClassification = str


@dataclass
class WorkspaceUpgradePlan:
    workspace_root: Path
    repo_root: Path
    installed_version: Optional[str] = None
    installer_version: Optional[str] = None
    launcher_version: Optional[str] = None
    bridge_version: Optional[str] = None
    daemon_version: Optional[str] = None
    workspace_health: Dict[str, Any] = field(default_factory=dict)
    managed_asset_status: Dict[str, str] = field(default_factory=dict)
    generated_artifact_status: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    consumer_config_present: Dict[str, bool] = field(default_factory=dict)
    workspace_install_root: Optional[Path] = None
    workspace_install_root_matches_repo_root: bool = False
    stale_workspace_runtime_paths: List[str] = field(default_factory=list)
    legacy_artifacts: List[str] = field(default_factory=list)
    classified_artifacts: Dict[str, ManagedArtifactClassification] = field(default_factory=dict)


@dataclass
class UpgradeReport:
    before_versions: Dict[str, Optional[str]] = field(default_factory=dict)
    after_versions: Dict[str, Optional[str]] = field(default_factory=dict)
    preserved_files: List[str] = field(default_factory=list)
    merged_files: List[str] = field(default_factory=list)
    replaced_files: List[str] = field(default_factory=list)
    regenerated_files: List[str] = field(default_factory=list)
    removed_files: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    validation_results: Dict[str, Any] = field(default_factory=dict)
    canonical_verification: Dict[str, Any] = field(default_factory=dict)
    rollback_location: Optional[str] = None
    elapsed_seconds: float = 0.0
    success: bool = False


class UpgradeWorkspacePipeline:
    def __init__(self, workspace_root: Path, repo_root: Optional[Path] = None):
        self.workspace_root = workspace_root.resolve()
        self.repo_root = repo_root.resolve() if repo_root else Path(__file__).resolve().parent.parent
        self.manager = WorkspaceAssetsManager(self.repo_root, self.workspace_root)
        self.plan: Optional[WorkspaceUpgradePlan] = None
        self.report: Optional[UpgradeReport] = None

    def run(self) -> UpgradeReport:
        started = time.time()
        self.plan = self.inspect_workspace()
        self.plan = self.classify_artifacts(self.plan)
        report = UpgradeReport()
        report.before_versions = self._versions_from_plan(self.plan)

        # Backup and deployment are performed together by the existing asset manager.
        install_result = self.manager.install_assets(upgrade=True, verify=False)
        # Remove obsolete paths BEFORE install_workspace so removal is detected
        # and reported (install_workspace also removes them but doesn't report).
        report.removed_files = self._perform_obsolete_cleanup()
        install_workspace(self.workspace_root, self.repo_root, preserve_existing=True)
        report.rollback_location = str(self.workspace_root / ".pecs" / "backups")
        report.warnings.extend(install_result.get("warnings", []))

        self._capture_deployment_report(report, self.plan)

        self.regenerate_artifacts()
        report.regenerated_files = self._regenerated_files()

        self.restart_daemon_if_required()

        validation_results = self.validate_workspace_installation()
        report.validation_results = validation_results
        report.canonical_verification = self._run_canonical_verification()

        report.after_versions = self._reload_versions()
        report.preserved_files = self._classified_files_by_type("PRESERVE")
        report.merged_files = self._classified_files_by_type("MERGE")
        report.replaced_files = self._classified_files_by_type("REPLACE")
        report.elapsed_seconds = time.time() - started
        report.success = (
            validation_results.get("verify", False)
            and validation_results.get("doctor", False)
            and bool(report.canonical_verification.get("valid", False))
        )
        self.report = report
        return report

    def inspect_workspace(self) -> WorkspaceUpgradePlan:
        plan = WorkspaceUpgradePlan(
            workspace_root=self.workspace_root,
            repo_root=self.repo_root,
        )

        plan.installed_version = self._read_repo_version(self.repo_root)
        plan.installer_version = plan.installed_version
        plan.launcher_version = self._detect_launcher_version()
        plan.bridge_version = self._detect_bridge_version()
        plan.daemon_version = self._detect_daemon_version()
        plan.workspace_health = self._read_daemon_health()
        plan.managed_asset_status = self._detect_managed_asset_status()
        plan.generated_artifact_status = self._detect_generated_artifacts()
        plan.consumer_config_present = self._detect_consumer_configurations()
        plan.workspace_install_root = self._read_workspace_install_root()
        plan.workspace_install_root_matches_repo_root = (
            plan.workspace_install_root == self.repo_root
            if plan.workspace_install_root is not None
            else False
        )
        plan.stale_workspace_runtime_paths = self._detect_stale_workspace_runtime_paths()
        plan.legacy_artifacts = self._detect_legacy_artifacts()

        return plan

    def classify_artifacts(self, plan: WorkspaceUpgradePlan) -> WorkspaceUpgradePlan:
        classified: Dict[str, ManagedArtifactClassification] = {}
        for asset_file, asset_info in plan.managed_asset_status.items():
            strategy = asset_info.get("merge_strategy")
            exists = asset_info.get("exists", False)
            if strategy in {"append", "append_or_merge", "merge_yaml", "merge_markdown"}:
                classified[asset_file] = "MERGE"
            elif strategy == "create_if_missing":
                classified[asset_file] = "PRESERVE" if exists else "REPLACE"
            elif strategy == "overwrite":
                classified[asset_file] = "REPLACE"
            elif strategy == "preserve_existing":
                classified[asset_file] = "PRESERVE" if exists else "REPLACE"
            else:
                classified[asset_file] = "REPLACE"

        for artifact in plan.generated_artifact_status.keys():
            classified[artifact] = "REGENERATE"

        for legacy in plan.legacy_artifacts:
            classified[legacy] = "REMOVE"

        plan.classified_artifacts = classified
        return plan

    def regenerate_artifacts(self) -> None:
        self._run_workspace_bridge("refresh")
        self._ensure_workspace_graph_and_registry()
        self._exercise_query_pipeline()

    def restart_daemon_if_required(self) -> None:
        health = self._read_daemon_health()
        if health.get("status") != "healthy" or not health.get("continuity_ready", False):
            self._start_workspace_daemon()
            self._wait_for_daemon_health()

    def validate_workspace_installation(self) -> Dict[str, Any]:
        results: Dict[str, Any] = {}
        results["verify"] = self._run_verify_workspace()
        results["doctor"] = self._run_doctor()
        results["legacy_validate"] = self._run_validate_workspace()
        results["canonical"] = bool(
            self._run_canonical_verification().get("valid", False)
        )
        results["validate"] = results["canonical"]
        return results

    def _run_canonical_verification(self) -> Dict[str, Any]:
        return run_canonical_workspace_validation(self.workspace_root, self.repo_root)

    def _capture_deployment_report(self, report: UpgradeReport, plan: WorkspaceUpgradePlan) -> None:
        report.warnings.extend(plan.workspace_health.get("warnings", []))

    def _consider_file_path(self, path: Path) -> str:
        return str(path.relative_to(self.workspace_root)).replace("\\", "/")

    def _versions_from_plan(self, plan: WorkspaceUpgradePlan) -> Dict[str, Optional[str]]:
        return {
            "installed": plan.installed_version,
            "installer": plan.installer_version,
            "launcher": plan.launcher_version,
            "bridge": plan.bridge_version,
            "daemon": plan.daemon_version,
        }

    def _reload_versions(self) -> Dict[str, Optional[str]]:
        return {
            "installed": self._read_repo_version(self.repo_root),
            "installer": self._read_repo_version(self.repo_root),
            "launcher": self._detect_launcher_version(),
            "bridge": self._detect_bridge_version(),
            "daemon": self._detect_daemon_version(),
        }

    def _classified_files_by_type(self, classification: str) -> List[str]:
        if not self.plan:
            return []
        return sorted([path for path, outcome in self.plan.classified_artifacts.items() if outcome == classification])

    def _read_repo_version(self, repo_root: Path) -> Optional[str]:
        version_file = repo_root / "VERSION"
        if version_file.exists():
            return version_file.read_text(encoding="utf-8").strip()
        return None

    def _detect_launcher_version(self) -> Optional[str]:
        run_shell = self.workspace_root / ".pecs" / "run_pecs.sh"
        if run_shell.exists():
            return "managed-launcher"
        return None

    def _detect_bridge_version(self) -> Optional[str]:
        run_bridge = self.workspace_root / ".pecs" / "bridge" / "run_bridge.py"
        if run_bridge.exists():
            return "managed-bridge"
        return None

    def _detect_daemon_version(self) -> Optional[str]:
        health = self._read_daemon_health()
        if health:
            return str(health.get("daemon_version", "unknown"))
        return None

    def _read_daemon_health(self) -> Dict[str, Any]:
        health_path = self.workspace_root / ".pecs" / "daemon_health.json"
        if health_path.exists():
            try:
                return json.loads(health_path.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}

    def _detect_managed_asset_status(self) -> Dict[str, Dict[str, Any]]:
        status: Dict[str, Dict[str, Any]] = {}
        for asset in self.manager.manifest.get("assets", []):
            target = self.workspace_root / asset.get("target", "")
            status[str(target.relative_to(self.workspace_root))] = {
                "exists": target.exists(),
                "merge_strategy": asset.get("merge_strategy", "overwrite"),
                "required": asset.get("required", False),
            }
        return status

    def _detect_generated_artifacts(self) -> Dict[str, Dict[str, Any]]:
        artifacts = [
            ".pecs/active_context.json",
            ".pecs/locality_index.json",
            ".pecs/topology_compact.json",
            ".pecs/compact_bundle.json",
            ".pecs/session_context.json",
            ".pecs/daemon_state.json",
            ".pecs/daemon_health.json",
            ".pecs/runtime_activation.jsonl",
            ".pecs/continuity/active_topology.json",
            ".pecs/continuity/locality_state.json",
            ".pecs/continuity/engineering_continuity_state.json",
            ".pecs/continuity/continuity_hydration_report.json",
        ]
        status: Dict[str, Dict[str, Any]] = {}
        for artifact in artifacts:
            path = self.workspace_root / artifact
            status[artifact] = {
                "exists": path.exists(),
                "size": path.stat().st_size if path.exists() else 0,
                "modified_time": path.stat().st_mtime if path.exists() else None,
            }
        return status

    def _detect_consumer_configurations(self) -> Dict[str, bool]:
        return {
            "copilot": (self.workspace_root / ".github" / "copilot-instructions.md").exists(),
            "continue": (self.workspace_root / ".continue" / "config.yaml").exists(),
            "kimi": (self.workspace_root / ".kimi" / "instructions.md").exists(),
            "commandcode": (self.workspace_root / ".commandcode" / "instructions.md").exists(),
        }

    def _detect_legacy_artifacts(self) -> List[str]:
        legacy: List[str] = []
        for path_name in UPGRADE_OBSOLETE_PATHS:
            candidate = self.workspace_root / path_name
            if candidate.exists():
                legacy.append(path_name)
        return legacy

    def _read_workspace_install_root(self) -> Optional[Path]:
        config_path = self.workspace_root / ".pecs" / "config" / "install_root.json"
        if not config_path.exists():
            return None

        try:
            payload = json.loads(config_path.read_text(encoding="utf-8"))
        except Exception:
            return None

        if not isinstance(payload, dict):
            return None

        raw_root = str(payload.get("install_root", "") or "").strip()
        if not raw_root:
            return None

        try:
            return Path(raw_root).resolve()
        except Exception:
            return None

    def _detect_stale_workspace_runtime_paths(self) -> List[str]:
        stale: List[str] = []
        for path_name in [".pecs/pecs_pro", ".pecs/pecs_pro.egg-info", ".pecs/pecs_pro.dist-info"]:
            if (self.workspace_root / path_name).exists():
                stale.append(path_name)
        return stale

    def _run_workspace_bridge(self, command: str) -> Dict[str, Any]:
        bridge_script = self.workspace_root / ".pecs" / "bridge" / "run_bridge.py"
        if not bridge_script.exists():
            raise FileNotFoundError(f"Workspace bridge not installed: {bridge_script}")

        result = subprocess.run(
            [
                os.environ.get("PYTHON", os.sys.executable),
                str(bridge_script),
                command,
                "--workspace",
                str(self.workspace_root),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        try:
            parsed = json.loads(result.stdout)
            if isinstance(parsed, dict):
                parsed.setdefault("success", result.returncode == 0)
                parsed["returncode"] = result.returncode
                return parsed
            return {
                "success": result.returncode == 0,
                "payload": parsed,
                "returncode": result.returncode,
            }
        except Exception:
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }

    def _ensure_workspace_graph_and_registry(self) -> None:
        try:
            from execution_graph.builders.workspace_graph_builder import (
                WorkspaceGraphBuilder,
            )
            from workspace_registry.builders.workspace_registry_builder import (
                WorkspaceRegistryBuilder,
            )
        except Exception:
            return

        locality_path = self.workspace_root / ".pecs" / "locality_index.json"
        topology_path = self.workspace_root / ".pecs" / "topology_compact.json"
        if not locality_path.exists() or not topology_path.exists():
            return

        try:
            locality_payload = json.loads(locality_path.read_text(encoding="utf-8"))
            topology_payload = json.loads(topology_path.read_text(encoding="utf-8"))
        except Exception:
            return

        entrypoints: List[Path] = []
        for entrypoint in topology_payload.get("entrypoints", []):
            try:
                candidate = self.workspace_root / (entrypoint.replace("PECS_ID:", "").replace(".", "/") + ".py")
                if candidate.exists():
                    entrypoints.append(candidate)
            except Exception:
                continue

        graph_builder = WorkspaceGraphBuilder(self.workspace_root)
        graph = graph_builder.build(
            reachable_files=set(),
            runtime_locality_payload=locality_payload,
            runtime_topology_edges=topology_payload.get("edges", []),
            entrypoints=entrypoints,
        )

        registry_builder = WorkspaceRegistryBuilder(self.workspace_root)
        registry = registry_builder.build(graph)

        graph_path = self.workspace_root / ".pecs" / "workspace_graph.json"
        registry_path = self.workspace_root / ".pecs" / "workspace_registry.json"
        graph_path.write_text(json.dumps(graph.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
        registry_path.write_text(json.dumps(registry.to_dict(), indent=2, sort_keys=True), encoding="utf-8")

    def _exercise_query_pipeline(self) -> None:
        try:
            from pecs_query.pipeline import PECSQueryPipeline
        except Exception:
            return

        pipeline = PECSQueryPipeline(self.workspace_root)
        pipeline.query(["upgrade"], max_clusters=1, max_nodes=1, max_depth=1)

    def _start_workspace_daemon(self) -> None:
        from workspace_bridge_cli import _start_workspace_daemon as _start_daemon

        _start_daemon(self.workspace_root)

    def _wait_for_daemon_health(self, timeout_seconds: int = 60) -> None:
        end_time = time.time() + timeout_seconds
        while time.time() < end_time:
            health = self._read_daemon_health()
            if health.get("status") == "healthy" and health.get("continuity_ready") is True:
                return
            time.sleep(1)
        raise RuntimeError("Daemon did not reach healthy state within timeout")

    def _run_verify_workspace(self) -> bool:
        try:
            from workspace_bridge_cli import _cmd_verify_workspace
        except Exception:
            return False

        args = type("Args", (), {"workspace_root": str(self.workspace_root), "repo_root": str(self.repo_root), "json": True})
        try:
            _cmd_verify_workspace(args)
            return True
        except SystemExit as exc:
            return exc.code == 0

    def _run_validate_workspace(self) -> bool:
        result = self._run_workspace_bridge("validate")
        if isinstance(result, dict):
            if "success" in result:
                return bool(result.get("success", False))
            return bool(result.get("returncode", 1) == 0)
        return False

    def _run_doctor(self) -> bool:
        try:
            from workspace_bridge_cli import _cmd_doctor
        except Exception:
            return False

        args = type("Args", (), {"workspace_root": str(self.workspace_root), "repo_root": str(self.repo_root)})
        try:
            _cmd_doctor(args)
            return True
        except SystemExit as exc:
            return exc.code == 0

    def _perform_obsolete_cleanup(self) -> List[str]:
        removed: List[str] = []
        from datetime import datetime
        for path_name in self.plan.legacy_artifacts if self.plan else []:
            target = self.workspace_root / path_name
            if not target.exists():
                continue
            # Backup before removal (mirrors install_workspace's _cleanup_stale_local_runtime_copy)
            try:
                backup_dir = self.workspace_root / ".pecs" / "backups"
                backup_dir.mkdir(parents=True, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = backup_dir / f"stale_obsolete_{path_name.replace('/', '_')}_{timestamp}"
                if target.is_dir():
                    # Ignore .git to avoid socket files (fsmonitor--daemon.ipc) that break copytree
                    shutil.copytree(target, backup_path, ignore=shutil.ignore_patterns(".git"))
                    shutil.rmtree(target, ignore_errors=True)
                else:
                    shutil.copy2(target, backup_path)
                    target.unlink()
                removed.append(path_name)
            except Exception as e:
                import logging
                logging.getLogger(__name__).error("Failed to remove obsolete path %s: %s", path_name, e)
                continue
        return removed

    def _regenerated_files(self) -> List[str]:
        if not self.plan:
            return []
        return sorted([p for p, classification in self.plan.classified_artifacts.items() if classification == "REGENERATE"])
