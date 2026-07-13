from __future__ import annotations

import math
import re
from collections import defaultdict
from typing import Any, Dict, Iterable, List, Optional, Set

from .runtime_activation_logger import RuntimeActivationLogger
from .runtime_activation_events import EVENT_TYPE_WEIGHTS


class LocalityActivationEngine:
    """Infer active runtime locality from structured activation signals."""

    MAX_ACTIVATED_OBJECTS = 20
    MAX_ACTIVE_ZONES = 3
    MAX_OBSERVED_EDGES = 160
    MAX_TOKEN_BUDGET = 1400
    MAX_CLUSTER_COUNT = 4
    MAX_CLUSTER_OBJECTS = 8

    ISSUE_TERM_WEIGHT = 2.6
    RUNTIME_EVENT_WEIGHT = 1.3
    SIGNAL_SLOT_WEIGHT = 2.4
    EXECUTION_PROXIMITY_WEIGHT = 1.8
    ZONE_MATCH_WEIGHT = 2.2
    RECENT_EDIT_WEIGHT = 0.7
    HISTORICAL_FIX_WEIGHT = 1.1
    SESSION_CONTINUITY_WEIGHT = 1.4
    CROSS_ZONE_PENALTY = 1.8
    INACTIVE_MODULE_PENALTY = 3.2

    _STOP_WORDS = {
        "about",
        "after",
        "again",
        "before",
        "being",
        "could",
        "doing",
        "from",
        "have",
        "into",
        "just",
        "more",
        "only",
        "other",
        "should",
        "than",
        "that",
        "them",
        "then",
        "there",
        "these",
        "they",
        "this",
        "those",
        "when",
        "which",
        "with",
        "would",
    }

    _INACTIVE_MODULE_HINTS = (
        "ocr",
        "toc",
        "mnist",
        "training",
        "recovery",
        "backup",
        "archive",
        "inactive_overlay",
    )

    _WRAPPER_SURFACE_HINTS = (
        "wrapper",
        "adapter",
        "bridge",
        "cli",
        "launcher",
    )

    _ZONE_KEYWORDS: Dict[str, Set[str]] = {
        "dock_pipeline": {"dock", "pane", "sidebar"},
        "notes_pipeline": {"note", "notes", "sticky"},
        "search_pipeline": {"find", "search", "lookup", "popup"},
        "monitor_pipeline": {"monitor", "persist", "persistence", "watch"},
        "viewer_pipeline": {"viewer", "canvas", "pdf"},
        "overlay_pipeline": {"overlay", "band", "wireframe"},
        "dialog_pipeline": {"dialog", "wizard", "modal"},
        "dispatch_pipeline": {"dispatch", "signal", "slot", "callback"},
        "runtime_pipeline": {"runtime", "activation", "session"},
    }

    def __init__(self, activation_logger: RuntimeActivationLogger) -> None:
        self.activation_logger = activation_logger

    def infer_locality(
        self,
        current_issue: str = "",
        edited_files: Optional[Iterable[str]] = None,
        dissatisfaction_signals: Optional[Iterable[str]] = None,
        active_topology_zone: str = "",
        historical_fix_locality: Optional[Iterable[str]] = None,
        current_session_objects: Optional[Iterable[str]] = None,
    ) -> Dict[str, object]:
        edited_files = list(edited_files or [])
        dissatisfaction_signals = list(dissatisfaction_signals or [])
        historical_fix_locality = list(historical_fix_locality or [])
        current_session_objects = list(current_session_objects or [])

        events = self.activation_logger.export_recent_events(limit=300)
        now_ts = int(events[-1].get("ts", 0)) if events else 0

        issue_terms = self._extract_issue_terms(current_issue)
        inferred_zone_hints = self._infer_issue_zones(issue_terms)
        preferred_zones = self._preferred_zones(
            active_topology_zone, inferred_zone_hints
        )

        runtime_confirmed: Set[str] = set()
        candidate_zones: Dict[str, str] = {}
        candidate_scores: Dict[str, float] = defaultdict(float)
        activation_reasons: Dict[str, List[str]] = defaultdict(list)
        zone_scores: Dict[str, float] = defaultdict(float)
        execution_depths: Dict[str, str] = {}
        observed_edges: List[Dict[str, object]] = []
        discarded_candidates: List[Dict[str, str]] = []

        for index, event in enumerate(events):
            event_type = str(event.get("event", ""))
            base_weight = float(EVENT_TYPE_WEIGHTS.get(event_type, 1))
            decay = self._event_decay(
                index=index, total_events=len(events), event=event, now_ts=now_ts
            )
            weight = base_weight * decay * self.RUNTIME_EVENT_WEIGHT
            source = str(event.get("source", ""))
            target = str(event.get("target", ""))
            runtime_zone = str(event.get("runtime_zone", "")) or "general_runtime"

            if source:
                runtime_confirmed.add(source)
                candidate_zones[source] = runtime_zone
                candidate_scores[source] += weight
                activation_reasons[source].append(f"event:{event_type}")
                execution_depths[source] = self._execution_depth_for_event(
                    event_type, source=True
                )

            if target:
                runtime_confirmed.add(target)
                candidate_zones[target] = runtime_zone
                candidate_scores[target] += max(weight * 0.82, 0.5)
                activation_reasons[target].append(f"event_target:{event_type}")
                execution_depths[target] = self._execution_depth_for_event(
                    event_type, source=False
                )

            if source and target:
                adjacency_boost = self.EXECUTION_PROXIMITY_WEIGHT * max(decay, 0.45)
                candidate_scores[source] += adjacency_boost
                candidate_scores[target] += adjacency_boost * 0.9
                activation_reasons[source].append("execution_path_proximity")
                activation_reasons[target].append("execution_path_proximity")

            if runtime_zone:
                zone_scores[runtime_zone] += weight

            if source and target:
                observed_edges.append(
                    {
                        "from": source,
                        "to": target,
                        "type": "observed_runtime_activation",
                        "weight": round(weight, 3),
                    }
                )

            if event_type == "signal_slot_activation":
                if source:
                    candidate_scores[source] += self.SIGNAL_SLOT_WEIGHT
                    activation_reasons[source].append("signal_slot_adjacency")
                if target:
                    candidate_scores[target] += self.SIGNAL_SLOT_WEIGHT * 0.92
                    activation_reasons[target].append("signal_slot_adjacency")

            if event_type in {"qaction_trigger", "dialog_launch"}:
                if source:
                    candidate_scores[source] -= 0.6
                    activation_reasons[source].append("ui_wrapper_penalty")

        for obj in list(candidate_scores.keys()):
            issue_hits = self._issue_term_hits(obj, issue_terms)
            if issue_hits:
                boost = float(issue_hits) * self.ISSUE_TERM_WEIGHT
                candidate_scores[obj] += boost
                activation_reasons[obj].append(f"issue_term:{issue_hits}")

        for path in edited_files:
            normalized = self._normalize_edited_path(path)
            if not normalized:
                continue

            edit_weight = self.RECENT_EDIT_WEIGHT
            if self._looks_wrapper_surface(normalized):
                edit_weight *= 0.45
                activation_reasons[normalized].append(
                    "wrapper_surface_recent_edit_downweighted"
                )

            if self._recent_edit_is_plausible(normalized, issue_terms, preferred_zones):
                candidate_scores[normalized] += edit_weight
                activation_reasons[normalized].append("recent_edit_reinforcement")
            else:
                discarded_candidates.append(
                    {
                        "candidate": normalized,
                        "reason": "recent_edit_without_locality_evidence",
                    }
                )

        for obj in historical_fix_locality:
            normalized = self._normalize_edited_path(str(obj))
            if not normalized:
                continue
            candidate_scores[normalized] += self.HISTORICAL_FIX_WEIGHT
            activation_reasons[normalized].append("historical_fix_locality")

        for obj in current_session_objects:
            normalized = self._normalize_edited_path(str(obj))
            if not normalized:
                continue
            continuity_weight = self.SESSION_CONTINUITY_WEIGHT
            if normalized not in runtime_confirmed:
                continuity_weight *= 0.45
            if self._looks_wrapper_surface(normalized) and normalized not in runtime_confirmed:
                continuity_weight *= 0.7
                activation_reasons[normalized].append(
                    "wrapper_surface_session_downweighted"
                )
            candidate_scores[normalized] += continuity_weight
            activation_reasons[normalized].append("current_session_continuity")

        for obj in list(candidate_scores.keys()):
            obj_zone = candidate_zones.get(obj, self._infer_zone_from_object(obj))
            candidate_zones[obj] = obj_zone

            if obj_zone in preferred_zones:
                candidate_scores[obj] += self.ZONE_MATCH_WEIGHT
                activation_reasons[obj].append("runtime_zone_match")
            elif (
                obj_zone
                and obj_zone != "general_runtime"
                and obj not in runtime_confirmed
            ):
                candidate_scores[obj] -= self.CROSS_ZONE_PENALTY
                activation_reasons[obj].append("cross_zone_penalty")

            if self._looks_inactive_module(obj) and obj not in runtime_confirmed:
                candidate_scores[obj] -= self.INACTIVE_MODULE_PENALTY
                activation_reasons[obj].append("inactive_module_downrank")

            depth = execution_depths.get(
                obj, self._infer_execution_depth(obj, activation_reasons[obj])
            )
            execution_depths[obj] = depth
            candidate_scores[obj] += self._execution_depth_weight(depth)
            activation_reasons[obj].append(f"execution_depth:{depth}")

        for signal in dissatisfaction_signals:
            normalized = signal.strip().lower()
            if normalized:
                zone_scores["general_runtime"] += 0.4
                discarded_candidates.append(
                    {
                        "candidate": f"dissatisfaction:{normalized}",
                        "reason": "tracked_signal",
                    }
                )

        selected_zones = self._select_active_zones(
            zone_scores=zone_scores,
            preferred_zones=preferred_zones,
            candidate_zones=candidate_zones,
            candidate_scores=candidate_scores,
        )

        selected_objects, budget_usage, object_details = self._select_object_budget(
            candidate_scores=candidate_scores,
            candidate_zones=candidate_zones,
            activation_reasons=activation_reasons,
            runtime_confirmed=runtime_confirmed,
            execution_depths=execution_depths,
            selected_zones=selected_zones,
        )

        clusters = self._build_locality_clusters(
            object_details=object_details,
            issue_terms=issue_terms,
        )

        object_score_map = {
            detail["pecs_id"]: round(float(detail["weighted_score"]), 3)
            for detail in object_details
        }

        total_score = sum(object_score_map.values())

        return {
            "issue_terms": issue_terms,
            "active_runtime_zones": selected_zones,
            "activated_objects": selected_objects,
            "activated_object_details": object_details,
            "active_locality_clusters": clusters,
            "activation_confidence": {
                "total_score": round(total_score, 3),
                "object_scores": object_score_map,
                "mean_locality_confidence": round(
                    sum(
                        float(detail["locality_confidence"])
                        for detail in object_details
                    )
                    / max(len(object_details), 1),
                    3,
                ),
                "budget_usage": budget_usage,
            },
            "activation_reasons": {
                key: list(values) for key, values in activation_reasons.items()
            },
            "observed_edges": observed_edges[: self.MAX_OBSERVED_EDGES],
            "activation_diagnostics": {
                "preferred_zones": preferred_zones,
                "zone_scores": {
                    zone: round(score, 3) for zone, score in sorted(zone_scores.items())
                },
                "wrapper_selected_count": len(
                    [
                        detail
                        for detail in object_details
                        if self._looks_wrapper_surface(str(detail.get("pecs_id", "")))
                    ]
                ),
                "runtime_confirmed_selected_count": len(
                    [
                        detail
                        for detail in object_details
                        if bool(detail.get("runtime_confirmed", False))
                    ]
                ),
                "discarded_candidates": discarded_candidates[:80],
                "candidate_count": len(candidate_scores),
                "selected_count": len(selected_objects),
            },
        }

    def _normalize_edited_path(self, path: str) -> Optional[str]:
        path = path.strip()
        if not path:
            return None
        if path.startswith("PECS_ID:"):
            return path
        safe = path.replace("\\", "/").strip("/ ")
        if safe:
            return f"PECS_ID:{safe.replace('/', '.') }"
        return None

    def _extract_issue_terms(self, current_issue: str) -> List[str]:
        terms: List[str] = []
        if current_issue:
            raw_terms = re.findall(r"[a-zA-Z_][a-zA-Z0-9_]{2,}", current_issue.lower())
            for term in raw_terms:
                if term in self._STOP_WORDS:
                    continue
                if term not in terms:
                    terms.append(term)
        return terms[:12]

    def _infer_issue_zones(self, issue_terms: List[str]) -> List[str]:
        terms = set(issue_terms)
        inferred: List[str] = []
        for zone, keywords in self._ZONE_KEYWORDS.items():
            if terms.intersection(keywords):
                inferred.append(zone)
        return inferred[: self.MAX_ACTIVE_ZONES]

    def _preferred_zones(
        self,
        active_topology_zone: str,
        inferred_zone_hints: List[str],
    ) -> List[str]:
        ordered: List[str] = []
        if active_topology_zone and active_topology_zone != "general_runtime":
            ordered.append(active_topology_zone)
        for zone in inferred_zone_hints:
            if zone not in ordered:
                ordered.append(zone)
        if not ordered:
            ordered.append("general_runtime")
        return ordered[: self.MAX_ACTIVE_ZONES]

    def _event_decay(
        self,
        index: int,
        total_events: int,
        event: Dict[str, object],
        now_ts: int,
    ) -> float:
        event_ts = int(event.get("ts", now_ts or 0) or 0)
        age_by_order = float(total_events - index - 1)
        age_by_time = (
            float(max((now_ts - event_ts), 0)) / 3600.0 if now_ts and event_ts else 0.0
        )
        age = age_by_order + age_by_time
        return max(0.25, math.exp(-age / 38.0))

    def _issue_term_hits(self, object_id: str, issue_terms: List[str]) -> int:
        lowered = object_id.lower()
        return sum(1 for term in issue_terms if term in lowered)

    def _infer_zone_from_object(self, object_id: str) -> str:
        lowered = object_id.lower()
        for zone, terms in self._ZONE_KEYWORDS.items():
            if any(term in lowered for term in terms):
                return zone
        return "general_runtime"

    def _recent_edit_is_plausible(
        self,
        object_id: str,
        issue_terms: List[str],
        preferred_zones: List[str],
    ) -> bool:
        lowered = object_id.lower()
        if any(term in lowered for term in issue_terms):
            return True
        zone = self._infer_zone_from_object(object_id)
        return zone in preferred_zones and zone != "general_runtime"

    def _looks_inactive_module(self, object_id: str) -> bool:
        lowered = object_id.lower()
        return any(token in lowered for token in self._INACTIVE_MODULE_HINTS)

    def _looks_wrapper_surface(self, object_id: str) -> bool:
        lowered = object_id.lower()
        return any(token in lowered for token in self._WRAPPER_SURFACE_HINTS)

    def _execution_depth_for_event(self, event_type: str, source: bool) -> str:
        if event_type in {"signal_slot_activation", "dispatch"}:
            return "mutation_owner"
        if event_type in {"subprocess_launch", "worker_start"}:
            return "dispatcher"
        if event_type in {"qaction_trigger", "dialog_launch"}:
            return "wrapper"
        if source:
            return "entrypoint"
        return "dispatcher"

    def _infer_execution_depth(self, object_id: str, reasons: List[str]) -> str:
        lowered = object_id.lower()
        if any("signal_slot" in reason for reason in reasons):
            return "mutation_owner"
        if any(token in lowered for token in ("dispatch", "callback", "slot")):
            return "dispatcher"
        if any(token in lowered for token in ("main", "entry", "controller")):
            return "entrypoint"
        return "wrapper"

    def _execution_depth_weight(self, depth: str) -> float:
        if depth == "mutation_owner":
            return 2.4
        if depth == "dispatcher":
            return 1.5
        if depth == "entrypoint":
            return 1.1
        return -0.6

    def _select_active_zones(
        self,
        zone_scores: Dict[str, float],
        preferred_zones: List[str],
        candidate_zones: Dict[str, str],
        candidate_scores: Dict[str, float],
    ) -> List[str]:
        merged: Dict[str, float] = defaultdict(float)
        for zone, score in zone_scores.items():
            merged[zone] += score
        for candidate, zone in candidate_zones.items():
            merged[zone] += max(candidate_scores.get(candidate, 0.0), 0.0) * 0.04
        for zone in preferred_zones:
            merged[zone] += 2.2

        ranked = sorted(merged.items(), key=lambda item: (-item[1], item[0]))
        selected = [zone for zone, _ in ranked[: self.MAX_ACTIVE_ZONES] if zone]
        if not selected:
            selected = ["general_runtime"]
        return selected

    def _score_to_confidence(self, score: float) -> float:
        normalized = 1.0 / (1.0 + math.exp(-0.28 * (score - 6.0)))
        return max(0.0, min(1.0, normalized))

    def _approx_token_cost(self, object_id: str, reasons: List[str]) -> int:
        return max(12, int(len(object_id) * 0.3) + len(reasons) * 3)

    def _select_object_budget(
        self,
        candidate_scores: Dict[str, float],
        candidate_zones: Dict[str, str],
        activation_reasons: Dict[str, List[str]],
        runtime_confirmed: Set[str],
        execution_depths: Dict[str, str],
        selected_zones: List[str],
    ) -> Any:
        ranked_candidates = sorted(
            candidate_scores.items(), key=lambda item: (-item[1], item[0])
        )

        selected: List[str] = []
        details: List[Dict[str, object]] = []
        token_usage = 0
        selected_zone_set: Set[str] = set()
        discarded_by_budget = 0

        for pecs_id, score in ranked_candidates:
            if score <= 0.6:
                continue

            zone = candidate_zones.get(pecs_id, "general_runtime")
            if zone not in selected_zones and zone != "general_runtime":
                continue

            reasons = activation_reasons.get(pecs_id, [])
            token_cost = self._approx_token_cost(pecs_id, reasons)

            if len(selected) >= self.MAX_ACTIVATED_OBJECTS:
                discarded_by_budget += 1
                continue
            if token_usage + token_cost > self.MAX_TOKEN_BUDGET:
                discarded_by_budget += 1
                continue

            selected.append(pecs_id)
            token_usage += token_cost
            selected_zone_set.add(zone)
            details.append(
                {
                    "pecs_id": pecs_id,
                    "locality_confidence": round(self._score_to_confidence(score), 3),
                    "activation_reasons": reasons[:8],
                    "runtime_zone": zone,
                    "execution_depth": execution_depths.get(pecs_id, "wrapper"),
                    "runtime_confirmed": pecs_id in runtime_confirmed,
                    "weighted_score": round(score, 3),
                }
            )

        budget = {
            "object_limit": self.MAX_ACTIVATED_OBJECTS,
            "object_used": len(selected),
            "zone_limit": self.MAX_ACTIVE_ZONES,
            "zone_used": len(selected_zone_set),
            "token_limit": self.MAX_TOKEN_BUDGET,
            "token_used": token_usage,
            "discarded_by_budget": discarded_by_budget,
            "continuity_depth_limit": self.MAX_CLUSTER_COUNT,
        }

        return selected, budget, details

    def _build_locality_clusters(
        self,
        object_details: List[Dict[str, object]],
        issue_terms: List[str],
    ) -> List[Dict[str, object]]:
        grouped: Dict[str, List[str]] = defaultdict(list)
        lowered_terms = issue_terms[:3]

        for detail in object_details:
            obj = str(detail.get("pecs_id", ""))
            zone = str(detail.get("runtime_zone", "general_runtime"))
            obj_lower = obj.lower()

            cluster_prefix = next(
                (term for term in lowered_terms if term in obj_lower), "runtime"
            )
            cluster_name = f"{cluster_prefix}_{zone}"
            grouped[cluster_name].append(obj)

        ranked_clusters = sorted(
            grouped.items(), key=lambda item: (-len(item[1]), item[0])
        )

        clusters: List[Dict[str, object]] = []
        for cluster_name, objects in ranked_clusters[: self.MAX_CLUSTER_COUNT]:
            clusters.append(
                {
                    "cluster": cluster_name,
                    "objects": objects[: self.MAX_CLUSTER_OBJECTS],
                }
            )
        return clusters
