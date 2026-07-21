from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict, List


def _load_history(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []

    if not isinstance(data, list):
        return []

    return [item for item in data if isinstance(item, dict)]


def _workspace_id(workspace_root: Path) -> str:
    return hashlib.sha256(str(workspace_root.resolve()).encode("utf-8")).hexdigest()


def _safe_json_object(raw: str) -> Dict[str, Any]:
    if not raw:
        return {}
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise ValueError("JSON payload must decode to an object")
    return parsed


def _event_id(payload: Dict[str, Any]) -> str:
    preferred = str(payload.get("event_id", "") or "").strip()
    if preferred:
        return preferred

    stable = {
        "workspace_id": payload.get("workspace_id", ""),
        "source": payload.get("source", ""),
        "event_type": payload.get("event_type", "chat_event"),
        "message": payload.get("message", ""),
        "correlation": payload.get("correlation", {}),
        "ts_bucket": int(float(payload.get("ts", time.time()))),
    }
    return hashlib.sha256(
        json.dumps(stable, sort_keys=True).encode("utf-8")
    ).hexdigest()


def _normalize_payload(raw_payload: Dict[str, Any], workspace_root: Path) -> Dict[str, Any]:
    workspace_identity = _workspace_id(workspace_root)
    payload = dict(raw_payload)
    payload["workspace_root"] = str(workspace_root)
    payload["workspace_id"] = workspace_identity
    payload["continuity_namespace"] = workspace_identity
    payload["source"] = str(payload.get("source", "manual") or "manual")
    payload["event_type"] = str(payload.get("event_type", "chat_event") or "chat_event")
    payload["message"] = str(payload.get("message", "") or "")

    ts = payload.get("ts", time.time())
    try:
        payload["ts"] = float(ts)
    except Exception:
        payload["ts"] = time.time()

    correlation = payload.get("correlation", {})
    if not isinstance(correlation, dict):
        correlation = {}

    # Normalize compact observational continuity fields only.
    for key in (
        "attempted_locality",
        "runtime_authority_candidate",
        "runtime_confirmation_signal",
        "runtime_effect_confirmed",
        "unresolved_persistence",
        "regression_confirmed",
        "accepted_fix",
        "rejected_fix",
        "duplicate_shadow_suspicion",
        "dead_execution_path_suspicion",
        "topology_mismatch_suspicion",
        "ownership_ambiguity",
        "locality_authority_confidence",
        "continuity_survivability_confidence",
        "rollback_after_no_effect",
        "wrapper_only_mutation",
        "runtime_activity_density",
        "historical_retention_signal",
        "validation_outcome",
    ):
        if key in payload and key not in correlation:
            correlation[key] = payload[key]

    for key in (
        "object_ids",
        "error_ids",
        "result_ids",
    ):
        if key in payload and key not in correlation:
            correlation[key] = payload[key]

    for key in (
        "runtime_confirmation_signal",
        "runtime_effect_confirmed",
        "unresolved_persistence",
        "regression_confirmed",
        "accepted_fix",
        "rejected_fix",
        "rollback_after_no_effect",
        "wrapper_only_mutation",
    ):
        if key in correlation:
            correlation[key] = bool(correlation[key])

    for key in (
        "duplicate_shadow_suspicion",
        "dead_execution_path_suspicion",
        "topology_mismatch_suspicion",
        "ownership_ambiguity",
        "locality_authority_confidence",
        "continuity_survivability_confidence",
        "runtime_activity_density",
        "historical_retention_signal",
    ):
        if key in correlation:
            try:
                correlation[key] = float(correlation[key])
            except Exception:
                correlation.pop(key, None)

    for key in ("object_ids", "error_ids", "result_ids"):
        value = correlation.get(key, [])
        if isinstance(value, list):
            correlation[key] = sorted(
                {
                    str(item).strip()
                    for item in value
                    if str(item).strip()
                }
            )
        elif str(value).strip():
            correlation[key] = [str(value).strip()]
        elif key in correlation:
            correlation[key] = []

    if "validation_outcome" in correlation:
        outcome = str(correlation.get("validation_outcome", "") or "").strip().lower()
        allowed = {
            "accepted",
            "rejected",
            "regression",
            "unresolved",
            "observed",
            "unknown",
        }
        correlation["validation_outcome"] = outcome if outcome in allowed else "unknown"

    payload["correlation"] = correlation

    payload["event_id"] = _event_id(payload)
    return payload


def _build_payload(args: argparse.Namespace, workspace_root: Path) -> Dict[str, Any]:
    if args.payload_json:
        payload = _safe_json_object(args.payload_json)
        return _normalize_payload(payload, workspace_root)

    correlation = _safe_json_object(args.correlation_json)

    payload: Dict[str, Any] = {
        "source": args.source,
        "event_type": args.event_type,
        "message": args.message,
        "ts": time.time(),
        "correlation": correlation,
    }
    return _normalize_payload(payload, workspace_root)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Append one chat event to .pecs/ai_chat_history.json"
    )
    parser.add_argument("workspace_root", help="Workspace root path")
    parser.add_argument(
        "--source",
        default="manual",
        help="Chat source name (e.g. copilot, continue)",
    )
    parser.add_argument(
        "--message",
        default="",
        help="Simple message text for manual append mode",
    )
    parser.add_argument(
        "--event-type",
        default="chat_event",
        help="Engineering continuity event type (e.g. attempted_fix, accepted_fix)",
    )
    parser.add_argument(
        "--correlation-json",
        default="",
        help=(
            "JSON object with continuity correlation fields "
            "(object_ids/error_ids/result_ids, fix outcomes, and runtime authority signals)."
        ),
    )
    parser.add_argument(
        "--payload-json",
        default="",
        help="Full JSON payload object string to append",
    )
    args = parser.parse_args()

    workspace_root = Path(args.workspace_root).resolve()
    pecs_dir = workspace_root / ".pecs"
    pecs_dir.mkdir(parents=True, exist_ok=True)

    chat_file = pecs_dir / "ai_chat_history.json"
    history = _load_history(chat_file)
    payload = _build_payload(args, workspace_root)

    known_ids = {
        str(entry.get("event_id", ""))
        for entry in history
        if isinstance(entry, dict) and entry.get("event_id")
    }
    if payload["event_id"] in known_ids:
        print(f"Skipped duplicate chat history event: {payload['event_id']}")
        return

    history.append(payload)

    chat_file.write_text(
        json.dumps(history, indent=2, ensure_ascii=True, sort_keys=True),
        encoding="utf-8",
    )
    print(f"Appended chat history to {chat_file}")


if __name__ == "__main__":
    main()
