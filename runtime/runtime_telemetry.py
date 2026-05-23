from __future__ import annotations

import inspect
import json
import os
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class RuntimeTelemetryEmitter:
    """Thread-safe structured runtime telemetry emitter."""

    def __init__(self, workspace_root: Path) -> None:
        self.workspace_root = workspace_root.resolve()
        self.telemetry_dir = self.workspace_root / "telemetry" / "runtime_jsonl"
        self.telemetry_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        self.file_path = self.telemetry_dir / f"pecs_runtime_{timestamp}.jsonl"
        self._lock = threading.Lock()

    def emit_runtime_event(
        self,
        subsystem: str,
        event: str,
        payload: Optional[Dict[str, Any]] = None,
        file: Optional[str] = None,
        function: Optional[str] = None,
    ) -> None:
        try:
            frame = inspect.currentframe()
            caller_frame = frame.f_back if frame is not None else None
            if caller_frame is not None:
                code = caller_frame.f_code
                file = file or Path(code.co_filename).name
                function = function or code.co_name

            payload = payload or {}
            record: Dict[str, Any] = {
                "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
                "subsystem": subsystem,
                "event": event,
                "file": str(file or ""),
                "function": str(function or ""),
                "payload": payload,
            }

            line = json.dumps(record, ensure_ascii=False, sort_keys=True)
            with self._lock:
                with self.file_path.open("a", encoding="utf-8") as handle:
                    handle.write(line + "\n")
                    handle.flush()
                    try:
                        os.fsync(handle.fileno())
                    except OSError:
                        pass
        except Exception:
            # Telemetry must be non-fatal and zero-noise by default.
            return


_global_runtime_telemetry: Dict[str, RuntimeTelemetryEmitter] = {}


def get_runtime_telemetry_emitter(workspace_root: Optional[Path] = None) -> RuntimeTelemetryEmitter:
    root = Path(workspace_root or Path.cwd()).resolve()
    key = str(root)
    if key not in _global_runtime_telemetry:
        _global_runtime_telemetry[key] = RuntimeTelemetryEmitter(root)
    return _global_runtime_telemetry[key]


def emit_runtime_event(
    subsystem: str,
    event: str,
    payload: Optional[Dict[str, Any]] = None,
    file: Optional[str] = None,
    function: Optional[str] = None,
    workspace_root: Optional[Path] = None,
) -> None:
    try:
        emitter = get_runtime_telemetry_emitter(workspace_root)
        emitter.emit_runtime_event(
            subsystem=subsystem,
            event=event,
            payload=payload,
            file=file,
            function=function,
        )
    except Exception:
        return
