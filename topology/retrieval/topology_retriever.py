from __future__ import annotations

import logging
from dataclasses import dataclass, field
from time import perf_counter
from typing import Dict, List, Optional

from execution_graph.indexes.execution_index import (
    ExecutionIndex,
)
from execution_graph.indexes.ownership_index import (
    OwnershipIndex,
)
from ..indexing.locality_index import LocalityIndex
from ..scoring.continuity_score_engine import (
    ContinuityScoreEngine,
)


LOG = logging.getLogger(__name__)


class RetrievalError(Exception):
    """Legacy compatibility error type for retrieval callers."""


@dataclass
class TopologyRetriever:
    """
    Consolidated topology-aware continuity retrieval engine.

    This intentionally consolidates:
    - locality retrieval
    - continuity reconstruction
    - ownership locality
    - execution locality
    - ranking
    - retrieval telemetry

    into ONE authority module.

    PECS avoids retrieval fragmentation deliberately.
    """

    locality_index: LocalityIndex
    execution_index: ExecutionIndex
    ownership_index: OwnershipIndex
    scoring_engine: ContinuityScoreEngine

    retrieval_metadata: Dict[str, object] = field(default_factory=dict)
    mode: str = "exploratory"
    minimum_confidence: float = 0.2
    allow_semantic_fallback: bool = True

    def retrieve_object_locality(
        self,
        object_id: str,
    ) -> List[str]:
        """
        Retrieve topology-local continuity anchors for an object.
        """
        return self.locality_index.resolve_locality(object_id)

    def retrieve_execution_locality(
        self,
        path_id: str,
    ) -> List[str]:
        """
        Retrieve execution-local continuity anchors for a path.
        """
        return self.execution_index.get_execution_locality(path_id)

    def retrieve_ownership_locality(
        self,
        owner_id: str,
    ) -> List[str]:
        """
        Retrieve ownership-local continuity anchors for an owner.
        """
        return self.ownership_index.get_owned_locality(owner_id)

    def _collect_anchors(
        self,
        object_locality: List[str],
        execution_locality: List[str],
        ownership_locality: List[str],
        continuity_signals: Optional[Dict[str, object]] = None,
    ) -> Dict[str, object]:
        source_weights = {
            "object_locality": 1.0,
            "execution_locality": 0.85,
            "ownership_locality": 0.75,
        }

        anchor_scores: Dict[str, float] = {}
        duplicate_counts: Dict[str, int] = {}
        first_seen: Dict[str, int] = {}

        all_sources = [
            ("object_locality", object_locality),
            ("execution_locality", execution_locality),
            ("ownership_locality", ownership_locality),
        ]

        position = 0
        for source_name, locality in all_sources:
            weight = source_weights.get(source_name, 0.0)
            for anchor in locality:
                duplicate_counts[anchor] = duplicate_counts.get(anchor, 0) + 1
                anchor_scores[anchor] = anchor_scores.get(anchor, 0.0) + weight
                if anchor not in first_seen:
                    first_seen[anchor] = position
                    position += 1

        if continuity_signals:
            accepted_scores = continuity_signals.get(
                "accepted_locality_scores",
                {},
            ) or {}
            rejected_scores = continuity_signals.get(
                "rejected_locality_scores",
                {},
            ) or {}
            runtime_confirmed_scores = continuity_signals.get(
                "runtime_confirmed_locality_scores",
                {},
            ) or {}
            survivability_scores = continuity_signals.get(
                "continuity_survivability_scores",
                {},
            ) or {}
            authority_scores = continuity_signals.get(
                "locality_authority_scores",
                {},
            ) or {}
            duplicate_shadow_scores = continuity_signals.get(
                "duplicate_shadow_scores",
                {},
            ) or {}
            dead_path_scores = continuity_signals.get(
                "dead_execution_path_scores",
                {},
            ) or {}
            topology_mismatch_scores = continuity_signals.get(
                "topology_mismatch_scores",
                {},
            ) or {}

            for anchor in list(anchor_scores):
                accepted_boost = float(accepted_scores.get(anchor, 0.0) or 0.0)
                if accepted_boost > 0.0:
                    anchor_scores[anchor] += accepted_boost * 0.4

                runtime_confirmed_boost = float(
                    runtime_confirmed_scores.get(anchor, 0.0) or 0.0
                )
                if runtime_confirmed_boost > 0.0:
                    anchor_scores[anchor] += runtime_confirmed_boost * 0.45

                survivability_boost = float(
                    survivability_scores.get(anchor, 0.0) or 0.0
                )
                if survivability_boost > 0.0:
                    anchor_scores[anchor] += survivability_boost * 0.25

                authority_boost = float(authority_scores.get(anchor, 0.0) or 0.0)
                if authority_boost > 0.0:
                    anchor_scores[anchor] += authority_boost * 0.35

                rejected_penalty = float(rejected_scores.get(anchor, 0.0) or 0.0)
                if rejected_penalty > 0.0:
                    anchor_scores[anchor] *= max(0.0, 1.0 - rejected_penalty * 0.5)

                duplicate_shadow_penalty = float(
                    duplicate_shadow_scores.get(anchor, 0.0) or 0.0
                )
                if duplicate_shadow_penalty > 0.0:
                    anchor_scores[anchor] *= max(
                        0.0, 1.0 - duplicate_shadow_penalty * 0.35
                    )

                dead_path_penalty = float(dead_path_scores.get(anchor, 0.0) or 0.0)
                if dead_path_penalty > 0.0:
                    anchor_scores[anchor] *= max(0.0, 1.0 - dead_path_penalty * 0.30)

                topology_mismatch_penalty = float(
                    topology_mismatch_scores.get(anchor, 0.0) or 0.0
                )
                if topology_mismatch_penalty > 0.0:
                    anchor_scores[anchor] *= max(
                        0.0, 1.0 - topology_mismatch_penalty * 0.40
                    )

        sorted_anchors = sorted(
            anchor_scores.keys(),
            key=lambda anchor: (
                -anchor_scores.get(anchor, 0.0),
                first_seen.get(anchor, 0),
            ),
        )

        duplicate_lineages = [
            anchor
            for anchor, count in duplicate_counts.items()
            if count > 1
        ]

        return {
            "anchors": sorted_anchors,
            "anchor_scores": anchor_scores,
            "duplicate_lineages": duplicate_lineages,
            "retrieval_source_count": len(sorted_anchors),
            "duplicate_count": len(duplicate_lineages),
        }

    def retrieve_continuity_context(
        self,
        object_id: str,
        path_id: Optional[str] = None,
        owner_id: Optional[str] = None,
        continuity_signals: Optional[Dict[str, object]] = None,
        locality_limit: int = 12,
        enforce: bool = False,
        manual_override: bool = False,
        minimum_confidence: Optional[float] = None,
    ) -> Dict[str, object]:
        """
        Retrieve and shape a structured continuity context for an object.

        This is the active PECS retrieval lifecycle. It returns advisory
        retrieval metadata, preserves topology provenance, and allows
        semantic fallback in weak-anchor scenarios.
        """
        start = perf_counter()

        object_locality = self.retrieve_object_locality(object_id)
        execution_locality = []
        ownership_locality = []

        if path_id:
            execution_locality = self.retrieve_execution_locality(path_id)

        lookup_owner = owner_id or object_id
        ownership_locality = self.retrieve_ownership_locality(lookup_owner)

        anchors_info = self._collect_anchors(
            object_locality=object_locality,
            execution_locality=execution_locality,
            ownership_locality=ownership_locality,
            continuity_signals=continuity_signals,
        )

        locality_score = self.scoring_engine.score_locality(
            anchors_info["anchors"]
        )
        runtime_score = self.scoring_engine.score_runtime_authority(
            len(execution_locality)
        )
        ownership_score = self.scoring_engine.score_ownership(
            len(ownership_locality)
        )
        propagation_score = self.scoring_engine.score_propagation(
            len(anchors_info["anchors"])
        )

        confidence = round(
            (
                locality_score * 0.4
                + runtime_score * 0.25
                + ownership_score * 0.2
                + propagation_score * 0.15
            ),
            3,
        )

        authority_signals = continuity_signals or {}
        authority_score = self.scoring_engine.score_locality_authority(
            locality_authority_confidence=authority_signals.get(
                "locality_authority_confidence"
            ),
            continuity_survivability_confidence=authority_signals.get(
                "continuity_survivability_confidence"
            ),
            duplicate_shadow_suspicion=authority_signals.get(
                "duplicate_shadow_suspicion"
            ),
            dead_execution_path_suspicion=authority_signals.get(
                "dead_execution_path_suspicion"
            ),
            topology_mismatch_suspicion=authority_signals.get(
                "topology_mismatch_suspicion"
            ),
        )
        confidence = round(max(0.0, min(1.0, confidence * 0.85 + authority_score * 0.15)), 3)

        effective_min_confidence = (
            minimum_confidence
            if minimum_confidence is not None
            else self.minimum_confidence
        )

        stage_status = {
            "object_locality": "ok" if object_locality else "missing",
            "execution_locality": "ok" if execution_locality else "missing",
            "ownership_locality": "ok" if ownership_locality else "missing",
        }

        missing_sources = [
            source_name
            for source_name, status in stage_status.items()
            if status != "ok"
        ]

        strict_mode = self.mode in (
            "strict",
            "deterministic_continuity_stabilization",
        )
        enforcement_active = strict_mode or enforce
        if manual_override:
            enforcement_active = False

        fallback_allowed = self.allow_semantic_fallback and not enforcement_active
        if manual_override:
            fallback_allowed = True

        result = {
            "object_id": object_id,
            "path_id": path_id,
            "owner_id": lookup_owner,
            "object_locality": object_locality,
            "execution_locality": execution_locality,
            "ownership_locality": ownership_locality,
            "anchors": anchors_info["anchors"],
            "anchor_scores": anchors_info["anchor_scores"],
            "duplicate_lineages": anchors_info["duplicate_lineages"],
            "stale_lineages": [],
            "source_counts": {
                "object_locality": len(object_locality),
                "execution_locality": len(execution_locality),
                "ownership_locality": len(ownership_locality),
                "total_unique": len(anchors_info["anchors"]),
            },
            "scores": {
                "locality_score": locality_score,
                "runtime_score": runtime_score,
                "ownership_score": ownership_score,
                "propagation_score": propagation_score,
                "confidence": confidence,
            },
            "token_estimate": max(1, len(anchors_info["anchors"])),
            "retrieval_latency_ms": round((perf_counter() - start) * 1000, 2),
            "retrieval_source_count": anchors_info["retrieval_source_count"],
            "fallback_allowed": fallback_allowed,
            "retrieval_mode": self.mode,
            "retrieval_policy": {
                "enforcement_active": enforcement_active,
                "manual_override": manual_override,
                "fallback_allowed": fallback_allowed,
                "minimum_confidence": effective_min_confidence,
                "missing_sources": missing_sources,
            },
            "stage_status": stage_status,
            "authority_signals": {
                "runtime_confirmed_locality": bool(
                    authority_signals.get("runtime_confirmed_locality", False)
                ),
                "locality_authority_confidence": round(
                    float(authority_signals.get("locality_authority_confidence", 0.0)
                    or 0.0),
                    3,
                ),
                "continuity_survivability_confidence": round(
                    float(
                        authority_signals.get(
                            "continuity_survivability_confidence", 0.0
                        )
                        or 0.0
                    ),
                    3,
                ),
                "duplicate_shadow_suspicion": round(
                    float(authority_signals.get("duplicate_shadow_suspicion", 0.0)
                    or 0.0),
                    3,
                ),
                "dead_execution_path_suspicion": round(
                    float(
                        authority_signals.get("dead_execution_path_suspicion", 0.0)
                        or 0.0
                    ),
                    3,
                ),
                "topology_mismatch_suspicion": round(
                    float(authority_signals.get("topology_mismatch_suspicion", 0.0)
                    or 0.0),
                    3,
                ),
                "authority_weight": authority_score,
            },
        }

        if not anchors_info["anchors"]:
            result["retrieval_status"] = "failed"
        elif confidence < effective_min_confidence:
            result["retrieval_status"] = "weak"
        else:
            result["retrieval_status"] = "ok"

        self.retrieval_metadata[object_id] = result

        if manual_override:
            LOG.warning(
                "Manual override enabled for retrieval of %s; fallback is explicit.",
                object_id,
            )
            return result

        if enforcement_active and result["retrieval_status"] != "ok":
            LOG.warning(
                "Strict retrieval requested for object_id=%s but returning advisory status=%s.",
                object_id,
                result["retrieval_status"],
            )

        if not anchors_info["anchors"]:
            LOG.warning(
                "Semantic fallback allowed for object_id=%s; retrieval produced no anchors. "
                "Check retrieval metadata for missing topology components.",
                object_id,
            )
        elif confidence < effective_min_confidence:
            LOG.warning(
                "Semantic fallback allowed for object_id=%s; low confidence retrieval (%.3f < %.3f).",
                object_id,
                confidence,
                effective_min_confidence,
            )
        elif missing_sources:
            LOG.info(
                "Partial continuity retrieval for object_id=%s; missing sources=%s; fallback_allowed=%s.",
                object_id,
                missing_sources,
                fallback_allowed,
            )

        return result

    def build_minimal_context(
        self,
        object_id: str,
        path_id: Optional[str] = None,
        owner_id: Optional[str] = None,
        continuity_signals: Optional[Dict[str, object]] = None,
        enforce: bool = False,
        manual_override: bool = False,
        minimum_confidence: Optional[float] = None,
    ) -> Dict[str, object]:
        retrieval = self.retrieve_continuity_context(
            object_id=object_id,
            path_id=path_id,
            owner_id=owner_id,
            continuity_signals=continuity_signals,
            enforce=enforce,
            manual_override=manual_override,
            minimum_confidence=minimum_confidence,
        )

        return {
            "object_id": object_id,
            "locality": retrieval["anchors"],
            "anchors": retrieval["anchors"],
            "confidence": retrieval["scores"]["confidence"],
            "retrieval_score": sum(retrieval["scores"].values()) / len(retrieval["scores"]),
            "token_estimate": retrieval["token_estimate"],
            "telemetry": retrieval,
        }

    def to_dict(self) -> Dict[str, object]:
        return {
            "retrieval_metadata": self.retrieval_metadata,
        }
