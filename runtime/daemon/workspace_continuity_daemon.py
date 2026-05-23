from __future__ import annotations

import ast
import errno
import hashlib
import importlib.metadata
import inspect
import json
import logging
import os
import re
import subprocess
import sys
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Deque, Dict, Iterable, List, Optional, Set, Tuple

from ..locality_activation_engine import LocalityActivationEngine
from ..runtime_activation_logger import RuntimeActivationLogger
from ..runtime_telemetry import RuntimeTelemetryEmitter
from topology.archaeology.continuity_archaeology import ContinuityArchaeology
from topology.compaction.compact_context_builder import CompactContextBuilder
from topology.locality_traversal import LocalityTraversal
from topology.runtime_edge_reinforcement import RuntimeEdgeReinforcement
from topology.topology_edge_weights import edge_weight
from ..session.workspace_runtime_session import WorkspaceRuntimeSession

# Keep watchdog imports at module scope so nested handlers can always resolve.
try:
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer
except ImportError:
    FileSystemEventHandler = None
    Observer = None

LOG = logging.getLogger(__name__)

HARD_EXCLUDED_DIRS = {
    ".pecs",
    "backup scripts",
    "backups",
    "archive",
    "archived",
    "old",
    "tmp",
    "temp",
    "__pycache__",
    ".git",
    "venv",
    "env",
    "node_modules",
    "dist",
    "build",
}

ENTRYPOINT_CANDIDATES = (
    "main_app.py",
    "Qt/main_app.py",
    "run_qt.py",
)

PECS_ENTRYPOINT_FALLBACKS = (
    "run_pecs_pro.py",
    "run_pecs_daemon.py",
    "workspace_bridge_cli.py",
)


