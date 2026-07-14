from __future__ import annotations

import argparse
import importlib.metadata
import json
import logging
import platform
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

UNSTABLE_ROOT_PATTERNS = [
    "Downloads",
    "Desktop",
    "/tmp/",
    "/private/tmp/",
    "/Volumes/",
]

RECOMMENDED_ROOTS = [
    "~/Developer/PECS",
    "~/Applications/PECS",
]

REQUIRED_DEPENDENCIES = ["watchdog"]
WORKSPACE_INSTALL_ROOT_CONFIG = "install_root.json"
GLOBAL_PECS_DIRNAME = ".pecs"
GLOBAL_PECS_CONFIG = "config.json"
GLOBAL_RUNTIME_REGISTRY = "runtime_registry.json"

DEFAULT_RETRIEVAL_PRIORITY = [
    "workspace_locality",
    "topology",
    "ownership",
    "governance_runtime",
    "modes",
]

MANAGED_TOOL_SCHEMA = "pecs.managed.asset.v1"


def _get_central_python(repo_root: Path) -> str:
    venv_python = repo_root / ".venv" / "bin" / "python"
    if venv_python.exists() and venv_python.is_file():
        return str(venv_python)
    return sys.executable


def is_unstable_root(path: Path) -> bool:
    path_str = str(path)
    for pattern in UNSTABLE_ROOT_PATTERNS:
        if pattern in path_str:
            return True
    return False


def validate_dependencies(verbose: bool = False) -> dict:
    results = {}
    for dep in REQUIRED_DEPENDENCIES:
        try:
            __import__(dep)
            results[dep] = "ok"
        except ImportError:
            results[dep] = "missing"
    if verbose:
        print("Dependency validation results:", results)
    return results


