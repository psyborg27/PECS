from __future__ import annotations

import datetime
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

from pecs_pro.install_workspace_integration import health_check
from pecs_pro.workspace_assets_manager import WorkspaceAssetsManager
from scripts.validate_workspace_continuity import validate_workspace_continuity

READINESS_SCHEMA = "pecs.workspace_readiness.v1"
READINESS_FILENAME = "workspace_readiness.json"
READINESS_REPORT_FILENAME = "workspace_readiness_report.json"


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def _read_pid_file(pid_file: Path) -> Optional[int]:
    try:
        raw = pid_file.read_text(encoding="utf-8").strip()
    except OSError:
        return None

    if raw.startswith('"') and raw.endswith('"'):
        raw = raw[1:-1].strip()
    if raw.startswith("'") and raw.endswith("'"):
        raw = raw[1:-1].strip()
    return int(raw) if raw.isdigit() else None


def _is_process_running(pid: int) -> bool:
    try:
        subprocess.run(["kill", "-0", str(pid)], check=True, capture_output=True)
        return True
    except Exception:
        return False


def _status_pass() -> Dict[str, str]:
    return {"status": "PASS"}


def _status_fail(reason: str, recommended_action: str) -> Dict[str, str]:
    return {
        "status": "FAIL",
        "reason": reason,
        "recommended_action": recommended_action,
    }


def _normalize_bool(value: Any) -> bool:
    return bool(value)


def _component_status(value: bool, fail_reason: str, recommended_action: str) -> Dict[str, str]:
    return _status_pass() if value else _status_fail(fail_reason, recommended_action)


def _install_stage_status(install_info: Dict[str, Any]) -> Dict[str, str]:
    dependencies = install_info.get("dependencies", {}) or {}
    dependencies_ok = all(str(status) == "ok" for status in dependencies.values())
    install_ok = bool(
        install_info.get("workspace_exists", False)
        and dependencies_ok
        and install_info.get("package_installed", False)
        and install_info.get("daemon_script_exists", False)
    )
    if install_ok:
        return _status_pass()

    missing_fields = []
    if not install_info.get("workspace_exists", False):
        missing_fields.append("workspace does not exist")
    if not install_info.get("package_installed", False):
        missing_fields.append("PECS package not installed")
    if not dependencies_ok:
        missing_deps = [name for name, status in dependencies.items() if status != "ok"]
        missing_fields.append(f"missing dependencies: {missing_deps}")
    if not install_info.get("daemon_script_exists", False):
        missing_fields.append("daemon launcher script missing")

    reason = "; ".join(missing_fields) if missing_fields else "Installation verification failed"
    return _status_fail(
        reason,
        "Activate the PECS repo venv, install required dependencies, and ensure the workspace bind is correct.",
    )


def _assets_stage_status(verify_result: Dict[str, Any]) -> Dict[str, str]:
    if verify_result.get("valid", False):
        return _status_pass()
    return _status_fail(
        "Workspace asset verification failed.",
        "Run 'pecs verify-workspace <workspace>' and repair missing or outdated assets.",
    )


def _bridge_stage_status(validate_result: Dict[str, Any], bridge_error: Optional[str]) -> Dict[str, str]:
    if bridge_error:
        return _status_fail(
            f"Bridge validation failed: {bridge_error}",
            "Fix bridge execution or local runtime import issues and retry 'pecs workspace-ready'.",
        )
    if validate_result.get("success", False):
        return _status_pass()
    return _status_fail(
        "Bridge validation reported failure.",
        "Inspect bridge validation output and fix workspace continuity issues.",
    )


def _daemon_stage_status(health_state: Dict[str, Any], daemon_pid: Optional[int], process_running: bool) -> Dict[str, str]:
    if not daemon_pid:
        return _status_fail(
            "Daemon PID file missing or invalid.",
            "Start the workspace daemon or restore .pecs/daemon.pid.",
        )
    if not process_running:
        return _status_fail(
            f"Daemon process not running (PID {daemon_pid}).",
            "Start the workspace daemon and verify the PID file.",
        )
    if not health_state:
        return _status_fail(
            "Daemon health artifact missing.",
            "Ensure the daemon has written .pecs/daemon_health.json after refresh.",
        )
    if health_state.get("status") != "healthy":
        return _status_fail(
            "Daemon health is not healthy.",
            "Review daemon logs and fix the daemon health issues.",
        )
    if not _normalize_bool(health_state.get("retrieval_ready")):
        return _status_fail(
            "Daemon retrieval_ready flag is false.",
            "Ensure the daemon successfully refreshed workspace continuity.",
        )
    if not _normalize_bool(health_state.get("topology_ready")):
        return _status_fail(
            "Daemon topology_ready flag is false.",
            "Run a workspace refresh and wait for topology rebuild to complete.",
        )
    if not _normalize_bool(health_state.get("continuity_ready")):
        return _status_fail(
            "Daemon continuity_ready flag is false.",
            "Refresh continuity state and verify the daemon has all required artifacts.",
        )
    return _status_pass()