@dataclass
class WorkspaceContinuityDaemon:
    """
    Persistent runtime-local continuity cache daemon.

    PECS v2 correction:
    - runtime-reachable topology only
    - deterministic entrypoint reconstruction
    - compact continuity outputs
    - no workspace-wide archival indexing
    """

    workspace_root: Path
    runtime_session: WorkspaceRuntimeSession
    compact_builder: CompactContextBuilder
    watch_pattern: str = "*.py"
    artifact_dir_name: str = ".pecs"
    monitor_recursive: bool = True

    artifact_dir: Path = field(init=False)
    observer: Optional[object] = field(default=None, init=False)
    current_changes: Set[Path] = field(default_factory=set, init=False)
    pid_file_name: str = "daemon.pid"
    cycle_lock_name: str = "daemon.lock"
    cycle_lock_ttl_seconds: int = 180
    continuity_refresh_throttle_seconds: int = 60
    max_log_bytes: int = 262144
    log_backup_count: int = 3

    workspace_id: str = field(init=False)
    runtime_reachable_files: Set[Path] = field(default_factory=set, init=False)
    log_dir: Path = field(init=False)
    activity_log_path: Path = field(init=False)
    continuity_log_path: Path = field(init=False)
    error_log_path: Path = field(init=False)
    _last_chat_event_ts: Optional[float] = field(default=None, init=False)
    runtime_locality_payload: Dict[str, Dict[str, object]] = field(
        default_factory=dict, init=False
    )
    runtime_topology_edges: List[Dict[str, str]] = field(
        default_factory=list, init=False
    )
    _start_timestamp: Optional[float] = field(default=None, init=False)
    _last_rebuild_timestamp: Optional[float] = field(default=None, init=False)
    _last_continuity_refresh_timestamp: Optional[float] = field(default=None, init=False)
    _last_continuity_refresh_status: str = field(default="", init=False)
    _cycle_lock_owned: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        self.workspace_root = self.workspace_root.resolve()
        self.artifact_dir = self.workspace_root / self.artifact_dir_name
        self.artifact_dir.mkdir(parents=True, exist_ok=True)
        self.runtime_telemetry = RuntimeTelemetryEmitter(self.workspace_root)
        self._init_observability()
        self.runtime_activation_logger = RuntimeActivationLogger(self.artifact_dir)
        self.locality_activation_engine = LocalityActivationEngine(
            self.runtime_activation_logger
        )
        self.runtime_telemetry.emit_runtime_event(
            subsystem="STARTUP",
            event="daemon_initialized",
            payload={
                "workspace_root": str(self.workspace_root),
                "artifact_dir": str(self.artifact_dir),
            },
        )
        self.edge_reinforcement = RuntimeEdgeReinforcement()
        self.locality_traversal = LocalityTraversal()
        self.continuity_archaeology = ContinuityArchaeology()
        self.runtime_snapshot_dir = self.artifact_dir / "runtime_topology_snapshots"
        self.runtime_snapshot_dir.mkdir(parents=True, exist_ok=True)

        if not self.workspace_root.exists():
            raise FileNotFoundError(
                f"Workspace root does not exist: {self.workspace_root}"
            )

        self.workspace_id = hashlib.sha256(
            str(self.workspace_root).encode("utf-8")
        ).hexdigest()

    def _init_observability(self) -> None:
        self.log_dir = self.artifact_dir / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.activity_log_path = self.log_dir / "daemon_activity.log"
        self.continuity_log_path = self.log_dir / "continuity_sync.log"
        self.error_log_path = self.log_dir / "daemon_errors.log"
        self._log_activity(
            "daemon_initialized",
            {
                "workspace_root": str(self.workspace_root),
                "artifact_dir": str(self.artifact_dir),
            },
        )

    def _current_iso_ts(self) -> str:
        return datetime.utcnow().isoformat() + "Z"

    def _emit_runtime_telemetry(
        self,
        subsystem: str,
        event: str,
        payload: Optional[Dict[str, Any]] = None,
        file: Optional[str] = None,
        function: Optional[str] = None,
    ) -> None:
        try:
            if file is None or function is None:
                frame = inspect.currentframe()
                caller_frame = frame.f_back if frame is not None else None
                if caller_frame is not None:
                    code = caller_frame.f_code
                    file = file or Path(code.co_filename).name
                    function = function or code.co_name

            self.runtime_telemetry.emit_runtime_event(
                subsystem=subsystem,
                event=event,
                payload=payload,
                file=file,
                function=function,
            )
        except Exception:
            pass

    def _rotate_log(self, path: Path) -> None:
        try:
            if not path.exists() or path.stat().st_size <= self.max_log_bytes:
                return

            for index in range(self.log_backup_count - 1, 0, -1):
                source = self.log_dir / f"{path.name}.{index}"
                target = self.log_dir / f"{path.name}.{index + 1}"
                if source.exists():
                    source.replace(target)

            rotated = self.log_dir / f"{path.name}.1"
            path.replace(rotated)
        except Exception:
            pass

    def _write_observability_line(self, path: Path, payload: Dict[str, Any]) -> None:
        payload_with_metadata = {
            "ts": self._current_iso_ts(),
            "event": payload.get("event", "unknown"),
            "details": payload.get("details", {}),
        }
        try:
            self._rotate_log(path)
            with path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(payload_with_metadata, ensure_ascii=False) + "\n")
        except OSError:
            pass

    def _log_activity(self, event: str, details: Optional[Dict[str, Any]] = None) -> None:
        self._write_observability_line(
            self.activity_log_path,
            {"event": event, "details": details or {}},
        )

    def _log_continuity(self, event: str, details: Optional[Dict[str, Any]] = None) -> None:
        self._write_observability_line(
            self.continuity_log_path,
            {"event": event, "details": details or {}},
        )

    def _log_error(self, event: str, details: Optional[Dict[str, Any]] = None) -> None:
        self._write_observability_line(
            self.error_log_path,
            {"event": event, "details": details or {}},
        )

    def _workspace_metadata(self) -> Dict[str, str]:
        return {
            "workspace_root": str(self.workspace_root),
            "workspace_id": self.workspace_id,
            "continuity_namespace": self.workspace_id,
        }

    def start(self) -> None:
        """Start live filesystem monitoring and artifact regeneration."""
        if FileSystemEventHandler is None or Observer is None:
            raise ImportError(
                "watchdog is required for the daemon. "
                "Install it with `pip3 install watchdog`."
            )

        self._start_timestamp = time.time()
        self._write_pid_file()

        self._chat_history_path = self.workspace_root / ".pecs" / "ai_chat_history.json"
        self._ensure_chat_history_file()
        self._last_chat_history_mtime = None
        if self._chat_history_path.exists():
            self._last_chat_history_mtime = self._chat_history_path.stat().st_mtime

        if self._should_full_scan():
            self._clean_core_artifacts()
            self._run_cycle_locked(
                cycle_name="startup_full_scan",
                operation=lambda: self._rebuild_runtime_topology(),
            )

        if not self.runtime_locality_payload:
            self._run_cycle_locked(
                cycle_name="startup_topology_bootstrap",
                operation=lambda: self._rebuild_runtime_topology(),
            )

        if self.runtime_locality_payload:
            self._run_continuity_refresh(
                trigger="startup",
                reason="daemon startup full scan or topology bootstrap",
            )

        self._append_system_chat_event(
            event_type="daemon_started",
            message="PECS daemon started",
            correlation={
                "runtime_reachable_count": len(self.runtime_reachable_files),
                "topology_edge_count": len(self.runtime_topology_edges),
            },
        )

        try:
            self._write_health_state()
        except Exception:
            pass

        class ChangeHandler(FileSystemEventHandler):
            def __init__(self, daemon: WorkspaceContinuityDaemon) -> None:
                self.daemon = daemon

            def on_created(self, event):
                self._handle(event)

            def on_modified(self, event):
                self._handle(event)

            def on_moved(self, event):
                if event.is_directory:
                    return
                self._handle(event)

            def on_deleted(self, event):
                if event.is_directory:
                    return
                self._handle(event)

            def _handle(self, event) -> None:
                if event.is_directory:
                    return

                path = Path(
                    event.dest_path if hasattr(event, "dest_path") else event.src_path
                )
                if self.daemon._is_monitored_file(path):
                    self.daemon._record_change(path)

        handler = ChangeHandler(self)
        observer = Observer()
        observer.schedule(
            handler, str(self.workspace_root), recursive=self.monitor_recursive
        )

        self.observer = observer
        observer.start()

        message = (
            f"PECS daemon started for {self.workspace_root}. "
            "Do not close this terminal."
        )
        print(message)
        LOG.info(message)
        self._emit_runtime_telemetry(
            subsystem="STARTUP",
            event="daemon_started",
            payload={
                "workspace_root": str(self.workspace_root),
                "pid": os.getpid(),
            },
        )

        try:
            while True:
                self._poll_chat_history()
                time.sleep(1.0)
        except KeyboardInterrupt:
            LOG.info("PECS daemon interrupted, stopping")
        finally:
            observer.stop()
            observer.join()
            self._release_cycle_lock()
            self._remove_pid_file()

    def stop(self) -> None:
        if self.observer is not None:
            try:
                self.observer.stop()
                self.observer.join()
            except Exception:
                pass

    def _should_full_scan(self) -> bool:
        compact_bundle = self.artifact_dir / "compact_bundle.json"
        locality_index = self.artifact_dir / "locality_index.json"

        for path in [compact_bundle, locality_index]:
            if not path.exists():
                return True
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                return True

            if not data:
                return True

            if path.name == "compact_bundle.json":
                if data.get("context_count", 0) == 0:
                    return True

            if path.name == "locality_index.json" and len(data) == 0:
                return True

        return False

    def _clean_core_artifacts(self) -> None:
        for name in [
            "locality_index.json",
            "topology_compact.json",
            "compact_bundle.json",
            "active_context.json",
            "session_context.json",
        ]:
            path = self.artifact_dir / name
            try:
                if path.exists():
                    path.unlink()
            except OSError as exc:
                LOG.warning("Failed to remove core PECS artifact %s: %s", path, exc)

    def _record_change(self, file_path: Path) -> None:
        file_path = file_path.resolve()
        self.current_changes.add(file_path)
        try:
            self._log_activity(
                "file_change_detected",
                {"path": str(file_path.relative_to(self.workspace_root))},
            )
            self._emit_runtime_telemetry(
                subsystem="WORKSPACE",
                event="file_change_detected",
                payload={"path": str(file_path.relative_to(self.workspace_root))},
            )
        except Exception:
            pass
        self._process_changes()

    def _process_changes(self) -> None:
        self._run_cycle_locked(
            cycle_name="incremental_refresh",
            operation=self._process_changes_unlocked,
        )

    def _process_changes_unlocked(self) -> None:
        if not self.current_changes:
            return

        changed_files = sorted(self.current_changes)
        self.current_changes.clear()

        try:
            if self._chat_history_path in changed_files:
                self._on_chat_history_update_unlocked()

            if self.runtime_activation_logger.event_path in changed_files:
                self._on_activation_update()

            python_changed_files = [p for p in changed_files if p.suffix == ".py"]
            if not python_changed_files:
                return

            # Rebuild from runtime topology roots (entrypoints), not filesystem-wide inventory.
            self._rebuild_runtime_topology(changed_files=python_changed_files)
        except Exception as exc:
            self._log_error(
                "incremental_sync_failed",
                {
                    "changed_files": [str(p.relative_to(self.workspace_root)) for p in changed_files],
                    "error": str(exc),
                },
            )
            raise

    def _rebuild_runtime_topology(
        self,
        changed_files: Optional[List[Path]] = None,
    ) -> None:
        self._log_activity(
            "topology_rebuild_started",
            {
                "changed_files": [
                    str(path.relative_to(self.workspace_root))
                    for path in (changed_files or [])
                ],
            },
        )
        self._emit_runtime_telemetry(
            subsystem="CONTINUITY",
            event="topology_rebuild_started",
            payload={
                "changed_files": [
                    str(path.relative_to(self.workspace_root))
                    for path in (changed_files or [])
                ],
            },
        )
        entrypoints = self._discover_entrypoints()
        reachable_files = self._resolve_runtime_reachable_files(entrypoints)
        self._populate_runtime_indexes(reachable_files)

        focus = self._infer_active_focus_from_chat()
        activation = self._infer_locality_activation(focus)
        compact_bundle = self._build_compact_bundle(focus, activation)
        active_context = self._build_active_context_payload(
            focus, compact_bundle, activation
        )
        topology_payload = {
            "entrypoints": [self._pecs_id_from_path(p) for p in entrypoints],
            "edges": self.runtime_topology_edges,
            "edge_count": len(self.runtime_topology_edges),
        }

        self._write_json("locality_index.json", self.runtime_locality_payload)
        self._write_json("topology_compact.json", topology_payload)
        self._write_json("compact_bundle.json", compact_bundle)
        self._write_json("active_context.json", active_context)
        self._write_runtime_topology_snapshot(activation)
        self._write_json(
            "session_context.json",
            {
                "workspace_root": str(self.workspace_root),
                "active_objects": sorted(self.runtime_session.active_objects),
                "active_paths": sorted(self.runtime_session.active_paths),
                "active_topology_zone": focus.get("active_topology_zone"),
                "current_issue": focus.get("current_issue"),
            },
        )
        self._write_json(
            "daemon_state.json",
            {
                "workspace_root": str(self.workspace_root),
                "artifact_dir": str(self.artifact_dir),
                "runtime_reachable_count": len(self.runtime_reachable_files),
                "topology_edge_count": len(self.runtime_topology_edges),
                "runtime_locality_payload_count": len(self.runtime_locality_payload),
                "last_rebuild_timestamp": time.time(),
            },
        )
        self._last_rebuild_timestamp = time.time()
        self._write_health_state()

        self._log_continuity(
            "projection_refresh_started",
            {
                "trigger": "runtime_topology",
                "reachable_files": len(self.runtime_reachable_files),
                "edge_count": len(self.runtime_topology_edges),
            },
        )
        self._log_continuity(
            "topology_compact_refreshed",
            {"edge_count": len(self.runtime_topology_edges)},
        )
        self._log_continuity(
            "locality_index_refreshed",
            {"payload_count": len(self.runtime_locality_payload)},
        )
        self._log_continuity(
            "compact_bundle_refreshed",
            {"context_count": len(compact_bundle.get("bundle", []))},
        )
        self._log_continuity(
            "active_context_refreshed",
            {
                "activated_objects": len(
                    active_context.get("activated_objects", [])
                ),
            },
        )
        self._log_continuity(
            "projection_refresh_completed",
            {"trigger": "runtime_topology"},
        )
        self._log_activity(
            "topology_rebuild_completed",
            {
                "runtime_reachable_files": len(self.runtime_reachable_files),
                "topology_edge_count": len(self.runtime_topology_edges),
            },
        )
        self._emit_runtime_telemetry(
            subsystem="CONTINUITY",
            event="topology_rebuild_completed",
            payload={
                "runtime_reachable_files": len(self.runtime_reachable_files),
                "topology_edge_count": len(self.runtime_topology_edges),
                "locality_payload_count": len(self.runtime_locality_payload),
            },
        )

        if self.runtime_locality_payload:
            self._run_continuity_refresh(
                trigger="runtime_topology",
                reason="runtime topology rebuild",
            )

    def _discover_entrypoints(self) -> List[Path]:
        entrypoints: List[Path] = []
        for relative in ENTRYPOINT_CANDIDATES:
            path = (self.workspace_root / relative).resolve()
            if path.exists() and path.suffix == ".py":
                entrypoints.append(path)

        if entrypoints:
            return entrypoints

        fallback_entrypoints: List[Path] = []
        for relative in PECS_ENTRYPOINT_FALLBACKS:
            path = (self.workspace_root / relative).resolve()
            if path.exists() and path.suffix == ".py":
                fallback_entrypoints.append(path)

        if fallback_entrypoints:
            return fallback_entrypoints

        fallback = self.workspace_root / "main.py"
        if fallback.exists():
            return [fallback.resolve()]

        return []

    def _resolve_runtime_reachable_files(self, entrypoints: List[Path]) -> Set[Path]:
        reachable: Set[Path] = set()
        excluded_paths: Set[str] = set()
        queue: Deque[Path] = deque(entrypoints)

        while queue:
            path = queue.popleft().resolve()

            if path in reachable:
                continue
            if not path.exists() or path.suffix != ".py":
                continue
            if self._is_hard_excluded(path):
                excluded_paths.add(str(path.relative_to(self.workspace_root)))
                continue

            reachable.add(path)

            for target in self._extract_local_import_targets(path):
                if target not in reachable:
                    queue.append(target)

        if excluded_paths:
            self._log_continuity(
                "workspace_filter_applied",
                {
                    "excluded_path_count": len(excluded_paths),
                    "example_excluded_paths": sorted(list(excluded_paths))[:8],
                },
            )
            self._emit_runtime_telemetry(
                subsystem="LOCALITY_AUTHORITY",
                event="workspace_filter_applied",
                payload={
                    "excluded_path_count": len(excluded_paths),
                    "example_excluded_paths": sorted(list(excluded_paths))[:8],
                },
            )

        return reachable

    def _extract_local_import_targets(self, path: Path) -> Set[Path]:
        targets: Set[Path] = set()

        try:
            source = path.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(source)
        except Exception:
            return targets

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    resolved = self._resolve_module_to_path(alias.name, path, 0)
                    if resolved is not None:
                        targets.add(resolved)

            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                base = self._resolve_module_to_path(module, path, node.level)
                if base is not None:
                    targets.add(base)

                for alias in node.names:
                    if alias.name == "*":
                        continue
                    symbol_module = f"{module}.{alias.name}" if module else alias.name
                    resolved = self._resolve_module_to_path(
                        symbol_module, path, node.level
                    )
                    if resolved is not None:
                        targets.add(resolved)

        for match in re.findall(
            r"['\"]([A-Za-z_][\w]*(?:\.[A-Za-z_][\w]*)+)['\"]", source
        ):
            resolved = self._resolve_module_to_path(match, path, 0)
            if resolved is not None:
                targets.add(resolved)

        return targets

    def _resolve_module_to_path(
        self,
        module: str,
        current_file: Path,
        level: int,
    ) -> Optional[Path]:
        module = module.strip(".")

        if level > 0:
            current_rel_parent = current_file.relative_to(self.workspace_root).parent
            base_parts = list(current_rel_parent.parts)
            trim = max(0, level - 1)
            if trim > 0:
                base_parts = base_parts[:-trim] if trim <= len(base_parts) else []
            module_parts = module.split(".") if module else []
            candidate = self._resolve_parts_to_file(base_parts + module_parts)
            if candidate is not None:
                return candidate

        if module:
            candidate = self._resolve_parts_to_file(module.split("."))
            if candidate is not None:
                return candidate

        return None

    def _resolve_parts_to_file(self, parts: List[str]) -> Optional[Path]:
        if not parts:
            return None

        module_path = self.workspace_root.joinpath(*parts)

        direct = module_path.with_suffix(".py")
        if direct.exists() and not self._is_hard_excluded(direct):
            return direct.resolve()

        init_file = module_path / "__init__.py"
        if init_file.exists() and not self._is_hard_excluded(init_file):
            return init_file.resolve()

        return None

    def _populate_runtime_indexes(self, reachable_files: Set[Path]) -> None:
        self.runtime_reachable_files = set(reachable_files)
        self.runtime_locality_payload.clear()
        self.runtime_topology_edges = []

        self.runtime_session.locality_index.object_locality.clear()
        self.runtime_session.locality_index.runtime_locality.clear()
        self.runtime_session.locality_index.ownership_locality.clear()
        self.runtime_session.execution_index.execution_paths.clear()
        self.runtime_session.execution_index.execution_chains.clear()
        self.runtime_session.graph_index.node_index.clear()
        self.runtime_session.graph_index.edge_index.clear()
        self.runtime_session.graph_index.zone_index.clear()
        self.runtime_session.topology_retriever.ownership_index.ownership_locality.clear()
        self.runtime_session.active_objects.clear()
        self.runtime_session.active_paths.clear()
        self.runtime_session.clear_context_cache()

        edge_seen: Set[Tuple[str, str, str]] = set()

        for path in sorted(reachable_files):
            object_id = self._object_id_from_path(path)
            path_id = self._path_id_from_path(path)
            pecs_id = self._pecs_id_from_path(path)

            class_name, method_name = self._extract_symbol_metadata(path)
            runtime_zone = self._runtime_zone_for_path(path)
            edges = self._extract_runtime_edges(path)
            runtime_anchor_ids = self._runtime_anchor_ids_from_edges(path, edges)

            self.runtime_locality_payload[pecs_id] = {
                "file": str(path.relative_to(self.workspace_root)),
                "class": class_name,
                "method": method_name,
                "runtime_zone": runtime_zone,
            }

            anchors = [pecs_id]
            if class_name:
                anchors.append(f"{pecs_id}.{class_name}")
            if method_name:
                anchors.append(f"{pecs_id}.{method_name}")
            for runtime_anchor in sorted(runtime_anchor_ids):
                anchors.append(runtime_anchor)
                self.runtime_locality_payload[runtime_anchor] = {
                    "file": str(path.relative_to(self.workspace_root)),
                    "class": class_name,
                    "method": method_name,
                    "runtime_zone": runtime_zone,
                }

            self.runtime_session.locality_index.register_object_locality(
                object_id, anchors
            )
            self.runtime_session.locality_index.runtime_locality[path_id] = anchors
            self.runtime_session.locality_index.ownership_locality[object_id] = anchors
            self.runtime_session.execution_index.register_execution_path(
                path_id, anchors
            )
            self.runtime_session.execution_index.register_execution_chain(
                f"{path_id}.chain", anchors
            )
            self.runtime_session.graph_index.register_node(
                object_id,
                {
                    "object_id": object_id,
                    "path": str(path.relative_to(self.workspace_root)),
                    "runtime_zone": runtime_zone,
                },
            )
            self.runtime_session.graph_index.register_zone(runtime_zone, [object_id])
            self.runtime_session.topology_retriever.ownership_index.register_ownership_locality(
                object_id,
                anchors,
            )
            self.runtime_session.active_objects.add(object_id)
            self.runtime_session.active_paths.add(path_id)

            for runtime_anchor in sorted(runtime_anchor_ids):
                self.runtime_session.locality_index.register_object_locality(
                    runtime_anchor,
                    [pecs_id],
                )
                self.runtime_session.locality_index.runtime_locality[runtime_anchor] = [pecs_id]
                self.runtime_session.locality_index.ownership_locality[runtime_anchor] = [pecs_id]
                self.runtime_session.topology_retriever.ownership_index.register_ownership_locality(
                    runtime_anchor,
                    [pecs_id],
                )
                self.runtime_session.active_objects.add(runtime_anchor)

            qaction_count = 0
            qaction_ownership_count = 0
            signal_slot_count = 0
            dialog_launch_count = 0
            subprocess_launch_count = 0

            for edge in edges:
                if edge["type"] == "qaction_register":
                    qaction_count += 1
                elif edge["type"] == "qaction_ownership":
                    qaction_ownership_count += 1
                elif edge["type"] == "signal_slot":
                    signal_slot_count += 1
                elif edge["type"] == "dialog_launch":
                    dialog_launch_count += 1
                elif edge["type"] == "subprocess_launch":
                    subprocess_launch_count += 1

                key = (edge["from"], edge["to"], edge["type"])
                if key in edge_seen:
                    continue
                edge_seen.add(key)
                self.runtime_topology_edges.append(edge)

            if qaction_count or qaction_ownership_count or signal_slot_count or dialog_launch_count or subprocess_launch_count:
                self._emit_runtime_telemetry(
                    subsystem="RUNTIME_REGISTRATION",
                    event="qaction_ownership_reconstructed",
                    payload={
                        "qaction_register_count": qaction_count,
                        "qaction_ownership_count": qaction_ownership_count,
                        "signal_slot_count": signal_slot_count,
                        "dialog_launch_count": dialog_launch_count,
                        "subprocess_launch_count": subprocess_launch_count,
                        "path": str(path.relative_to(self.workspace_root)),
                    },
                )


    def _extract_runtime_edges(self, path: Path) -> List[Dict[str, str]]:
        edges: List[Dict[str, str]] = []
        source_id = self._pecs_id_from_path(path)

        for target in self._extract_local_import_targets(path):
            edges.append(
                {
                    "from": source_id,
                    "to": self._pecs_id_from_path(target),
                    "type": "import",
                }
            )

        source = ""
        try:
            source = path.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(source)
        except Exception:
            return edges

        qaction_factories = self._discover_qaction_factories(tree)
        qaction_vars: Set[str] = set()
        qshortcut_vars: Set[str] = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                names = [self._extract_name(target) for target in node.targets]
                values = [name for name in names if name]
                if not values:
                    continue

                if self._is_qaction_call(node.value):
                    for action_var in values:
                        qaction_vars.add(action_var)
                        edges.append(
                            {
                                "from": source_id,
                                "to": f"PECS_ID:action.{action_var}",
                                "type": "qaction_register",
                            }
                        )
                elif self._is_qshortcut_call(node.value):
                    for shortcut_var in values:
                        qshortcut_vars.add(shortcut_var)
                        edges.append(
                            {
                                "from": source_id,
                                "to": f"PECS_ID:shortcut.{shortcut_var}",
                                "type": "shortcut_register",
                            }
                        )
                elif self._is_action_factory_call(node.value, qaction_factories):
                    for action_var in values:
                        qaction_vars.add(action_var)
                        edges.append(
                            {
                                "from": source_id,
                                "to": f"PECS_ID:action.{action_var}",
                                "type": "qaction_factory_register",
                            }
                        )

            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                call = node.value
                if self._is_connect_call(call):
                    source_anchor = self._extract_connect_source(call.func, qaction_vars, qshortcut_vars)
                    target_anchor = self._extract_connect_target(call)
                    if source_anchor and target_anchor:
                        edges.append(
                            {
                                "from": source_anchor,
                                "to": target_anchor,
                                "type": "signal_slot",
                            }
                        )
                if self._is_qaction_ownership_call(call):
                    action_var = self._extract_action_argument(call)
                    if action_var:
                        edges.append(
                            {
                                "from": source_id,
                                "to": f"PECS_ID:action.{action_var}",
                                "type": "qaction_ownership",
                            }
                        )
                if self._is_shortcut_ownership_call(call):
                    shortcut_var = self._extract_action_argument(call)
                    if shortcut_var:
                        edges.append(
                            {
                                "from": source_id,
                                "to": f"PECS_ID:shortcut.{shortcut_var}",
                                "type": "shortcut_ownership",
                            }
                        )

        # Preserve legacy regex extraction for narrow compatibility while adding broader AST capture.
        for action_var in re.findall(r"\b(\w+)\s*=\s*QAction\s*\(", source):
            if f"PECS_ID:action.{action_var}" not in {edge["to"] for edge in edges if edge["type"] == "qaction_register"}:
                edges.append(
                    {
                        "from": source_id,
                        "to": f"PECS_ID:action.{action_var}",
                        "type": "qaction_register",
                    }
                )

        for action_var, method_name in re.findall(
            r"\b(\w+)\.triggered\.connect\(\s*self\.(\w+)\s*\)",
            source,
        ):
            target_id = f"{source_id}.{method_name}"
            if {
                "from": f"PECS_ID:action.{action_var}",
                "to": target_id,
                "type": "signal_slot",
            } not in edges:
                edges.append(
                    {
                        "from": f"PECS_ID:action.{action_var}",
                        "to": target_id,
                        "type": "signal_slot",
                    }
                )

        for method_name in re.findall(
            r"\b(?:open|launch|show)_([A-Za-z_][\w]*)\s*\(", source
        ):
            target_id = f"PECS_ID:dialog.{method_name}"
            edges.append(
                {
                    "from": source_id,
                    "to": target_id,
                    "type": "dialog_launch",
                }
            )

        for _ in re.findall(r"\bsubprocess\.(?:run|Popen)\s*\(", source):
            target_id = "PECS_ID:subprocess.launch"
            edges.append(
                {
                    "from": source_id,
                    "to": target_id,
                    "type": "subprocess_launch",
                }
            )

        return edges

    def _runtime_anchor_ids_from_edges(
        self,
        path: Path,
        edges: List[Dict[str, str]],
    ) -> Set[str]:
        anchors: Set[str] = set()
        source_id = self._pecs_id_from_path(path)
        for edge in edges:
            for direction in ("from", "to"):
                anchor = str(edge.get(direction, "") or "")
                if not anchor or anchor == source_id:
                    continue
                if self._is_runtime_interaction_anchor(anchor):
                    anchors.add(anchor)
        return anchors

    def _is_runtime_interaction_anchor(self, anchor: str) -> bool:
        return any(
            anchor.startswith(prefix)
            for prefix in (
                "PECS_ID:action.",
                "PECS_ID:shortcut.",
                "PECS_ID:callback.",
                "PECS_ID:dialog.",
                "PECS_ID:signal.",
            )
        )

    def _discover_qaction_factories(self, tree: ast.AST) -> Set[str]:
        factories: Set[str] = set()

        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue
            returns_qaction = False
            for child in ast.walk(node):
                if isinstance(child, ast.Call) and self._is_qaction_call(child):
                    returns_qaction = True
                    break
            if returns_qaction:
                factories.add(node.name)
        return factories

    def _extract_name(self, node: ast.AST) -> Optional[str]:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            value = self._extract_name(node.value)
            if value:
                return f"{value}.{node.attr}"
            return node.attr
        return None

    def _is_qaction_call(self, node: ast.AST) -> bool:
        if not isinstance(node, ast.Call):
            return False
        func = node.func
        if isinstance(func, ast.Name):
            return func.id == "QAction"
        if isinstance(func, ast.Attribute):
            return func.attr == "QAction"
        return False

    def _is_qshortcut_call(self, node: ast.AST) -> bool:
        if not isinstance(node, ast.Call):
            return False
        func = node.func
        if isinstance(func, ast.Name):
            return func.id == "QShortcut"
        if isinstance(func, ast.Attribute):
            return func.attr == "QShortcut"
        return False

    def _is_action_factory_call(self, node: ast.AST, factories: Set[str]) -> bool:
        if not isinstance(node, ast.Call):
            return False
        func = node.func
        if isinstance(func, ast.Name) and func.id in factories:
            return True
        if isinstance(func, ast.Attribute) and func.attr in factories:
            return True
        return False

    def _is_connect_call(self, call: ast.Call) -> bool:
        if not isinstance(call, ast.Call):
            return False
        if isinstance(call.func, ast.Attribute):
            return call.func.attr == "connect"
        return False

    def _extract_connect_source(
        self, func: ast.AST, qaction_vars: Set[str], qshortcut_vars: Set[str]
    ) -> Optional[str]:
        if not isinstance(func, ast.Attribute):
            return None

        if func.attr != "connect":
            return None

        signal_object = func.value
        if isinstance(signal_object, ast.Attribute):
            base = self._extract_name(signal_object.value)
            if base:
                if base in qshortcut_vars:
                    return f"PECS_ID:shortcut.{base}"
                if base in qaction_vars:
                    return f"PECS_ID:action.{base}"
                return f"PECS_ID:{signal_object.attr}.{base}"
        if isinstance(signal_object, ast.Name):
            base = signal_object.id
            if base in qshortcut_vars:
                return f"PECS_ID:shortcut.{base}"
            if base in qaction_vars:
                return f"PECS_ID:action.{base}"
            return f"PECS_ID:signal.{base}"
        return None

    def _extract_connect_target(self, call: ast.Call) -> Optional[str]:
        if not call.args:
            return None
        target = call.args[0]
        if isinstance(target, ast.Name):
            return f"PECS_ID:callback.{target.id}"
        if isinstance(target, ast.Attribute):
            name = self._extract_name(target)
            return f"PECS_ID:callback.{name.replace('.', '_')}"
        if isinstance(target, ast.Lambda):
            return f"PECS_ID:callback.lambda.{target.lineno}"
        if isinstance(target, ast.Call):
            if self._is_partial_call(target):
                return self._extract_partial_callable(target)
            return self._extract_connect_target(target)
        return None

    def _is_partial_call(self, node: ast.Call) -> bool:
        if isinstance(node.func, ast.Name) and node.func.id == "partial":
            return True
        if isinstance(node.func, ast.Attribute) and node.func.attr == "partial":
            return True
        return False

    def _extract_partial_callable(self, node: ast.Call) -> Optional[str]:
        if not node.args:
            return None
        target = node.args[0]
        if isinstance(target, ast.Name):
            return f"PECS_ID:callback.partial.{target.id}"
        if isinstance(target, ast.Attribute):
            name = self._extract_name(target)
            return f"PECS_ID:callback.partial.{name.replace('.', '_')}"
        return None

    def _is_qaction_ownership_call(self, call: ast.Call) -> bool:
        if isinstance(call.func, ast.Attribute):
            if call.func.attr in {"addAction", "setDefaultAction", "registerAction", "register_action"}:
                return True
        if isinstance(call.func, ast.Name):
            if call.func.id in {"registerAction", "register_action"}:
                return True
        return False

    def _is_shortcut_ownership_call(self, call: ast.Call) -> bool:
        if isinstance(call.func, ast.Attribute):
            return call.func.attr in {"setShortcut", "registerShortcut", "addShortcut"}
        if isinstance(call.func, ast.Name):
            return call.func.id in {"setShortcut", "registerShortcut", "addShortcut"}
        return False

    def _extract_action_argument(self, call: ast.Call) -> Optional[str]:
        if not call.args:
            return None
        arg = call.args[0]
        if isinstance(arg, ast.Name):
            return arg.id
        if isinstance(arg, ast.Attribute):
            return self._extract_name(arg)
        return None

    def _extract_symbol_metadata(self, path: Path) -> Tuple[str, str]:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
        except Exception:
            return "", ""

        class_name = ""
        method_name = ""

        for node in ast.walk(tree):
            if not class_name and isinstance(node, ast.ClassDef):
                class_name = node.name
            if not method_name and isinstance(node, ast.FunctionDef):
                method_name = node.name
            if class_name and method_name:
                break

        return class_name, method_name

    def _runtime_zone_for_path(self, path: Path) -> str:
        rel = str(path.relative_to(self.workspace_root)).lower()
        if "dock" in rel:
            return "dock_pipeline"
        if "notes" in rel:
            return "notes_pipeline"
        if "search" in rel or "find" in rel:
            return "search_pipeline"
        if "monitor" in rel:
            return "monitor_pipeline"
        if "overlay" in rel:
            return "overlay_pipeline"
        if "dialog" in rel:
            return "dialog_pipeline"
        if "viewer" in rel:
            return "viewer_pipeline"
        if "qaction" in rel or "toolbar" in rel or "menu" in rel:
            return "action_pipeline"
        if "subprocess" in rel:
            return "subprocess_pipeline"
        if "dispatch" in rel:
            return "dispatch_pipeline"
        if "runtime" in rel:
            return "runtime_pipeline"
        return "general_runtime"

    def _infer_active_focus_from_chat(self) -> Dict[str, object]:
        payload: Dict[str, object] = {
            "current_issue": "",
            "active_topology_zone": "general_runtime",
            "dissatisfaction_signals": [],
            "rejected_edits": [],
            "focus_terms": [],
            "issue_terms": [],
        }

        if not self._chat_history_path.exists():
            return payload

        try:
            chat = json.loads(self._chat_history_path.read_text(encoding="utf-8"))
        except Exception:
            return payload

        if not isinstance(chat, list) or not chat:
            return payload

        recent = chat[-30:]
        messages: List[str] = []
        for entry in recent:
            if not isinstance(entry, dict):
                continue
            text = entry.get("message", "")
            if not text and isinstance(entry.get("messages"), list):
                chunks = [
                    m.get("content", "")
                    for m in entry.get("messages", [])
                    if isinstance(m, dict)
                ]
                text = " ".join(chunk for chunk in chunks if chunk)
            if text:
                messages.append(str(text))

        if not messages:
            return payload

        payload["current_issue"] = messages[-1][:300]

        joined = " ".join(messages).lower()
        dissatisfaction = []
        for token in [
            "not working",
            "wrong",
            "error",
            "failed",
            "broken",
            "regression",
            "drift",
        ]:
            if token in joined:
                dissatisfaction.append(token)

        rejected = []
        for token in ["do not", "don't", "avoid", "revert", "not this"]:
            if token in joined:
                rejected.append(token)

        zone_keywords = {
            "dock_pipeline": ["dock", "pane", "sidebar", "geometry"],
            "notes_pipeline": ["notes", "note", "sticky"],
            "search_pipeline": ["search", "find", "lookup", "popup"],
            "monitor_pipeline": ["monitor", "persist", "persistence", "watch"],
            "overlay_pipeline": ["overlay", "band", "wireframe"],
            "dialog_pipeline": ["dialog", "wizard", "popup"],
            "viewer_pipeline": ["viewer", "pdf", "canvas"],
            "action_pipeline": ["qaction", "toolbar", "menu", "shortcut"],
            "subprocess_pipeline": ["subprocess", "runner", "process"],
            "dispatch_pipeline": ["dispatch", "signal", "slot", "callback"],
        }

        zone_scores: Dict[str, int] = {}
        for zone, terms in zone_keywords.items():
            zone_scores[zone] = sum(1 for term in terms if term in joined)

        chosen_zone = "general_runtime"
        ranked_zones = sorted(zone_scores.items(), key=lambda item: (-item[1], item[0]))
        if ranked_zones and ranked_zones[0][1] > 0:
            chosen_zone = ranked_zones[0][0]

        focus_terms = re.findall(
            r"[a-zA-Z_][a-zA-Z0-9_]{3,}", payload["current_issue"].lower()
        )
        issue_terms = re.findall(
            r"[a-zA-Z_][a-zA-Z0-9_]{2,}", payload["current_issue"].lower()
        )

        compact_issue_terms: List[str] = []
        for term in issue_terms:
            if len(compact_issue_terms) >= 10:
                break
            if term not in compact_issue_terms:
                compact_issue_terms.append(term)

        payload["active_topology_zone"] = chosen_zone
        payload["dissatisfaction_signals"] = dissatisfaction
        payload["rejected_edits"] = rejected
        payload["focus_terms"] = sorted(set(focus_terms))[:16]
        payload["issue_terms"] = compact_issue_terms
        return payload

    def _infer_locality_activation(
        self,
        focus: Dict[str, object],
    ) -> Dict[str, object]:
        issue = str(focus.get("current_issue", ""))
        edited_files = [
            str(path.relative_to(self.workspace_root))
            for path in sorted(self.runtime_reachable_files)
            if path.suffix == ".py"
        ]
        dissatisfaction = focus.get("dissatisfaction_signals", [])
        active_zone = str(focus.get("active_topology_zone", "general_runtime"))
        historical_fix_locality = self.runtime_session.session_metadata.get(
            "recent_fix_locality", []
        )
        current_session_objects = sorted(self.runtime_session.active_objects)
        activation = self.locality_activation_engine.infer_locality(
            current_issue=issue,
            edited_files=edited_files,
            dissatisfaction_signals=dissatisfaction,
            active_topology_zone=active_zone,
            historical_fix_locality=historical_fix_locality,
            current_session_objects=current_session_objects,
        )
        self.edge_reinforcement.reset()
        self.edge_reinforcement.reinforce_edges(activation.get("observed_edges", []))
        return activation

    def _on_activation_update(self) -> None:
        if not self.runtime_locality_payload:
            self._log_continuity(
                "projection_skipped",
                {"reason": "runtime_locality_payload_missing"},
            )
            return

        self._log_activity(
            "runtime_activation_detected",
            {
                "event_path": str(
                    self.runtime_activation_logger.event_path.relative_to(
                        self.workspace_root
                    )
                ),
            },
        )
        self._emit_runtime_telemetry(
            subsystem="LOCALITY_AUTHORITY",
            event="runtime_activation_detected",
            payload={
                "event_path": str(
                    self.runtime_activation_logger.event_path.relative_to(
                        self.workspace_root
                    )
                ),
            },
        )

        focus = self._infer_active_focus_from_chat()
        activation = self._infer_locality_activation(focus)
        compact_bundle = self._build_compact_bundle(focus, activation)
        active_context = self._build_active_context_payload(
            focus, compact_bundle, activation
        )
        self._write_json("compact_bundle.json", compact_bundle)
        self._write_json("active_context.json", active_context)
        self._log_continuity(
            "projection_refresh_started",
            {"trigger": "runtime_activation"},
        )
        self._log_continuity(
            "compact_bundle_refreshed",
            {"context_count": len(compact_bundle.get("bundle", []))},
        )
        self._log_continuity(
            "active_context_refreshed",
            {"activated_objects": len(active_context.get("activated_objects", []))},
        )
        self._log_continuity(
            "projection_refresh_completed",
            {"trigger": "runtime_activation"},
        )
        self._run_continuity_refresh(
            trigger="runtime_activation",
            reason="runtime activation update",
        )

    def _write_runtime_topology_snapshot(self, activation: Dict[str, object]) -> None:
        snapshot_path = self.runtime_snapshot_dir / "latest_snapshot.json"
        snapshot = {
            "workspace_root": str(self.workspace_root),
            "active_runtime_zones": activation.get("active_runtime_zones", []),
            "activated_objects": activation.get("activated_objects", []),
            "activation_confidence": activation.get("activation_confidence", {}),
            "runtime_edges": [edge for edge in self.runtime_topology_edges[:80]],
        }
        self._write_json_path(snapshot_path, snapshot)

    def _should_run_continuity_refresh(self) -> bool:
        now = time.time()
        if self._last_continuity_refresh_timestamp is None:
            return True
        return (
            now - self._last_continuity_refresh_timestamp
            >= float(self.continuity_refresh_throttle_seconds)
        )

    def _run_continuity_refresh(self, trigger: str, reason: str) -> None:
        if not self.runtime_locality_payload:
            self._log_continuity(
                "projection_skipped",
                {"reason": "runtime_locality_payload_missing", "trigger": trigger},
            )
            return

        if not self._should_run_continuity_refresh():
            self._log_continuity(
                "projection_skipped",
                {"reason": "throttled", "trigger": trigger},
            )
            return

        self._log_activity(
            "continuity_refresh_started",
            {"trigger": trigger, "reason": reason},
        )
        self._emit_runtime_telemetry(
            subsystem="CONTINUITY",
            event="continuity_refresh_started",
            payload={"trigger": trigger, "reason": reason},
        )
        LOG.info(
            "Starting continuity refresh: trigger=%s reason=%s",
            trigger,
            reason,
        )

        refresh_state = {
            "trigger": trigger,
            "reason": reason,
            "started_at": time.time(),
            "status": "pending",
        }
        self._write_json("continuity_refresh_state.json", refresh_state)

        try:
            self._execute_bridge_refresh()
            self._last_continuity_refresh_timestamp = time.time()
            self._last_continuity_refresh_status = "success"
            refresh_state["status"] = "success"
            refresh_state["completed_at"] = self._last_continuity_refresh_timestamp
            self._log_activity(
                "continuity_refresh_completed",
                {"trigger": trigger, "status": "success"},
            )
            self._emit_runtime_telemetry(
                subsystem="CONTINUITY",
                event="continuity_refresh_completed",
                payload={"trigger": trigger, "status": "success"},
            )
            LOG.info("Continuity refresh succeeded: trigger=%s", trigger)
        except Exception as exc:
            self._last_continuity_refresh_timestamp = time.time()
            self._last_continuity_refresh_status = "failed"
            refresh_state["status"] = "failed"
            refresh_state["completed_at"] = self._last_continuity_refresh_timestamp
            refresh_state["error"] = str(exc)
            self._log_error(
                "bridge_execution_failed",
                {"trigger": trigger, "reason": reason, "error": str(exc)},
            )
            self._emit_runtime_telemetry(
                subsystem="CONTINUITY",
                event="bridge_execution_failed",
                payload={"trigger": trigger, "reason": reason, "error": str(exc)},
            )
            LOG.warning(
                "Continuity refresh failed: trigger=%s reason=%s error=%s",
                trigger,
                reason,
                exc,
            )
        finally:
            self._write_json("continuity_refresh_state.json", refresh_state)

    def _execute_bridge_refresh(self) -> None:
        run_bridge_sh = self.artifact_dir / "bridge" / "run_bridge.sh"
        run_bridge_py = self.artifact_dir / "bridge" / "run_bridge.py"
        if run_bridge_sh.exists() and os.access(run_bridge_sh, os.X_OK):
            cmd = [str(run_bridge_sh), str(self.workspace_root), "refresh"]
        elif run_bridge_py.exists():
            cmd = [
                sys.executable,
                str(run_bridge_py),
                "refresh",
                "--workspace",
                str(self.workspace_root),
            ]
        else:
            error_payload = {
                "workspace_root": str(self.workspace_root),
                "bridge_dir": str(self.artifact_dir / "bridge"),
            }
            self._log_error("bridge_execution_failed", error_payload)
            raise FileNotFoundError(
                "No bridge refresh command available: expected run_bridge.sh or run_bridge.py"
            )

        result = subprocess.run(
            cmd,
            cwd=str(self.workspace_root),
            capture_output=True,
            text=True,
            timeout=240,
        )

        if result.returncode != 0:
            error_details = {
                "cmd": cmd,
                "return_code": result.returncode,
                "stderr": result.stderr.strip(),
                "stdout": result.stdout.strip(),
            }
            self._log_error("bridge_execution_failed", error_details)
            LOG.warning(
                "Bridge refresh stderr: %s",
                result.stderr.strip(),
            )
            raise RuntimeError(
                f"Bridge refresh failed with exit code {result.returncode}"
            )

        self._log_activity(
            "bridge_execution_succeeded",
            {"cmd": cmd, "stdout": result.stdout.strip()},
        )
        self._emit_runtime_telemetry(
            subsystem="CONTINUITY",
            event="bridge_execution_succeeded",
            payload={"cmd": cmd, "stdout": result.stdout.strip()},
        )
        LOG.info("Bridge refresh stdout: %s", result.stdout.strip())

    def _build_compact_bundle(
        self,
        focus: Dict[str, object],
        activation: Dict[str, object],
    ) -> Dict[str, object]:
        focus_terms = set(focus.get("focus_terms", []))
        active_zone = str(focus.get("active_topology_zone", "general_runtime"))
        seeds = list(activation.get("activated_objects", []))

        self.edge_reinforcement.reset()
        self.edge_reinforcement.reinforce_edges(activation.get("observed_edges", []))
        weighted_edges = self.edge_reinforcement.weighted_edges(
            self.runtime_topology_edges
        )

        if not seeds:
            seeds = [
                pecs_id
                for pecs_id, meta in self.runtime_locality_payload.items()
                if meta.get("runtime_zone") == active_zone
            ][:6]

        selected_ids = self.locality_traversal.traverse(
            seed_ids=seeds,
            edges=weighted_edges,
            max_nodes=40,
            max_budget=120,
        )

        scored: List[Tuple[int, str, Dict[str, object]]] = []
        for pecs_id, meta in self.runtime_locality_payload.items():
            if pecs_id not in selected_ids:
                continue

            score = 0
            runtime_zone = str(meta.get("runtime_zone", ""))
            file_name = str(meta.get("file", "")).lower()

            if runtime_zone == active_zone:
                score += 5

            if pecs_id in seeds:
                score += 8

            for term in focus_terms:
                if term in file_name or term in pecs_id.lower():
                    score += 2

            scored.append((score, pecs_id, meta))

        scored.sort(key=lambda item: (-item[0], item[1]))

        selected = scored[:40]
        bundle = [
            {
                "pecs_id": pecs_id,
                "file": meta.get("file", ""),
                "runtime_zone": meta.get("runtime_zone", "general_runtime"),
                "score": score,
            }
            for score, pecs_id, meta in selected
        ]

        return {
            "bundle": bundle,
            "context_count": len(bundle),
            "active_topology_zone": active_zone,
            "issue_terms": activation.get("issue_terms", focus.get("issue_terms", [])),
            "active_runtime_zones": activation.get("active_runtime_zones", []),
            "activated_objects": activation.get("activated_objects", []),
            "activated_object_details": activation.get("activated_object_details", []),
            "active_locality_clusters": activation.get("active_locality_clusters", []),
            "activation_confidence": activation.get("activation_confidence", {}),
            "activation_reasons": activation.get("activation_reasons", {}),
            "activation_diagnostics": activation.get("activation_diagnostics", {}),
        }

    def _build_active_context_payload(
        self,
        focus: Dict[str, object],
        compact_bundle: Dict[str, object],
        activation: Dict[str, object],
    ) -> Dict[str, object]:
        bundle_ids = [
            entry.get("pecs_id", "") for entry in compact_bundle.get("bundle", [])
        ]

        neighborhood = [
            edge
            for edge in self.runtime_topology_edges
            if edge.get("from") in bundle_ids or edge.get("to") in bundle_ids
        ][:120]

        active_objects = activation.get("activated_objects", [])
        self.runtime_session.active_objects = set(active_objects)
        self.runtime_session.active_zones = set(
            activation.get("active_runtime_zones", [])
        )

        return {
            "current_issue": focus.get("current_issue", ""),
            "issue_terms": activation.get("issue_terms", focus.get("issue_terms", [])),
            "active_topology_zone": focus.get(
                "active_topology_zone", "general_runtime"
            ),
            "active_runtime_zones": activation.get("active_runtime_zones", []),
            "activated_objects": active_objects,
            "activated_object_details": activation.get("activated_object_details", []),
            "active_locality_clusters": activation.get("active_locality_clusters", []),
            "activation_confidence": activation.get("activation_confidence", {}),
            "activation_reasons": activation.get("activation_reasons", {}),
            "activation_diagnostics": activation.get("activation_diagnostics", {}),
            "recent_locality": bundle_ids[:25],
            "runtime_neighborhood": neighborhood,
            "dissatisfaction_signals": focus.get("dissatisfaction_signals", []),
            "rejected_edits": focus.get("rejected_edits", []),
        }

    def _poll_chat_history(self) -> None:
        if not self._chat_history_path.exists():
            return

        mtime = self._chat_history_path.stat().st_mtime
        if (
            self._last_chat_history_mtime is None
            or mtime > self._last_chat_history_mtime
        ):
            self._last_chat_history_mtime = mtime
            self._on_chat_history_update()

    def _ensure_chat_history_file(self) -> None:
        self._chat_history_path.parent.mkdir(parents=True, exist_ok=True)
        if not self._chat_history_path.exists():
            self._chat_history_path.write_text("[]\n", encoding="utf-8")

    def _append_system_chat_event(
        self,
        event_type: str,
        message: str,
        correlation: Optional[Dict[str, object]] = None,
    ) -> None:
        ts = time.time()
        correlation_data = correlation or {}
        event_id_seed = {
            "event_type": event_type,
            "message": message,
            "workspace_id": self.workspace_id,
            "pid": os.getpid(),
            "ts_bucket": int(ts),
        }
        event_id = hashlib.sha256(
            json.dumps(event_id_seed, sort_keys=True).encode("utf-8")
        ).hexdigest()

        payload: Dict[str, Any] = {
            "event_id": event_id,
            "event_type": event_type,
            "source": "pecs_daemon",
            "message": message,
            "workspace_root": str(self.workspace_root),
            "workspace_id": self.workspace_id,
            "continuity_namespace": self.workspace_id,
            "ts": ts,
            "correlation": correlation_data,
        }

        try:
            raw = json.loads(self._chat_history_path.read_text(encoding="utf-8"))
        except Exception:
            raw = []

        history = raw if isinstance(raw, list) else []
        if history and isinstance(history[-1], dict):
            if history[-1].get("event_id") == event_id:
                return

        history.append(payload)
        self._chat_history_path.write_text(
            json.dumps(history, indent=2, ensure_ascii=True),
            encoding="utf-8",
        )
        try:
            self._last_chat_history_mtime = self._chat_history_path.stat().st_mtime
        except OSError:
            pass

    def _on_chat_history_update(self) -> None:
        self._run_cycle_locked(
            cycle_name="chat_history_refresh",
            operation=self._on_chat_history_update_unlocked,
        )

    def _on_chat_history_update_unlocked(self) -> None:
        chat_data: object = []
        try:
            chat_data = json.loads(self._chat_history_path.read_text(encoding="utf-8"))
            self._write_json(
                "chat_history_state.json",
                {
                    "chat_entry_count": (
                        len(chat_data) if isinstance(chat_data, list) else 0
                    ),
                },
            )
        except Exception as exc:
            LOG.warning("Failed to load ai_chat_history.json: %s", exc)
            self._log_error(
                "continuity_extraction_failed",
                {"error": str(exc)},
            )

        if isinstance(chat_data, list):
            chat_entry_count = len(chat_data)
            latest_event = chat_data[-1] if chat_entry_count > 0 else {}
            latest_source = str(latest_event.get("source", "")).lower()
            latest_ts = float(latest_event.get("ts", 0) or 0)

            self._log_continuity(
                "continuity_entries_extracted",
                {
                    "chat_entry_count": chat_entry_count,
                    "latest_source": latest_source,
                },
            )

            if self._last_chat_event_ts is not None and latest_ts <= self._last_chat_event_ts:
                self._log_continuity(
                    "timestamp_gap_detected",
                    {
                        "previous_ts": self._last_chat_event_ts,
                        "latest_ts": latest_ts,
                    },
                )
            self._last_chat_event_ts = latest_ts

            if "copilot" in latest_source:
                self._log_activity(
                    "copilot_activity_detected",
                    {"source": latest_source},
                )
            if "continue" in latest_source:
                self._log_activity(
                    "continue_activity_detected",
                    {"source": latest_source},
                )

            if self.runtime_locality_payload:
                focus = self._infer_active_focus_from_chat()
                activation = self._infer_locality_activation(focus)
                compact_bundle = self._build_compact_bundle(focus, activation)
                active_context = self._build_active_context_payload(
                    focus, compact_bundle, activation
                )
                self._write_json("compact_bundle.json", compact_bundle)
                self._write_json("active_context.json", active_context)
                self._log_continuity(
                    "projection_refresh_started",
                    {"trigger": "chat_history"},
                )
                self._log_continuity(
                    "compact_bundle_refreshed",
                    {"context_count": len(compact_bundle.get("bundle", []))},
                )
                self._log_continuity(
                    "active_context_refreshed",
                    {
                        "activated_objects": len(
                            active_context.get("activated_objects", [])
                        ),
                    },
                )
                self._log_continuity(
                    "projection_refresh_completed",
                    {"trigger": "chat_history"},
                )
            else:
                self._log_continuity(
                    "projection_skipped",
                    {"reason": "runtime_locality_payload_missing"},
                )

            self._refresh_locality_authority_state(chat_data)
            self._run_continuity_refresh(
                trigger="chat_history",
                reason="AI chat history update",
            )
        else:
            self._log_continuity(
                "continuity_entries_skipped",
                {"reason": "invalid_chat_history_format"},
            )

    def _cycle_lock_path(self) -> Path:
        return self.artifact_dir / self.cycle_lock_name

    def _pid_alive(self, pid: int) -> bool:
        if pid <= 0:
            return False
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False

    def _acquire_cycle_lock(self) -> bool:
        if self._cycle_lock_owned:
            return True

        lock_path = self._cycle_lock_path()
        now = time.time()
        payload = {
            "pid": os.getpid(),
            "workspace_root": str(self.workspace_root),
            "ts": now,
        }

        def _try_create() -> bool:
            flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
            fd = os.open(str(lock_path), flags)
            try:
                os.write(fd, json.dumps(payload, sort_keys=True).encode("utf-8"))
            finally:
                os.close(fd)
            return True

        try:
            _try_create()
            self._cycle_lock_owned = True
            return True
        except FileExistsError:
            pass
        except Exception as exc:
            LOG.warning("Failed to create cycle lock %s: %s", lock_path, exc)
            return False

        try:
            stale = False
            lock_payload = {}
            if lock_path.exists():
                lock_payload = json.loads(lock_path.read_text(encoding="utf-8"))
            lock_pid = int(lock_payload.get("pid", 0) or 0)
            lock_ts = float(lock_payload.get("ts", 0.0) or 0.0)
            lock_age = max(0.0, now - lock_ts)
            stale = (not self._pid_alive(lock_pid)) or (
                lock_age > float(self.cycle_lock_ttl_seconds)
            )
            if stale:
                try:
                    lock_path.unlink(missing_ok=True)
                except TypeError:
                    if lock_path.exists():
                        lock_path.unlink()
                _try_create()
                self._cycle_lock_owned = True
                return True
        except Exception as exc:
            LOG.warning("Failed to inspect or recover cycle lock %s: %s", lock_path, exc)

        return False

    def _release_cycle_lock(self) -> None:
        if not self._cycle_lock_owned:
            return

        lock_path = self._cycle_lock_path()
        try:
            if lock_path.exists():
                lock_path.unlink()
        except OSError as exc:
            LOG.warning("Failed to release cycle lock %s: %s", lock_path, exc)
        finally:
            self._cycle_lock_owned = False

    def _validate_topology_integrity(self) -> Dict[str, object]:
        return {
            "topology_edges": len(self.runtime_topology_edges),
            "runtime_reachable_files": len(self.runtime_reachable_files),
            "topology_ok": len(self.runtime_topology_edges) >= 0,
        }

    def _validate_archaeology_consistency(self) -> Dict[str, object]:
        archaeology = self.continuity_archaeology.to_dict()
        return {
            "archaeology_ok": isinstance(archaeology, dict),
            "locality_authority_tracks": len(
                archaeology.get("locality_authority_history", {})
                if isinstance(archaeology, dict)
                else {}
            ),
        }

    def _validate_confidence_coherence(self) -> Dict[str, object]:
        active_context_path = self.artifact_dir / "active_context.json"
        activation_mean = 0.0
        if active_context_path.exists():
            try:
                data = json.loads(active_context_path.read_text(encoding="utf-8"))
                activation_mean = float(
                    data.get("activation_confidence", {}).get(
                        "mean_locality_confidence", 0.0
                    )
                    or 0.0
                )
            except Exception:
                activation_mean = 0.0

        bounded = 0.0 <= activation_mean <= 1.0
        return {
            "confidence_ok": bounded,
            "mean_locality_confidence": round(
                max(0.0, min(1.0, activation_mean)),
                3,
            ),
        }

    def _run_cycle_locked(
        self,
        cycle_name: str,
        operation,
    ) -> None:
        if not self._acquire_cycle_lock():
            LOG.info(
                "Skipped daemon cycle '%s' for workspace %s due to active lock.",
                cycle_name,
                self.workspace_root,
            )
            return

        try:
            operation()
            cycle_validation = {
                "cycle": cycle_name,
                "ts": time.time(),
                "topology_validation": self._validate_topology_integrity(),
                "archaeology_validation": self._validate_archaeology_consistency(),
                "confidence_validation": self._validate_confidence_coherence(),
            }
            self._write_json("daemon_cycle_validation.json", cycle_validation)
        finally:
            self._release_cycle_lock()

    def _count_persistence_signals(self, chat_data: List[Dict[str, object]]) -> int:
        persistence_tokens = (
            "issue persists",
            "same behavior",
            "still broken",
            "no effect",
            "nothing changed",
        )
        count = 0
        for entry in chat_data[-40:]:
            if not isinstance(entry, dict):
                continue
            message = str(entry.get("message", "") or "").lower()
            if any(token in message for token in persistence_tokens):
                count += 1
            correlation = entry.get("correlation", {})
            if isinstance(correlation, dict) and bool(
                correlation.get("unresolved_persistence", False)
            ):
                count += 1
        return count

    def _refresh_locality_authority_state(
        self,
        chat_data: List[Dict[str, object]],
    ) -> None:
        attempted_locality = ""
        runtime_authority_candidate = ""
        runtime_effect_confirmed: Optional[bool] = None
        topology_mismatch_signal = 0.0
        duplicate_shadow_signal = 0.0
        dead_path_signal = 0.0
        ownership_ambiguity = 0.0
        wrapper_only_mutation = False

        for entry in reversed(chat_data[-40:]):
            if not isinstance(entry, dict):
                continue
            correlation = entry.get("correlation", {})
            if not isinstance(correlation, dict):
                continue

            if not attempted_locality:
                attempted_locality = str(
                    correlation.get("attempted_locality", correlation.get("locality", ""))
                    or ""
                ).strip()
            if not runtime_authority_candidate:
                runtime_authority_candidate = str(
                    correlation.get("runtime_authority_candidate", "") or ""
                ).strip()
            if runtime_effect_confirmed is None and "runtime_effect_confirmed" in correlation:
                runtime_effect_confirmed = bool(correlation.get("runtime_effect_confirmed"))

            topology_mismatch_signal = max(
                topology_mismatch_signal,
                float(correlation.get("topology_mismatch_suspicion", 0.0) or 0.0),
            )
            duplicate_shadow_signal = max(
                duplicate_shadow_signal,
                float(correlation.get("duplicate_shadow_suspicion", 0.0) or 0.0),
            )
            dead_path_signal = max(
                dead_path_signal,
                float(correlation.get("dead_execution_path_suspicion", 0.0) or 0.0),
            )
            ownership_ambiguity = max(
                ownership_ambiguity,
                float(correlation.get("ownership_ambiguity", 0.0) or 0.0),
            )
            wrapper_only_mutation = wrapper_only_mutation or bool(
                correlation.get("wrapper_only_mutation", False)
            )

        if not attempted_locality:
            focus = self._infer_active_focus_from_chat()
            attempted_locality = str(focus.get("active_topology_zone", "") or "")

        if not runtime_authority_candidate:
            runtime_authority_candidate = attempted_locality

        runtime_activity_density: Optional[float] = None
        if self.runtime_reachable_files:
            runtime_activity_density = min(
                1.0,
                len(self.runtime_topology_edges) / max(1, len(self.runtime_reachable_files) * 2),
            )

        historical_retention_signal = min(1.0, len(chat_data[-40:]) / 40.0)
        persistence_signal_count = self._count_persistence_signals(chat_data)

        evidence = self.continuity_archaeology.derive_locality_authority_evidence(
            attempted_locality=attempted_locality,
            runtime_authority_candidate=runtime_authority_candidate,
            runtime_effect_confirmed=runtime_effect_confirmed,
            persistence_signal_count=persistence_signal_count,
            duplicate_lineage_count=1 if duplicate_shadow_signal > 0.5 else 0,
            wrapper_only_mutation=wrapper_only_mutation,
            ownership_ambiguity=ownership_ambiguity,
            topology_mismatch_signal=topology_mismatch_signal,
            dead_execution_path_signal=dead_path_signal,
            runtime_activity_density=runtime_activity_density,
            historical_retention_signal=historical_retention_signal,
        )
        self.continuity_archaeology.register_locality_authority_evidence(
            "active_issue",
            evidence,
        )

        continuity_dir = self.artifact_dir / "continuity"
        continuity_dir.mkdir(parents=True, exist_ok=True)
        self._write_json_path(
            continuity_dir / "locality_authority_state.json",
            {
                "schema": "pecs.locality_authority_state.v1",
                "active_issue_evidence": evidence,
                "archaeology": self.continuity_archaeology.to_dict(),
            },
        )

    def _write_json(self, name: str, data: object) -> None:
        path = self.artifact_dir / name
        self._write_json_path(path, data)

    def _canonical_json(self, data: object) -> str:
        return json.dumps(
            data, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )

    def _write_json_path(self, path: Path, data: object) -> None:
        if isinstance(data, dict) and "workspace_metadata" not in data:
            data = dict(data)
            data["workspace_metadata"] = self._workspace_metadata()

        canonical_new = self._canonical_json(data)
        if path.exists():
            try:
                existing = json.loads(path.read_text(encoding="utf-8"))
                canonical_existing = self._canonical_json(existing)
                if canonical_existing == canonical_new:
                    if path.name in {
                        "compact_bundle.json",
                        "active_context.json",
                        "topology_compact.json",
                        "locality_index.json",
                    }:
                        self._log_continuity(
                            "projection_no_changes",
                            {"path": str(path.relative_to(self.artifact_dir))},
                        )
                    return
            except Exception:
                # If existing content is invalid, rewrite once with canonical payload.
                pass

        for attempt in range(1, 4):
            try:
                path.write_text(
                    json.dumps(data, indent=2, sort_keys=True), encoding="utf-8"
                )
                return
            except OSError as exc:
                if attempt >= 3:
                    self._log_error(
                        "write_timeout",
                        {
                            "path": str(path.relative_to(self.artifact_dir)),
                            "error": str(exc),
                        },
                    )
                    LOG.warning("Failed to write PECS artifact %s: %s", path, exc)
                    break
                transient = exc.errno in {
                    errno.EAGAIN,
                    errno.EINTR,
                    errno.EWOULDBLOCK,
                    errno.ETIMEDOUT,
                }
                if transient:
                    self._log_error(
                        "write_retry",
                        {
                            "path": str(path.relative_to(self.artifact_dir)),
                            "attempt": attempt,
                            "error": str(exc),
                        },
                    )
                    time.sleep(0.25 * attempt)
                    continue
                self._log_error(
                    "projection_refresh_failed",
                    {
                        "path": str(path.relative_to(self.artifact_dir)),
                        "error": str(exc),
                    },
                )
                LOG.warning("Failed to write PECS artifact %s: %s", path, exc)
                break

    def _write_pid_file(self) -> None:
        pid_path = self.artifact_dir / self.pid_file_name
        try:
            pid_path.write_text(str(os.getpid()), encoding="utf-8")
        except OSError as exc:
            LOG.warning("Failed to write PECS daemon PID file: %s", exc)

    def _remove_pid_file(self) -> None:
        pid_path = self.artifact_dir / self.pid_file_name
        try:
            if pid_path.exists():
                pid_path.unlink()
        except OSError as exc:
            LOG.warning("Failed to remove PECS daemon PID file: %s", exc)

    def _daemon_version(self) -> str:
        try:
            return importlib.metadata.version("pecs_pro")
        except Exception:
            return "local"

    def _health_status(self) -> Dict[str, object]:
        runtime_ready = bool(self.runtime_locality_payload)
        topology_ready = bool(self.runtime_reachable_files)
        continuity_ready = runtime_ready and bool(self.runtime_topology_edges)
        issues: List[str] = []

        if not runtime_ready:
            issues.append("runtime locality payload not initialized")
        if not topology_ready:
            issues.append("runtime topology not initialized")
        if runtime_ready and not continuity_ready:
            issues.append("continuity graph incomplete")

        core_artifacts = {
            "locality_index.json": (self.artifact_dir / "locality_index.json").exists(),
            "topology_compact.json": (self.artifact_dir / "topology_compact.json").exists(),
            "compact_bundle.json": (self.artifact_dir / "compact_bundle.json").exists(),
            "active_context.json": (self.artifact_dir / "active_context.json").exists(),
            "session_context.json": (self.artifact_dir / "session_context.json").exists(),
            "daemon_state.json": (self.artifact_dir / "daemon_state.json").exists(),
        }

        status = "healthy" if not issues else "unhealthy"
        if self._start_timestamp is None:
            start_timestamp = None
            uptime_seconds = 0.0
        else:
            start_timestamp = self._start_timestamp
            uptime_seconds = max(0.0, time.time() - self._start_timestamp)

        return {
            "workspace_root": str(self.workspace_root),
            "artifact_dir": str(self.artifact_dir),
            "pid": os.getpid(),
            "daemon_version": self._daemon_version(),
            "start_time": start_timestamp,
            "last_health_update": time.time(),
            "uptime_seconds": round(uptime_seconds, 2),
            "runtime_reachable_count": len(self.runtime_reachable_files),
            "topology_edge_count": len(self.runtime_topology_edges),
            "runtime_locality_payload_count": len(self.runtime_locality_payload),
            "retrieval_ready": runtime_ready,
            "topology_ready": topology_ready,
            "continuity_ready": continuity_ready,
            "last_rebuild_timestamp": self._last_rebuild_timestamp,
            "last_continuity_refresh_timestamp": self._last_continuity_refresh_timestamp,
            "last_continuity_refresh_status": self._last_continuity_refresh_status,
            "health_issues": issues,
            "status": status,
            "core_artifacts": core_artifacts,
        }

    def _write_health_state(self) -> None:
        self._write_json(
            "daemon_health.json",
            self._health_status(),
        )

    def _is_monitored_file(self, path: Path) -> bool:
        path = path.resolve()

        if path == self._chat_history_path:
            return True

        if path == self.runtime_activation_logger.event_path:
            return True

        if path.suffix != ".py":
            return False

        if self._is_hard_excluded(path):
            return False

        return True

    def _is_hard_excluded(self, path: Path) -> bool:
        try:
            rel_parts = [
                part.lower() for part in path.relative_to(self.workspace_root).parts
            ]
        except ValueError:
            return True

        for part in rel_parts:
            if part in HARD_EXCLUDED_DIRS:
                return True

        return False

    def _pecs_id_from_path(self, path: Path) -> str:
        relative = path.relative_to(self.workspace_root)
        return f"PECS_ID:{'.'.join(relative.with_suffix('').parts)}"

    def _object_id_from_path(self, path: Path) -> str:
        relative = path.relative_to(self.workspace_root)
        return ".".join(relative.with_suffix("").parts)

    def _path_id_from_path(self, path: Path) -> str:
        return self._object_id_from_path(path)
