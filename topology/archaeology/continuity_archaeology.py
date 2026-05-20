from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ContinuityArchaeology:
    """
    Consolidated continuity archaeology infrastructure.

    Tracks:
    - duplicate evolution
    - historical continuity
    - canonical drift
    - regression-prone topology

    This intentionally remains observational only.

    PECS archaeology NEVER mutates runtime truth.
    """

    duplicate_history: Dict[str, List[str]] = field(default_factory=dict)

    canonical_drift_history: Dict[str, List[str]] = field(default_factory=dict)

    regression_zones: Dict[str, List[str]] = field(default_factory=dict)

    locality_authority_history: Dict[str, List[Dict[str, object]]] = field(
        default_factory=dict
    )

    persistence_signal_index: Dict[str, int] = field(default_factory=dict)

    PERSISTENCE_TOKENS = (
        "issue persists",
        "same behavior",
        "still broken",
        "no effect",
        "nothing changed",
    )

    @staticmethod
    def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
        return max(low, min(high, value))

    def register_duplicate_evolution(
        self,
        cluster_id: str,
        node_ids: List[str],
    ) -> None:
        self.duplicate_history[cluster_id] = node_ids

    def register_regression_zone(
        self,
        zone_id: str,
        node_ids: List[str],
    ) -> None:
        self.regression_zones[zone_id] = node_ids

    def register_persistence_signal(
        self,
        issue_id: str,
        signal_text: str,
    ) -> int:
        lowered = str(signal_text or "").lower()
        if not any(token in lowered for token in self.PERSISTENCE_TOKENS):
            return self.persistence_signal_index.get(issue_id, 0)

        current = int(self.persistence_signal_index.get(issue_id, 0))
        updated = current + 1
        self.persistence_signal_index[issue_id] = updated
        return updated

    def derive_locality_authority_evidence(
        self,
        attempted_locality: str,
        runtime_authority_candidate: Optional[str] = None,
        runtime_effect_confirmed: Optional[bool] = None,
        persistence_signal_count: int = 0,
        duplicate_lineage_count: int = 0,
        wrapper_only_mutation: bool = False,
        ownership_ambiguity: float = 0.0,
        topology_mismatch_signal: float = 0.0,
        dead_execution_path_signal: float = 0.0,
        runtime_activity_density: Optional[float] = None,
        historical_retention_signal: Optional[float] = None,
    ) -> Dict[str, object]:
        attempted = str(attempted_locality or "").strip()
        authority_candidate = (
            str(runtime_authority_candidate or "").strip() or None
        )

        unresolved_persistence = bool(
            persistence_signal_count > 0 and runtime_effect_confirmed is not True
        )
        same_locality = bool(
            attempted
            and authority_candidate
            and attempted == authority_candidate
        )
        mismatch = bool(
            attempted
            and authority_candidate
            and attempted != authority_candidate
        )

        duplicate_shadow_suspicion = self._clamp(
            0.18 * float(duplicate_lineage_count)
            + 0.07 * float(persistence_signal_count)
            + (0.22 if mismatch else 0.0)
            + (0.08 if unresolved_persistence else 0.0)
        )

        dead_execution_path_suspicion = self._clamp(
            float(dead_execution_path_signal)
            + (0.18 if wrapper_only_mutation else 0.0)
            + (
                0.16
                if runtime_activity_density is not None
                and float(runtime_activity_density) < 0.2
                else 0.0
            )
        )

        topology_mismatch_suspicion = self._clamp(
            float(topology_mismatch_signal)
            + (0.25 if mismatch else 0.0)
            + (0.12 if unresolved_persistence else 0.0)
        )

        locality_authority_confidence = 0.55
        if same_locality:
            locality_authority_confidence += 0.22
        if runtime_effect_confirmed is True:
            locality_authority_confidence += 0.17
        if unresolved_persistence:
            locality_authority_confidence -= 0.20
        locality_authority_confidence -= topology_mismatch_suspicion * 0.28
        locality_authority_confidence -= duplicate_shadow_suspicion * 0.18
        locality_authority_confidence = self._clamp(locality_authority_confidence)

        survivability = 0.52
        if runtime_activity_density is not None:
            survivability += (float(runtime_activity_density) - 0.5) * 0.35
        if historical_retention_signal is not None:
            survivability += (float(historical_retention_signal) - 0.5) * 0.20
        if runtime_effect_confirmed is True:
            survivability += 0.15
        if unresolved_persistence:
            survivability -= 0.20
        survivability -= dead_execution_path_suspicion * 0.18
        survivability = self._clamp(survivability)

        return {
            "attempted_locality": attempted,
            "runtime_authority_candidate": authority_candidate,
            "runtime_effect_confirmed": runtime_effect_confirmed,
            "unresolved_persistence": unresolved_persistence,
            "duplicate_shadow_suspicion": round(duplicate_shadow_suspicion, 3),
            "dead_execution_path_suspicion": round(dead_execution_path_suspicion, 3),
            "wrapper_only_mutation": bool(wrapper_only_mutation),
            "topology_mismatch_suspicion": round(topology_mismatch_suspicion, 3),
            "ownership_ambiguity": round(self._clamp(float(ownership_ambiguity)), 3),
            "locality_authority_confidence": round(locality_authority_confidence, 3),
            "continuity_survivability_confidence": round(survivability, 3),
            "runtime_activity_density": (
                round(self._clamp(float(runtime_activity_density)), 3)
                if runtime_activity_density is not None
                else None
            ),
            "historical_retention_signal": (
                round(self._clamp(float(historical_retention_signal)), 3)
                if historical_retention_signal is not None
                else None
            ),
            "persistence_signal_count": int(max(0, persistence_signal_count)),
        }

    def register_locality_authority_evidence(
        self,
        issue_id: str,
        evidence: Dict[str, object],
        max_records: int = 40,
    ) -> None:
        records = self.locality_authority_history.setdefault(issue_id, [])
        records.append(dict(evidence))
        if len(records) > max_records:
            self.locality_authority_history[issue_id] = records[-max_records:]

    def to_dict(self) -> Dict[str, object]:
        return {
            "duplicate_history": (self.duplicate_history),
            "canonical_drift_history": (self.canonical_drift_history),
            "regression_zones": self.regression_zones,
            "locality_authority_history": self.locality_authority_history,
            "persistence_signal_index": self.persistence_signal_index,
        }
