from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ContinuityScoreEngine:
    """
    Consolidated probabilistic continuity scoring engine.

    Consolidates:
    - locality scoring
    - runtime authority scoring
    - ownership confidence
    - topology confidence

    into ONE scoring authority.

    PECS intentionally avoids scoring-layer proliferation.
    """

    runtime_authority_weight: float = 1.0
    execution_locality_weight: float = 0.9
    ownership_weight: float = 0.8
    propagation_weight: float = 0.7

    @staticmethod
    def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
        return max(low, min(high, value))

    def score_locality(
        self,
        locality_nodes: List[str],
    ) -> float:
        if not locality_nodes:
            return 0.0

        base_score = min(
            len(locality_nodes) * 0.1,
            self.execution_locality_weight,
        )

        return round(base_score, 3)

    def score_runtime_authority(
        self,
        runtime_nodes: int,
    ) -> float:
        if runtime_nodes <= 0:
            return 0.0

        return round(
            min(
                runtime_nodes * 0.15,
                self.runtime_authority_weight,
            ),
            3,
        )

    def score_ownership(
        self,
        ownership_nodes: int,
    ) -> float:
        if ownership_nodes <= 0:
            return 0.0

        return round(
            min(
                0.08 + ownership_nodes * 0.06,
                self.ownership_weight,
            ),
            3,
        )

    def score_propagation(
        self,
        anchor_count: int,
    ) -> float:
        if anchor_count <= 0:
            return 0.0

        return round(
            min(
                0.05 + anchor_count * 0.05,
                self.propagation_weight,
            ),
            3,
        )

    def score_locality_authority(
        self,
        locality_authority_confidence: Optional[float],
        continuity_survivability_confidence: Optional[float],
        duplicate_shadow_suspicion: Optional[float] = None,
        dead_execution_path_suspicion: Optional[float] = None,
        topology_mismatch_suspicion: Optional[float] = None,
    ) -> float:
        locality = self._clamp(float(locality_authority_confidence or 0.0))
        survivability = self._clamp(float(continuity_survivability_confidence or 0.0))
        duplicate_shadow = self._clamp(float(duplicate_shadow_suspicion or 0.0))
        dead_path = self._clamp(float(dead_execution_path_suspicion or 0.0))
        topology_mismatch = self._clamp(float(topology_mismatch_suspicion or 0.0))

        blended = (
            locality * 0.5
            + survivability * 0.35
            - duplicate_shadow * 0.18
            - dead_path * 0.12
            - topology_mismatch * 0.2
        )
        return round(self._clamp(blended), 3)
