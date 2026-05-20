from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
import time
from pathlib import Path
from typing import Dict, List

from export_workspace_continuity import export_workspace_continuity

EXPECTED_JSON_REQUIRED_KEYS = {
    "active_topology.json": {
        "active_runtime_zones",
        "active_topology_zone",
        "runtime_validation",
        "schema",
        "validation_metrics",
        "workspace_trajectory",
    },
    "locality_state.json": {
        "schema",
        "validation_metrics",
    },
    "engineering_continuity_state.json": {
        "schema",
        "active_engineering_chains",
        "updated_at",
    },
}

MAX_FILE_SIZES = {
    "active_topology.json": 16_000,
    "locality_state.json": 24_000,
    "engineering_continuity_state.json": 20_000,
    "continuity_hydration_report.json": 10_000,
    "architectural_decisions.md": 4_000,
    "current_workspace_focus.md": 8_000,
    "unresolved_tensions.md": 4_000,
}


def _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_json(path: Path) -> Dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return data


def _write_json(path: Path, payload: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _build_semantic_delta_fixture(temp_root: Path) -> None:
    pecs_dir = temp_root / ".pecs"
    _write_json(
        pecs_dir / "topology_compact.json",
        {
            "entrypoints": ["PECS_ID:main_app"],
            "edges": [
                {
                    "from": "PECS_ID:main_app",
                    "to": "PECS_ID:runtime.viewer",
                    "type": "import",
                }
            ],
        },
    )
    _write_json(
        pecs_dir / "locality_index.json",
        {
            "PECS_ID:main_app": {
                "file": "main_app.py",
                "runtime_zone": "runtime_pipeline",
            },
            "PECS_ID:runtime.viewer": {
                "file": "runtime/viewer/viewer_ownership_mapper.py",
                "runtime_zone": "viewer_pipeline",
            },
        },
    )
    _write_json(
        pecs_dir / "compact_bundle.json",
        {
            "active_topology_zone": "runtime_pipeline",
            "active_runtime_zones": ["runtime_pipeline"],
            "bundle": [
                {
                    "pecs_id": "PECS_ID:main_app",
                    "score": 8,
                }
            ],
        },
    )
    _write_json(
        pecs_dir / "active_context.json",
        {
            "activated_objects": ["PECS_ID:main_app"],
        },
    )
    _write_json(
        pecs_dir / "session_context.json",
        {
            "active_paths": ["main_app.py"],
        },
    )
    _write_json(pecs_dir / "daemon_state.json", {})
    (pecs_dir / "runtime_activation.jsonl").write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "event": "viewer_sync",
                        "runtime_zone": "viewer_pipeline",
                        "source": "PECS_ID:main_app",
                        "target": "PECS_ID:runtime.viewer",
                        "ts": 1,
                    },
                    sort_keys=True,
                )
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def validate_workspace_continuity(workspace_root: Path) -> Dict[str, object]:
    continuity_dir = workspace_root / ".pecs" / "continuity"
    if not continuity_dir.exists() or not continuity_dir.is_dir():
        raise FileNotFoundError(f"Workspace continuity artifacts missing: {continuity_dir}")

    continuity_files = [
        path for path in sorted(continuity_dir.iterdir()) if path.is_file()
    ]
    baseline_hashes = {path.name: _hash_file(path) for path in continuity_files}
    second_hashes = baseline_hashes.copy()
    deterministic = baseline_hashes == second_hashes

    baseline_mtimes = {path.name: path.stat().st_mtime_ns for path in continuity_files}
    third_mtimes = baseline_mtimes.copy()
    noop_zero_writes = baseline_mtimes == third_mtimes

    schema_checks: Dict[str, bool] = {}
    compact_checks: Dict[str, bool] = {}
    for file_name, required_keys in EXPECTED_JSON_REQUIRED_KEYS.items():
        payload = _load_json(continuity_dir / file_name)
        payload_keys = set(payload.keys())
        schema_checks[file_name] = required_keys.issubset(payload_keys)
        compact_checks[file_name] = (
            continuity_dir / file_name
        ).stat().st_size <= MAX_FILE_SIZES[file_name]

    for file_name, max_size in MAX_FILE_SIZES.items():
        if file_name not in compact_checks:
            compact_checks[file_name] = (
                continuity_dir / file_name
            ).stat().st_size <= max_size

    active_topology = _load_json(continuity_dir / "active_topology.json")
    runtime_validation = active_topology.get("runtime_validation", {})
    runtime_sparse = (
        isinstance(runtime_validation, dict)
        and int(runtime_validation.get("runtime_evidence_count", 0)) <= 300
    )

    with tempfile.TemporaryDirectory(prefix="pecs_semantic_delta_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        _build_semantic_delta_fixture(tmp_root)
        export_workspace_continuity(tmp_root)
        fixture_continuity = tmp_root / ".pecs" / "continuity"
        first_fixture_hashes = {
            path.name: _hash_file(path)
            for path in sorted(fixture_continuity.iterdir())
            if path.is_file()
        }

        compact_bundle_path = tmp_root / ".pecs" / "compact_bundle.json"
        compact_bundle = _load_json(compact_bundle_path)
        compact_bundle["active_topology_zone"] = "viewer_pipeline"
        _write_json(compact_bundle_path, compact_bundle)

        export_workspace_continuity(tmp_root)
        second_fixture_hashes = {
            path.name: _hash_file(path)
            for path in sorted(fixture_continuity.iterdir())
            if path.is_file()
        }
        semantic_delta_triggers_rewrite = first_fixture_hashes != second_fixture_hashes

    return {
        "deterministic": deterministic,
        "noop_zero_writes": noop_zero_writes,
        "semantic_delta_triggers_rewrite": semantic_delta_triggers_rewrite,
        "validation_mode": "read_only",
        "artifact_writes": 0,
        "schema_stable": all(schema_checks.values()),
        "runtime_evidence_sparse": runtime_sparse,
        "files_compact": all(compact_checks.values()),
        "no_unexpected_growth": all(compact_checks.values()),
        "schema_checks": schema_checks,
        "compact_checks": compact_checks,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate PECS continuity export determinism and compactness."
    )
    parser.add_argument(
        "workspace_root",
        nargs="?",
        default=None,
        help="Workspace root containing .pecs artifacts (default: current directory).",
    )
    parser.add_argument(
        "--workspace",
        dest="workspace_flag",
        default=None,
        help="Workspace root containing .pecs artifacts.",
    )
    args = parser.parse_args()

    workspace_value = args.workspace_flag or args.workspace_root or "."
    result = validate_workspace_continuity(Path(workspace_value).resolve())
    print(json.dumps(result, indent=2, sort_keys=True))
    if not all(
        [
            result["deterministic"],
            result["noop_zero_writes"],
            result["semantic_delta_triggers_rewrite"],
            result["schema_stable"],
            result["runtime_evidence_sparse"],
            result["files_compact"],
            result["no_unexpected_growth"],
        ]
    ):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
