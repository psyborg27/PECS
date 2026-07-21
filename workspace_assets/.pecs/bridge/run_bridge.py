from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path
from typing import Optional


def _resolve_install_root() -> Optional[Path]:
    config_path = (
        Path(__file__).resolve().parent.parent / "config" / "install_root.json"
    )
    if not config_path.exists():
        return None

    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except Exception:
        return None

    install_root = data.get("install_root")
    if isinstance(install_root, str) and install_root.strip():
        return Path(install_root).resolve()
    return None


def _load_bridge_modules():
    install_root = _resolve_install_root()
    if install_root and str(install_root) not in sys.path:
        sys.path.insert(0, str(install_root))

    try:
        export_module = importlib.import_module("scripts.export_workspace_continuity")
        validate_module = importlib.import_module("scripts.validate_workspace_continuity")
        return export_module.export_workspace_continuity, validate_module.validate_workspace_continuity
    except Exception as exc:
        raise RuntimeError(
            "Unable to import PECS bridge runtime modules. "
            f"Resolved install_root={install_root!s}. "
            f"sys.path={sys.path}"
        ) from exc


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Workspace-local PECS deterministic continuity bridge"
    )
    parser.add_argument(
        "command",
        choices=["refresh", "validate"],
        help="Bridge command to run",
    )
    parser.add_argument(
        "workspace_root",
        nargs="?",
        default=None,
        help="Workspace root path (default: current directory).",
    )
    parser.add_argument(
        "--workspace",
        dest="workspace_flag",
        default=None,
        help="Workspace root path.",
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
    args = parser.parse_args()

    workspace_value = args.workspace_flag or args.workspace_root or "."
    workspace_root = Path(workspace_value).resolve()

    export_workspace_continuity, validate_workspace_continuity = _load_bridge_modules()

    if args.command == "refresh":
        result = export_workspace_continuity(workspace_root)
    else:
        result = validate_workspace_continuity(workspace_root)

    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