def install_missing_dependencies():
    missing = [dep for dep, status in validate_dependencies().items() if status != "ok"]
    if missing:
        print(f"Attempting to install missing dependencies: {missing}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
        except Exception as e:
            print(f"ERROR: Failed to install dependencies: {missing}")
            sys.exit(2)
        print(f"Dependencies installed: {missing}")
    else:
        print("All required dependencies are present.")


def print_install_root_guidance(repo_root: Path):
    if is_unstable_root(repo_root):
        print(
            f"WARNING: PECS is being installed from an unstable or transient location: {repo_root}",
            file=sys.stderr,
        )
        print(
            "It is strongly recommended to install PECS in a stable, user-owned directory such as:",
            file=sys.stderr,
        )
        for rec in RECOMMENDED_ROOTS:
            print(f"  {rec}", file=sys.stderr)
        print(
            "PECS acts as persistent continuity infrastructure and should not reside in transient directories.",
            file=sys.stderr,
        )


def health_check(workspace_root: Path, repo_root: Path, verbose: bool = False) -> dict:
    global_registry_path = _global_runtime_registry_path()
    governance_runtime_path = _global_pecs_dir() / "GOVERNANCE_RUNTIME.md"
    modes_path = _global_pecs_dir() / "MODES.md"

    results = {
        "install_root": str(repo_root),
        "install_root_stable": not is_unstable_root(repo_root),
        "dependencies": validate_dependencies(verbose=verbose),
        "python_executable": sys.executable,
        "python_executable_is_repo_venv": str(repo_root / ".venv" / "bin" / "python")
        == str(Path(sys.executable).resolve()),
        "daemon_script": str(repo_root / "launch_pecs_daemon.sh"),
        "daemon_script_exists": (repo_root / "launch_pecs_daemon.sh").exists(),
        "workspace_root": str(workspace_root),
        "workspace_exists": workspace_root.exists(),
        "workspace_install_root": None,
        "workspace_install_root_matches_repo_root": False,
        "package_installed": False,
        "console_scripts": {},
        "runtime_registry_path": str(global_registry_path),
        "runtime_registry_exists": global_registry_path.exists(),
        "governance_runtime_path": str(governance_runtime_path),
        "governance_runtime_exists": governance_runtime_path.exists(),
        "modes_path": str(modes_path),
        "modes_exists": modes_path.exists(),
    }

    try:
        dist = importlib.metadata.distribution("pecs_pro")
        results["package_installed"] = True
        results["console_scripts"] = {
            ep.name: ep.value
            for ep in dist.entry_points
            if ep.group == "console_scripts"
        }
    except importlib.metadata.PackageNotFoundError:
        results["package_installed"] = False

    pecs_path = shutil.which("pecs")
    results["pecs_entrypoint_path"] = pecs_path if pecs_path else None

    workspace_install_root = _read_workspace_install_root(workspace_root)
    if workspace_install_root is not None:
        results["workspace_install_root"] = str(workspace_install_root)
        results["workspace_install_root_matches_repo_root"] = (
            workspace_install_root == repo_root
        )

    return results


def _workspace_install_root_config_path(workspace_root: Path) -> Path:
    return workspace_root / ".pecs" / "config" / WORKSPACE_INSTALL_ROOT_CONFIG


def _global_pecs_dir() -> Path:
    return Path.home() / GLOBAL_PECS_DIRNAME


def _global_pecs_config_path() -> Path:
    return _global_pecs_dir() / GLOBAL_PECS_CONFIG


def _global_runtime_registry_path() -> Path:
    return _global_pecs_dir() / GLOBAL_RUNTIME_REGISTRY


def _load_json_object(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

    return data if isinstance(data, dict) else {}


def _default_governance_runtime_content() -> str:
    return """# PECS Governance Runtime

This file is optional runtime governance guidance loaded dynamically by clients.

Principles:
- PECS is observational continuity infrastructure.
- PECS provides locality-authority evidence, not governance enforcement.
- Retrieval is topology-first and ownership-aware.
- Missing overlays must never hard-fail runtime startup.

Hydration mode:
- Dynamic discovery via ~/.pecs/runtime_registry.json
- Graceful degradation when overlays are absent
"""


def _default_modes_content() -> str:
    return """# PECS Operational Modes

This file is optional and dynamically loaded by clients.

Suggested operational modes:
- exploratory
- locality_authority
- validation

Rules:
- Mode selection is advisory.
- Runtime behavior remains deterministic and continuity-safe.
- Missing modes overlay must not break runtime.
"""


def _ensure_global_runtime_registry(repo_root: Path) -> Dict[str, Any]:
    global_dir = _global_pecs_dir()
    global_dir.mkdir(parents=True, exist_ok=True)

    config_path = _global_pecs_config_path()
    config = _load_json_object(config_path)
    pecs_root = str(config.get("pecs_root", "") or "").strip()
    if not pecs_root:
        config["pecs_root"] = str(repo_root.resolve())
    config_path.write_text(
        json.dumps(config, indent=2, ensure_ascii=True, sort_keys=True),
        encoding="utf-8",
    )

    registry_path = _global_runtime_registry_path()
    registry = _load_json_object(registry_path)
    if "governance_runtime" not in registry:
        registry["governance_runtime"] = "/.pecs/GOVERNANCE_RUNTIME.md"
    if "modes" not in registry:
        registry["modes"] = "/.pecs/MODES.md"
    priority = registry.get("retrieval_priority")
    if not isinstance(priority, list) or not priority:
        registry["retrieval_priority"] = list(DEFAULT_RETRIEVAL_PRIORITY)

    registry_path.write_text(
        json.dumps(registry, indent=2, ensure_ascii=True, sort_keys=True),
        encoding="utf-8",
    )

    governance_runtime_path = global_dir / "GOVERNANCE_RUNTIME.md"
    if not governance_runtime_path.exists():
        governance_runtime_path.write_text(
            _default_governance_runtime_content(),
            encoding="utf-8",
        )

    modes_path = global_dir / "MODES.md"
    if not modes_path.exists():
        modes_path.write_text(_default_modes_content(), encoding="utf-8")

    return {
        "global_pecs_dir": str(global_dir),
        "config_path": str(config_path),
        "runtime_registry_path": str(registry_path),
        "governance_runtime_path": str(governance_runtime_path),
        "modes_path": str(modes_path),
    }


def _workspace_registry_path(repo_root: Path) -> Path:
    return repo_root / ".pecs_workspaces.json"


def _discover_install_runtime_info(repo_root: Path) -> Dict[str, Any]:
    python_path = _get_central_python(repo_root)
    runtime_info = {
        "install_root": str(repo_root.resolve()),
        "created_at": datetime.utcnow().isoformat() + "Z",
        "python_path": str(Path(python_path)),
        "console_scripts": {},
    }

    bin_dir = Path(runtime_info["python_path"]).parent
    candidates = [
        ("pecs", "pecs"),
        ("pecs-pro-daemon", "pecs-pro-daemon"),
        ("pecs-pro-install-workspace", "pecs-pro-install-workspace"),
    ]

    for name, executable in candidates:
        script_path = bin_dir / executable
        if script_path.exists():
            runtime_info["console_scripts"][name] = str(script_path)
            continue
        script_path = bin_dir / f"{executable}.exe"
        if script_path.exists():
            runtime_info["console_scripts"][name] = str(script_path)

    return runtime_info


def _write_workspace_install_root(workspace_root: Path, repo_root: Path) -> None:
    config_path = _workspace_install_root_config_path(workspace_root)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(_discover_install_runtime_info(repo_root), indent=2, sort_keys=True)
    _write_managed_text_asset(
        workspace_root,
        config_path,
        payload,
        backup_suffix="pecs-config-backup",
    )


def _read_workspace_install_root(workspace_root: Path) -> Optional[Path]:
    config_path = _workspace_install_root_config_path(workspace_root)
    if not config_path.exists():
        return None

    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except Exception:
        return None

    if not isinstance(data, dict):
        return None

    raw = str(data.get("install_root", "") or "").strip()
    if not raw:
        return None

    return Path(raw).resolve()


def register_workspace(repo_root: Path, workspace_root: Path) -> None:
    registry_path = _workspace_registry_path(repo_root)
    workspace_list: List[str] = []
    if registry_path.exists():
        try:
            workspace_list = json.loads(registry_path.read_text(encoding="utf-8"))
        except Exception:
            workspace_list = []

    workspace_root_str = str(workspace_root.resolve())
    if workspace_root_str not in workspace_list:
        workspace_list.append(workspace_root_str)
        registry_path.write_text(
            json.dumps(workspace_list, indent=2, sort_keys=True),
            encoding="utf-8",
        )


def read_registered_workspaces(repo_root: Path) -> List[Path]:
    registry_path = _workspace_registry_path(repo_root)
    if not registry_path.exists():
        return []

    try:
        workspace_list = json.loads(registry_path.read_text(encoding="utf-8"))
    except Exception:
        return []

    return [Path(path).resolve() for path in workspace_list if isinstance(path, str)]


def _read_json(path: Path, default: Dict[str, Any]) -> Dict[str, Any]:
    if not path.exists():
        return default

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default

    if isinstance(data, dict):
        return data

    return default


def _sanitize_vscode_task_command(command: str) -> str:
    return (
        command
        .replace("${{workspaceFolder}}", "${workspaceFolder}")
        .replace("${{input:pecsChatSource}}", "${input:pecsChatSource}")
        .replace("${{input:pecsChatMessage}}", "${input:pecsChatMessage}")
        .replace("${{input:pecsObservationQuery}}", "${input:pecsObservationQuery}")
        .replace("${{input:pecsObservationModelName}}", "${input:pecsObservationModelName}")
        .replace("${{input:pecsObservationProfileClass}}", "${input:pecsObservationProfileClass}")
        .replace("${{input:pecsObservationLocalVsFrontier}}", "${input:pecsObservationLocalVsFrontier}")
        .replace("${{input:pecsObservationIterations}}", "${input:pecsObservationIterations}")
        .replace("${{input:pecsObservationIntervalSeconds}}", "${input:pecsObservationIntervalSeconds}")
    )


def _sanitize_vscode_task(task: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(task, dict):
        return task

    if isinstance(task.get("command"), str):
        task["command"] = _sanitize_vscode_task_command(task["command"])

    windows = task.get("windows")
    if isinstance(windows, dict) and isinstance(windows.get("command"), str):
        windows["command"] = _sanitize_vscode_task_command(windows["command"])

    return task


def _merge_tasks(tasks_path: Path, repo_root: Path) -> None:
    base = _read_json(tasks_path, {"version": "2.0.0", "tasks": [], "inputs": []})
    tasks: List[Dict[str, Any]] = (
        base.get("tasks", []) if isinstance(base.get("tasks"), list) else []
    )
    inputs: List[Dict[str, Any]] = (
        base.get("inputs", []) if isinstance(base.get("inputs"), list) else []
    )

    python_bin = _get_central_python(repo_root)

    start_task = {
        "label": "PECS: Start Daemon",
        "type": "shell",
        "command": (
            'bash -lc \'cd "${workspaceFolder}" '
            '&& bash .pecs/run_pecs_daemon.sh "${workspaceFolder}"\''
        ),
        "windows": {
            "command": (
                'cd "${workspaceFolder}" && .\\pecs\\run_pecs_daemon.cmd "${workspaceFolder}"'
            )
        },
        "isBackground": True,
        "problemMatcher": [],
    }

    auto_start_task = {
        "label": "PECS: Auto Start Daemon On Folder Open",
        "type": "shell",
        "command": start_task["command"],
        "windows": start_task["windows"],
        "isBackground": True,
        "problemMatcher": [],
        "runOptions": {"runOn": "folderOpen"},
    }

    stop_task = {
        "label": "PECS: Stop Daemon",
        "type": "shell",
        "command": (
            'bash -lc \'cd "${workspaceFolder}" '
            "&& if [[ -f .pecs/daemon.pid ]]; then "
            "pid=$(<.pecs/daemon.pid); "
            "pid=\"${pid//\"/}\"; "
            "pid=\"${pid//\'/}\"; "
            "pid=\"${pid//$'\\r'/}\"; "
            "pid=\"${pid//$'\\n'/}\"; "
            "pid=\"${pid//[[:space:]]/}\"; "
            'if [[ "$pid" =~ ^[0-9]+$ ]] && kill -0 "$pid" 2>/dev/null; then kill "$pid"; fi; '
            "fi'"
        ),
        "windows": {
            "command": (
                'cd "${workspaceFolder}" && powershell.exe -NoProfile -Command "if (Test-Path \'.pecs/daemon.pid\') { $pid = Get-Content \'.pecs/daemon.pid\' | Select-Object -First 1; $pid = $pid.Trim().Trim(\"\").Trim(\'\'); if ($pid -match \'^[0-9]+$\') { Stop-Process -Id $pid -ErrorAction SilentlyContinue } }"'
            )
        },
    }

    append_task = {
        "label": "PECS: Append Chat Event",
        "type": "shell",
        "command": (
            'bash -lc \'cd "${workspaceFolder}" '
            '&& bash .pecs/tools/append_ai_chat_history.sh "${workspaceFolder}" '
            '--source "${input:pecsChatSource}" --message "${input:pecsChatMessage}"\''
        ),
        "windows": {
            "command": (
                'cd "${workspaceFolder}" && .\\pecs\\tools\\append_ai_chat_history.cmd "${workspaceFolder}" "${input:pecsChatSource}" "${input:pecsChatMessage}"'
            )
        },
    }

    manual_update_task = {
        "label": "PECS: Manual Update Chat History",
        "type": "shell",
        "command": (
            'bash -lc \'cd "${workspaceFolder}" '
            '&& bash .pecs/tools/update_ai_chat_history.sh "${workspaceFolder}" "${input:pecsChatSource}" "${input:pecsChatMessage}"\''
        ),
        "windows": {
            "command": (
                'cd "${workspaceFolder}" && .\\pecs\\tools\\update_ai_chat_history.cmd "${workspaceFolder}" "${input:pecsChatSource}" "${input:pecsChatMessage}"'
            )
        },
    }

    refresh_continuity_task = {
        "label": "PECS: Refresh Continuity State",
        "type": "shell",
        "command": (
            'bash -lc \'cd "${workspaceFolder}" '
            '&& bash .pecs/bridge/run_bridge.sh "${workspaceFolder}" refresh\''
        ),
        "windows": {
            "command": (
                'cd "${workspaceFolder}" && .\\pecs\\bridge\\run_bridge.cmd "${workspaceFolder}" refresh'
            )
        },
    }

    validate_continuity_task = {
        "label": "PECS: Validate Continuity State",
        "type": "shell",
        "command": (
            'bash -lc \'cd "${workspaceFolder}" '
            '&& bash .pecs/bridge/run_bridge.sh "${workspaceFolder}" validate\''
        ),
        "windows": {
            "command": (
                'cd "${workspaceFolder}" && .\\pecs\\bridge\\run_bridge.cmd "${workspaceFolder}" validate'
            )
        },
    }

    observation_snapshot_task = {
        "label": "PECS: Observation Snapshot (Opt-In)",
        "type": "shell",
        "command": (
            'bash -lc \'cd "${workspaceFolder}" '
            '&& bash .pecs/run_pecs.sh observe-projection-snapshot "${workspaceFolder}" '
            '--query "${input:pecsObservationQuery}" '
            '--query-source "${input:pecsChatSource}" '
            '--model-name "${input:pecsObservationModelName}" '
            '--profile-class "${input:pecsObservationProfileClass}" '
            '--local-vs-frontier "${input:pecsObservationLocalVsFrontier}"\''
        ),
        "windows": {
            "command": (
                'cd "${workspaceFolder}" && .\\pecs\\run_pecs.cmd observe-projection-snapshot "${workspaceFolder}" --query "${input:pecsObservationQuery}" --query-source "${input:pecsChatSource}" --model-name "${input:pecsObservationModelName}" --profile-class "${input:pecsObservationProfileClass}" --local-vs-frontier "${input:pecsObservationLocalVsFrontier}"'
            )
        },
    }

    observation_daemon_task = {
        "label": "PECS: Observation Daemon (Opt-In)",
        "type": "shell",
        "command": (
            'bash -lc \'cd "${workspaceFolder}" '
            '&& bash .pecs/run_pecs.sh observe-projection-daemon "${workspaceFolder}" '
            '--query "${input:pecsObservationQuery}" '
            '--query-source "${input:pecsChatSource}" '
            '--model-name "${input:pecsObservationModelName}" '
            '--profile-class "${input:pecsObservationProfileClass}" '
            '--local-vs-frontier "${input:pecsObservationLocalVsFrontier}" '
            '--iterations "${input:pecsObservationIterations}" '
            '--interval-seconds "${input:pecsObservationIntervalSeconds}"\''
        ),
        "windows": {
            "command": (
                'cd "${workspaceFolder}" && .\\pecs\\run_pecs.cmd observe-projection-daemon "${workspaceFolder}" --query "${input:pecsObservationQuery}" --query-source "${input:pecsChatSource}" --model-name "${input:pecsObservationModelName}" --profile-class "${input:pecsObservationProfileClass}" --local-vs-frontier "${input:pecsObservationLocalVsFrontier}" --iterations "${input:pecsObservationIterations}" --interval-seconds "${input:pecsObservationIntervalSeconds}"'
            )
        },
        "isBackground": True,
    }

    stop_observation_daemon_task = {
        "label": "PECS: Stop Observation Daemon (Opt-In)",
        "type": "shell",
        "command": (
            'bash -lc \'cd "${workspaceFolder}" '
            '&& ps -eo pid,args | grep "[o]bserve-projection-daemon" | grep "${workspaceFolder}" | awk "{print $1}" | xargs -r kill || echo "No observation daemon process found."\''
        ),
        "windows": {
            "command": (
                'cd "${workspaceFolder}" && powershell.exe -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match \'observe-projection-daemon\' -and $_.CommandLine -match [regex]::Escape(\'${workspaceFolder}\') } | ForEach-Object { Stop-Process -Id $_.ProcessId -ErrorAction SilentlyContinue } ; if (-not $?) { Write-Output \'No observation daemon process found.\' }"'
            )
        },
    }

    emitted_envelope_log_task = {
        "label": "PECS: Show Emitted Envelope Log (Opt-In)",
        "type": "shell",
        "command": (
            'bash -lc \'cd "${workspaceFolder}" '
            '&& if [[ -f .pecs/logs/observation/emitted_envelope.jsonl ]]; then tail -n 120 .pecs/logs/observation/emitted_envelope.jsonl; else echo "No emitted envelope log found."; fi\''
        ),
        "windows": {
            "command": (
                'cd "${workspaceFolder}" && powershell.exe -NoProfile -Command "if (Test-Path \'.pecs/logs/observation/emitted_envelope.jsonl\') { Get-Content \'.pecs/logs/observation/emitted_envelope.jsonl\' -Tail 120 } else { Write-Output \'No emitted envelope log found.\' }"'
            )
        },
    }

    projection_snapshot_log_task = {
        "label": "PECS: Show Projection Snapshot Log (Opt-In)",
        "type": "shell",
        "command": (
            'bash -lc \'cd "${workspaceFolder}" '
            '&& if [[ -f .pecs/logs/observation/projection_snapshot.jsonl ]]; then tail -n 120 .pecs/logs/observation/projection_snapshot.jsonl; else echo "No projection snapshot log found."; fi\''
        ),
        "windows": {
            "command": (
                'cd "${workspaceFolder}" && powershell.exe -NoProfile -Command "if (Test-Path \'.pecs/logs/observation/projection_snapshot.jsonl\') { Get-Content \'.pecs/logs/observation/projection_snapshot.jsonl\' -Tail 120 } else { Write-Output \'No projection snapshot log found.\' }"'
            )
        },
    }

    desired_tasks = [
        start_task,
        auto_start_task,
        stop_task,
        append_task,
        manual_update_task,
        refresh_continuity_task,
        validate_continuity_task,
        observation_snapshot_task,
        observation_daemon_task,
        stop_observation_daemon_task,
        emitted_envelope_log_task,
        projection_snapshot_log_task,
    ]

    existing_by_label = {
        task.get("label"): task
        for task in tasks
        if isinstance(task, dict) and task.get("label")
    }
    for task in desired_tasks:
        existing_by_label[task["label"]] = task

    merged_tasks = [_sanitize_vscode_task(task) for task in existing_by_label.values()]

    desired_inputs = [
        {
            "id": "pecsChatSource",
            "type": "promptString",
            "description": "Chat source (copilot or continue)",
            "default": "copilot",
        },
        {
            "id": "pecsChatMessage",
            "type": "promptString",
            "description": "Message/event text",
            "default": "manual append",
        },
        {
            "id": "pecsObservationQuery",
            "type": "promptString",
            "description": "Observation query text",
            "default": "runtime locality reconciliation",
        },
        {
            "id": "pecsObservationModelName",
            "type": "promptString",
            "description": "Model identity for diagnostics (e.g. actual model name or unknown)",
            "default": "unknown",
        },
        {
            "id": "pecsObservationProfileClass",
            "type": "promptString",
            "description": "Profile class for the model: local, frontier, or unknown",
            "default": "unknown",
        },
        {
            "id": "pecsObservationLocalVsFrontier",
            "type": "promptString",
            "description": "Runtime target class: local, frontier, or unknown",
            "default": "unknown",
        },
        {
            "id": "pecsObservationIterations",
            "type": "promptString",
            "description": "Bounded observation iterations",
            "default": "20",
        },
        {
            "id": "pecsObservationIntervalSeconds",
            "type": "promptString",
            "description": "Seconds between observation snapshots",
            "default": "2.0",
        },
    ]

    existing_inputs = {
        item.get("id"): item
        for item in inputs
        if isinstance(item, dict) and item.get("id")
    }
    for item in desired_inputs:
        existing_inputs[item["id"]] = item

    base["version"] = "2.0.0"
    base["tasks"] = merged_tasks
    base["inputs"] = list(existing_inputs.values())

    tasks_path.parent.mkdir(parents=True, exist_ok=True)
    tasks_path.write_text(
        json.dumps(base, indent=2, ensure_ascii=True), encoding="utf-8"
    )


def _merge_json_dict(path: Path, updates: Dict[str, Any]) -> None:
    current = _read_json(path, {})
    current.update(updates)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(current, indent=2, ensure_ascii=True), encoding="utf-8")


MANAGED_CONFIG_START = "# PECS MANAGED CONFIG START"
MANAGED_CONFIG_END = "# PECS MANAGED CONFIG END"


def _backup_target_file(workspace_root: Path, target: Path, suffix: str = "pecs-backup") -> Path:
    backup_dir = workspace_root / ".pecs" / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{target.name}.{suffix}.{timestamp}"
    backup_path = backup_dir / backup_name
    shutil.copy2(target, backup_path)
    return backup_path


def _write_managed_text_asset(
    workspace_root: Path,
    target: Path,
    content: str,
    *,
    backup_suffix: str = "pecs-managed-backup",
    only_if_missing: bool = False,
) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        target.write_text(content, encoding="utf-8")
        return

    if only_if_missing:
        return

    existing = target.read_text(encoding="utf-8")
    if existing == content:
        return

    _backup_target_file(workspace_root, target, suffix=backup_suffix)
    target.write_text(content, encoding="utf-8")


def _copy_canonical_asset(source: Path, target: Path, workspace_root: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        shutil.copy2(source, target)
        return

    source_text = source.read_text(encoding="utf-8")
    target_text = target.read_text(encoding="utf-8")
    if source_text != target_text:
        _backup_target_file(workspace_root, target, suffix="pecs-asset-backup")
        shutil.copy2(source, target)


def _replace_managed_block(existing: str, canonical: str) -> str:
    if MANAGED_CONFIG_START in existing and MANAGED_CONFIG_END in existing:
        prefix, remainder = existing.split(MANAGED_CONFIG_START, 1)
        _, suffix = remainder.split(MANAGED_CONFIG_END, 1)
        return prefix + canonical + suffix
    return canonical


def _write_continue_config(workspace_root: Path, repo_root: Path) -> None:
    config_source = repo_root / "workspace_assets" / ".continue" / "config.yaml"
    config_target = workspace_root / ".continue" / "config.yaml"
    config_target.parent.mkdir(parents=True, exist_ok=True)

    if not config_source.exists():
        return

    canonical_config = config_source.read_text(encoding="utf-8")
    if not config_target.exists():
        config_target.write_text(canonical_config, encoding="utf-8")
        return

    existing_config = config_target.read_text(encoding="utf-8")
    if existing_config == canonical_config:
        return

    if MANAGED_CONFIG_START in existing_config and MANAGED_CONFIG_END in existing_config:
        merged = _replace_managed_block(existing_config, canonical_config)
        if merged != existing_config:
            _backup_target_file(workspace_root, config_target, suffix="pecs-config-backup")
            config_target.write_text(merged, encoding="utf-8")
        return

    # Preserve pre-existing user YAML and append a managed PECS block instead of replacing it.
    merged = existing_config.rstrip() + "\n\n" + canonical_config.strip() + "\n"
    _backup_target_file(workspace_root, config_target, suffix="pecs-config-backup")
    config_target.write_text(merged, encoding="utf-8")


def _write_continue_rule_inventory(workspace_root: Path, rules_dir: Path, canonical_names: set[str]) -> None:
    existing_files = sorted(
        [path.name for path in rules_dir.iterdir() if path.is_file() and path.name != "PECS_RULES_INVENTORY.md"]
    )
    extra_files = [name for name in existing_files if name not in canonical_names]

    inventory_lines = [
        "# PECS Continue Rules Inventory",
        "",
        "This file documents canonical PECS Continue rule assets installed into this workspace.",
        "Do not edit canonical PECS rule files unless you are explicitly customizing your workspace integration.",
        "",
        "## Canonical Rule Assets",
    ]
    inventory_lines.extend([f"- {name}" for name in sorted(canonical_names)])

    if extra_files:
        inventory_lines.extend([
            "",
            "## Extra files detected in .continue/rules",
            "These files are not part of the canonical PECS rule set and may be stale or user-defined.",
        ])
        inventory_lines.extend([f"- {name}" for name in extra_files])
        inventory_lines.append("")
        inventory_lines.append(
            "If these files are stale, remove them or move them to a local customization directory."
        )

    inventory_path = rules_dir / "PECS_RULES_INVENTORY.md"
    inventory_path.write_text("\n".join(inventory_lines), encoding="utf-8")


def _write_continue_rules(workspace_root: Path) -> None:
    rules_dir = workspace_root / ".continue" / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)

    repo_root = Path(__file__).resolve().parent
    workspace_assets_rules = repo_root / "workspace_assets" / ".continue" / "rules"
    if not workspace_assets_rules.exists():
        return

    canonical_rule_names = set()
    for source_file in sorted(workspace_assets_rules.iterdir()):
        if source_file.is_file():
            canonical_rule_names.add(source_file.name)
            target_file = rules_dir / source_file.name
            _copy_canonical_asset(source_file, target_file, workspace_root)

    _write_continue_rule_inventory(workspace_root, rules_dir, canonical_rule_names)


def _write_copilot_instructions(workspace_root: Path, repo_root: Path) -> None:
    github_dir = workspace_root / ".github"
    github_dir.mkdir(parents=True, exist_ok=True)

    source = repo_root / "workspace_assets" / ".github" / "copilot-instructions.md"
    target = github_dir / "copilot-instructions.md"
    if not source.exists():
        return

    source_text = source.read_text(encoding="utf-8")
    if not target.exists():
        target.write_text(source_text, encoding="utf-8")
        return

    existing_text = target.read_text(encoding="utf-8")
    if source_text.strip() in existing_text:
        return

    _backup_target_file(workspace_root, target, suffix="pecs-copilot-backup")
    append_path = github_dir / "PECS_COPILOT_APPEND.md"
    append_path.write_text(
        "# PECS Copilot Instructions Append\n\n"
        "The existing `.github/copilot-instructions.md` file was preserved. "
        "Use this file to review PECS-specific workspace guidance and merge it manually if needed.\n\n"
        + source_text,
        encoding="utf-8",
    )



def _install_chat_tools(workspace_root: Path, repo_root: Path) -> None:
    tools_dir = workspace_root / ".pecs" / "tools"
    tools_dir.mkdir(parents=True, exist_ok=True)

    source_script = repo_root / "append_ai_chat_history.py"
    target_script = tools_dir / "append_ai_chat_history.py"
    _write_managed_text_asset(
        workspace_root,
        target_script,
        source_script.read_text(encoding="utf-8"),
        backup_suffix="pecs-tool-backup",
    )

    manual_source_script = repo_root / "update_ai_chat_history.sh"
    manual_target_script = tools_dir / "update_ai_chat_history.sh"
    if manual_source_script.exists():
        _write_managed_text_asset(
            workspace_root,
            manual_target_script,
            manual_source_script.read_text(encoding="utf-8"),
            backup_suffix="pecs-tool-backup",
        )

    append_cmd = tools_dir / "append_ai_chat_history.cmd"
    _write_managed_text_asset(
        workspace_root,
        append_cmd,
        """@echo off
setlocal enabledelayedexpansion
set SCRIPT_DIR=%~dp0
set WORKSPACE_ROOT=%~1
shift
set SOURCE=%~1
shift
set MESSAGE=%*
if "%WORKSPACE_ROOT%"=="" set WORKSPACE_ROOT=.
set PYTHON_EXEC=python
where python >nul 2>&1 || set PYTHON_EXEC=py -3
rem Prefer installed module over local copy for current runtime
"%PYTHON_EXEC%" -m append_ai_chat_history "%WORKSPACE_ROOT%" --source "!SOURCE!" --message "!MESSAGE!" 2>nul
if errorlevel 1 (
  "%PYTHON_EXEC%" "%SCRIPT_DIR%append_ai_chat_history.py" "%WORKSPACE_ROOT%" --source "!SOURCE!" --message "!MESSAGE!"
)
""",
    backup_suffix="pecs-tool-backup",
    )

    append_ps1 = tools_dir / "append_ai_chat_history.ps1"
    _write_managed_text_asset(
        workspace_root,
        append_ps1,
        """$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$WorkspaceRoot = if ($args.Count -ge 1) { $args[0] } else { "." }
$RemainingArgs = if ($args.Count -gt 1) { $args[1..($args.Count - 1)] } else { @() }
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) { $python = Get-Command py -ErrorAction SilentlyContinue }
if (-not $python) { Write-Error "Python is not available on PATH"; exit 1 }
# Prefer installed module over local copy for current runtime
$result = & $python.Source -m append_ai_chat_history $WorkspaceRoot @RemainingArgs 2>$null
if ($LASTEXITCODE -ne 0) {
  & $python.Source (Join-Path $ScriptDir "append_ai_chat_history.py") $WorkspaceRoot @RemainingArgs
}
""",
    backup_suffix="pecs-tool-backup",
    )

    update_cmd = tools_dir / "update_ai_chat_history.cmd"
    _write_managed_text_asset(
        workspace_root,
        update_cmd,
        """@echo off
setlocal enabledelayedexpansion
set SCRIPT_DIR=%~dp0
set WORKSPACE_ROOT=%~1
shift
set SOURCE=%~1
shift
set MESSAGE=%*
if "%WORKSPACE_ROOT%"=="" set WORKSPACE_ROOT=.
set PYTHON_EXEC=python
where python >nul 2>&1 || set PYTHON_EXEC=py -3
rem Prefer installed module over local copy for current runtime
"%PYTHON_EXEC%" -m append_ai_chat_history "%WORKSPACE_ROOT%" --source "!SOURCE!" --message "!MESSAGE!" 2>nul
if errorlevel 1 (
  "%PYTHON_EXEC%" "%SCRIPT_DIR%append_ai_chat_history.py" "%WORKSPACE_ROOT%" --source "!SOURCE!" --message "!MESSAGE!"
)
""",
    backup_suffix="pecs-tool-backup",
    )

    update_ps1 = tools_dir / "update_ai_chat_history.ps1"
    _write_managed_text_asset(
        workspace_root,
        update_ps1,
        """$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$WorkspaceRoot = if ($args.Count -ge 1) { $args[0] } else { "." }
$RemainingArgs = if ($args.Count -gt 1) { $args[1..($args.Count - 1)] } else { @() }
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) { $python = Get-Command py -ErrorAction SilentlyContinue }
if (-not $python) { Write-Error "Python is not available on PATH"; exit 1 }
# Prefer installed module over local copy for current runtime
$result = & $python.Source -m append_ai_chat_history $WorkspaceRoot @RemainingArgs 2>$null
if ($LASTEXITCODE -ne 0) {
  & $python.Source (Join-Path $ScriptDir "append_ai_chat_history.py") $WorkspaceRoot @RemainingArgs
}
""",
    backup_suffix="pecs-tool-backup",
    )

    chat_history = workspace_root / ".pecs" / "ai_chat_history.json"
    if not chat_history.exists():
        chat_history.write_text("[]\n", encoding="utf-8")


def _install_bridge_runtime(workspace_root: Path, repo_root: Path) -> None:
    bridge_dir = workspace_root / ".pecs" / "bridge"
    config_dir = workspace_root / ".pecs" / "config"
    runtime_dir = workspace_root / ".pecs" / "runtime"
    continuity_dir = workspace_root / ".pecs" / "continuity"

    bridge_dir.mkdir(parents=True, exist_ok=True)
    config_dir.mkdir(parents=True, exist_ok=True)
    runtime_dir.mkdir(parents=True, exist_ok=True)
    continuity_dir.mkdir(parents=True, exist_ok=True)

    _write_managed_text_asset(
        workspace_root,
        runtime_dir / ".gitkeep",
        "",
        backup_suffix="pecs-runtime-backup",
    )

    # Bridge scripts are NOT copied to the workspace. They are imported
    # from the installed PECS runtime's `scripts` package. This ensures
    # every workspace always executes the current runtime with no
    # workspace-local copies that can go stale.

    # WARNING: run_bridge.py is a THIN DELEGATE that always invokes the installed
    # PECS CLI. It MUST NOT import from workspace-local copies of bridge scripts.
    # All continuity logic lives in the installed PECS runtime's `scripts` package.
    bridge_runner = """\"\"\"PECS workspace bridge — thin CLI delegate.

Resolves the installed PECS runtime via install_root.json and delegates
all operations to the installed ``pecs`` CLI. Never imports from
workspace-local copies of bridge scripts.
\"\"\"

import argparse
import subprocess
import sys
from pathlib import Path


def _resolve_python() -> str:
    \"\"\"Resolve installed Python from install_root.json.\"\"\"
    config_path = Path(__file__).resolve().parent.parent / \"config\" / \"install_root.json\"
    if config_path.exists():
        try:
            import json
            data = json.loads(config_path.read_text(encoding=\"utf-8\"))
            python_path = data.get(\"python_path\", \"\")
            if python_path and Path(python_path).exists():
                return python_path
        except Exception:
            pass
    return sys.executable


def main() -> None:
    parser = argparse.ArgumentParser(
        description=\"PECS workspace bridge — delegates to installed PECS CLI\"
    )
    parser.add_argument(
        \"command\",
        choices=[\"refresh\", \"validate\"],
        help=\"Bridge command to run\",
    )
    parser.add_argument(
        \"workspace_root\",
        nargs=\"?\",
        default=None,
        help=\"Workspace root path (default: current directory).\",
    )
    parser.add_argument(
        \"--workspace\",
        dest=\"workspace_flag\",
        default=None,
        help=\"Workspace root path.\",
    )
    args = parser.parse_args()

    workspace_value = args.workspace_flag or args.workspace_root or \".\"
    workspace_root = Path(workspace_value).resolve()
    python_exe = _resolve_python()

    result = subprocess.run(
        [python_exe, \"-m\", \"workspace_bridge_cli\", args.command, \"--workspace\", str(workspace_root)],
        capture_output=True, text=True,
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    sys.exit(result.returncode)


if __name__ == \"__main__\":
    main()
"""
    _write_managed_text_asset(
        workspace_root,
        bridge_dir / "run_bridge.py",
        bridge_runner,
        backup_suffix="pecs-bridge-backup",
    )

    bridge_sh = """#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_ROOT="${1:-.}"
COMMAND="${2:-refresh}"
BRIDGE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$BRIDGE_DIR/../config/install_root.json"
INSTALL_ROOT=""
INSTALL_PYTHON=""
PECS_EXE=""
PECS_DAEMON_EXE=""

if [[ -f "$CONFIG_FILE" ]]; then
  PYTHON_CMD="python3"
  if ! command -v "$PYTHON_CMD" >/dev/null 2>&1; then
    PYTHON_CMD="python"
  fi
  if command -v "$PYTHON_CMD" >/dev/null 2>&1; then
    eval "$("$PYTHON_CMD" - "$CONFIG_FILE" <<'PY'
import json, pathlib, sys, shlex
path = pathlib.Path(sys.argv[1])
try:
    data = json.loads(path.read_text(encoding='utf-8'))
except Exception:
    data = {}
for key in ["install_root", "python_path"]:
    value = str(data.get(key, "") or "")
    print(f"{key.upper()}={shlex.quote(value)}")
console = data.get("console_scripts", {}) or {}
value = str(console.get("pecs", "") or "")
print(f"PECS={shlex.quote(value)}")
value = str(console.get("pecs-pro-daemon", "") or "")
print(f"PECS_PRO_DAEMON={shlex.quote(value)}")
PY
)"
  fi
  INSTALL_ROOT="${INSTALL_ROOT:-}"
  INSTALL_PYTHON="${PYTHON_PATH:-}"
  PECS_EXE="${PECS:-}"
  PECS_DAEMON_EXE="${PECS_PRO_DAEMON:-}"
fi

if [[ -n "$INSTALL_ROOT" && -f "$INSTALL_ROOT/.venv/bin/activate" ]]; then
  source "$INSTALL_ROOT/.venv/bin/activate"
fi

if [[ "$WORKSPACE_ROOT" == "refresh" || "$WORKSPACE_ROOT" == "validate" ]]; then
    COMMAND="$WORKSPACE_ROOT"
    WORKSPACE_ROOT="$(pwd)"
fi

cd "$WORKSPACE_ROOT"
PYTHON_CMD="python3"
if ! command -v "$PYTHON_CMD" >/dev/null 2>&1; then
  PYTHON_CMD="python"
fi
"$PYTHON_CMD" .pecs/bridge/run_bridge.py "$COMMAND" --workspace "$WORKSPACE_ROOT"
"""
    _write_managed_text_asset(
        workspace_root,
        bridge_dir / "run_bridge.sh",
        bridge_sh,
        backup_suffix="pecs-bridge-backup",
    )
    bridge_cmd = bridge_dir / "run_bridge.cmd"
    _write_managed_text_asset(
        workspace_root,
        bridge_cmd,
        """@echo off
setlocal enabledelayedexpansion
set SCRIPT_DIR=%~dp0
set WORKSPACE_ROOT=%~1
set COMMAND=%~2
if "%WORKSPACE_ROOT%"=="" set WORKSPACE_ROOT=.
if "%COMMAND%"=="" set COMMAND=refresh
set PYTHON_EXEC=python
where python >nul 2>&1 || set PYTHON_EXEC=py -3
"%PYTHON_EXEC%" "%SCRIPT_DIR%run_bridge.py" "%COMMAND%" --workspace "%WORKSPACE_ROOT%"
""",
        backup_suffix="pecs-bridge-backup",
    )
    bridge_ps1 = bridge_dir / "run_bridge.ps1"
    _write_managed_text_asset(
        workspace_root,
        bridge_ps1,
        """$args = $args
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$Command = if ($args.Count -ge 1) { $args[0] } else { "refresh" }
$WorkspaceRoot = if ($args.Count -ge 2) { $args[1] } else { "." }
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) { $python = Get-Command py -ErrorAction SilentlyContinue }
if (-not $python) { Write-Error "Python is not available on PATH"; exit 1 }
& $python.Source (Join-Path $ScriptDir "run_bridge.py") $Command --workspace $WorkspaceRoot
""",
    backup_suffix="pecs-bridge-backup",
    )

    bridge_config = {
        "schema": "pecs.bridge.config.v1",
        "mode": "exploratory",
        "compare_before_write": True,
        "omit_empty_sections": True,
        "sparse_output": True,
    }
    _write_managed_text_asset(
        workspace_root,
        config_dir / "continuity_bridge.json",
        json.dumps(bridge_config, indent=2, sort_keys=True),
        backup_suffix="pecs-config-backup",
    )

    continuity_scaffold = {
        "active_topology.json": {
            "schema": "pecs.active_topology.v1",
            "active_topology_zone": "general_runtime",
            "active_runtime_zones": [],
            "runtime_validation": {
                "runtime_evidence_count": 0,
                "runtime_confirmations": 0,
                "active_topology_targeting": 0.0,
                "runtime_confirmation_density": 0.0,
            },
            "validation_metrics": {
                "edit_locality_improvement": 0.0,
                "active_topology_targeting": 0.0,
                "continuity_hotspot_identification": 0.0,
                "runtime_confirmation_density": 0.0,
                "continuity_compression_effectiveness": 0.0,
            },
            "workspace_trajectory": "general_runtime",
        },
        "locality_state.json": {
            "schema": "pecs.locality_state.v1",
            "validation_metrics": {
                "edit_locality_improvement": 0.0,
                "active_topology_targeting": 0.0,
                "continuity_hotspot_identification": 0.0,
                "runtime_confirmation_density": 0.0,
                "continuity_compression_effectiveness": 0.0,
            },
        },
        "engineering_continuity_state.json": {
            "schema": "pecs.engineering_continuity.v1",
            "active_engineering_chains": [],
            "updated_at": "",
        },
        "continuity_hydration_report.json": {
            "schema": "pecs.continuity_hydration_report.v1",
            "generated_at": "",
            "chain_count": 0,
            "source_counts": {},
            "merged_client_count": 0,
            "note": "Structured engineering continuity hydration report.",
        },
    }

    for file_name, payload in continuity_scaffold.items():
        path = continuity_dir / file_name
        if not path.exists():
            path.write_text(
                json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8"
            )

    markdown_scaffold = {
        "architectural_decisions.md": "# Architectural Decisions\n",
        "current_workspace_focus.md": "# Current Workspace Focus\n",
        "unresolved_tensions.md": "# Unresolved Tensions\n",
    }
    for file_name, content in markdown_scaffold.items():
        path = continuity_dir / file_name
        if not path.exists():
            path.write_text(content, encoding="utf-8")


def _install_workspace_local_launchers(workspace_root: Path, repo_root: Path) -> None:
    launcher_dir = workspace_root / ".pecs"
    launcher_dir.mkdir(parents=True, exist_ok=True)

    common_loader = """#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/config/install_root.json"
INSTALL_ROOT=""
INSTALL_PYTHON=""
PECS_EXE=""
PECS_DAEMON_EXE=""

if [[ -f "$CONFIG_FILE" ]]; then
  PYTHON_CMD="python3"
  if ! command -v "$PYTHON_CMD" >/dev/null 2>&1; then
    PYTHON_CMD="python"
  fi
  if command -v "$PYTHON_CMD" >/dev/null 2>&1; then
    eval "$("$PYTHON_CMD" - "$CONFIG_FILE" <<'PY'
import json, pathlib, sys, shlex
path = pathlib.Path(sys.argv[1])
try:
    data = json.loads(path.read_text(encoding='utf-8'))
except Exception:
    data = {}
for key in ["install_root", "python_path"]:
    value = str(data.get(key, "") or "")
    print(f"{key.upper()}={shlex.quote(value)}")
console = data.get("console_scripts", {}) or {}
value = str(console.get("pecs", "") or "")
print(f"PECS={shlex.quote(value)}")
value = str(console.get("pecs-pro-daemon", "") or "")
print(f"PECS_PRO_DAEMON={shlex.quote(value)}")
PY
    )"
  fi
  INSTALL_ROOT="${INSTALL_ROOT:-}"
  INSTALL_PYTHON="${PYTHON_PATH:-}"
  PECS_EXE="${PECS:-}"
  PECS_DAEMON_EXE="${PECS_PRO_DAEMON:-}"
fi
"""


    run_pecs = launcher_dir / "run_pecs.sh"
    _write_managed_text_asset(
        workspace_root,
        run_pecs,
        common_loader
        + "\n"
        + "if [[ -n \"$PECS_EXE\" && -x \"$PECS_EXE\" ]]; then\n"
        + "  exec \"$PECS_EXE\" \"$@\"\n"
        + "fi\n"
        + "if command -v pecs >/dev/null 2>&1; then\n"
        + "  exec pecs \"$@\"\n"
        + "fi\n"
        + "if [[ -n \"$INSTALL_PYTHON\" && -x \"$INSTALL_PYTHON\" ]]; then\n"
        + "  exec \"$INSTALL_PYTHON\" -m workspace_bridge_cli \"$@\"\n"
        + "fi\n"
        + "echo \"ERROR: Could not resolve PECS runtime from install root or PATH.\" >&2\n"
        + "echo \"Expected install root: $INSTALL_ROOT\" >&2\n"
        + "exit 1\n"
        ,
        backup_suffix="pecs-launcher-backup",
    )
    run_pecs.chmod(0o755)

    run_daemon = launcher_dir / "run_pecs_daemon.sh"
    _write_managed_text_asset(
        workspace_root,
        run_daemon,
        common_loader
        + "\n"
        + "WORKSPACE_ROOT=\"${1:-.}\"\n"
        + "WORKSPACE_ROOT=\"$(cd \"$WORKSPACE_ROOT\" && pwd)\"\n"
        + "LOG_DIR=\"$WORKSPACE_ROOT/.pecs\"\n"
        + "LOG_FILE=\"$LOG_DIR/daemon.log\"\n"
        + "PID_FILE=\"$LOG_DIR/daemon.pid\"\n"
        + "HEALTH_FILE=\"$LOG_DIR/daemon_health.json\"\n"
        + "STARTUP_TIMEOUT=\"${PECS_DAEMON_STARTUP_TIMEOUT:-30}\"\n"
        + "STARTUP_INTERVAL=\"${PECS_DAEMON_STARTUP_INTERVAL:-0.5}\"\n"
        + "mkdir -p \"$LOG_DIR\"\n"
        + "check_daemon_health() {\n"
        + "  if [[ ! -f \"$HEALTH_FILE\" ]]; then\n"
        + "    return 1\n"
        + "  fi\n"
        + "  if ! command -v \"$PYTHON_CMD\" >/dev/null 2>&1; then\n"
        + "    return 1\n"
        + "  fi\n"
        + "  local status\n"
        + "  status=\"$($PYTHON_CMD - \"$HEALTH_FILE\" <<'PY'\nfrom pathlib import Path\nimport json, sys\n\npath = Path(sys.argv[1])\ntry:\n    data = json.loads(path.read_text(encoding='utf-8'))\nexcept Exception:\n    sys.exit(1)\nif (\n    data.get('status') == 'healthy'\n    and data.get('retrieval_ready') is True\n    and data.get('topology_ready') is True\n    and data.get('continuity_ready') is True\n):\n    sys.stdout.write('healthy')\nPY\n)\"\n"
        + "  [[ \"$status\" == \"healthy\" ]]\n"
        + "}\n"
        + "if [[ -f \"$PID_FILE\" ]]; then\n"
        + "  pid=\"$(tr -d '\"[:space:]' < \"$PID_FILE\")\"\n"
        + "  if [[ \"$pid\" =~ ^[0-9]+$ ]] && kill -0 \"$pid\" 2>/dev/null; then\n"
        + "    echo \"PECS daemon is already running for workspace: $WORKSPACE_ROOT (pid=$pid)\"\n"
        + "    exit 0\n"
        + "  fi\n"
        + "  rm -f \"$PID_FILE\"\n"
        + "fi\n"
        + "resolve_cmd() {\n"
        + "  if [[ -n \"$PECS_DAEMON_EXE\" && -x \"$PECS_DAEMON_EXE\" ]]; then\n"
        + "    echo \"$PECS_DAEMON_EXE\"\n"
        + "    return 0\n"
        + "  fi\n"
        + "  if command -v pecs-pro-daemon >/dev/null 2>&1; then\n"
        + "    echo \"pecs-pro-daemon\"\n"
        + "    return 0\n"
        + "  fi\n"
        + "  if [[ -n \"$INSTALL_PYTHON\" && -x \"$INSTALL_PYTHON\" ]]; then\n"
        + "    echo \"$INSTALL_PYTHON\"\n"
        + "    return 0\n"
        + "  fi\n"
        + "  return 1\n"
        + "}\n"
        + "DAEMON_CMD=\"$(resolve_cmd)\"\n"
        + "if [[ -z \"$DAEMON_CMD\" ]]; then\n"
        + "  echo \"ERROR: Could not resolve PECS daemon runtime from install root or PATH.\" >&2\n"
        + "  echo \"Expected install root: $INSTALL_ROOT\" >&2\n"
        + "  exit 1\n"
        + "fi\n"
        + "if [[ \"$DAEMON_CMD\" == \"$INSTALL_PYTHON\" ]]; then\n"
        + "  DAEMON_ARGS=(-m run_pecs_daemon \"$WORKSPACE_ROOT\")\n"
        + "else\n"
        + "  DAEMON_ARGS=(\"$WORKSPACE_ROOT\")\n"
        + "fi\n"
        + "cd \"$WORKSPACE_ROOT\"\n"
        + "if command -v setsid >/dev/null 2>&1; then\n"
        + "  setsid \"$DAEMON_CMD\" \"${DAEMON_ARGS[@]}\" >> \"$LOG_FILE\" 2>&1 &\n"
        + "else\n"
        + "  nohup \"$DAEMON_CMD\" \"${DAEMON_ARGS[@]}\" >> \"$LOG_FILE\" 2>&1 &\n"
        + "fi\n"
        + "launcher_pid=$!\n"
        + "end_time=$(( $(date +%s) + STARTUP_TIMEOUT ))\n"
        + "while [[ $(date +%s) -lt $end_time ]]; do\n"
        + "  if [[ -f \"$PID_FILE\" ]]; then\n"
        + "    pid=\"$(tr -d '\"[:space:]' < \"$PID_FILE\")\"\n"
        + "    if [[ \"$pid\" =~ ^[0-9]+$ ]] && kill -0 \"$pid\" 2>/dev/null; then\n"
        + "      echo \"Daemon started successfully (PID $pid)\"\n"
        + "      exit 0\n"
        + "    fi\n"
        + "  fi\n"
        + "  if ! kill -0 \"$launcher_pid\" 2>/dev/null; then\n"
        + "    echo \"Daemon launcher process exited before startup. Check $LOG_FILE\" >&2\n"
        + "    tail -n 20 \"$LOG_FILE\" >&2 || true\n"
        + "    exit 1\n"
        + "  fi\n"
        + "  sleep \"$STARTUP_INTERVAL\"\n"
        + "done\n"
        + "echo \"Daemon startup timed out waiting for daemon readiness. See $LOG_FILE\" >&2\n"
        + "tail -n 20 \"$LOG_FILE\" >&2 || true\n"
        + "if [[ -f \"$HEALTH_FILE\" ]]; then\n"
        + "  echo \"--- health artifact ---\" >&2\n"
        + "  cat \"$HEALTH_FILE\" >&2 || true\n"
        + "fi\n"
        + "exit 1\n"
        ,
        backup_suffix="pecs-launcher-backup",
    )
    run_daemon.chmod(0o755)

    run_pecs_cmd = launcher_dir / "run_pecs.cmd"
    _write_managed_text_asset(
        workspace_root,
        run_pecs_cmd,
        """@echo off
setlocal enabledelayedexpansion
set SCRIPT_DIR=%~dp0
set CONFIG_FILE=%SCRIPT_DIR%config\\install_root.json
set INSTALL_ROOT=
set INSTALL_PYTHON=
set PECS_EXE=
set IDX=0
set PYTHON_EXEC=python
where python >nul 2>&1 || set PYTHON_EXEC=py -3
for /f "usebackq delims=" %%A in (`%PYTHON_EXEC% -c "import json,sys; p=sys.argv[1]; data=json.loads(open(p,encoding='utf-8').read()); print(data.get('install_root','')); print(data.get('python_path','')); print(data.get('console_scripts',{}).get('pecs','')); print(data.get('console_scripts',{}).get('pecs-pro-daemon',''))" "%CONFIG_FILE%"`) do (
  set /a IDX+=1
  if !IDX! EQU 1 set INSTALL_ROOT=%%A
  if !IDX! EQU 2 set INSTALL_PYTHON=%%A
  if !IDX! EQU 3 set PECS_EXE=%%A
)
if defined PECS_EXE if exist "%PECS_EXE%" (
  "%PECS_EXE%" %*
  goto :EOF
)
if defined INSTALL_PYTHON if exist "%INSTALL_PYTHON%" (
  "%INSTALL_PYTHON%" -m workspace_bridge_cli %*
  goto :EOF
)
pecs %*
""",
    backup_suffix="pecs-launcher-backup",
    )

    run_daemon_cmd = launcher_dir / "run_pecs_daemon.cmd"
    _write_managed_text_asset(
        workspace_root,
        run_daemon_cmd,
        """@echo off
setlocal enabledelayedexpansion
set WORKSPACE_ROOT=%~1
if "%WORKSPACE_ROOT%"=="" set WORKSPACE_ROOT=.
set SCRIPT_DIR=%~dp0
set LAUNCHER=%SCRIPT_DIR%run_pecs_daemon.ps1
if exist "%LAUNCHER%" (
  powershell -NoProfile -ExecutionPolicy Bypass -File "%LAUNCHER%" "%WORKSPACE_ROOT%"
  goto :EOF
)
echo ERROR: Workspace daemon launcher missing: %LAUNCHER%
exit /b 1
""",
    backup_suffix="pecs-launcher-backup",
    )

    run_pecs_ps1 = launcher_dir / "run_pecs.ps1"
    _write_managed_text_asset(
        workspace_root,
        run_pecs_ps1,
        """$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$InstallRoot = $null
$InstallPython = $null
$PecsExe = $null
$PecsDaemonExe = $null
$ConfigFile = Join-Path $ScriptDir "config" "install_root.json"
if (Test-Path $ConfigFile) {
  $data = Get-Content $ConfigFile -Raw | ConvertFrom-Json
  $InstallRoot = $data.install_root
  $InstallPython = $data.python_path
  $PecsExe = $data.console_scripts.pecs
  $PecsDaemonExe = $data.console_scripts."pecs-pro-daemon"
}
$WorkspaceArgs = $args
if ($PecsExe -and (Test-Path $PecsExe)) {
  & $PecsExe @WorkspaceArgs
  exit $LASTEXITCODE
}
if ($InstallPython -and (Test-Path $InstallPython)) {
  & $InstallPython -m workspace_bridge_cli @WorkspaceArgs
  exit $LASTEXITCODE
}
Write-Error "ERROR: Could not resolve PECS runtime from install root or PATH."
Write-Error "Expected install root: $InstallRoot"
exit 1
""",
    backup_suffix="pecs-launcher-backup",
    )

    run_daemon_ps1 = launcher_dir / "run_pecs_daemon.ps1"
    _write_managed_text_asset(
        workspace_root,
        run_daemon_ps1,
        """param([string]$WorkspaceRoot = ".")
Set-StrictMode -Version Latest

$WorkspacePath = Resolve-Path -Path $WorkspaceRoot -ErrorAction Stop
$WorkspaceRoot = $WorkspacePath.Path
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ConfigFile = Join-Path $ScriptDir "config" "install_root.json"
$InstallRoot = $null
$InstallPython = $null
$PecsDaemonExe = $null

if (Test-Path $ConfigFile) {
  $data = Get-Content $ConfigFile -Raw | ConvertFrom-Json
  $InstallRoot = $data.install_root
  $InstallPython = $data.python_path
  $PecsDaemonExe = $data.console_scripts."pecs-pro-daemon"
}

$PecsRoot = Join-Path $WorkspaceRoot ".pecs"
$LogFile = Join-Path $PecsRoot "daemon.log"
$PidFile = Join-Path $PecsRoot "daemon.pid"
$StartupTimeout = 10
$StartupInterval = 0.5

New-Item -ItemType Directory -Force -Path $PecsRoot | Out-Null

function Normalize-Pid {
    param([string]$RawPid)
    if ($RawPid -eq $null) {
      return $null
    }
    $value = $RawPid.Trim()
    if ($value.StartsWith('"') -and $value.EndsWith('"')) {
      $value = $value.Trim('"')
    }
    if ($value.StartsWith("'") -and $value.EndsWith("'")) {
      $value = $value.Trim("'")
    }
    return $value
  }

  if (Test-Path $PidFile) {
  try {
    $pid = Normalize-Pid (Get-Content $PidFile | Select-Object -First 1)
    if ($pid -match '^[0-9]+$' -and (Get-Process -Id $pid -ErrorAction SilentlyContinue)) {
      Write-Host "PECS daemon is already running for workspace: $WorkspaceRoot (pid=$pid)"
      exit 0
    }
  } catch {
    # ignore stale PID file content
  }
  Remove-Item -Force -Path $PidFile -ErrorAction SilentlyContinue
}

function Resolve-DaemonCommand {
  if ($PecsDaemonExe -and (Test-Path $PecsDaemonExe)) {
    return $PecsDaemonExe
  }
  if (Get-Command pecs-pro-daemon -ErrorAction SilentlyContinue) {
    return (Get-Command pecs-pro-daemon).Source
  }
  if ($InstallPython -and (Test-Path $InstallPython)) {
    return $InstallPython
  }
  return $null
}

$DaemonCmd = Resolve-DaemonCommand
if (-not $DaemonCmd) {
  Write-Error "ERROR: Could not resolve PECS daemon runtime from install root or PATH."
  Write-Error "Expected install root: $InstallRoot"
  exit 1
}

if ($DaemonCmd -eq $InstallPython) {
  $ArgumentList = @('-m', 'run_pecs_daemon', $WorkspaceRoot)
} else {
  $ArgumentList = @($WorkspaceRoot)
}

$process = Start-Process -FilePath $DaemonCmd -ArgumentList $ArgumentList -RedirectStandardOutput $LogFile -RedirectStandardError $LogFile -NoNewWindow -WindowStyle Hidden -PassThru

$endTime = (Get-Date).AddSeconds($StartupTimeout)
while ((Get-Date) -lt $endTime) {
  Start-Sleep -Seconds $StartupInterval
  if (Test-Path $PidFile) {
    try {
      $pid = Normalize-Pid (Get-Content $PidFile | Select-Object -First 1)
      if ($pid -match '^[0-9]+$' -and (Get-Process -Id $pid -ErrorAction SilentlyContinue)) {
        Write-Host "Daemon started successfully (PID $pid)"
        exit 0
      }
    } catch {
      # continue waiting
    }
  }
  if ($process.HasExited) {
    Write-Error "Daemon process exited before startup. Check $LogFile"
    exit $process.ExitCode
  }
}

Write-Error "Daemon startup timed out waiting for .pecs/daemon.pid. See $LogFile"
exit 1
""",
    backup_suffix="pecs-launcher-backup",
    )


def _write_readme(workspace_root: Path) -> None:
    readme = workspace_root / ".pecs" / "README_WORKSPACE_INTEGRATION.md"
    content = """# PECS Workspace Integration

This workspace was configured by PECS workspace installer.

PECS artifacts are generated continuity infrastructure only.
Do NOT edit or patch .pecs files.
PECS does not contain engineering sourcecode.
Runtime workspace modules are the authoritative implementation.

Installed items:
- .vscode/tasks.json (PECS tasks, including folder-open auto-start)
- .vscode/settings.json with pecs.contextPath
- .continue/config.yaml
- .continue/rules/pecs-first-routing.yaml
- .continue/rules/PECS_CONTEXT_RULE.md
- .continue/rules/PECS_APPEND_RULE.md
- .continue/rules/CONTINUITY_MAP.md
- .continue/rules/PECS_CODING_PROTOCOL.md
- .continue/rules/PECS_PROMPT.md
- .continue/rules/live-context.md
- .github/copilot-instructions.md
- .pecs/tools/append_ai_chat_history.py
- .pecs/ai_chat_history.json
- .pecs/bridge/run_bridge.py
- .pecs/bridge/export_workspace_continuity.py
- .pecs/bridge/validate_workspace_continuity.py
- .pecs/config/install_root.json
- .pecs/config/continuity_bridge.json
- .pecs/run_pecs.sh
- .pecs/run_pecs.cmd
- .pecs/run_pecs_daemon.sh
- .pecs/run_pecs_daemon.cmd
- .pecs/continuity/engineering_continuity_state.json
- .pecs/continuity/continuity_hydration_report.json
- .pecs/README_MANUAL_SETUP.md

PECS v2 Process Flow:
1. Install workspace assets to configure VS Code, Continue, Copilot, and .pecs infrastructure.
2. Start or auto-start the workspace daemon to generate `.pecs/` continuity artifacts from runtime workspace modules.
3. PECS-PRO writes deterministic continuity outputs such as active context and locality index.
4. PECS-LITE reads those outputs and returns runtime target projections to the AI model.
5. The model uses runtime workspace modules for edits; `.pecs` files remain infrastructure only.
6. Accepted engineering continuity chains preserve high-signal issue-locality-outcome guidance.

Key rules:
- Workspace runtime modules are authoritative.
- `.pecs` files are not sourcecode.
- Use `.pecs` only to identify locality and execution neighborhood.
- Do not edit or patch `.pecs` artifacts.
- Do not use raw chat narratives as locality authority.
- Use structured accepted/rejected locality continuity with confidence.

Run manually:
- Task: PECS: Start Daemon
- Task: PECS: Stop Daemon
- Task: PECS: Refresh Continuity State
- Task: PECS: Validate Continuity State
- Task: PECS: Observation Snapshot (Opt-In)
- Task: PECS: Observation Daemon (Opt-In)
- Task: PECS: Stop Observation Daemon (Opt-In)
- Task: PECS: Show Emitted Envelope Log (Opt-In)
- Task: PECS: Show Projection Snapshot Log (Opt-In)

Refresh behavior:
- Existing `.pecs` continuity artifacts, chat history, and runtime evidence are preserved.
- Continue and Copilot assets are merged/appended when possible.
- Managed launcher/bridge/tool updates are backup-aware before replacement.
- Runtime workspace modules and topology are not modified by installer flows.

Notes:
- Auto-start task may require VS Code confirmation for automatic tasks.
- Continue/Copilot integration is configured to use PECS locality projection and runtime targets.
- PECS-LITE is stateless and query-driven. It does not scan the workspace.
- The canonical query entrypoint is `pecs observe-projection-snapshot "<workspace>" --query "<query>" --query-source "<source>" --model-name "<model>" --profile-class "<local|frontier|unknown>" --local-vs-frontier "<local|frontier|unknown>"`; use `pecs observe-projection-daemon` for repeated observation.
- Use preserve-first workspace lifecycle commands for asset refresh and continuity rebuilds.
"""
    # PECS Workspace Integration\n\nThis workspace was configured by PECS workspace installer.\n\nPECS artifacts are generated continuity infrastructure only.\nDo NOT edit or patch .pecs files.\nPECS does not contain engineering sourcecode.\nRuntime workspace modules are the authoritative implementation.\n\nInstalled items:\n- .vscode/tasks.json (PECS tasks, including folder-open auto-start)\n- .vscode/settings.json with pecs.contextPath\n- .continue/rules/PECS_CONTEXT_RULE.md\n- .continue/rules/PECS_APPEND_RULE.md\n- .github/copilot-instructions.md\n- .pecs/tools/append_ai_chat_history.py\n- .pecs/ai_chat_history.json\n- .pecs/bridge/run_bridge.py\n- .pecs/bridge/export_workspace_continuity.py\n- .pecs/bridge/validate_workspace_continuity.py\n- .pecs/config/continuity_bridge.json\n- .pecs/README_MANUAL_SETUP.md\n\nRun manually:\n- Task: PECS: Start Daemon\n- Task: PECS: Stop Daemon\n- Task: PECS: Refresh Continuity State\n- Task: PECS: Validate Continuity State\n\nNotes:\n- Auto-start task may require VS Code confirmation for automatic tasks.\n- Continue/Copilot integration is configured to use PECS locality projection and runtime targets.\n- PECS artifacts are infrastructure only; do not treat them as source.\n"""
    readme.parent.mkdir(parents=True, exist_ok=True)
    _write_managed_text_asset(
        workspace_root,
        readme,
        content,
        backup_suffix="pecs-doc-backup",
    )


def _install_consumer_guidance_assets(workspace_root: Path, repo_root: Path) -> None:
    guidance_assets = [
        (repo_root / "workspace_assets" / ".pecs" / "PECS_CONSUMER_PROTOCOL.md", workspace_root / ".pecs" / "PECS_CONSUMER_PROTOCOL.md"),
        (repo_root / "workspace_assets" / ".kimi" / "instructions.md", workspace_root / ".kimi" / "instructions.md"),
        (repo_root / "workspace_assets" / ".commandcode" / "instructions.md", workspace_root / ".commandcode" / "instructions.md"),
    ]

    for source, target in guidance_assets:
        if not source.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        _write_managed_text_asset(
            workspace_root,
            target,
            source.read_text(encoding="utf-8"),
            backup_suffix="pecs-guidance-backup",
        )


def _copy_manual_setup_guide(workspace_root: Path, repo_root: Path) -> None:
    source = repo_root / "README_MANUAL_SETUP.md"
    target = workspace_root / ".pecs" / "README_MANUAL_SETUP.md"
    if source.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        _write_managed_text_asset(
            workspace_root,
            target,
            source.read_text(encoding="utf-8"),
            backup_suffix="pecs-doc-backup",
        )


def _has_existing_workspace_assets(workspace_root: Path) -> bool:
    if not (workspace_root / ".pecs").exists():
        return False

    markers = [
        workspace_root / ".pecs" / "config" / "install_root.json",
        workspace_root / ".vscode" / "tasks.json",
        workspace_root / ".continue" / "config.yaml",
        workspace_root / ".github" / "copilot-instructions.md",
    ]
    return any(path.exists() for path in markers)


def _cleanup_stale_local_runtime_copy(workspace_root: Path) -> None:
    stale_paths = [
        workspace_root / ".pecs" / "pecs_pro",
        workspace_root / ".pecs" / "pecs_pro.egg-info",
        workspace_root / ".pecs" / "pecs_pro.dist-info",
    ]
    backup_dir = workspace_root / ".pecs" / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    for path in stale_paths:
        if not path.exists():
            continue
        target_backup = backup_dir / f"stale_local_runtime_{path.name}_{timestamp}"
        try:
            if path.is_dir():
                shutil.move(str(path), str(target_backup))
            else:
                shutil.copy2(str(path), str(target_backup))
                path.unlink()
        except Exception:
            # Do not fail install because of cleanup; this is remediation only.
            continue


def install_workspace(workspace_root: Path, repo_root: Path, preserve_existing: bool = True) -> None:
    _ensure_global_runtime_registry(repo_root)
    _install_chat_tools(workspace_root, repo_root)
    _install_bridge_runtime(workspace_root, repo_root)
    _merge_tasks(workspace_root / ".vscode" / "tasks.json", repo_root)
    _merge_json_dict(
        workspace_root / ".vscode" / "settings.json",
        {
            "pecs.contextPath": ".pecs/active_context.json",
        },
    )
    _write_continue_config(workspace_root, repo_root)
    _write_continue_rules(workspace_root)
    _write_copilot_instructions(workspace_root, repo_root)
    _install_consumer_guidance_assets(workspace_root, repo_root)
    _copy_manual_setup_guide(workspace_root, repo_root)
    _write_readme(workspace_root)
    _cleanup_stale_local_runtime_copy(workspace_root)
    _write_workspace_install_root(workspace_root, repo_root)
    _install_workspace_local_launchers(workspace_root, repo_root)
    register_workspace(repo_root, workspace_root)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Install PECS VS Code/Continue/Copilot integration files into a workspace"
    )
    parser.add_argument("workspace_root", help="Target workspace root path")
    parser.add_argument(
        "--repo-root",
        default="",
        help="PECS repository root (defaults to this script's directory)",
    )
    parser.add_argument(
        "--upgrade",
        dest="preserve",
        action="store_true",
        help="Preserve existing user configuration during upgrade",
    )
    parser.add_argument(
        "--preserve",
        dest="preserve",
        action="store_true",
        help="Preserve existing user configuration (alias)",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Verify installation without installing",
    )
    parser.add_argument(
        "--validate-deps",
        action="store_true",
        help="Validate required Python dependencies and exit",
    )
    parser.add_argument(
        "--health-check",
        action="store_true",
        help="Run installation health check and exit",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    workspace_root = Path(args.workspace_root).resolve()
    repo_root = (
        Path(args.repo_root).resolve()
        if args.repo_root
        else Path(__file__).resolve().parent
    )

    # Install-root safety guidance
    print_install_root_guidance(repo_root)

    # Dependency validation/health check CLI
    if args.validate_deps:
        results = validate_dependencies(verbose=True)
        missing = [dep for dep, status in results.items() if status != "ok"]
        if missing:
            print(f"Missing dependencies: {missing}")
            sys.exit(2)
        print("All required dependencies are present.")
        sys.exit(0)

    if args.health_check:
        results = health_check(workspace_root, repo_root, verbose=True)
        print(json.dumps(results, indent=2))
        if not results["install_root_stable"]:
            print("WARNING: Unstable install root detected.", file=sys.stderr)
        if any(v != "ok" for v in results["dependencies"].values()):
            print("ERROR: Missing dependencies.", file=sys.stderr)
            sys.exit(2)
        if not results["daemon_script_exists"]:
            print("ERROR: Daemon launch script missing.", file=sys.stderr)
            sys.exit(3)
        print("PECS installation health check passed.")
        sys.exit(0)

    if not workspace_root.exists():
        logger.error(f"Workspace does not exist: {workspace_root}")
        sys.exit(1)

    try:
        logger.info(f"PECS workspace integration installer started")
        logger.info(f"Workspace: {workspace_root}")
        logger.info(f"PECS repository: {repo_root}")

        # Dependency guarantee before install
        install_missing_dependencies()

        # Try to use manifest-based manager if available
        try:
            try:
                from pecs_pro.workspace_assets_manager import WorkspaceAssetsManager
            except ImportError:
                from .workspace_assets_manager import WorkspaceAssetsManager

            logger.info("Using manifest-based workspace assets manager")
            manager = WorkspaceAssetsManager(repo_root, workspace_root)

            if args.verify_only:
                logger.info("Running verification only (no changes)")
                result = manager.verify_installation()
                print(json.dumps(result, indent=2))
                sys.exit(0 if result["valid"] else 1)

            # Install assets
            existing_assets = _has_existing_workspace_assets(workspace_root)
            preserve_existing = bool(getattr(args, 'preserve', False) or existing_assets)

            install_result = manager.install_assets(upgrade=preserve_existing, verify=False)
            logger.info(f"Asset installation status: {install_result['status']}")
            logger.info(f"Installed {len(install_result['installed_assets'])} asset(s)")

            if install_result.get("errors"):
                logger.warning(f"Installation warnings: {install_result['errors']}")

        except ImportError:
            logger.warning(
                "Manifest-based manager not available, using legacy installer"
            )

        # Always run legacy installer as fallback/supplementary
        logger.info("Installing workspace integration (legacy flow)")
        install_workspace(
            workspace_root,
            repo_root,
            preserve_existing=_has_existing_workspace_assets(workspace_root),
        )
        logger.info("Legacy installation completed")

        from validation.canonical_workspace_validator import (
            run_canonical_workspace_validation,
        )

        canonical_report = run_canonical_workspace_validation(workspace_root, repo_root)
        if not bool(canonical_report.get("valid", False)):
            logger.error("Canonical Alpha 1 verification failed after installation")
            print(json.dumps(canonical_report, indent=2, sort_keys=True))
            sys.exit(1)

        logger.info(
            f"PECS workspace integration successfully installed at: {workspace_root}"
        )
        print(
            f"Installation complete. Run 'pecs verify-workspace {workspace_root}' to verify."
        )

    except Exception as e:
        logger.error(f"Installation failed: {e}", exc_info=args.verbose)
        sys.exit(1)


if __name__ == "__main__":
    main()
