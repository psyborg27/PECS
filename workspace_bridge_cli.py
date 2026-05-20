from __future__ import annotations

import argparse
import datetime
import importlib.metadata
import json
import logging
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Optional

from pecs_pro.install_workspace_integration import (
    install_workspace,
    print_install_root_guidance,
    read_registered_workspaces,
    validate_dependencies,
)
from pecs_pro.workspace_assets_manager import WorkspaceAssetsManager

logger = logging.getLogger(__name__)


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
        result = manager.install_assets(upgrade=args.upgrade, verify=False)

        logger.info(f"Status: {result['status']}")
        logger.info(f"Installed: {len(result.get('installed_assets', []))} asset(s)")

        if result.get("errors"):
            for error in result["errors"]:
                logger.error(f"  - {error}")
            sys.exit(1)

        logger.info("Applying PECS workspace integration configuration")
        install_workspace(workspace_root, repo_root)

        verification = manager.verify_installation()
        if not verification["valid"]:
            logger.error("Workspace verification failed after installation")
            for error in verification.get("errors", []):
                logger.error(f"  - {error}")
            sys.exit(1)

        logger.info("Workspace assets installed successfully")
    except Exception as e:
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
        result = manager.install_assets(upgrade=args.upgrade, verify=False)

        logger.info(f"Status: {result['status']}")
        logger.info(f"Installed: {len(result.get('installed_assets', []))} asset(s)")

        if result.get("errors"):
            for error in result["errors"]:
                logger.error(f"  - {error}")
            sys.exit(1)

        logger.info("Applying PECS workspace integration configuration")
        install_workspace(workspace_root, repo_root)
        _start_workspace_daemon(workspace_root)
        _run_workspace_bridge(workspace_root, "refresh")

        verification = manager.verify_installation()
        if not verification["valid"]:
            logger.error("Workspace verification failed after bootstrap")
            for error in verification.get("errors", []):
                logger.error(f"  - {error}")
            sys.exit(1)

        logger.info("Workspace bootstrap completed successfully")
    except Exception as e:
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
        upgrade=args.upgrade,
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
        result = manager.install_assets(upgrade=args.upgrade, verify=False)

        if result.get("errors"):
            logger.error("Workspace rebind encountered errors:")
            for error in result["errors"]:
                logger.error(f"  - {error}")
            sys.exit(1)

        install_workspace(workspace_root, repo_root)
        verification = manager.verify_installation()
        if not verification["valid"]:
            logger.error("Workspace verification failed after rebind")
            for error in verification.get("errors", []):
                logger.error(f"  - {error}")
            sys.exit(1)

        _run_workspace_bridge(workspace_root, "refresh")
        logger.info("Workspace rebind completed successfully")
    except Exception as e:
        logger.error(f"Workspace rebind failed: {e}")
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
                upgrade=args.upgrade,
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
        result = manager.repair_installation()

        logger.info(f"Repair status: {result['status']}")
        logger.info(f"Repaired: {len(result.get('repairs', []))} item(s)")

        if result.get("repairs"):
            for repair in result["repairs"]:
                logger.info(f"  ✓ {repair}")

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
        health_state = _load_health_state(workspace_root)

        logger.info(f"Workspace: {workspace_root}")

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
        _run_workspace_bridge(workspace_root, "refresh")
        logger.info(f"Continuity refresh completed: {workspace_root}")
    except Exception as e:
        logger.error(f"Continuity refresh failed: {e}")
        sys.exit(1)


def _cmd_validate_workspace(args: argparse.Namespace) -> None:
    """Validate continuity state using the workspace bridge."""
    workspace_root = Path(args.workspace_root).resolve()

    if not workspace_root.exists():
        logger.error(f"Workspace does not exist: {workspace_root}")
        sys.exit(1)

    try:
        _run_workspace_bridge(workspace_root, "validate")
        logger.info(f"Continuity validation completed: {workspace_root}")
    except Exception as e:
        logger.error(f"Continuity validation failed: {e}")
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

        # Continuity health checks
        logger.info("\nContinuity Health:")
        active_context = _load_json(
            workspace_root / ".pecs" / "active_context.json", {}
        )
        locality_state = _load_json(
            workspace_root / ".pecs" / "locality_index.json", {}
        )
        continuity_topology = _load_json(
            workspace_root / ".pecs" / "continuity" / "active_topology.json", {}
        )
        continuity_locality_state = _load_json(
            workspace_root / ".pecs" / "continuity" / "locality_state.json", {}
        )

        active_size = (
            len(active_context.get("activated_objects", []))
            if isinstance(active_context, dict)
            else 0
        )
        cluster_count = (
            len(continuity_locality_state.get("active_locality_clusters", []))
            if isinstance(continuity_locality_state, dict)
            else 0
        )
        touched_count = (
            len(continuity_locality_state.get("active_runtime_touched_files", []))
            if isinstance(continuity_locality_state, dict)
            else 0
        )
        confirmation = float(
            continuity_topology.get("runtime_validation", {}).get(
                "runtime_confirmation_density", 0.0
            )
            if isinstance(continuity_topology, dict)
            else 0.0
        )

        logger.info(f"  Active context objects: {active_size}")
        logger.info(f"  Active locality clusters: {cluster_count}")
        logger.info(f"  Active runtime touched files: {touched_count}")
        logger.info(f"  Runtime confirmation density: {confirmation:.3f}")

        projection_path = workspace_root / ".pecs" / "pecs_lite_runtime_projection.json"
        if projection_path.exists():
            projection = _load_json(projection_path, {})
            runtime_targets = projection.get("runtime_targets", [])
            wrapper_warning = projection.get("wrapper_warning")
            authority_violation = any(
                str(path).startswith(".pecs/")
                for path in runtime_targets
                if isinstance(path, str)
            )
            logger.info("\nPECS-LITE Projection:")
            logger.info(f"  ✓ Projection file found: {projection_path}")
            logger.info(f"  Runtime targets: {len(runtime_targets)}")
            logger.info(f"  Wrapper warning: {wrapper_warning}")
            logger.info(
                f"  Authority violation: {'YES' if authority_violation else 'NO'}"
            )
        else:
            logger.info("\nPECS-LITE Projection:")
            logger.info(
                "  ✗ Projection file missing: .pecs/pecs_lite_runtime_projection.json"
            )

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
        action="store_true",
        help="Preserve existing user configuration",
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
        action="store_true",
        help="Preserve existing user configuration",
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
        action="store_true",
        help="Preserve existing user configuration",
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
        action="store_true",
        help="Preserve existing user configuration",
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
        action="store_true",
        help="Preserve existing user configuration",
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
        action="store_true",
        help="Preserve existing user configuration",
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
        action="store_true",
        help="Preserve existing user configuration",
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
        action="store_true",
        help="Preserve existing user configuration",
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

    args = parser.parse_args()

    _setup_logging(args.verbose)

    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
