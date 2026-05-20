from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List

try:
    from continuity.confidence.confidence_model import ConfidenceModel
except Exception:  # pragma: no cover - optional portability fallback
    ConfidenceModel = None

try:
    from topology.archaeology.continuity_archaeology import ContinuityArchaeology
except Exception:  # pragma: no cover - optional portability fallback
    ContinuityArchaeology = None

ARTIFACT_DIR = ".pecs"
CONTINUITY_DIR = ".pecs/continuity"
ACTIVE_TOPOLOGY_SCHEMA = "pecs.active_topology.v1"
LOCALITY_STATE_SCHEMA = "pecs.locality_state.v1"
ENGINEERING_CONTINUITY_SCHEMA = "pecs.engineering_continuity.v1"
CONTINUITY_HYDRATION_REPORT_SCHEMA = "pecs.continuity_hydration_report.v1"
PRESERVE_EMPTY_KEYS = {
    "schema",
    "disclaimer",
    "active_topology_zone",
    "active_runtime_zones",
    "runtime_validation",
    "validation_metrics",
}

GENERATED_DISCLAIMER = (
    "THIS FILE IS GENERATED CONTINUITY INFRASTRUCTURE. "
    "DO NOT EDIT. DO NOT PATCH. "
    "ENGINEERING TRUTH EXISTS ONLY IN WORKSPACE RUNTIME MODULES."
)


