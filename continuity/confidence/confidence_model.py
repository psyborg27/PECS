from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class ConfidenceModel:
    """
    Deterministic topology-first confidence model.

    Runtime topology evidence always dominates
    static structural evidence.
    """

    runtime_weight: float = 1.0
    execution_weight: float = 0.95
    dispatch_weight: float = 0.90
    signal_slot_weight: float = 0.90
    subprocess_weight: float = 0.85
    propagation_weight: float = 0.85
    ownership_weight: float = 0.80

    import_weight: float = 0.45
    locality_weight: float = 0.40
    semantic_weight: float = 0.10

    metadata: Dict[str, object] = field(default_factory=dict)

    @staticmethod
    def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
        return max(low, min(high, value))

    def derive_locality_authority_confidence(
        self,
        locality_authority_confidence: float,
        duplicate_shadow_suspicion: float,
        runtime_confirmation_weight: float,
        continuity_survivability_confidence: float,
        topology_mismatch_weight: float,
        dead_execution_path_suspicion: float = 0.0,
        persistence_signal_count: int = 0,
        runtime_activity_density: Optional[float] = None,
    ) -> Dict[str, float]:
        locality = self._clamp(float(locality_authority_confidence))
        duplicate_shadow = self._clamp(float(duplicate_shadow_suspicion))
        runtime_confirmation = self._clamp(float(runtime_confirmation_weight))
        survivability = self._clamp(float(continuity_survivability_confidence))
        topology_mismatch = self._clamp(float(topology_mismatch_weight))
        dead_path = self._clamp(float(dead_execution_path_suspicion))

        persistence_penalty = min(0.28, 0.04 * max(0, int(persistence_signal_count)))
        density_penalty = 0.0
        if runtime_activity_density is not None:
            density_penalty = max(0.0, 0.2 - self._clamp(float(runtime_activity_density)))

        blended = (
            locality * 0.40
            + runtime_confirmation * 0.22
            + survivability * 0.28
            - duplicate_shadow * 0.15
            - topology_mismatch * 0.18
            - dead_path * 0.10
            - persistence_penalty
            - density_penalty * 0.5
        )

        return {
            "locality_authority_confidence": round(self._clamp(blended), 3),
            "duplicate_shadow_probability": round(duplicate_shadow, 3),
            "runtime_confirmation_weight": round(runtime_confirmation, 3),
            "continuity_survivability_confidence": round(survivability, 3),
            "topology_mismatch_weight": round(topology_mismatch, 3),
            "dead_execution_path_weight": round(dead_path, 3),
        }

    def to_dict(self) -> Dict[str, object]:
        return {
            "runtime_weight": self.runtime_weight,
            "execution_weight": self.execution_weight,
            "dispatch_weight": self.dispatch_weight,
            "signal_slot_weight": self.signal_slot_weight,
            "subprocess_weight": self.subprocess_weight,
            "propagation_weight": self.propagation_weight,
            "ownership_weight": self.ownership_weight,
            "import_weight": self.import_weight,
            "locality_weight": self.locality_weight,
            "semantic_weight": self.semantic_weight,
            "metadata": self.metadata,
        }
