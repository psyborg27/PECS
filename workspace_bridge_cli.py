from __future__ import annotations

import argparse
import datetime
import hashlib
import importlib.metadata
import json
import logging
import os
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from dataclasses import asdict
from pecs_pro.install_workspace_integration import (
    install_workspace,
    print_install_root_guidance,
    read_registered_workspaces,
    validate_dependencies,
)
from pecs_pro.upgrade_workspace_pipeline import UpgradeWorkspacePipeline
from pecs_pro.workspace_assets_manager import WorkspaceAssetsManager

logger = logging.getLogger(__name__)


def _workspace_has_existing_assets(workspace_root: Path) -> bool:
    if not (workspace_root / ".pecs").exists():
        return False

    markers = [
        workspace_root / ".pecs" / "config" / "install_root.json",
        workspace_root / ".vscode" / "tasks.json",
        workspace_root / ".continue" / "config.yaml",
        workspace_root / ".github" / "copilot-instructions.md",
    ]
    return any(path.exists() for path in markers)


def _append_bounded_jsonl(path: Path, record: Dict[str, Any], max_records: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(record, ensure_ascii=True, sort_keys=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(payload + "\n")

    if max_records <= 0:
        return

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except Exception:
        return

    if len(lines) <= max_records:
        return

    trimmed = lines[-max_records:]
    path.write_text("\n".join(trimmed) + "\n", encoding="utf-8")


def _new_stable_id() -> str:
    return str(uuid.uuid4())


def _append_lifecycle_record(
    workspace_root: Path,
    event: str,
    payload: Dict[str, Any],
    max_records: int = 1000,
) -> None:
    record = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "workspace_root": str(workspace_root),
        "event": event,
        "payload": payload,
    }
    _append_bounded_jsonl(
        workspace_root / ".pecs" / "logs" / "lifecycle_commands.jsonl",
        record,
        max_records,
    )


def _ensure_correlation_context(args: argparse.Namespace) -> None:
    if not getattr(args, "trace_id", None):
        args.trace_id = _new_stable_id()
    if not getattr(args, "request_id", None):
        args.request_id = _new_stable_id()
    if not getattr(args, "causality_chain_id", None):
        args.causality_chain_id = args.trace_id


def _build_session_lineage(args: argparse.Namespace) -> Dict[str, Any]:
    workspace_root = Path(args.workspace_root).resolve()
    return {
        "workspace_id": hashlib.sha256(str(workspace_root).encode("utf-8")).hexdigest(),
        "session_id": str(args.session_id or ""),
        "query_source": str(args.query_source or ""),
        "profile_class": str(args.profile_class or ""),
        "local_vs_frontier": str(args.local_vs_frontier or ""),
        "request_id": str(getattr(args, "request_id", "")),
        "trace_id": str(getattr(args, "trace_id", "")),
        "causality_chain_id": str(getattr(args, "causality_chain_id", "")),
    }


def _capture_projection_observation(args: argparse.Namespace) -> Dict[str, Any]:
    try:
        from integrations.pecs_lite_runtime_adapter import PECSLiteRuntimeAdapter
    except Exception:
        try:
            from PECS.integrations.pecs_lite_runtime_adapter import PECSLiteRuntimeAdapter
        except Exception:
            from pecs_pro.integrations.pecs_lite_runtime_adapter import PECSLiteRuntimeAdapter

    workspace_root = Path(args.workspace_root).resolve()
    missing_identity_fields: List[str] = []
    if not str(args.model_name or "").strip():
        missing_identity_fields.append("model_name")
    if not str(args.model_source or args.provider or "").strip():
        missing_identity_fields.append("provider_or_source")
    if not str(args.profile_class or "").strip():
        missing_identity_fields.append("profile_class")
    if not str(args.local_vs_frontier or "").strip():
        missing_identity_fields.append("local_vs_frontier")

    unknown_model_identity = bool(missing_identity_fields)
    if unknown_model_identity:
        logger.warning(
            "unknown_model_identity: missing=%s; conservative shaping will be used",
            ",".join(missing_identity_fields),
        )

    projection = PECSLiteRuntimeAdapter.build_projection_safe(
        str(workspace_root),
        query=args.query,
        model_name=args.model_name,
        model_source=args.model_source,
        context_window=args.context_window,
        model_size=args.model_size,
        provider=args.provider,
        profile_class=str(args.profile_class or ""),
        local_vs_frontier=str(args.local_vs_frontier or ""),
        reasoning_capability_class=str(args.reasoning_capability_class or ""),
        query_source=args.query_source,
    )

    observability = projection.get("final_emission_observability", {}) or {}
    telemetry = projection.get("pecs_lite_telemetry", {}) or {}
    runtime_targets = projection.get("runtime_targets", []) or []
    secondary_neighbors = projection.get("secondary_neighbors", []) or []
    emitted = projection.get("emitted_advisory_cognition", {}) or {}
    discarded = projection.get("discarded_cognition_summary", {}) or {}
    shaping_losses = projection.get("shaping_losses", {}) or {}
    advisories = emitted.get("advisories", []) if isinstance(emitted, dict) else []

    workspace_id = hashlib.sha256(str(workspace_root).encode("utf-8")).hexdigest()
    snapshot = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "session_lineage": {
            "workspace_id": workspace_id,
            "session_id": str(observability.get("session_id", "") or args.session_id),
            "query_source": args.query_source,
        },
        "workspace_root": str(workspace_root),
        "query": args.query,
        "adapter": "PECSLiteRuntimeAdapter",
        "model": {
            "name": args.model_name,
            "source": args.model_source,
            "provider": args.provider,
            "provider_or_source": str(args.model_source or args.provider or ""),
            "runtime_origin": str(args.provider or args.model_source or ""),
            "size": args.model_size,
            "context_window": args.context_window,
            "profile_class": str(args.profile_class or ""),
            "local_vs_frontier": str(args.local_vs_frontier or ""),
            "reasoning_capability_class": str(args.reasoning_capability_class or ""),
            "unknown_model_identity": unknown_model_identity,
            "identity_missing_fields": missing_identity_fields,
        },
        "profile": observability.get("selected_projection_profile", "unknown"),
        "runtime_targets": runtime_targets,
        "secondary_neighbors": secondary_neighbors,
        "runtime_target_count": len(runtime_targets),
        "secondary_neighbor_count": len(secondary_neighbors),
        "emitted_advisory_cognition": emitted,
        "discarded_cognition_summary": discarded,
        "shaping_losses": shaping_losses,
        "advisory_reasoning": advisories,
        "payload_size_exact": len(json.dumps(projection, sort_keys=True, default=str)),
        "payload_compression": {
            "continuity_size": telemetry.get("continuity_size", 0),
            "compressed_continuity_size": telemetry.get("compressed_continuity_size", 0),
        },
        "projection_size": telemetry.get("payload_size", 0),
        "token_budget_selected": observability.get("token_budget_selected", 0),
        "suppression_reason_breakdown": observability.get("suppression_reason_breakdown", {}),
        "advisory_signal_priority": observability.get("advisory_signal_priority", []),
        "authority_confidence_band": observability.get("authority_confidence_band", "low"),
        "cognition_density_score": observability.get("cognition_density_score", 0.0),
        "topology_noise_ratio": observability.get("topology_noise_ratio", 0.0),
        "reconstructed_lineage_density": observability.get("reconstructed_lineage_density", 0.0),
        "continuity_reconstruction_confidence": observability.get("continuity_reconstruction_confidence", 0.0),
        "historical_engineering_gravity": observability.get("historical_engineering_gravity", 0.0),
        "continuity_condensation_score": observability.get("continuity_condensation_score", 0.0),
        "protected_authority_reinforcement": observability.get("protected_authority_reinforcement", {}),
        "lineage_fragmentation_score": observability.get("lineage_fragmentation_score", 0.0),
        "canonical_authority_clusters": observability.get("canonical_authority_clusters", []),
    }
    return snapshot