def _topology_stage_status(workspace_root: Path, health_state: Dict[str, Any]) -> Dict[str, str]:
    graph_exists = (workspace_root / ".pecs" / "workspace_graph.json").exists()
    registry_exists = (workspace_root / ".pecs" / "workspace_registry.json").exists()
    topology_ready = _normalize_bool(health_state.get("topology_ready"))
    if topology_ready and graph_exists and registry_exists:
        return _status_pass()
    missing = []
    if not topology_ready:
        missing.append("topology_ready flag false")
    if not graph_exists:
        missing.append("workspace_graph.json missing")
    if not registry_exists:
        missing.append("workspace_registry.json missing")
    return _status_fail(
        f"Topology rebuild status incomplete: {', '.join(missing)}.",
        "Refresh the workspace continuity and ensure the workspace graph and registry artifacts are present.",
    )


def _validation_stage_status(validation_report: Dict[str, Any], stage_name: str) -> Dict[str, str]:
    if validation_report.get("valid", False):
        return _status_pass()
    return _status_fail(
        f"{stage_name} validation failed.",
        f"Inspect .pecs/{stage_name.lower()}_validation.json and fix reported issues.",
    )


def _canonical_stage_status(canonical_report: Dict[str, Any]) -> Dict[str, str]:
    if canonical_report.get("valid", False):
        return _status_pass()
    return _status_fail(
        "Canonical workspace validation failed.",
        "Run 'pecs validate <workspace>' and fix the canonical verification issues.",
    )


def _consumer_stage_status(canonical_report: Dict[str, Any]) -> Dict[str, str]:
    checks = canonical_report.get("checks", {}) if isinstance(canonical_report, dict) else {}
    integrations_ok = bool(checks.get("consumer_integrations", False))
    compliance_ok = bool(checks.get("consumer_compliance", False))
    if integrations_ok and compliance_ok:
        return _status_pass()
    return _status_fail(
        "Consumer integration validation failed.",
        "Fix consumer integration assets and compliance failures reported by canonical validation.",
    )


def _write_readiness_artifact(workspace_root: Path, payload: Dict[str, Any]) -> None:
    pecs_dir = workspace_root / ".pecs"
    pecs_dir.mkdir(parents=True, exist_ok=True)
    artifact = pecs_dir / READINESS_FILENAME
    artifact.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_readiness_report_artifact(workspace_root: Path, payload: Dict[str, Any]) -> None:
    pecs_dir = workspace_root / ".pecs"
    pecs_dir.mkdir(parents=True, exist_ok=True)
    artifact = pecs_dir / READINESS_REPORT_FILENAME
    artifact.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _artifact_inventory(workspace_root: Path) -> Dict[str, bool]:
    pecs_dir = workspace_root / ".pecs"
    return {
        "daemon_health": (pecs_dir / "daemon_health.json").exists(),
        "daemon_pid": (pecs_dir / "daemon.pid").exists(),
        "workspace_graph": (pecs_dir / "workspace_graph.json").exists(),
        "workspace_registry": (pecs_dir / "workspace_registry.json").exists(),
        "workspace_graph_validation": (pecs_dir / "workspace_graph_validation.json").exists(),
        "workspace_registry_validation": (pecs_dir / "workspace_registry_validation.json").exists(),
        "readiness": (pecs_dir / READINESS_FILENAME).exists(),
    }


def _collect_component_summaries(report: Dict[str, Any]) -> Dict[str, Any]:
    failures = []
    warnings = []
    recommendations = []

    for key, component in report.items():
        if not isinstance(component, dict):
            continue
        status = component.get("status")
        if status == "FAIL":
            reason = component.get("reason")
            action = component.get("recommended_action")
            if reason:
                failures.append(f"{key}: {reason}")
            if action:
                recommendations.append(action)
        if component.get("warnings"):
            warnings.extend(component.get("warnings") if isinstance(component.get("warnings"), list) else [str(component.get("warnings"))])

    return {
        "failures": failures,
        "warnings": warnings,
        "recommendations": [rec for rec in dict.fromkeys(recommendations) if rec],
    }