def _safe_ratio(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(numerator / denominator, 3)


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default
    return data


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []

    records: List[Dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        try:
            record = json.loads(stripped)
            if isinstance(record, dict):
                records.append(record)
        except Exception:
            continue
    return records


def _cluster_paths(paths: Iterable[str]) -> List[Dict[str, Any]]:
    cluster_counts: Counter[str] = Counter()
    for raw in paths:
        path = str(raw).replace("\\", "/").strip()
        if not path:
            continue
        parts = [p for p in path.split("/") if p]
        if not parts:
            continue
        if len(parts) >= 2:
            cluster = "/".join(parts[:2])
        else:
            cluster = parts[0]
        cluster_counts[cluster] += 1

    return [
        {"cluster": key, "count": cluster_counts[key]}
        for key in sorted(cluster_counts, key=lambda k: (-cluster_counts[k], k))
    ]


def _build_locality_file_map(locality_index: Dict[str, Any]) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    for object_id, value in locality_index.items():
        if isinstance(value, dict):
            file_path = value.get("file")
            if isinstance(file_path, str) and file_path.strip():
                mapping[str(object_id)] = file_path.strip()
    return mapping


def _normalize_runtime_events(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    normalized: List[Dict[str, Any]] = []
    for event in events:
        if not isinstance(event, dict):
            continue
        normalized.append(
            {
                "event": str(event.get("event", "")).strip(),
                "runtime_zone": str(event.get("runtime_zone", "")).strip(),
                "source": str(event.get("source", "")).strip(),
                "target": str(event.get("target", "")).strip(),
                "ts": (
                    int(event.get("ts", 0)) if str(event.get("ts", "")).isdigit() else 0
                ),
            }
        )
    normalized.sort(
        key=lambda item: (
            item["ts"],
            item["event"],
            item["source"],
            item["target"],
            item["runtime_zone"],
        )
    )
    return normalized


def _resolve_runtime_touched_files(
    events: List[Dict[str, Any]],
    locality_file_map: Dict[str, str],
) -> List[Dict[str, Any]]:
    touched: Counter[str] = Counter()

    def _resolve_id(maybe_id: Any) -> str:
        value = str(maybe_id or "").strip()
        if not value:
            return ""
        if value in locality_file_map:
            return locality_file_map[value]

        # Prefix fallback for anchors like PECS_ID:file.symbol.method
        for key, file_path in locality_file_map.items():
            if value.startswith(key + "."):
                return file_path
        return ""

    for event in events:
        src_file = _resolve_id(event.get("source"))
        tgt_file = _resolve_id(event.get("target"))
        if src_file:
            touched[src_file] += 1
        if tgt_file:
            touched[tgt_file] += 1

    return [
        {"file": file_path, "touch_count": touched[file_path]}
        for file_path in sorted(touched, key=lambda p: (-touched[p], p))
    ]


def _normalize_chat_history_entries(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    normalized: List[Dict[str, Any]] = []
    persistence_tokens = (
        "issue persists",
        "same behavior",
        "still broken",
        "no effect",
        "nothing changed",
    )
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        message = str(entry.get("message", "") or "").strip()
        event_type = str(entry.get("event_type", "") or "").strip().lower()
        if not message and not event_type:
            continue
        source = str(entry.get("source", "") or "").strip().lower()
        ts = entry.get("ts", 0)
        try:
            ts = float(ts)
        except Exception:
            ts = 0.0
        correlation = entry.get("correlation", {})
        if not isinstance(correlation, dict):
            correlation = {}

        object_ids = correlation.get("object_ids", [])
        error_ids = correlation.get("error_ids", [])
        result_ids = correlation.get("result_ids", [])

        if not isinstance(object_ids, list):
            object_ids = [object_ids] if str(object_ids).strip() else []
        if not isinstance(error_ids, list):
            error_ids = [error_ids] if str(error_ids).strip() else []
        if not isinstance(result_ids, list):
            result_ids = [result_ids] if str(result_ids).strip() else []

        object_ids = sorted({str(item).strip() for item in object_ids if str(item).strip()})
        error_ids = sorted({str(item).strip() for item in error_ids if str(item).strip()})
        result_ids = sorted({str(item).strip() for item in result_ids if str(item).strip()})

        validation_outcome = str(correlation.get("validation_outcome", "") or "").strip().lower()
        if validation_outcome not in {"accepted", "rejected", "regression", "unresolved", "observed", "unknown"}:
            validation_outcome = "unknown"

        lowered_message = message.lower()
        persistence_signal = any(token in lowered_message for token in persistence_tokens)
        normalized.append(
            {
                "source": source,
                "message": message,
                "event_type": event_type,
                "correlation": correlation,
                "ts": ts,
                "persistence_signal": persistence_signal,
                "object_ids": object_ids,
                "error_ids": error_ids,
                "result_ids": result_ids,
                "validation_outcome": validation_outcome,
            }
        )
    normalized.sort(key=lambda item: (item["ts"], item["source"], item["message"]))
    return normalized


def _infer_engineering_continuity_topic(message: str) -> str:
    text = message.lower()
    if any(keyword in text for keyword in ["continuity", "hydrate", "hydration"]):
        return "continuity_hydration"
    if any(keyword in text for keyword in ["install", "bootstrap", "rebind", "bind", "asset"]):
        return "workspace_installation"
    if any(keyword in text for keyword in ["daemon", "bridge", "task", "launch"]):
        return "workspace_daemon_bridge"
    if any(keyword in text for keyword in ["copilot", "continue", "chat"]):
        return "ai_interaction_ingestion"
    return "workspace_onboarding"


def _infer_engineering_continuity_locality(message: str) -> str:
    text = message.lower()
    if any(keyword in text for keyword in ["daemon", "bridge", "launch", "startup"]):
        return "workspace_bridge_cli.py"
    if any(keyword in text for keyword in ["install", "bootstrap", "register", "bind", "rebind", "assets"]):
        return "install_workspace_integration.py"
    if any(keyword in text for keyword in ["continuity", "hydrate", "hydration", "locality", "topology"]):
        return "scripts/export_workspace_continuity.py"
    if any(keyword in text for keyword in ["copilot", "continue", "chat"]):
        return "append_ai_chat_history.py"
    return "install_workspace_integration.py"


def _build_engineering_continuity_state(workspace_root: Path) -> Dict[str, Any]:
    history_path = workspace_root / ".pecs" / "ai_chat_history.json"
    entries = _normalize_chat_history_entries(_read_json(history_path, []))
    if not entries:
        return {
            "schema": ENGINEERING_CONTINUITY_SCHEMA,
            "active_engineering_chains": [],
            "updated_at": "",
        }

    class _FallbackArchaeology:
        @staticmethod
        def _clamp(value: float) -> float:
            return max(0.0, min(1.0, value))

        def __init__(self) -> None:
            self.locality_authority_history: Dict[str, List[Dict[str, object]]] = {}

        def derive_locality_authority_evidence(self, **kwargs) -> Dict[str, object]:
            attempted = str(kwargs.get("attempted_locality", "") or "")
            candidate = kwargs.get("runtime_authority_candidate", None)
            runtime_effect = kwargs.get("runtime_effect_confirmed", None)
            persistence_count = int(kwargs.get("persistence_signal_count", 0) or 0)
            unresolved = bool(persistence_count > 0 and runtime_effect is not True)
            mismatch = bool(attempted and candidate and attempted != candidate)

            duplicate_shadow = self._clamp(
                0.18 * float(kwargs.get("duplicate_lineage_count", 0) or 0)
                + 0.08 * persistence_count
                + (0.22 if mismatch else 0.0)
            )
            dead_path = self._clamp(float(kwargs.get("dead_execution_path_signal", 0.0) or 0.0))
            mismatch_score = self._clamp(
                float(kwargs.get("topology_mismatch_signal", 0.0) or 0.0)
                + (0.25 if mismatch else 0.0)
            )

            authority = self._clamp(
                0.55
                + (0.18 if runtime_effect is True else 0.0)
                - (0.2 if unresolved else 0.0)
                - duplicate_shadow * 0.18
                - mismatch_score * 0.24
            )
            survivability = self._clamp(
                0.5
                + (0.15 if runtime_effect is True else 0.0)
                - (0.2 if unresolved else 0.0)
                - dead_path * 0.18
            )

            return {
                "attempted_locality": attempted,
                "runtime_authority_candidate": candidate,
                "runtime_effect_confirmed": runtime_effect,
                "unresolved_persistence": unresolved,
                "duplicate_shadow_suspicion": round(duplicate_shadow, 3),
                "dead_execution_path_suspicion": round(dead_path, 3),
                "wrapper_only_mutation": bool(kwargs.get("wrapper_only_mutation", False)),
                "topology_mismatch_suspicion": round(mismatch_score, 3),
                "ownership_ambiguity": round(
                    self._clamp(float(kwargs.get("ownership_ambiguity", 0.0) or 0.0)),
                    3,
                ),
                "locality_authority_confidence": round(authority, 3),
                "continuity_survivability_confidence": round(survivability, 3),
                "runtime_activity_density": kwargs.get("runtime_activity_density", None),
                "historical_retention_signal": kwargs.get("historical_retention_signal", None),
                "persistence_signal_count": persistence_count,
            }

        def register_locality_authority_evidence(self, issue_id: str, evidence: Dict[str, object]) -> None:
            self.locality_authority_history.setdefault(issue_id, []).append(dict(evidence))

        def to_dict(self) -> Dict[str, object]:
            return {"locality_authority_history": self.locality_authority_history}

    class _FallbackConfidenceModel:
        @staticmethod
        def _clamp(value: float) -> float:
            return max(0.0, min(1.0, value))

        def derive_locality_authority_confidence(self, **kwargs) -> Dict[str, float]:
            locality = self._clamp(float(kwargs.get("locality_authority_confidence", 0.0) or 0.0))
            duplicate_shadow = self._clamp(float(kwargs.get("duplicate_shadow_suspicion", 0.0) or 0.0))
            runtime_confirmation = self._clamp(float(kwargs.get("runtime_confirmation_weight", 0.0) or 0.0))
            survivability = self._clamp(float(kwargs.get("continuity_survivability_confidence", 0.0) or 0.0))
            mismatch = self._clamp(float(kwargs.get("topology_mismatch_weight", 0.0) or 0.0))
            score = self._clamp(
                locality * 0.42
                + runtime_confirmation * 0.22
                + survivability * 0.28
                - duplicate_shadow * 0.16
                - mismatch * 0.18
            )
            return {
                "locality_authority_confidence": round(score, 3),
                "duplicate_shadow_probability": round(duplicate_shadow, 3),
                "runtime_confirmation_weight": round(runtime_confirmation, 3),
                "continuity_survivability_confidence": round(survivability, 3),
                "topology_mismatch_weight": round(mismatch, 3),
            }

    archaeology = ContinuityArchaeology() if ContinuityArchaeology is not None else _FallbackArchaeology()
    confidence_model = ConfidenceModel() if ConfidenceModel is not None else _FallbackConfidenceModel()

    chains: Dict[str, Dict[str, Any]] = {}
    source_counts: Dict[str, int] = {}
    for entry in entries:
        source = str(entry.get("source", "") or "unknown").lower()
        message = str(entry.get("message", "") or "")
        correlation = entry.get("correlation", {})
        if not isinstance(correlation, dict):
            correlation = {}
        topic = _infer_engineering_continuity_topic(message)
        accepted_locality = _infer_engineering_continuity_locality(message)

        chain = chains.setdefault(
            topic,
            {
                "chain_id": f"engineering_continuity:{topic}",
                "issue": topic.replace("_", " "),
                "accepted_locality": accepted_locality,
                "rejected_locality": [],
                "accepted_followup": False,
                "continuity_strength": 0.5,
                "locality_stability": 0.65,
                "stable_engineering_owner": accepted_locality,
                "continuity_outcome": "accepted",
                "continuity_confidence": 0.0,
                "source_tags": [],
                "event_count": 0,
                "source_counts": {},
                "attempted_locality": accepted_locality,
                "runtime_authority_candidate": None,
                "runtime_effect_confirmed": None,
                "unresolved_persistence": False,
                "duplicate_shadow_suspicion": 0.0,
                "dead_execution_path_suspicion": 0.0,
                "wrapper_only_mutation": False,
                "topology_mismatch_suspicion": 0.0,
                "ownership_ambiguity": 0.0,
                "locality_authority_confidence": 0.0,
                "continuity_survivability_confidence": 0.0,
                "runtime_activity_density": None,
                "historical_retention_signal": None,
                "persistence_signal_count": 0,
                "validation_accept_count": 0,
                "validation_reject_count": 0,
                "validation_regression_count": 0,
                "validation_unresolved_count": 0,
                "object_error_links": {},
            },
        )
        chain["event_count"] = int(chain.get("event_count", 0)) + 1
        chain["source_tags"] = sorted(
            set(chain.get("source_tags", []) + [source])
        )
        chain_source_counts = chain.get("source_counts", {})
        chain_source_counts[source] = chain_source_counts.get(source, 0) + 1
        chain["source_counts"] = chain_source_counts
        chain["accepted_followup"] = chain["event_count"] > 1
        chain["continuity_strength"] = min(
            0.9,
            0.5 + 0.06 * chain["event_count"] + 0.1 * len(chain["source_tags"]),
        )
        chain["locality_stability"] = min(
            0.92, 0.60 + 0.05 * chain["event_count"]
        )
        chain["continuity_confidence"] = round(
            min(1.0, chain["continuity_strength"] + 0.08), 3
        )

        attempted_locality = str(
            correlation.get("attempted_locality", correlation.get("locality", accepted_locality))
            or accepted_locality
        )
        runtime_authority_candidate = str(
            correlation.get("runtime_authority_candidate", accepted_locality) or accepted_locality
        )

        runtime_effect_confirmed_raw = correlation.get("runtime_effect_confirmed", None)
        if runtime_effect_confirmed_raw is None:
            runtime_effect_confirmed_raw = correlation.get("runtime_confirmation_signal", None)
        runtime_effect_confirmed = (
            bool(runtime_effect_confirmed_raw)
            if runtime_effect_confirmed_raw is not None
            else None
        )

        if bool(entry.get("persistence_signal", False)):
            chain["persistence_signal_count"] = int(chain.get("persistence_signal_count", 0)) + 1

        if bool(correlation.get("unresolved_persistence", False)):
            chain["persistence_signal_count"] = int(chain.get("persistence_signal_count", 0)) + 1

        validation_outcome = str(entry.get("validation_outcome", "unknown") or "unknown")
        if validation_outcome == "accepted":
            chain["validation_accept_count"] = int(chain.get("validation_accept_count", 0)) + 1
        elif validation_outcome == "rejected":
            chain["validation_reject_count"] = int(chain.get("validation_reject_count", 0)) + 1
        elif validation_outcome == "regression":
            chain["validation_regression_count"] = int(chain.get("validation_regression_count", 0)) + 1
        elif validation_outcome == "unresolved":
            chain["validation_unresolved_count"] = int(chain.get("validation_unresolved_count", 0)) + 1

        object_ids = entry.get("object_ids", []) if isinstance(entry.get("object_ids", []), list) else []
        error_ids = entry.get("error_ids", []) if isinstance(entry.get("error_ids", []), list) else []
        link_counts = chain.get("object_error_links", {}) if isinstance(chain.get("object_error_links", {}), dict) else {}
        for object_id in object_ids:
            for error_id in error_ids or ["UNSPECIFIED_ERROR"]:
                link_key = f"{object_id}::{error_id}"
                link_counts[link_key] = int(link_counts.get(link_key, 0)) + 1
        chain["object_error_links"] = link_counts

        persistence_signal_count = int(chain.get("persistence_signal_count", 0))
        duplicate_shadow = float(correlation.get("duplicate_shadow_suspicion", 0.0) or 0.0)
        dead_path = float(correlation.get("dead_execution_path_suspicion", 0.0) or 0.0)
        topology_mismatch = float(correlation.get("topology_mismatch_suspicion", 0.0) or 0.0)
        ownership_ambiguity = float(correlation.get("ownership_ambiguity", 0.0) or 0.0)
        runtime_activity_density = correlation.get("runtime_activity_density", None)
        historical_retention_signal = correlation.get("historical_retention_signal", None)
        wrapper_only_mutation = bool(correlation.get("wrapper_only_mutation", False))

        derived_evidence = archaeology.derive_locality_authority_evidence(
            attempted_locality=attempted_locality,
            runtime_authority_candidate=runtime_authority_candidate,
            runtime_effect_confirmed=runtime_effect_confirmed,
            persistence_signal_count=persistence_signal_count,
            duplicate_lineage_count=1 if duplicate_shadow > 0.5 else 0,
            wrapper_only_mutation=wrapper_only_mutation,
            ownership_ambiguity=ownership_ambiguity,
            topology_mismatch_signal=topology_mismatch,
            dead_execution_path_signal=dead_path,
            runtime_activity_density=runtime_activity_density,
            historical_retention_signal=historical_retention_signal,
        )

        derived_confidence = confidence_model.derive_locality_authority_confidence(
            locality_authority_confidence=float(
                derived_evidence.get("locality_authority_confidence", 0.0)
            ),
            duplicate_shadow_suspicion=float(
                derived_evidence.get("duplicate_shadow_suspicion", 0.0)
            ),
            runtime_confirmation_weight=(
                1.0 if runtime_effect_confirmed is True else 0.0
            ),
            continuity_survivability_confidence=float(
                derived_evidence.get("continuity_survivability_confidence", 0.0)
            ),
            topology_mismatch_weight=float(
                derived_evidence.get("topology_mismatch_suspicion", 0.0)
            ),
            dead_execution_path_suspicion=float(
                derived_evidence.get("dead_execution_path_suspicion", 0.0)
            ),
            persistence_signal_count=persistence_signal_count,
            runtime_activity_density=derived_evidence.get("runtime_activity_density", None),
        )

        chain["attempted_locality"] = attempted_locality
        chain["runtime_authority_candidate"] = runtime_authority_candidate
        chain["runtime_effect_confirmed"] = runtime_effect_confirmed
        chain["unresolved_persistence"] = bool(
            derived_evidence.get("unresolved_persistence", False)
        )
        chain["duplicate_shadow_suspicion"] = float(
            max(
                chain.get("duplicate_shadow_suspicion", 0.0),
                derived_evidence.get("duplicate_shadow_suspicion", 0.0),
            )
        )
        chain["dead_execution_path_suspicion"] = float(
            max(
                chain.get("dead_execution_path_suspicion", 0.0),
                derived_evidence.get("dead_execution_path_suspicion", 0.0),
            )
        )
        chain["wrapper_only_mutation"] = bool(
            chain.get("wrapper_only_mutation", False) or wrapper_only_mutation
        )
        chain["topology_mismatch_suspicion"] = float(
            max(
                chain.get("topology_mismatch_suspicion", 0.0),
                derived_evidence.get("topology_mismatch_suspicion", 0.0),
            )
        )
        chain["ownership_ambiguity"] = float(
            max(
                chain.get("ownership_ambiguity", 0.0),
                derived_evidence.get("ownership_ambiguity", 0.0),
            )
        )
        chain["locality_authority_confidence"] = float(
            max(
                chain.get("locality_authority_confidence", 0.0),
                derived_confidence.get("locality_authority_confidence", 0.0),
            )
        )
        chain["continuity_survivability_confidence"] = float(
            max(
                chain.get("continuity_survivability_confidence", 0.0),
                derived_confidence.get("continuity_survivability_confidence", 0.0),
            )
        )
        chain["runtime_activity_density"] = derived_evidence.get(
            "runtime_activity_density", None
        )
        chain["historical_retention_signal"] = derived_evidence.get(
            "historical_retention_signal", None
        )

        archaeology.register_locality_authority_evidence(topic, derived_evidence)

        if "continue" in source and "copilot" in chain["source_tags"]:
            chain["continuity_outcome"] = "merged_cross_client_guidance"
        elif topic == "continuity_hydration":
            chain["continuity_outcome"] = "hydrated"
        else:
            chain["continuity_outcome"] = "accepted"

        if int(chain.get("validation_regression_count", 0)) > 0:
            chain["continuity_outcome"] = "regression"
        elif int(chain.get("validation_unresolved_count", 0)) > 0 and int(chain.get("validation_accept_count", 0)) == 0:
            chain["continuity_outcome"] = "unresolved"

    chains_list = list(chains.values())
    chains_list.sort(
        key=lambda item: (-float(item.get("continuity_confidence", 0.0)), item.get("issue", ""))
    )

    return {
        "schema": ENGINEERING_CONTINUITY_SCHEMA,
        "active_engineering_chains": chains_list,
        "locality_authority_archaeology": archaeology.to_dict(),
        "updated_at": datetime.utcnow().isoformat() + "Z",
    }


def _build_continuity_hydration_report(
    workspace_root: Path, continuity_state: Dict[str, Any]
) -> Dict[str, Any]:
    chains = (
        continuity_state.get("active_engineering_chains", [])
        if isinstance(continuity_state, list) or isinstance(
            continuity_state, dict
        )
        else []
    )
    source_counts: Dict[str, int] = {}
    for chain in chains:
        if not isinstance(chain, dict):
            continue
        for source, count in (
            chain.get("source_counts", {}) if isinstance(chain.get("source_counts", {}), dict) else {}
        ).items():
            if not str(source).strip():
                continue
            source_counts[str(source)] = source_counts.get(str(source), 0) + int(count)

    return {
        "schema": CONTINUITY_HYDRATION_REPORT_SCHEMA,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "chain_count": len(chains),
        "source_counts": source_counts,
        "merged_client_count": len({source for chain in chains if isinstance(chain, dict) for source in (chain.get("source_tags", []) or [])}),
        "note": "Structured engineering continuity is derived from accepted workspace AI interaction signals only.",
    }


def _collect_hotspots(
    compact_bundle: Dict[str, Any],
    runtime_touched_files: List[Dict[str, Any]],
    active_context: Dict[str, Any],
) -> List[Dict[str, Any]]:
    hotspot_scores: Counter[str] = Counter()
    reasons: Dict[str, List[str]] = defaultdict(list)

    for entry in compact_bundle.get("bundle", []):
        if not isinstance(entry, dict):
            continue
        object_id = str(entry.get("pecs_id", "")).strip()
        score = (
            int(entry.get("score", 0)) if str(entry.get("score", "")).isdigit() else 0
        )
        if not object_id:
            continue
        hotspot_scores[object_id] += max(1, score)
        reasons[object_id].append("compact_bundle")

    for item in active_context.get("activated_objects", [])[:30]:
        object_id = str(item).strip()
        if not object_id:
            continue
        hotspot_scores[object_id] += 2
        reasons[object_id].append("runtime_activation")

    for touched in runtime_touched_files[:20]:
        file_path = str(touched.get("file", "")).strip()
        count = int(touched.get("touch_count", 0))
        if not file_path:
            continue
        synthetic_id = f"PECS_ID:{file_path.replace('/', '.').removesuffix('.py')}"
        hotspot_scores[synthetic_id] += max(1, count)
        reasons[synthetic_id].append("runtime_touched_file")

    ordered = sorted(hotspot_scores, key=lambda k: (-hotspot_scores[k], k))
    return [
        {
            "id": object_id,
            "score": hotspot_scores[object_id],
            "signals": sorted(set(reasons[object_id])),
        }
        for object_id in ordered[:20]
    ]


def _validate_runtime_topology(
    topology_compact: Dict[str, Any],
    events: List[Dict[str, Any]],
    compact_bundle: Dict[str, Any],
) -> Dict[str, Any]:
    edge_pairs = {
        (
            str(edge.get("from", "")).strip(),
            str(edge.get("to", "")).strip(),
        )
        for edge in topology_compact.get("edges", [])
        if isinstance(edge, dict)
    }

    runtime_pairs = {
        (
            str(event.get("source", "")).strip(),
            str(event.get("target", "")).strip(),
        )
        for event in events
        if isinstance(event, dict)
    }

    supported_pairs = runtime_pairs.intersection(edge_pairs)

    bundled_ids = {
        str(entry.get("pecs_id", "")).strip()
        for entry in compact_bundle.get("bundle", [])
        if isinstance(entry, dict)
    }

    activated_ids = {
        str(event.get("source", "")).strip()
        for event in events
        if isinstance(event, dict)
    }
    bundled_activated = activated_ids.intersection(bundled_ids)

    evidence_count = len(events)
    runtime_confirmation_density = _safe_ratio(len(supported_pairs), evidence_count)
    active_topology_targeting = _safe_ratio(len(bundled_activated), len(bundled_ids))

    return {
        "runtime_evidence_count": evidence_count,
        "runtime_confirmations": len(supported_pairs),
        "active_topology_targeting": active_topology_targeting,
        "runtime_confirmation_density": runtime_confirmation_density,
    }


def _build_validation_metrics(
    recent_edit_clusters: List[Dict[str, Any]],
    repeated_modifications: List[Dict[str, Any]],
    compact_bundle: Dict[str, Any],
    hotspots: List[Dict[str, Any]],
    runtime_validation: Dict[str, Any],
) -> Dict[str, float]:
    bundle_count = (
        len(compact_bundle.get("bundle", [])) if isinstance(compact_bundle, dict) else 0
    )
    hotspot_count = len(hotspots)
    cluster_count = len(recent_edit_clusters)
    repeated_count = len(repeated_modifications)

    return {
        "edit_locality_improvement": _safe_ratio(repeated_count, cluster_count),
        "active_topology_targeting": float(
            runtime_validation.get("active_topology_targeting", 0.0)
        ),
        "continuity_hotspot_identification": _safe_ratio(
            hotspot_count, max(bundle_count, hotspot_count)
        ),
        "runtime_confirmation_density": float(
            runtime_validation.get("runtime_confirmation_density", 0.0)
        ),
        "continuity_compression_effectiveness": _safe_ratio(
            hotspot_count + cluster_count, max(bundle_count, 1)
        ),
    }


def _build_workspace_trajectory(
    active_topology_zone: str,
    recent_edit_clusters: List[Dict[str, Any]],
) -> str:
    if recent_edit_clusters:
        return f"{active_topology_zone}:{recent_edit_clusters[0]['cluster']}"
    return active_topology_zone


def _normalize_for_compare(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _normalize_for_compare(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return [_normalize_for_compare(item) for item in value]
    if isinstance(value, str):
        return value.strip()
    return value


def _drop_empty_sections(payload: Dict[str, Any]) -> Dict[str, Any]:
    cleaned: Dict[str, Any] = {}
    for key, value in payload.items():
        if key in PRESERVE_EMPTY_KEYS:
            cleaned[key] = value
            continue
        if value in (None, "", [], {}):
            continue
        cleaned[key] = value
    return cleaned


def _write_json(path: Path, payload: Dict[str, Any]) -> bool:
    normalized_payload = _normalize_for_compare(payload)
    canonical_new = json.dumps(
        normalized_payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )

    if path.exists():
        try:
            existing_payload = json.loads(path.read_text(encoding="utf-8"))
            canonical_existing = json.dumps(
                _normalize_for_compare(existing_payload),
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
            if canonical_existing == canonical_new:
                return False
        except Exception:
            pass

    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return True


def _write_markdown(path: Path, lines: List[str]) -> bool:
    body = "\n".join(lines).rstrip() + "\n"
    normalized_new = (
        "\n".join(line.rstrip() for line in body.splitlines()).rstrip() + "\n"
    )

    if path.exists():
        existing = path.read_text(encoding="utf-8")
        normalized_existing = (
            "\n".join(line.rstrip() for line in existing.splitlines()).rstrip() + "\n"
        )
        if normalized_existing == normalized_new:
            return False

    path.write_text(body, encoding="utf-8")
    return True


def export_workspace_continuity(workspace_root: Path) -> Dict[str, Any]:
    artifact_dir = workspace_root / ARTIFACT_DIR
    continuity_dir = workspace_root / CONTINUITY_DIR
    continuity_dir.mkdir(parents=True, exist_ok=True)

    topology_compact = _read_json(artifact_dir / "topology_compact.json", {})
    locality_index = _read_json(artifact_dir / "locality_index.json", {})
    compact_bundle = _read_json(artifact_dir / "compact_bundle.json", {})
    active_context = _read_json(artifact_dir / "active_context.json", {})
    session_context = _read_json(artifact_dir / "session_context.json", {})
    daemon_state = _read_json(artifact_dir / "daemon_state.json", {})
    runtime_events = _normalize_runtime_events(
        _read_jsonl(artifact_dir / "runtime_activation.jsonl")
    )

    locality_file_map = _build_locality_file_map(
        locality_index if isinstance(locality_index, dict) else {}
    )

    changed_files = daemon_state.get("changed_files", [])
    active_paths = session_context.get("active_paths", [])
    recent_edit_clusters = _cluster_paths([*changed_files, *active_paths])

    repeated_modifications = [
        cluster for cluster in recent_edit_clusters if int(cluster.get("count", 0)) >= 2
    ]

    runtime_touched_files = _resolve_runtime_touched_files(
        runtime_events, locality_file_map
    )

    active_regions = {
        "active_topology_zone": compact_bundle.get(
            "active_topology_zone", "general_runtime"
        ),
        "active_runtime_zones": compact_bundle.get("active_runtime_zones", []),
    }

    hotspots = _collect_hotspots(
        compact_bundle if isinstance(compact_bundle, dict) else {},
        runtime_touched_files,
        active_context if isinstance(active_context, dict) else {},
    )

    runtime_validation = _validate_runtime_topology(
        topology_compact if isinstance(topology_compact, dict) else {},
        runtime_events,
        compact_bundle if isinstance(compact_bundle, dict) else {},
    )
    validation_metrics = _build_validation_metrics(
        recent_edit_clusters,
        repeated_modifications,
        compact_bundle if isinstance(compact_bundle, dict) else {},
        hotspots,
        runtime_validation,
    )
    workspace_trajectory = _build_workspace_trajectory(
        str(active_regions.get("active_topology_zone", "general_runtime")),
        recent_edit_clusters,
    )

    ownership_density_counter: Counter[str] = Counter()
    for edge in (
        topology_compact.get("edges", []) if isinstance(topology_compact, dict) else []
    ):
        if not isinstance(edge, dict):
            continue
        source_id = str(edge.get("from", "")).strip()
        if source_id:
            ownership_density_counter[source_id] += 1

    ownership_density = [
        {"id": key, "edge_count": ownership_density_counter[key]}
        for key in sorted(
            ownership_density_counter, key=lambda k: (-ownership_density_counter[k], k)
        )[:20]
    ]

    active_topology_payload = _drop_empty_sections(
        {
            "schema": ACTIVE_TOPOLOGY_SCHEMA,
            "disclaimer": GENERATED_DISCLAIMER,
            "active_topology_zone": active_regions["active_topology_zone"],
            "active_runtime_zones": active_regions["active_runtime_zones"],
            "workspace_trajectory": workspace_trajectory,
            "continuity_hotspots": hotspots,
            "runtime_validation": runtime_validation,
            "validation_metrics": validation_metrics,
        }
    )

    locality_state_payload = _drop_empty_sections(
        {
            "schema": LOCALITY_STATE_SCHEMA,
            "disclaimer": GENERATED_DISCLAIMER,
            "active_locality_clusters": recent_edit_clusters[:12],
            "repeated_edit_clusters": repeated_modifications[:8],
            "active_runtime_touched_files": runtime_touched_files[:12],
            "ownership_hotspots": ownership_density[:12],
            "continuity_hotspots": hotspots[:10],
            "validation_metrics": validation_metrics,
        }
    )

    unresolved_tensions: List[str] = []
    if not topology_compact:
        unresolved_tensions.append("topology_compact.json missing or empty")
    if runtime_validation.get("runtime_evidence_count", 0) == 0:
        unresolved_tensions.append("no runtime activation evidence available")
    if (
        runtime_validation.get("runtime_confirmation_density", 0.0) < 0.2
        and runtime_validation.get("runtime_evidence_count", 0) > 0
    ):
        unresolved_tensions.append(
            "runtime evidence weakly aligned with topology edges"
        )
    if not hotspots:
        unresolved_tensions.append("continuity hotspots unresolved")

    _write_json(continuity_dir / "active_topology.json", active_topology_payload)
    _write_json(continuity_dir / "locality_state.json", locality_state_payload)

    _write_markdown(
        continuity_dir / "architectural_decisions.md",
        [
            "# Architectural Decisions",
            "",
            "- PECS continuity state remains topology-first and deterministic.",
            "- Runtime activation is used as sparse validation evidence, not reconstruction authority.",
            "- Continuity exports are compact, human-readable, and append-light.",
            "- Continuity snapshots preserve only architectural state, locality, hotspots, and unresolved tensions.",
            f"- Active topology zone: {active_regions['active_topology_zone']}.",
        ],
    )

    _write_markdown(
        continuity_dir / "unresolved_tensions.md",
        ["# Unresolved Tensions", "", *[f"- {item}" for item in unresolved_tensions]],
    )

    focus_lines = [
        "# Current Workspace Focus",
        "",
        f"- Active topology zone: {active_regions['active_topology_zone']}",
        f"- Workspace trajectory: {workspace_trajectory}",
        f"- Runtime evidence count: {runtime_validation['runtime_evidence_count']}",
        f"- Runtime confirmation density: {runtime_validation['runtime_confirmation_density']}",
    ]

    if recent_edit_clusters:
        focus_lines.extend(["", "## Active Locality Clusters"])
        for cluster in recent_edit_clusters[:5]:
            focus_lines.append(f"- {cluster['cluster']} (count={cluster['count']})")

    if hotspots:
        focus_lines.extend(["", "## Continuity Hotspots"])
        for item in hotspots[:10]:
            focus_lines.append(
                f"- {item['id']} (score={item['score']}, signals={','.join(item['signals'])})"
            )

    _write_markdown(continuity_dir / "current_workspace_focus.md", focus_lines)

    engineering_continuity_state = _build_engineering_continuity_state(workspace_root)
    hydration_report = _build_continuity_hydration_report(
        workspace_root, engineering_continuity_state
    )
    _write_json(
        continuity_dir / "engineering_continuity_state.json",
        engineering_continuity_state,
    )
    _write_json(
        continuity_dir / "continuity_hydration_report.json",
        hydration_report,
    )

    return {
        "continuity_dir": str(continuity_dir),
        "active_topology": str(continuity_dir / "active_topology.json"),
        "locality_state": str(continuity_dir / "locality_state.json"),
        "engineering_continuity_state": str(
            continuity_dir / "engineering_continuity_state.json"
        ),
        "continuity_hydration_report": str(
            continuity_dir / "continuity_hydration_report.json"
        ),
        "architectural_decisions": str(continuity_dir / "architectural_decisions.md"),
        "unresolved_tensions": str(continuity_dir / "unresolved_tensions.md"),
        "current_workspace_focus": str(continuity_dir / "current_workspace_focus.md"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export minimal PECS workspace continuity stabilization state."
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
    workspace_root = Path(workspace_value).resolve()
    result = export_workspace_continuity(workspace_root)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