def _cmd_observe_projection_snapshot(args: argparse.Namespace) -> None:
    workspace_root = Path(args.workspace_root).resolve()
    if not workspace_root.exists():
        logger.error(f"Workspace does not exist: {workspace_root}")
        sys.exit(1)

    _ensure_correlation_context(args)
    projection_id = _new_stable_id()
    snapshot_event_id = _new_stable_id()
    _append_lifecycle_record(
        workspace_root,
        "observe_projection_snapshot_started",
        {
            "event_id": snapshot_event_id,
            "parent_event_id": getattr(args, "parent_event_id", ""),
            "request_id": args.request_id,
            "trace_id": args.trace_id,
            "causality_chain_id": args.causality_chain_id,
            "projection_id": projection_id,
            "query": args.query,
            "query_source": args.query_source,
            "model_name": args.model_name,
            "profile_class": args.profile_class,
            "local_vs_frontier": args.local_vs_frontier,
            "session_id": args.session_id,
            "workspace_root": str(workspace_root),
        },
    )
    try:
        snapshot = _capture_projection_observation(args)
        snapshot["request_id"] = args.request_id
        snapshot["trace_id"] = args.trace_id
        snapshot["causality_chain_id"] = args.causality_chain_id
        snapshot["projection_id"] = projection_id
        snapshot["parent_event_id"] = snapshot_event_id
        snapshot["session_lineage"] = _build_session_lineage(args)
        observation_dir = workspace_root / ".pecs" / "logs" / "observation"
        projection_log = observation_dir / "projection_snapshot.jsonl"
        emitted_log = observation_dir / "emitted_envelope.jsonl"

        _append_bounded_jsonl(projection_log, snapshot, args.max_records)
        _append_bounded_jsonl(
            emitted_log,
            {
                "timestamp": snapshot["timestamp"],
                "session_lineage": snapshot["session_lineage"],
                "query": snapshot["query"],
                "adapter": snapshot["adapter"],
                "model": snapshot["model"],
                "profile": snapshot["profile"],
                "request_id": snapshot["request_id"],
                "trace_id": snapshot["trace_id"],
                "projection_id": snapshot["projection_id"],
                "causality_chain_id": snapshot["causality_chain_id"],
                "parent_event_id": snapshot["parent_event_id"],
                "emitted_advisory_cognition": snapshot["emitted_advisory_cognition"],
                "discarded_cognition_summary": snapshot["discarded_cognition_summary"],
                "shaping_losses": snapshot["shaping_losses"],
                "suppression_reason_breakdown": snapshot.get("suppression_reason_breakdown", {}),
                "advisory_signal_priority": snapshot.get("advisory_signal_priority", []),
                "authority_confidence_band": snapshot.get("authority_confidence_band", "low"),
                "cognition_density_score": snapshot.get("cognition_density_score", 0.0),
                "topology_noise_ratio": snapshot.get("topology_noise_ratio", 0.0),
                "reconstructed_lineage_density": snapshot.get("reconstructed_lineage_density", 0.0),
                "continuity_reconstruction_confidence": snapshot.get("continuity_reconstruction_confidence", 0.0),
                "historical_engineering_gravity": snapshot.get("historical_engineering_gravity", 0.0),
                "continuity_condensation_score": snapshot.get("continuity_condensation_score", 0.0),
                "protected_authority_reinforcement": snapshot.get("protected_authority_reinforcement", {}),
                "lineage_fragmentation_score": snapshot.get("lineage_fragmentation_score", 0.0),
                "canonical_authority_clusters": snapshot.get("canonical_authority_clusters", []),
                "payload_size_exact": snapshot["payload_size_exact"],
            },
            args.max_records,
        )
        logger.info(f"Projection observation snapshot written: {projection_log}")
        logger.info(f"Emitted envelope snapshot written: {emitted_log}")
        _append_lifecycle_record(
            workspace_root,
            "observe_projection_snapshot_completed",
            {
                "event_id": _new_stable_id(),
                "parent_event_id": snapshot_event_id,
                "request_id": args.request_id,
                "trace_id": args.trace_id,
                "causality_chain_id": args.causality_chain_id,
                "projection_id": projection_id,
                "query": args.query,
                "query_source": args.query_source,
                "model_name": args.model_name,
                "profile_class": args.profile_class,
                "local_vs_frontier": args.local_vs_frontier,
                "session_id": args.session_id,
                "projection_log": str(projection_log),
                "emitted_log": str(emitted_log),
                "workspace_root": str(workspace_root),
            },
        )
    except Exception as e:
        _append_lifecycle_record(
            workspace_root,
            "observe_projection_snapshot_failed",
            {
                "event_id": _new_stable_id(),
                "parent_event_id": snapshot_event_id,
                "request_id": args.request_id,
                "trace_id": args.trace_id,
                "causality_chain_id": args.causality_chain_id,
                "projection_id": projection_id,
                "query": args.query,
                "query_source": args.query_source,
                "model_name": args.model_name,
                "profile_class": args.profile_class,
                "local_vs_frontier": args.local_vs_frontier,
                "session_id": args.session_id,
                "error": str(e),
                "workspace_root": str(workspace_root),
            },
        )
        logger.error(f"Projection observation snapshot failed: {e}")
        sys.exit(1)


def _cmd_observe_projection_daemon(args: argparse.Namespace) -> None:
    if args.iterations <= 0:
        logger.error("--iterations must be greater than 0")
        sys.exit(1)

    workspace_root = Path(args.workspace_root).resolve()
    request_id = _new_stable_id()
    trace_id = _new_stable_id()
    causality_chain_id = trace_id
    args.request_id = request_id
    args.trace_id = trace_id
    args.causality_chain_id = causality_chain_id
    daemon_event_id = _new_stable_id()
    args.parent_event_id = daemon_event_id
    _append_lifecycle_record(
        workspace_root,
        "observe_projection_daemon_started",
        {
            "event_id": daemon_event_id,
            "request_id": request_id,
            "trace_id": trace_id,
            "causality_chain_id": causality_chain_id,
            "query": args.query,
            "query_source": args.query_source,
            "model_name": args.model_name,
            "profile_class": args.profile_class,
            "local_vs_frontier": args.local_vs_frontier,
            "session_id": args.session_id,
            "iterations": args.iterations,
            "interval_seconds": args.interval_seconds,
            "workspace_root": str(workspace_root),
        },
    )

    for iteration in range(args.iterations):
        _cmd_observe_projection_snapshot(args)
        if iteration < args.iterations - 1:
            time.sleep(args.interval_seconds)

    _append_lifecycle_record(
        Path(args.workspace_root).resolve(),
        "observe_projection_daemon_completed",
        {
            "event_id": _new_stable_id(),
            "parent_event_id": daemon_event_id,
            "request_id": args.request_id,
            "trace_id": args.trace_id,
            "causality_chain_id": args.causality_chain_id,
            "query": args.query,
            "query_source": args.query_source,
            "session_id": args.session_id,
            "profile_class": args.profile_class,
            "local_vs_frontier": args.local_vs_frontier,
            "iterations": args.iterations,
            "workspace_root": args.workspace_root,
        },
    )


def _run_workspace_bridge(workspace_root: Path, command: str) -> None:
    bridge_runner = workspace_root / ".pecs" / "bridge" / "run_bridge.py"
    if not bridge_runner.exists():
        raise FileNotFoundError(
            f"Workspace bridge not installed: {bridge_runner}. Run init first."
        )

    subprocess.run(
        [
            sys.executable,
            str(bridge_runner),
            command,
            "--workspace",
            str(workspace_root),
        ],
        check=True,
    )


def _is_process_running(pid: int) -> bool:
    try:
        subprocess.run(["kill", "-0", str(pid)], check=True, capture_output=True)
        return True
    except Exception:
        return False


def _read_pid_file(pid_file: Path) -> Optional[int]:
    try:
        raw = pid_file.read_text(encoding="utf-8")
    except OSError:
        return None

    pid_text = raw.strip()
    if (pid_text.startswith('"') and pid_text.endswith('"')) or (
        pid_text.startswith("'") and pid_text.endswith("'")
    ):
        pid_text = pid_text[1:-1].strip()

    pid_text = pid_text.strip()
    if pid_text.isdigit():
        return int(pid_text)
    return None


def _start_workspace_daemon(workspace_root: Path) -> None:
    shell_daemon = workspace_root / ".pecs" / "run_pecs_daemon.sh"
    cmd_daemon = workspace_root / ".pecs" / "run_pecs_daemon.cmd"
    ps1_daemon = workspace_root / ".pecs" / "run_pecs_daemon.ps1"

    if not shell_daemon.exists() and not cmd_daemon.exists() and not ps1_daemon.exists():
        raise FileNotFoundError(
            "Workspace daemon launcher missing: .pecs/run_pecs_daemon.(sh|cmd|ps1). Run install-workspace-assets or bootstrap-workspace first."
        )

    pid_file = workspace_root / ".pecs" / "daemon.pid"
    if pid_file.exists():
        try:
            pid = _read_pid_file(pid_file)
            if pid is not None and _is_process_running(pid):
                logger.info(f"Daemon already running (PID {pid})")
                return
            logger.warning("Stale daemon PID file found. Removing and restarting daemon.")
            pid_file.unlink(missing_ok=True)
        except Exception:
            pid_file.unlink(missing_ok=True)

    launch_cmd = None
    if os.name == "nt":
        if cmd_daemon.exists():
            launch_cmd = [str(cmd_daemon), str(workspace_root)]
        elif ps1_daemon.exists():
            powershell_exe = shutil.which("powershell") or shutil.which("pwsh")
            if not powershell_exe:
                raise RuntimeError("Cannot start daemon: PowerShell is not available on PATH.")
            launch_cmd = [
                powershell_exe,
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(ps1_daemon),
                str(workspace_root),
            ]
    else:
        bash_path = shutil.which("bash")
        if not bash_path:
            raise RuntimeError("Cannot start daemon: bash is not available on PATH.")
        launch_cmd = [bash_path, str(shell_daemon), str(workspace_root)]

    if launch_cmd is None:
        raise RuntimeError("No supported daemon launcher found for this platform.")

    logger.info(f"Starting workspace daemon for {workspace_root}")
    subprocess.Popen(
        launch_cmd,
        cwd=str(workspace_root),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )

    time.sleep(2)
    if pid_file.exists():
        try:
            pid = _read_pid_file(pid_file)
            if pid is not None and _is_process_running(pid):
                logger.info(f"Daemon started successfully (PID {pid})")
                return
        except Exception:
            pass
    logger.warning(
        "Daemon launch requested, but PID file was not written within startup window. "
        "Check .pecs/daemon.pid and workspace logs if startup failed."
    )