def generate_workspace_readiness_report(
    workspace_root: Path,
    repo_root: Optional[Path] = None,
) -> Dict[str, Any]:
    workspace_root = workspace_root.resolve()
    repo_root = repo_root.resolve() if repo_root is not None else Path(__file__).resolve().parents[1]

    health_info: Dict[str, Any] = {}
    install_status: Dict[str, str] = _status_fail(
        "Installation verification failed.",
        "Activate the PECS repo venv and fix installation issues.",
    )
    assets_status: Dict[str, str] = _status_fail(
        "Workspace assets verification failed.",
        "Inspect workspace assets and run 'pecs verify-workspace'.",
    )
    bridge_status: Dict[str, str] = _status_fail(
        "Bridge verification failed.",
        "Inspect bridge configuration and run 'pecs validate'.",
    )
    daemon_status: Dict[str, str] = _status_fail(
        "Daemon health check failed.",
        "Start the workspace daemon and inspect daemon health.",
    )
    topology_status: Dict[str, str] = _status_fail(
        "Topology rebuild status failed.",
        "Trigger a workspace refresh and verify topology artifacts.",
    )
    graph_status: Dict[str, str] = _status_fail(
        "Workspace graph validation failed.",
        "Inspect the workspace graph validation artifact in .pecs.",
    )
    registry_status: Dict[str, str] = _status_fail(
        "Workspace registry validation failed.",
        "Inspect the workspace registry validation artifact in .pecs.",
    )
    canonical_status: Dict[str, str] = _status_fail(
        "Canonical validation failed.",
        "Run 'pecs validate' and resolve canonical verification failures.",
    )
    consumer_status: Dict[str, str] = _status_fail(
        "Consumer integration validation failed.",
        "Fix consumer integration compliance issues and required assets.",
    )

    install_info: Dict[str, Any] = {}
    asset_verify_info: Dict[str, Any] = {}
    bridge_info: Dict[str, Any] = {}
    canonical_info: Dict[str, Any] = {}
    daemon_health: Dict[str, Any] = {}
    topology_info: Dict[str, Any] = {}
    graph_validation: Dict[str, Any] = {}
    registry_validation: Dict[str, Any] = {}

    if workspace_root.exists():
        try:
            install_info = health_check(workspace_root, repo_root, verbose=False)
            install_status = _install_stage_status(install_info)
        except Exception as exc:
            install_status = _status_fail(
                f"Installation verification error: {exc}",
                "Run dependency and install health checks from the PECS repository.",
            )

        try:
            manager = WorkspaceAssetsManager(repo_root, workspace_root)
            asset_verify_info = manager.verify_installation()
            assets_status = _assets_stage_status(asset_verify_info)
        except Exception as exc:
            assets_status = _status_fail(
                f"Workspace assets verification error: {exc}",
                "Inspect workspace asset installation and retry.",
            )

        bridge_error: Optional[str] = None
        try:
            bridge_info = validate_workspace_continuity(workspace_root)
            bridge_status = _bridge_stage_status(bridge_info, None)
            canonical_info = bridge_info.get("canonical_verification", {}) or {}
            canonical_status = _canonical_stage_status(canonical_info)
            consumer_status = _consumer_stage_status(canonical_info)
        except Exception as exc:
            bridge_error = str(exc)
            bridge_status = _bridge_stage_status({}, bridge_error)
            canonical_status = _status_fail(
                "Canonical validation unavailable due to bridge validation error.",
                "Fix bridge validation errors and retry readiness.",
            )
            consumer_status = _status_fail(
                "Consumer integration validation unavailable.",
                "Resolve bridge validation errors before running consumer integration checks.",
            )

        daemon_health = _load_json(workspace_root / ".pecs" / "daemon_health.json")
        pid_file = workspace_root / ".pecs" / "daemon.pid"
        daemon_pid = _read_pid_file(pid_file) if pid_file.exists() else None
        daemon_running = _is_process_running(daemon_pid) if daemon_pid else False
        daemon_status = _daemon_stage_status(daemon_health, daemon_pid, daemon_running)

        topology_status = _topology_stage_status(workspace_root, daemon_health)

        graph_validation = _load_json(workspace_root / ".pecs" / "workspace_graph_validation.json")
        graph_status = _validation_stage_status(graph_validation, "Workspace graph")

        registry_validation = _load_json(workspace_root / ".pecs" / "workspace_registry_validation.json")
        registry_status = _validation_stage_status(registry_validation, "Workspace registry")

    else:
        install_status = _status_fail(
            "Workspace does not exist.",
            "Provide a valid workspace root for readiness evaluation.",
        )

    overall_ready = all(
        component["status"] == "PASS"
        for component in [
            install_status,
            assets_status,
            bridge_status,
            daemon_status,
            topology_status,
            graph_status,
            registry_status,
            canonical_status,
            consumer_status,
        ]
    )

    summary = _collect_component_summaries({
        "installation": install_status,
        "workspace_assets": assets_status,
        "bridge": bridge_status,
        "daemon": daemon_status,
        "topology": topology_status,
        "workspace_graph": graph_status,
        "workspace_registry": registry_status,
        "canonical_validation": canonical_status,
        "consumer_integration": consumer_status,
    })

    result: Dict[str, Any] = {
        "schema": READINESS_SCHEMA,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "workspace": str(workspace_root),
        "ready": overall_ready,
        "installation": install_status,
        "workspace_assets": assets_status,
        "bridge": bridge_status,
        "daemon": daemon_status,
        "topology": topology_status,
        "workspace_graph": graph_status,
        "workspace_registry": registry_status,
        "canonical_validation": canonical_status,
        "consumer_integration": consumer_status,
        "artifact_inventory": _artifact_inventory(workspace_root),
        "failures": summary["failures"],
        "warnings": summary["warnings"],
        "recommendations": summary["recommendations"],
        "overall": {"status": "READY" if overall_ready else "NOT READY"},
    }

    write_workspace_readiness_json(workspace_root, result)
    _write_readiness_report_artifact(workspace_root, result)
    return result


def write_workspace_readiness_json(workspace_root: Path, report: Dict[str, Any]) -> None:
    _write_readiness_artifact(workspace_root, report)