def _load_json(path: Path, default=None):
    if default is None:
        default = {}
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _format_timestamp(timestamp: object) -> str:
    if timestamp is None:
        return "n/a"
    try:
        timestamp = float(timestamp)
        return datetime.datetime.fromtimestamp(timestamp).isoformat()
    except Exception:
        return str(timestamp)


def _load_health_state(workspace_root: Path) -> Dict[str, object]:
    return _load_json(workspace_root / ".pecs" / "daemon_health.json", {})


def _load_daemon_state(workspace_root: Path) -> Dict[str, object]:
    return _load_json(workspace_root / ".pecs" / "daemon_state.json", {})


def _load_daemon_cycle_validation(workspace_root: Path) -> Dict[str, object]:
    return _load_json(workspace_root / ".pecs" / "daemon_cycle_validation.json", {})


def _load_validation_report(workspace_root: Path, name: str) -> Dict[str, object]:
    return _load_json(workspace_root / ".pecs" / name, {})


def _format_health_summary(health_state: Dict[str, object]) -> str:
    lines = []
    lines.append(f"  Daemon version: {health_state.get('daemon_version', 'unknown')}")
    lines.append(f"  Health status: {health_state.get('status', 'unknown')}")
    lines.append(f"  Uptime (s): {health_state.get('uptime_seconds', 0.0)}")
    lines.append(f"  Retrieval ready: {health_state.get('retrieval_ready', False)}")
    lines.append(f"  Topology ready: {health_state.get('topology_ready', False)}")
    lines.append(f"  Continuity ready: {health_state.get('continuity_ready', False)}")
    lines.append(
        f"  Last rebuild: {_format_timestamp(health_state.get('last_rebuild_timestamp'))}"
    )
    lines.append(
        f"  Last health update: {_format_timestamp(health_state.get('last_health_update'))}"
    )
    return "\n".join(lines)


def _setup_logging(verbose: bool) -> None:
    """Setup logging for CLI."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(message)s",
    )


def _run_canonical_verification_or_exit(workspace_root: Path, repo_root: Path) -> None:
    from validation.canonical_workspace_validator import run_canonical_workspace_validation

    report = run_canonical_workspace_validation(workspace_root, repo_root)
    if not bool(report.get("valid", False)):
        logger.error("Canonical workspace verification failed")
        print(json.dumps(report, indent=2, sort_keys=True))
        sys.exit(1)


def _cmd_init(args: argparse.Namespace) -> None:
    """Initialize PECS workspace (legacy command)."""
    workspace_root = Path(args.workspace_root).resolve()
    repo_root = (
        Path(args.repo_root).resolve()
        if args.repo_root
        else Path(__file__).resolve().parent
    )

    if not workspace_root.exists():
        logger.error(f"Workspace does not exist: {workspace_root}")
        sys.exit(1)

    try:
        install_workspace(workspace_root, repo_root)
        _run_workspace_bridge(workspace_root, "refresh")
        logger.info(f"PECS initialized for workspace: {workspace_root}")
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        sys.exit(1)


def _cmd_install_workspace_assets(args: argparse.Namespace) -> None:
    """Install PECS workspace assets."""
    workspace_root = Path(args.workspace_root).resolve()
    repo_root = (
        Path(args.repo_root).resolve()
        if args.repo_root
        else Path(__file__).resolve().parent
    )

    if not workspace_root.exists():
        logger.error(f"Workspace does not exist: {workspace_root}")
        sys.exit(1)

    try:
        manager = WorkspaceAssetsManager(repo_root, workspace_root)
        preserve_existing = bool(getattr(args, 'preserve', False) or _workspace_has_existing_assets(workspace_root))
        _append_lifecycle_record(
            workspace_root,
            "install_workspace_assets_started",
            {
                "preserve_existing": preserve_existing,
                "workspace_root": str(workspace_root),
            },
        )
        result = manager.install_assets(upgrade=preserve_existing, verify=False)

        logger.info(f"Status: {result['status']}")
        logger.info(f"Installed: {len(result.get('installed_assets', []))} asset(s)")

        if result.get("errors"):
            for error in result["errors"]:
                logger.error(f"  - {error}")
            sys.exit(1)

        logger.info("Applying PECS workspace integration configuration")
        install_workspace(workspace_root, repo_root, preserve_existing=True)

        verification = manager.verify_installation()
        if not verification["valid"]:
            logger.error("Workspace verification failed after installation")
            for error in verification.get("errors", []):
                logger.error(f"  - {error}")
            sys.exit(1)
        _run_canonical_verification_or_exit(workspace_root, repo_root)

        _append_lifecycle_record(
            workspace_root,
            "install_workspace_assets_completed",
            {
                "status": result.get("status"),
                "installed_assets": len(result.get("installed_assets", [])),
                "workspace_root": str(workspace_root),
            },
        )
        logger.info("Workspace assets installed successfully")
    except Exception as e:
        _append_lifecycle_record(
            workspace_root,
            "install_workspace_assets_failed",
            {
                "error": str(e),
                "workspace_root": str(workspace_root),
            },
        )
        logger.error(f"Asset installation failed: {e}")
        sys.exit(1)


def _cmd_bootstrap_workspace(args: argparse.Namespace) -> None:
    """Bootstrap a workspace end-to-end: install assets, start daemon, refresh continuity, and validate."""
    workspace_root = Path(args.workspace_root).resolve()
    repo_root = (
        Path(args.repo_root).resolve()
        if args.repo_root
        else Path(__file__).resolve().parent
    )

    if not workspace_root.exists():
        logger.error(f"Workspace does not exist: {workspace_root}")
        sys.exit(1)

    print_install_root_guidance(repo_root)
    missing = [dep for dep, status in validate_dependencies().items() if status != "ok"]
    if missing:
        logger.error(
            f"Missing required dependencies: {missing}. "
            "Activate the PECS repo venv and install requirements before bootstrapping."
        )
        sys.exit(1)

    try:
        manager = WorkspaceAssetsManager(repo_root, workspace_root)
        preserve_existing = bool(getattr(args, 'preserve', False) or _workspace_has_existing_assets(workspace_root))
        _append_lifecycle_record(
            workspace_root,
            "bootstrap_workspace_started",
            {
                "preserve_existing": preserve_existing,
                "workspace_root": str(workspace_root),
            },
        )
        result = manager.install_assets(upgrade=preserve_existing, verify=False)

        logger.info(f"Status: {result['status']}")
        logger.info(f"Installed: {len(result.get('installed_assets', []))} asset(s)")

        if result.get("errors"):
            for error in result["errors"]:
                logger.error(f"  - {error}")
            sys.exit(1)

        logger.info("Applying PECS workspace integration configuration")
        install_workspace(workspace_root, repo_root, preserve_existing=True)
        _start_workspace_daemon(workspace_root)
        _run_workspace_bridge(workspace_root, "refresh")

        verification = manager.verify_installation()
        if not verification["valid"]:
            logger.error("Workspace verification failed after bootstrap")
            for error in verification.get("errors", []):
                logger.error(f"  - {error}")
            sys.exit(1)
        _run_canonical_verification_or_exit(workspace_root, repo_root)

        _append_lifecycle_record(
            workspace_root,
            "bootstrap_workspace_completed",
            {
                "status": result.get("status"),
                "installed_assets": len(result.get("installed_assets", [])),
                "workspace_root": str(workspace_root),
            },
        )
        logger.info("Workspace bootstrap completed successfully")
    except Exception as e:
        _append_lifecycle_record(
            workspace_root,
            "bootstrap_workspace_failed",
            {
                "error": str(e),
                "workspace_root": str(workspace_root),
            },
        )
        logger.error(f"Workspace bootstrap failed: {e}")
        sys.exit(1)


def _cmd_interactive_setup(args: argparse.Namespace) -> None:
    """Interactively configure and bootstrap a workspace."""
    repo_root = (
        Path(args.repo_root).resolve()
        if args.repo_root
        else Path(__file__).resolve().parent
    )

    workspace_root = None
    if args.workspace_root:
        workspace_root = Path(args.workspace_root).resolve()
    else:
        user_input = input("Enter the target workspace root path: ").strip()
        if user_input:
            workspace_root = Path(user_input).resolve()

    if not workspace_root:
        logger.error("Workspace root is required for interactive setup.")
        sys.exit(1)

    if not workspace_root.exists():
        logger.error(f"Workspace does not exist: {workspace_root}")
        sys.exit(1)

    logger.info(f"Interactive workspace bootstrap: {workspace_root}")
    inner_args = argparse.Namespace(
        workspace_root=str(workspace_root),
        repo_root=str(repo_root),
        preserve=getattr(args, 'preserve', False),
    )
    _cmd_bootstrap_workspace(inner_args)


def _cmd_rebind_workspace(args: argparse.Namespace) -> None:
    """Rebind workspace integration to the current PECS install root."""
    workspace_root = Path(args.workspace_root).resolve()
    repo_root = (
        Path(args.repo_root).resolve()
        if args.repo_root
        else Path(__file__).resolve().parent
    )

    if not workspace_root.exists():
        logger.error(f"Workspace does not exist: {workspace_root}")
        sys.exit(1)

    try:
        manager = WorkspaceAssetsManager(repo_root, workspace_root)
        preserve_existing = bool(getattr(args, 'preserve', False) or _workspace_has_existing_assets(workspace_root))
        _append_lifecycle_record(
            workspace_root,
            "rebind_workspace_started",
            {
                "preserve_existing": preserve_existing,
                "command": getattr(args, "command", "rebind-workspace"),
                "workspace_root": str(workspace_root),
            },
        )
        result = manager.install_assets(upgrade=preserve_existing, verify=False)

        if result.get("errors"):
            logger.error("Workspace rebind encountered errors:")
            for error in result["errors"]:
                logger.error(f"  - {error}")
            sys.exit(1)

        install_workspace(workspace_root, repo_root, preserve_existing=True)
        verification = manager.verify_installation()
        if not verification["valid"]:
            logger.error("Workspace verification failed after rebind")
            for error in verification.get("errors", []):
                logger.error(f"  - {error}")
            sys.exit(1)
        _run_canonical_verification_or_exit(workspace_root, repo_root)

        _run_workspace_bridge(workspace_root, "refresh")
        _append_lifecycle_record(
            workspace_root,
            "rebind_workspace_completed",
            {
                "status": result.get("status"),
                "workspace_root": str(workspace_root),
            },
        )
        logger.info("Workspace rebind completed successfully")
    except Exception as e:
        _append_lifecycle_record(
            workspace_root,
            "rebind_workspace_failed",
            {
                "error": str(e),
                "workspace_root": str(workspace_root),
            },
        )
        logger.error(f"Workspace rebind failed: {e}")
        sys.exit(1)


def _cmd_upgrade_workspace(args: argparse.Namespace) -> None:
    workspace_root = Path(args.workspace_root).resolve()
    repo_root = (
        Path(args.repo_root).resolve()
        if args.repo_root
        else Path(__file__).resolve().parent
    )

    if not workspace_root.exists():
        logger.error(f"Workspace does not exist: {workspace_root}")
        sys.exit(1)

    print_install_root_guidance(repo_root)
    missing = [dep for dep, status in validate_dependencies().items() if status != "ok"]
    if missing:
        logger.error(
            f"Missing required dependencies: {missing}. Activate the PECS repo venv and install requirements before upgrading."
        )
        sys.exit(1)

    _append_lifecycle_record(
        workspace_root,
        "upgrade_workspace_started",
        {
            "workspace_root": str(workspace_root),
            "repo_root": str(repo_root),
        },
    )

    try:
        pipeline = UpgradeWorkspacePipeline(workspace_root, repo_root)
        report = pipeline.run()

        if report.warnings:
            for warning in report.warnings:
                logger.warning(warning)

        _append_lifecycle_record(
            workspace_root,
            "upgrade_workspace_completed",
            {
                "success": report.success,
                "elapsed_seconds": report.elapsed_seconds,
                "rollback_location": report.rollback_location,
            },
        )

        logger.info("Workspace upgrade completed successfully")
        print(json.dumps(asdict(report), indent=2, sort_keys=True))
        if not report.success:
            sys.exit(1)
    except Exception as e:
        _append_lifecycle_record(
            workspace_root,
            "upgrade_workspace_failed",
            {
                "error": str(e),
                "workspace_root": str(workspace_root),
            },
        )
        logger.error(f"Workspace upgrade failed: {e}")
        sys.exit(1)


def _cmd_migrate_workspace(args: argparse.Namespace) -> None:
    """Migrate a workspace by regenerating bindings and refresh bridge paths."""
    _cmd_rebind_workspace(args)


def _cmd_rebind_all_workspaces(args: argparse.Namespace) -> None:
    """Rebind all registered PECS workspaces to the current install root."""
    repo_root = (
        Path(args.repo_root).resolve()
        if args.repo_root
        else Path(__file__).resolve().parent
    )

    workspace_paths = read_registered_workspaces(repo_root)
    if not workspace_paths:
        logger.error("No registered workspaces found to rebind.")
        sys.exit(1)

    failures = []
    for workspace_root in workspace_paths:
        try:
            logger.info(f"Rebinding workspace: {workspace_root}")
            inner_args = argparse.Namespace(
                workspace_root=str(workspace_root),
                repo_root=str(repo_root),
                preserve=getattr(args, 'preserve', False),
            )
            _cmd_rebind_workspace(inner_args)
            logger.info(f"Successfully rebound: {workspace_root}")
        except SystemExit as e:
            if e.code != 0:
                failures.append((workspace_root, e.code))
        except Exception as e:
            failures.append((workspace_root, str(e)))

    if failures:
        logger.error("Some workspaces failed to rebind:")
        for workspace_root, reason in failures:
            logger.error(f"  - {workspace_root}: {reason}")
        sys.exit(1)
    logger.info("Rebind-all-workspaces completed successfully.")


def _cmd_verify_workspace(args: argparse.Namespace) -> None:
    """Verify PECS workspace installation."""
    workspace_root = Path(args.workspace_root).resolve()
    repo_root = (
        Path(args.repo_root).resolve()
        if args.repo_root
        else Path(__file__).resolve().parent
    )

    if not workspace_root.exists():
        logger.error(f"Workspace does not exist: {workspace_root}")
        sys.exit(1)

    try:
        manager = WorkspaceAssetsManager(repo_root, workspace_root)
        result = manager.verify_installation()

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            logger.info(f"Verification: {'PASSED' if result['valid'] else 'FAILED'}")

            for asset, exists in result.get("checks", {}).items():
                status = "✓" if exists else "✗"
                logger.info(f"  {status} {asset}")

            if result.get("errors"):
                logger.error("Errors found:")
                for error in result["errors"]:
                    logger.error(f"  - {error}")

        sys.exit(0 if result["valid"] else 1)

    except Exception as e:
        logger.error(f"Verification failed: {e}")
        sys.exit(1)


def _cmd_repair_workspace(args: argparse.Namespace) -> None:
    """Repair broken PECS workspace installation."""
    workspace_root = Path(args.workspace_root).resolve()
    repo_root = (
        Path(args.repo_root).resolve()
        if args.repo_root
        else Path(__file__).resolve().parent
    )

    if not workspace_root.exists():
        logger.error(f"Workspace does not exist: {workspace_root}")
        sys.exit(1)

    try:
        manager = WorkspaceAssetsManager(repo_root, workspace_root)
        _append_lifecycle_record(
            workspace_root,
            "repair_workspace_started",
            {"workspace_root": str(workspace_root)},
        )
        result = manager.repair_installation()

        logger.info(f"Repair status: {result['status']}")
        logger.info(f"Repaired: {len(result.get('repairs', []))} item(s)")

        if result.get("repairs"):
            for repair in result["repairs"]:
                logger.info(f"  ✓ {repair}")

        _append_lifecycle_record(
            workspace_root,
            "repair_workspace_completed",
            {
                "status": result.get("status"),
                "repaired_items": len(result.get("repairs", [])),
                "workspace_root": str(workspace_root),
            },
        )
        if result.get("errors"):
            logger.warning("Repair encountered errors:")
            for error in result["errors"]:
                logger.warning(f"  - {error}")

        sys.exit(0 if result["status"] != "failed" else 1)

    except Exception as e:
        logger.error(f"Repair failed: {e}")
        sys.exit(1)


def _cmd_status(args: argparse.Namespace) -> None:
    """Show PECS daemon and workspace status."""
    workspace_root = (
        Path(args.workspace_root).resolve() if args.workspace_root else Path.cwd()
    )

    try:
        if not workspace_root.exists():
            logger.error(f"Workspace does not exist: {workspace_root}")
            sys.exit(1)

        daemon_pid_file = workspace_root / ".pecs" / "daemon.pid"
        daemon_state = _load_daemon_state(workspace_root)
        health_state = _load_health_state(workspace_root)
        cycle_validation = _load_daemon_cycle_validation(workspace_root)
        graph_validation = _load_validation_report(
            workspace_root, "workspace_graph_validation.json"
        )
        registry_validation = _load_validation_report(
            workspace_root, "workspace_registry_validation.json"
        )

        logger.info(f"Workspace: {workspace_root}")
        logger.info(
            "Runtime locality payload count: %s",
            daemon_state.get("runtime_locality_payload_count", 0),
        )
        logger.info(
            "Runtime reachable count: %s",
            daemon_state.get("runtime_reachable_count", 0),
        )
        logger.info(
            "Topology edge count: %s",
            daemon_state.get("topology_edge_count", 0),
        )
        logger.info(
            "Daemon health: %s",
            health_state.get("status", "unknown"),
        )
        logger.info(
            "Workspace graph health: %s",
            "healthy" if graph_validation.get("valid", False) else "unhealthy",
        )
        logger.info(
            "Workspace registry health: %s",
            "healthy" if registry_validation.get("valid", False) else "unhealthy",
        )
        if cycle_validation:
            logger.info("Cycle validation: present")
        else:
            logger.info("Cycle validation: missing")

        if not daemon_pid_file.exists():
            logger.info("Daemon: NOT RUNNING (no PID file)")
            if health_state:
                logger.info("Daemon health artifact exists but daemon is not running.")
            return

        try:
            pid = _read_pid_file(daemon_pid_file)
            if pid is None:
                raise ValueError("invalid PID file")
            subprocess.run(["kill", "-0", str(pid)], check=True, capture_output=True)
            logger.info(f"Daemon: RUNNING (PID {pid})")
            if health_state:
                logger.info("Daemon health: %s", health_state.get("status", "unknown"))
                logger.info(_format_health_summary(health_state))
            else:
                logger.info("Daemon health: NONE (health artifact missing)")
        except (ValueError, subprocess.CalledProcessError):
            logger.info("Daemon: STOPPED (stale PID file)")
            if health_state:
                logger.info("Daemon health artifact exists but PID is stale.")

    except Exception as e:
        logger.error(f"Status check failed: {e}")
        sys.exit(1)


def _cmd_health(args: argparse.Namespace) -> None:
    """Show authoritative PECS daemon health status."""
    workspace_root = (
        Path(args.workspace_root).resolve() if args.workspace_root else Path.cwd()
    )

    if not workspace_root.exists():
        logger.error(f"Workspace does not exist: {workspace_root}")
        sys.exit(1)

    daemon_pid_file = workspace_root / ".pecs" / "daemon.pid"
    health_state = _load_health_state(workspace_root)

    if not daemon_pid_file.exists():
        logger.error("Daemon health: NOT RUNNING (no PID file)")
        sys.exit(1)

    try:
        pid = _read_pid_file(daemon_pid_file)
        if pid is None:
            raise ValueError("invalid PID file")
    except Exception:
        logger.error("Daemon health: invalid PID file")
        sys.exit(1)

    if not _is_process_running(pid):
        logger.error(f"Daemon health: process {pid} is not running")
        sys.exit(1)

    if not health_state:
        logger.error("Daemon health: health artifact missing (.pecs/daemon_health.json)")
        sys.exit(1)

    if health_state.get("status") != "healthy":
        logger.error("Daemon health: UNHEALTHY")
        logger.error(_format_health_summary(health_state))
        sys.exit(1)

    logger.info(f"Workspace: {workspace_root}")
    logger.info(f"Daemon PID: {pid}")
    logger.info(_format_health_summary(health_state))
    sys.exit(0)


def _cmd_refresh_workspace(args: argparse.Namespace) -> None:
    """Refresh continuity state using the workspace bridge."""
    workspace_root = Path(args.workspace_root).resolve()

    if not workspace_root.exists():
        logger.error(f"Workspace does not exist: {workspace_root}")
        sys.exit(1)

    try:
        _append_lifecycle_record(
            workspace_root,
            "refresh_workspace_started",
            {"workspace_root": str(workspace_root)},
        )
        _run_workspace_bridge(workspace_root, "refresh")
        _append_lifecycle_record(
            workspace_root,
            "refresh_workspace_completed",
            {"workspace_root": str(workspace_root)},
        )
        logger.info(f"Continuity refresh completed: {workspace_root}")
    except Exception as e:
        _append_lifecycle_record(
            workspace_root,
            "refresh_workspace_failed",
            {"workspace_root": str(workspace_root), "error": str(e)},
        )
        logger.error(f"Continuity refresh failed: {e}")
        sys.exit(1)


def _cmd_validate_workspace(args: argparse.Namespace) -> None:
    """Validate workspace state using the canonical Alpha 1 validator."""
    workspace_root = Path(args.workspace_root).resolve()
    repo_root = (
        Path(args.repo_root).resolve()
        if args.repo_root
        else Path(__file__).resolve().parent
    )

    if not workspace_root.exists():
        logger.error(f"Workspace does not exist: {workspace_root}")
        sys.exit(1)

    try:
        from validation.canonical_workspace_validator import (
            run_canonical_workspace_validation,
        )

        _append_lifecycle_record(
            workspace_root,
            "validate_workspace_started",
            {"workspace_root": str(workspace_root)},
        )
        report = run_canonical_workspace_validation(workspace_root, repo_root)
        print(json.dumps(report, indent=2, sort_keys=True))
        _append_lifecycle_record(
            workspace_root,
            "validate_workspace_completed",
            {
                "workspace_root": str(workspace_root),
                "valid": bool(report.get("valid", False)),
            },
        )
        if not bool(report.get("valid", False)):
            logger.error(f"Continuity validation failed: {workspace_root}")
            sys.exit(1)
        logger.info(f"Continuity validation completed: {workspace_root}")
    except Exception as e:
        _append_lifecycle_record(
            workspace_root,
            "validate_workspace_failed",
            {"workspace_root": str(workspace_root), "error": str(e)},
        )
        logger.error(f"Continuity validation failed: {e}")
        sys.exit(1)


def _pecs_id_to_path(workspace_root: Path, pecs_id: str) -> Path:
    """Convert a PECS_ID module anchor back to a workspace-relative path."""
    body = pecs_id
    if body.startswith("PECS_ID:"):
        body = body[len("PECS_ID:") :]
    return workspace_root / (body.replace(".", "/") + ".py")


def _load_json_or_default(path: Path, default=None):
    if default is None:
        default = {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _load_query_pipeline_artifacts(
    workspace_root: Path,
    use_dumps: bool,
) -> tuple:
    """
    Load or build the Workspace Graph and Workspace Registry needed by the
    query pipeline.

    When ``use_dumps`` is True and the daemon has written
    ``workspace_graph.json`` / ``workspace_registry.json``, those are loaded
    directly. Otherwise the graph is rebuilt deterministically from the
    legacy ``locality_index.json`` and ``topology_compact.json`` artifacts,
    and the registry is loaded from its dump or rebuilt from the graph.
    """
    pecs_dir = workspace_root / ".pecs"
    locality_path = pecs_dir / "locality_index.json"
    topology_path = pecs_dir / "topology_compact.json"
    graph_path = pecs_dir / "workspace_graph.json"
    registry_path = pecs_dir / "workspace_registry.json"

    if not locality_path.exists() or not topology_path.exists():
        raise FileNotFoundError(
            f"Required PECS artifacts missing: {locality_path} or {topology_path}. "
            "Run 'pecs refresh' first."
        )

    locality_payload = _load_json_or_default(locality_path)
    topology_payload = _load_json_or_default(topology_path)

    from execution_graph.builders.workspace_graph_builder import (
        WorkspaceGraphBuilder,
    )
    from execution_graph.graph.workspace_graph import Graph
    from workspace_registry.builders.workspace_registry_builder import (
        WorkspaceRegistryBuilder,
    )
    from workspace_registry.models import WorkspaceRegistry

    graph: Graph
    if use_dumps and graph_path.exists():
        graph = Graph.from_dict(_load_json_or_default(graph_path))
    else:
        entrypoint_paths = []
        for ep in topology_payload.get("entrypoints", []):
            try:
                candidate = _pecs_id_to_path(workspace_root, ep)
                if candidate.exists():
                    entrypoint_paths.append(candidate)
            except Exception:
                continue

        graph_builder = WorkspaceGraphBuilder(workspace_root)
        graph = graph_builder.build(
            reachable_files=set(),
            runtime_locality_payload=locality_payload,
            runtime_topology_edges=topology_payload.get("edges", []),
            entrypoints=entrypoint_paths,
        )

    registry: WorkspaceRegistry
    if use_dumps and registry_path.exists():
        registry = WorkspaceRegistry.from_dict(
            _load_json_or_default(registry_path)
        )
    else:
        registry_builder = WorkspaceRegistryBuilder(workspace_root)
        registry = registry_builder.build(graph)

    return graph, registry


def _cmd_query_pipeline(args: argparse.Namespace) -> None:
    """
    Run the PECS Query Pipeline.

    Correlates architectural query terms against deterministic workspace
    evidence, selects the strongest Evidence Clusters, and projects a bounded
    Navigation Graph with live line ranges.
    """
    workspace_root = (
        Path(args.workspace_root).resolve()
        if args.workspace_root
        else Path.cwd()
    )

    if not workspace_root.exists():
        logger.error(f"Workspace does not exist: {workspace_root}")
        sys.exit(1)

    query_terms = [
        token.strip()
        for raw_term in args.terms
        for token in raw_term.split()
        if token.strip()
    ]
    if not query_terms:
        logger.error("At least one query term is required (--terms).")
        sys.exit(1)

    try:
        _append_lifecycle_record(
            workspace_root,
            "query_pipeline_started",
            {
                "workspace_root": str(workspace_root),
                "query_terms": query_terms,
            },
        )

        graph, registry = _load_query_pipeline_artifacts(
            workspace_root,
            use_dumps=getattr(args, "use_dumps", False),
        )

        from evidence_correlation.engines.evidence_correlator import (
            EvidenceCorrelator,
        )
        from navigation_builder.builders.navigation_graph_builder import (
            NavigationGraphBuilder,
        )

        correlator = EvidenceCorrelator(
            workspace_root=workspace_root,
            graph=graph,
            registry=registry,
        )
        correlator.build_index()
        correlation_result = correlator.correlate(
            query_terms=query_terms,
            max_clusters=args.max_clusters,
        )

        nav_builder = NavigationGraphBuilder(
            workspace_root=workspace_root,
            graph=graph,
            max_nodes=args.max_nodes,
            max_depth=args.max_depth,
        )
        navigation_graph = nav_builder.build(
            clusters=correlation_result.clusters,
            query_terms=query_terms,
        )

        response = {
            "schema": "pecs.query_pipeline.v1",
            "workspace_root": str(workspace_root),
            "query_terms": sorted(query_terms),
            "deterministic": True,
            "correlation": correlation_result.to_dict(),
            "navigation_graph": navigation_graph.to_dict(),
        }

        payload = json.dumps(response, indent=2, sort_keys=True)
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(payload, encoding="utf-8")
            logger.debug(f"Query pipeline result written to {output_path}")
        else:
            print(payload)

        _append_lifecycle_record(
            workspace_root,
            "query_pipeline_completed",
            {
                "workspace_root": str(workspace_root),
                "query_terms": query_terms,
                "cluster_count": len(correlation_result.clusters),
                "navigation_node_count": len(navigation_graph.nodes),
                "navigation_edge_count": len(navigation_graph.edges),
            },
        )
    except Exception as e:
        _append_lifecycle_record(
            workspace_root,
            "query_pipeline_failed",
            {
                "workspace_root": str(workspace_root),
                "query_terms": query_terms,
                "error": str(e),
            },
        )
        logger.error(f"Query pipeline failed: {e}")
        sys.exit(1)


def _stop_workspace_daemon(workspace_root: Path) -> None:
    pid_file = workspace_root / ".pecs" / "daemon.pid"
    if not pid_file.exists():
        logger.info("No daemon PID file found; nothing to stop.")
        return

    pid = _read_pid_file(pid_file)
    if pid is None:
        logger.warning("Invalid daemon PID file; removing stale PID file.")
        pid_file.unlink(missing_ok=True)
        return

    if _is_process_running(pid):
        logger.info(f"Stopping daemon PID {pid}")
        try:
            subprocess.run(["kill", str(pid)], check=True)
        except Exception as exc:
            logger.warning(f"Failed to stop daemon PID {pid}: {exc}")
    pid_file.unlink(missing_ok=True)
    logger.info("Daemon stopped.")


def _cmd_restart_daemon(args: argparse.Namespace) -> None:
    workspace_root = Path(args.workspace_root).resolve()
    if not workspace_root.exists():
        logger.error(f"Workspace does not exist: {workspace_root}")
        sys.exit(1)

    try:
        _append_lifecycle_record(
            workspace_root,
            "restart_daemon_started",
            {"workspace_root": str(workspace_root)},
        )
        _stop_workspace_daemon(workspace_root)
        _start_workspace_daemon(workspace_root)
        _append_lifecycle_record(
            workspace_root,
            "restart_daemon_completed",
            {"workspace_root": str(workspace_root)},
        )
        logger.info(f"Daemon restarted: {workspace_root}")
    except Exception as e:
        _append_lifecycle_record(
            workspace_root,
            "restart_daemon_failed",
            {"workspace_root": str(workspace_root), "error": str(e)},
        )
        logger.error(f"Daemon restart failed: {e}")
        sys.exit(1)


def _cmd_doctor(args: argparse.Namespace) -> None:
    """Diagnose PECS installation and environment."""
    workspace_root = (
        Path(args.workspace_root).resolve() if args.workspace_root else Path.cwd()
    )
    repo_root = (
        Path(args.repo_root).resolve()
        if args.repo_root
        else Path(__file__).resolve().parent
    )

    try:
        logger.info("PECS Diagnostics Report")
        logger.info("=" * 60)

        # Check environment
        logger.info(f"Python: {sys.executable}")
        logger.info(f"PECS Repository: {repo_root}")
        logger.info(f"Workspace: {workspace_root}")

        if not workspace_root.exists():
            logger.error(f"Workspace does not exist: {workspace_root}")
            sys.exit(1)

        # Check assets
        logger.info("\nAssets:")
        required_files = [
            ".pecs/README.md",
            ".pecs/tools/append_ai_chat_history.py",
            ".pecs/bridge/run_bridge.py",
            ".pecs/bridge/run_bridge.sh",
            ".pecs/run_pecs.sh",
            ".pecs/run_pecs.cmd",
            ".pecs/run_pecs_daemon.sh",
            ".pecs/run_pecs_daemon.cmd",
            ".github/copilot-instructions.md",
            ".continue/rules/pecs-first-routing.yaml",
            ".vscode/tasks.json",
        ]

        for file_path in required_files:
            full_path = workspace_root / file_path
            exists = full_path.exists()
            status = "✓" if exists else "✗"
            logger.info(f"  {status} {file_path}")

        # Check daemon
        logger.info("\nDaemon:")
        daemon_pid_file = workspace_root / ".pecs" / "daemon.pid"
        health_state = _load_health_state(workspace_root)
        if daemon_pid_file.exists():
            try:
                pid = _read_pid_file(daemon_pid_file)
                if pid is None:
                    raise ValueError("invalid PID file")
                subprocess.run(
                    ["kill", "-0", str(pid)], check=True, capture_output=True
                )
                logger.info(f"  ✓ Running (PID {pid})")
                if health_state:
                    logger.info(f"  ✓ Health status: {health_state.get('status', 'unknown')}")
                    logger.info(
                        f"    Retrieval ready: {health_state.get('retrieval_ready', False)}"
                    )
                    logger.info(
                        f"    Topology ready: {health_state.get('topology_ready', False)}"
                    )
                    logger.info(
                        f"    Continuity ready: {health_state.get('continuity_ready', False)}"
                    )
                else:
                    logger.info("  - Health artifact missing: .pecs/daemon_health.json")
            except:
                logger.info(f"  ✗ Stale PID file (PID {pid} not running)")
                if health_state:
                    logger.info("  ✗ Health artifact present but daemon process is stale.")
        else:
            logger.info("  ✗ Not running")

        # Check venv
        logger.info("\nVirtual Environment:")
        venv_path = workspace_root / ".venv"
        if venv_path.exists():
            logger.info(f"  ✓ Found: {venv_path}")
        else:
            logger.info("  - Not found (optional)")

        # Check installation and entrypoints
        logger.info("\nPECS Environment:")
        try:
            dist = importlib.metadata.distribution("pecs_pro")
            logger.info(f"  ✓ Installed distribution: {dist.metadata['Name']}")
            console_scripts = [
                ep for ep in dist.entry_points if ep.group == "console_scripts"
            ]
            for ep in console_scripts:
                logger.info(f"    - console script: {ep.name} -> {ep.value}")
        except importlib.metadata.PackageNotFoundError:
            logger.info("  ✗ Installed distribution 'pecs_pro' not found")

        pecs_path = shutil.which("pecs")
        if pecs_path:
            logger.info(f"  ✓ 'pecs' entrypoint found: {pecs_path}")
        else:
            logger.info("  ✗ 'pecs' entrypoint missing from PATH")

        install_root_config = workspace_root / ".pecs" / "config" / "install_root.json"
        if install_root_config.exists():
            try:
                config = json.loads(install_root_config.read_text(encoding="utf-8"))
                install_root = Path(config.get("install_root", "")).resolve()
                if install_root == repo_root:
                    logger.info(
                        f"  ✓ Workspace is bound to current PECS install root: {install_root}"
                    )
                else:
                    logger.info(
                        f"  ✗ Workspace is bound to stale PECS install root: {install_root}"
                    )
            except Exception:
                logger.info(
                    "  ✗ Workspace install root config is invalid: .pecs/config/install_root.json"
                )
        else:
            logger.info(
                "  ✗ Workspace install root config missing: .pecs/config/install_root.json"
            )

        repo_venv = Path(__file__).resolve().parent / ".venv"
        if (
            repo_venv.exists()
            and Path(sys.executable).resolve() == repo_venv / "bin" / "python"
        ):
            logger.info("  ✓ Running from repository venv Python")
        else:
            logger.info(
                "  - Current Python is not the repository venv Python; "
                "editable install recovery may require activating .venv"
            )

        # Runtime authority checks
        logger.info("\nRuntime Authority Health:")
        daemon_state = _load_daemon_state(workspace_root)
        cycle_validation = _load_daemon_cycle_validation(workspace_root)
        graph_validation = _load_validation_report(
            workspace_root, "workspace_graph_validation.json"
        )
        registry_validation = _load_validation_report(
            workspace_root, "workspace_registry_validation.json"
        )

        logger.info(
            "  Runtime locality payload count: %s",
            daemon_state.get("runtime_locality_payload_count", 0),
        )
        logger.info(
            "  Runtime reachable count: %s",
            daemon_state.get("runtime_reachable_count", 0),
        )
        logger.info(
            "  Topology edge count: %s",
            daemon_state.get("topology_edge_count", 0),
        )
        logger.info(
            "  Daemon health: %s",
            health_state.get("status", "unknown"),
        )
        logger.info(
            "  Workspace graph health: %s",
            "healthy" if graph_validation.get("valid", False) else "unhealthy",
        )
        logger.info(
            "  Workspace registry health: %s",
            "healthy" if registry_validation.get("valid", False) else "unhealthy",
        )
        logger.info(
            "  Cycle validation present: %s",
            bool(cycle_validation),
        )

        logger.info("\nCanonical Validation:")
        try:
            from validation.canonical_workspace_validator import (
                run_canonical_workspace_validation,
            )

            canonical = run_canonical_workspace_validation(workspace_root, repo_root)
            logger.info(
                "  Canonical validation: %s",
                "PASSED" if canonical.get("valid", False) else "FAILED",
            )
        except Exception as exc:
            logger.info("  Canonical validation unavailable: %s", exc)

        logger.info("\n" + "=" * 60)

    except Exception as e:
        logger.error(f"Diagnostic failed: {e}")
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="PECS workspace management CLI")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Legacy init command
    init_parser = subparsers.add_parser(
        "init", help="Initialize PECS workspace (legacy)"
    )
    init_parser.add_argument("workspace_root", help="Target workspace root path")
    init_parser.add_argument(
        "--repo-root",
        default="",
        help="PECS repository root",
    )
    init_parser.set_defaults(func=_cmd_init)

    # New commands
    install_parser = subparsers.add_parser(
        "install-workspace-assets", help="Install PECS workspace assets"
    )
    install_parser.add_argument("workspace_root", help="Target workspace root path")
    install_parser.add_argument(
        "--repo-root",
        default="",
        help="PECS repository root",
    )
    install_parser.add_argument(
        "--upgrade",
        dest="preserve",
        action="store_true",
        help="Preserve existing user configuration",
    )
    install_parser.add_argument(
        "--preserve",
        dest="preserve",
        action="store_true",
        help="Preserve existing user configuration (alias)",
    )
    install_parser.set_defaults(func=_cmd_install_workspace_assets)

    bootstrap_parser = subparsers.add_parser(
        "bootstrap-workspace",
        help="Install, start daemon, refresh continuity, and validate a workspace",
    )
    bootstrap_parser.add_argument("workspace_root", help="Target workspace root path")
    bootstrap_parser.add_argument(
        "--repo-root",
        default="",
        help="PECS repository root",
    )
    bootstrap_parser.add_argument(
        "--upgrade",
        dest="preserve",
        action="store_true",
        help="Preserve existing user configuration",
    )
    bootstrap_parser.add_argument(
        "--preserve",
        dest="preserve",
        action="store_true",
        help="Preserve existing user configuration (alias)",
    )
    bootstrap_parser.set_defaults(func=_cmd_bootstrap_workspace)

    setup_parser = subparsers.add_parser(
        "setup-workspace",
        help="Alias for bootstrap-workspace",
    )
    setup_parser.add_argument("workspace_root", help="Target workspace root path")
    setup_parser.add_argument(
        "--repo-root",
        default="",
        help="PECS repository root",
    )
    setup_parser.add_argument(
        "--upgrade",
        dest="preserve",
        action="store_true",
        help="Preserve existing user configuration",
    )
    setup_parser.add_argument(
        "--preserve",
        dest="preserve",
        action="store_true",
        help="Preserve existing user configuration (alias)",
    )
    setup_parser.set_defaults(func=_cmd_bootstrap_workspace)

    interactive_parser = subparsers.add_parser(
        "interactive-setup",
        help="Interactively configure and bootstrap a workspace",
    )
    interactive_parser.add_argument(
        "workspace_root",
        nargs="?",
        default="",
        help="Target workspace root path",
    )
    interactive_parser.add_argument(
        "--repo-root",
        default="",
        help="PECS repository root",
    )
    interactive_parser.add_argument(
        "--upgrade",
        dest="preserve",
        action="store_true",
        help="Preserve existing user configuration",
    )
    interactive_parser.add_argument(
        "--preserve",
        dest="preserve",
        action="store_true",
        help="Preserve existing user configuration (alias)",
    )
    interactive_parser.set_defaults(func=_cmd_interactive_setup)

    rebind_parser = subparsers.add_parser(
        "rebind-workspace",
        help="Refresh PECS workspace bindings after install root relocation",
    )
    rebind_parser.add_argument("workspace_root", help="Target workspace root path")
    rebind_parser.add_argument(
        "--repo-root",
        default="",
        help="PECS repository root",
    )
    rebind_parser.add_argument(
        "--upgrade",
        dest="preserve",
        action="store_true",
        help="Preserve existing user configuration",
    )
    rebind_parser.add_argument(
        "--preserve",
        dest="preserve",
        action="store_true",
        help="Preserve existing user configuration (alias)",
    )
    rebind_parser.add_argument(
        "--safe-migration",
        dest="preserve",
        action="store_true",
        help="Preserve existing user configuration during migration",
    )
    rebind_parser.set_defaults(func=_cmd_rebind_workspace)

    refresh_bindings_parser = subparsers.add_parser(
        "refresh-workspace-bindings",
        help="Alias for rebind-workspace",
    )
    refresh_bindings_parser.add_argument("workspace_root", help="Target workspace root path")
    refresh_bindings_parser.add_argument(
        "--repo-root",
        default="",
        help="PECS repository root",
    )
    refresh_bindings_parser.add_argument(
        "--upgrade",
        dest="preserve",
        action="store_true",
        help="Preserve existing user configuration",
    )
    refresh_bindings_parser.add_argument(
        "--preserve",
        dest="preserve",
        action="store_true",
        help="Preserve existing user configuration (alias)",
    )
    refresh_bindings_parser.set_defaults(func=_cmd_rebind_workspace)

    migrate_parser = subparsers.add_parser(
        "migrate-workspace",
        help="Migrate workspace bindings to current PECS install root",
    )
    migrate_parser.add_argument("workspace_root", help="Target workspace root path")
    migrate_parser.add_argument(
        "--repo-root",
        default="",
        help="PECS repository root",
    )
    migrate_parser.add_argument(
        "--upgrade",
        dest="preserve",
        action="store_true",
        help="Preserve existing user configuration",
    )
    migrate_parser.add_argument(
        "--preserve",
        dest="preserve",
        action="store_true",
        help="Preserve existing user configuration (alias)",
    )
    migrate_parser.set_defaults(func=_cmd_migrate_workspace)

    rebind_all_parser = subparsers.add_parser(
        "rebind-all-workspaces",
        help="Rebind all registered PECS workspaces to current install root",
    )
    rebind_all_parser.add_argument(
        "--repo-root",
        default="",
        help="PECS repository root",
    )
    rebind_all_parser.add_argument(
        "--upgrade",
        dest="preserve",
        action="store_true",
        help="Preserve existing user configuration",
    )
    rebind_all_parser.add_argument(
        "--preserve",
        dest="preserve",
        action="store_true",
        help="Preserve existing user configuration (alias)",
    )
    rebind_all_parser.set_defaults(func=_cmd_rebind_all_workspaces)

    verify_parser = subparsers.add_parser(
        "verify-workspace", help="Verify workspace installation"
    )
    verify_parser.add_argument("workspace_root", help="Target workspace root path")
    verify_parser.add_argument(
        "--repo-root",
        default="",
        help="PECS repository root",
    )
    verify_parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    verify_parser.set_defaults(func=_cmd_verify_workspace)

    repair_parser = subparsers.add_parser(
        "repair-workspace", help="Repair broken workspace installation"
    )
    repair_parser.add_argument("workspace_root", help="Target workspace root path")
    repair_parser.add_argument(
        "--repo-root",
        default="",
        help="PECS repository root",
    )
    repair_parser.set_defaults(func=_cmd_repair_workspace)

    status_parser = subparsers.add_parser(
        "status", help="Show daemon and workspace status"
    )
    status_parser.add_argument(
        "workspace_root",
        nargs="?",
        default="",
        help="Target workspace root path (default: current directory)",
    )
    status_parser.set_defaults(func=_cmd_status)

    health_parser = subparsers.add_parser(
        "health", help="Show authoritative daemon health status"
    )
    health_parser.add_argument(
        "workspace_root",
        nargs="?",
        default="",
        help="Target workspace root path (default: current directory)",
    )
    health_parser.set_defaults(func=_cmd_health)

    doctor_parser = subparsers.add_parser(
        "doctor", help="Diagnose PECS installation and environment"
    )
    doctor_parser.add_argument(
        "workspace_root",
        nargs="?",
        default="",
        help="Target workspace root path (default: current directory)",
    )
    doctor_parser.add_argument(
        "--repo-root",
        default="",
        help="PECS repository root",
    )
    doctor_parser.set_defaults(func=_cmd_doctor)

    upgrade_parser = subparsers.add_parser(
        "upgrade-workspace",
        help="Run the canonical PECS workspace upgrade pipeline",
    )
    upgrade_parser.add_argument("workspace_root", help="Target workspace root path")
    upgrade_parser.add_argument(
        "--repo-root",
        default="",
        help="PECS repository root",
    )
    upgrade_parser.set_defaults(func=_cmd_upgrade_workspace)

    refresh_managed_parser = subparsers.add_parser(
        "refresh-managed-assets",
        help="Refresh managed PECS workspace assets without wiping continuity",
    )
    refresh_managed_parser.add_argument("workspace_root", help="Target workspace root path")
    refresh_managed_parser.add_argument(
        "--repo-root",
        default="",
        help="PECS repository root",
    )
    refresh_managed_parser.add_argument(
        "--upgrade",
        dest="preserve",
        action="store_true",
        help="Preserve existing user configuration",
    )
    refresh_managed_parser.add_argument(
        "--preserve",
        dest="preserve",
        action="store_true",
        help="Preserve existing user configuration (alias)",
    )
    refresh_managed_parser.set_defaults(func=_cmd_install_workspace_assets)

    stop_daemon_parser = subparsers.add_parser(
        "stop-daemon",
        help="Stop the PECS daemon for the workspace",
    )
    stop_daemon_parser.add_argument("workspace_root", help="Target workspace root path")
    stop_daemon_parser.set_defaults(func=lambda args: _stop_workspace_daemon(Path(args.workspace_root).resolve()))

    restart_daemon_parser = subparsers.add_parser(
        "restart-daemon",
        help="Restart the PECS daemon for the workspace",
    )
    restart_daemon_parser.add_argument("workspace_root", help="Target workspace root path")
    restart_daemon_parser.set_defaults(func=_cmd_restart_daemon)

    rebuild_continuity_parser = subparsers.add_parser(
        "rebuild-continuity",
        help="Regenerate derived continuity artifacts without destructive reset",
    )
    rebuild_continuity_parser.add_argument("workspace_root", help="Target workspace root path")
    rebuild_continuity_parser.add_argument(
        "--repo-root",
        default="",
        help="PECS repository root",
    )
    rebuild_continuity_parser.set_defaults(func=_cmd_refresh_workspace)

    rebuild_topology_parser = subparsers.add_parser(
        "rebuild-topology",
        help="Refresh runtime and topology artifacts without destroying continuity",
    )
    rebuild_topology_parser.add_argument("workspace_root", help="Target workspace root path")
    rebuild_topology_parser.add_argument(
        "--repo-root",
        default="",
        help="PECS repository root",
    )
    rebuild_topology_parser.set_defaults(func=_cmd_refresh_workspace)

    safe_migration_parser = subparsers.add_parser(
        "safe-migration",
        help="Alias for rebind-workspace with preserve-first behavior",
    )
    safe_migration_parser.add_argument("workspace_root", help="Target workspace root path")
    safe_migration_parser.add_argument(
        "--repo-root",
        default="",
        help="PECS repository root",
    )
    safe_migration_parser.add_argument(
        "--upgrade",
        dest="preserve",
        action="store_true",
        help="Preserve existing user configuration",
    )
    safe_migration_parser.add_argument(
        "--preserve",
        dest="preserve",
        action="store_true",
        help="Preserve existing user configuration (alias)",
    )
    safe_migration_parser.set_defaults(func=_cmd_rebind_workspace)

    # Legacy refresh command
    refresh_parser = subparsers.add_parser(
        "refresh",
        help="Refresh continuity state (continuity bootstrap)",
    )
    refresh_parser.add_argument("workspace_root", help="Target workspace root path")
    refresh_parser.add_argument(
        "--repo-root",
        default="",
        help="PECS repository root",
    )
    refresh_parser.set_defaults(func=_cmd_refresh_workspace)

    hydrate_parser = subparsers.add_parser(
        "hydrate-workspace",
        help="Hydrate workspace continuity from chat history and runtime artifacts",
    )
    hydrate_parser.add_argument("workspace_root", help="Target workspace root path")
    hydrate_parser.add_argument(
        "--repo-root",
        default="",
        help="PECS repository root",
    )
    hydrate_parser.set_defaults(func=_cmd_refresh_workspace)

    # Legacy validate command
    validate_parser = subparsers.add_parser(
        "validate", help="Validate continuity state"
    )
    validate_parser.add_argument("workspace_root", help="Target workspace root path")
    validate_parser.add_argument(
        "--repo-root",
        default="",
        help="PECS repository root",
    )
    validate_parser.set_defaults(func=_cmd_validate_workspace)

    query_pipeline_parser = subparsers.add_parser(
        "query-pipeline",
        help="Run query terms through Evidence Correlation -> Navigation Graph",
    )
    query_pipeline_parser.add_argument(
        "workspace_root",
        nargs="?",
        default=".",
        help="Target workspace root path (default: current directory)",
    )
    query_pipeline_parser.add_argument(
        "--terms",
        dest="terms",
        action="append",
        default=[],
        help="Query term (can be repeated)",
    )
    query_pipeline_parser.add_argument(
        "--max-clusters",
        type=int,
        default=3,
        help="Maximum evidence clusters to select (default: 3)",
    )
    query_pipeline_parser.add_argument(
        "--max-nodes",
        type=int,
        default=40,
        help="Maximum navigation graph nodes (default: 40)",
    )
    query_pipeline_parser.add_argument(
        "--max-depth",
        type=int,
        default=2,
        help="Maximum graph expansion depth (default: 2)",
    )
    query_pipeline_parser.add_argument(
        "--output",
        default="",
        help="Write JSON result to this file instead of stdout",
    )
    query_pipeline_parser.add_argument(
        "--use-dumps",
        action="store_true",
        default=False,
        help="Prefer daemon-written workspace_graph.json / workspace_registry.json dumps when available",
    )
    query_pipeline_parser.set_defaults(func=_cmd_query_pipeline)

    observe_snapshot_parser = subparsers.add_parser(
        "observe-projection-snapshot",
        help="Capture one optional emitted-envelope projection snapshot",
    )
    observe_snapshot_parser.add_argument("workspace_root", help="Target workspace root path")
    observe_snapshot_parser.add_argument("--query", default="runtime locality reconciliation")
    observe_snapshot_parser.add_argument("--query-source", default="copilot")
    observe_snapshot_parser.add_argument("--model-name", required=True)
    observe_snapshot_parser.add_argument("--model-source", default="")
    observe_snapshot_parser.add_argument("--provider", default="")
    observe_snapshot_parser.add_argument("--model-size", default="medium")
    observe_snapshot_parser.add_argument("--profile-class", required=True, choices=["local", "frontier", "unknown"])
    observe_snapshot_parser.add_argument("--local-vs-frontier", required=True, choices=["local", "frontier", "unknown"])
    observe_snapshot_parser.add_argument("--reasoning-capability-class", default="unknown", choices=["small", "medium", "frontier", "unknown"])
    observe_snapshot_parser.add_argument("--context-window", type=int, default=32768)
    observe_snapshot_parser.add_argument("--session-id", default="")
    observe_snapshot_parser.add_argument("--max-records", type=int, default=400)
    observe_snapshot_parser.set_defaults(func=_cmd_observe_projection_snapshot)

    observe_daemon_parser = subparsers.add_parser(
        "observe-projection-daemon",
        help="Capture bounded optional emitted-envelope projection snapshots",
    )
    observe_daemon_parser.add_argument("workspace_root", help="Target workspace root path")
    observe_daemon_parser.add_argument("--query", default="runtime locality reconciliation")
    observe_daemon_parser.add_argument("--query-source", default="copilot")
    observe_daemon_parser.add_argument("--model-name", required=True)
    observe_daemon_parser.add_argument("--model-source", default="")
    observe_daemon_parser.add_argument("--provider", default="")
    observe_daemon_parser.add_argument("--model-size", default="medium")
    observe_daemon_parser.add_argument("--profile-class", required=True, choices=["local", "frontier", "unknown"])
    observe_daemon_parser.add_argument("--local-vs-frontier", required=True, choices=["local", "frontier", "unknown"])
    observe_daemon_parser.add_argument("--reasoning-capability-class", default="unknown", choices=["small", "medium", "frontier", "unknown"])
    observe_daemon_parser.add_argument("--context-window", type=int, default=32768)
    observe_daemon_parser.add_argument("--session-id", default="")
    observe_daemon_parser.add_argument("--max-records", type=int, default=400)
    observe_daemon_parser.add_argument("--iterations", type=int, default=20)
    observe_daemon_parser.add_argument("--interval-seconds", type=float, default=2.0)
    observe_daemon_parser.set_defaults(func=_cmd_observe_projection_daemon)

    args = parser.parse_args()

    _setup_logging(args.verbose)

    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
