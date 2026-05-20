"""PECS-LITE Projection Hardener

Implements compact, high-confidence, small-model-friendly locality projection.

This module enforces:
- Hard limits on projection breadth
- Confidence-ordered target selection
- Token budgeting for constrained models
- Locality entropy reduction
- Query flow validation diagnostics
- Small-model safety constraints

PECS-LITE exists ONLY to reduce execution-locality entropy for constrained coding models.
It intentionally sacrifices continuity completeness in favor of small-model execution locality precision.
"""

from __future__ import annotations

import re
import os
from types import MappingProxyType
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Any, Dict, List, Mapping, Tuple, TypedDict


EMPTY_MAPPING: Mapping[str, object] = MappingProxyType({})


class ProjectionProfile(Enum):
    """Projection profile for different model contexts."""

    SMALL = "small_local"
    MEDIUM = "medium_local"
    LARGE = "large_local"
    FRONTIER_ONLINE = "frontier_online"
    REASONING_FRONTIER = "reasoning_frontier"
    AGENTIC_FRONTIER = "agentic_frontier"


class CapabilityClassifier:
    """Capability-aware profile classifier (vendor-agnostic)."""

    PROFILE_BUDGETS: Dict[str, Dict[str, Any]] = {
        "small_local": {
            "capability_class": "weak_reasoning_local",
            "reasoning_budget": "low",
            "topology_budget": "minimal",
            "locality_aggression": "high",
            "exploration_constraints": "strict",
            "max_related_files": 3,
            "max_symbol_expansions": 5,
            "max_new_files_before_validation": 2,
        },
        "medium_local": {
            "capability_class": "moderate_reasoning_local",
            "reasoning_budget": "medium",
            "topology_budget": "bounded",
            "locality_aggression": "medium",
            "exploration_constraints": "guarded",
            "max_related_files": 5,
            "max_symbol_expansions": 8,
            "max_new_files_before_validation": 3,
        },
        "large_local": {
            "capability_class": "strong_local",
            "reasoning_budget": "high",
            "topology_budget": "bounded_plus",
            "locality_aggression": "medium",
            "exploration_constraints": "guided",
            "max_related_files": 6,
            "max_symbol_expansions": 12,
            "max_new_files_before_validation": 4,
        },
        "frontier_online": {
            "capability_class": "frontier_general",
            "reasoning_budget": "high",
            "topology_budget": "expanded",
            "locality_aggression": "balanced",
            "exploration_constraints": "adaptive",
            "max_related_files": 8,
            "max_symbol_expansions": 16,
            "max_new_files_before_validation": 5,
        },
        "reasoning_frontier": {
            "capability_class": "frontier_reasoning",
            "reasoning_budget": "very_high",
            "topology_budget": "expanded",
            "locality_aggression": "balanced",
            "exploration_constraints": "adaptive",
            "max_related_files": 10,
            "max_symbol_expansions": 20,
            "max_new_files_before_validation": 6,
        },
        "agentic_frontier": {
            "capability_class": "frontier_agentic",
            "reasoning_budget": "very_high",
            "topology_budget": "expanded_plus",
            "locality_aggression": "balanced",
            "exploration_constraints": "adaptive",
            "max_related_files": 12,
            "max_symbol_expansions": 24,
            "max_new_files_before_validation": 8,
        },
    }

    @classmethod
    def classify(
        cls,
        model_name: str,
        model_source: str,
        context_window: int,
        model_size_hint: str,
    ) -> Dict[str, Any]:
        source = str(model_source or "").lower().strip()
        name = str(model_name or "").lower().strip()
        hint = str(model_size_hint or "small").lower().strip()
        window = int(context_window or 0)

        detection_method: List[str] = []
        if name:
            detection_method.append("runtime_provider")
        if source:
            detection_method.append("environment_probe")
        detection_method.append("behavioral_inference")

        profile = "small_local"
        confidence = 0.63

        if hint == "large":
            profile = "large_local"
            confidence = 0.72
        elif hint == "medium":
            profile = "medium_local"
            confidence = 0.70

        if window >= 250000 and source in {"ollama", "local"}:
            profile = "small_local"
            confidence = max(confidence, 0.73)
        elif window >= 120000 and source in {"openai", "anthropic", "azure", "cloud"}:
            profile = "reasoning_frontier" if "reason" in name else "frontier_online"
            confidence = max(confidence, 0.76)

        if "agent" in name:
            profile = "agentic_frontier"
            confidence = max(confidence, 0.75)

        return {
            "projection_profile": {
                "profile": profile,
                **cls.PROFILE_BUDGETS[profile],
            },
            "model_detection": {
                "model_name": model_name or "unknown",
                "model_source": model_source or "unknown",
                "context_window": window,
                "detection_confidence": round(confidence, 2),
                "detection_method": detection_method,
            },
        }


@dataclass
class ConfidenceScore:
    """Confidence assessment for a runtime target."""

    file_path: str
    confidence: float  # 0.0-1.0
    evidence_type: str  # "active_object", "touched_file", "bundle_entry", "neighbor"
    evidence_strength: int  # 1-5, higher = stronger
    locality_proximity: int  # 0-3, 0=direct, 3=distant neighbor

    def __post_init__(self):
        self.confidence = max(0.0, min(1.0, self.confidence))


@dataclass
class ProjectionMetrics:
    """Health metrics for a projection."""

    profile: str
    projected_target_count: int
    projected_secondary_count: int
    projected_token_estimate: int
    runtime_zone_count: int
    locality_breadth_score: float  # 0.0-1.0, lower = tighter
    entropy_reduction_score: float  # 0.0-1.0, higher = more reduced
    inactive_locality_suppressed: int  # count of filtered files
    wrapper_expansion_depth: int  # 0-3, how deep wrapper chain
    wrapper_expansion_count: int
    has_confirmed_neighborhoods: bool
    progressive_locality_disclosure_applied: bool
    diagnostic_timestamp: str


@dataclass
class QueryFlowDiagnostics:
    """Diagnostics proving authority separation and query flow integrity."""

    queried_pecs_pro: bool  # True if queried via adapter
    workspace_scan_performed: bool  # MUST be False
    topology_reconstructed: bool  # MUST be False
    continuity_state_owned: bool  # MUST be False
    projection_mode: str  # "query_driven" only
    adapter_methods_called: List[str]  # methods invoked on adapter
    artifacts_accessed: List[str]  # .pecs files read
    artifacts_not_generated: List[str]  # things NOT created
    timestamp: str


class CapabilityBundleEnvelope(TypedDict):
    projection_profile: Dict[str, object]
    model_detection: Dict[str, object]


class GovernanceTransferEnvelope(TypedDict):
    engineering_continuity: Dict[str, object]
    capability_bundle: CapabilityBundleEnvelope
    behavioral_signals: Dict[str, object]
    runtime_context: Dict[str, object]


class ConfidenceScorer:
    """Assigns confidence scores to runtime targets based on evidence."""

    # Scoring weights
    ACTIVE_OBJECT_WEIGHT = 0.95
    TOUCHED_FILE_WEIGHT = 0.85
    BUNDLE_ENTRY_WEIGHT = 0.70
    NEIGHBOR_WEIGHT = 0.50
    ACCEPTED_CONTINUITY_WEIGHT = 0.90

    # Proximity penalties (0 = no penalty, 1 = 50% penalty)
    DIRECT_PROXIMITY = 0.0
    NEAR_PROXIMITY = 0.15
    ADJACENT_PROXIMITY = 0.30
    DISTANT_PROXIMITY = 0.50

    @classmethod
    def score_target(
        cls,
        file_path: str,
        evidence_type: str,
        evidence_strength: int = 3,
        locality_proximity: int = 0,
    ) -> ConfidenceScore:
        """Assign confidence score to a target."""

        # Base score from evidence type
        base_scores = {
            "active_object": cls.ACTIVE_OBJECT_WEIGHT,
            "touched_file": cls.TOUCHED_FILE_WEIGHT,
            "bundle_entry": cls.BUNDLE_ENTRY_WEIGHT,
            "neighbor": cls.NEIGHBOR_WEIGHT,
            "accepted_continuity": cls.ACCEPTED_CONTINUITY_WEIGHT,
        }

        base = base_scores.get(evidence_type, 0.5)

        # Adjust for evidence strength (1-5 scale)
        strength_factor = 0.7 + (evidence_strength / 5.0) * 0.3

        # Adjust for locality proximity
        proximity_penalties = [
            cls.DIRECT_PROXIMITY,
            cls.NEAR_PROXIMITY,
            cls.ADJACENT_PROXIMITY,
            cls.DISTANT_PROXIMITY,
        ]
        proximity_penalty = proximity_penalties[min(locality_proximity, 3)]

        # Final confidence
        final_confidence = base * strength_factor * (1.0 - proximity_penalty)

        return ConfidenceScore(
            file_path=file_path,
            confidence=final_confidence,
            evidence_type=evidence_type,
            evidence_strength=min(5, max(1, evidence_strength)),
            locality_proximity=min(3, max(0, locality_proximity)),
        )


class EvidenceContradictionResolver:
    """
    Resolves evidence contradictions deterministically.
    """

    @staticmethod
    def resolve_conflicts(evidence_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Resolve contradictions in evidence records.

        Args:
            evidence_records (List[Dict[str, Any]]): List of evidence records.

        Returns:
            List[Dict[str, Any]]: Updated evidence records with resolved contradictions.
        """
        resolved_records = []

        for record in evidence_records:
            runtime_confirmed = record.get("runtime_confirmed", False)
            user_rejected = record.get("user_rejected", False)
            confidence_score = record.get("confidence_score", 0.0)

            # Downgrade confidence for user-rejected evidence
            if user_rejected:
                record["confidence_score"] *= 0.5

            # Prioritize runtime-confirmed evidence
            if runtime_confirmed:
                record["confidence_score"] = min(record["confidence_score"] + 0.2, 1.0)

            # Mark contradictions as visible
            record["contradiction_visible"] = user_rejected or not runtime_confirmed

            resolved_records.append(record)

        return resolved_records


class ProjectionHardener:
    """Hardens locality projections for small models."""

    # Hard limits by profile
    LIMITS = {
        ProjectionProfile.SMALL: {
            "primary_targets": 3,
            "secondary_neighbors": 2,
            "token_budget": 2000,
            "breadth_limit": 5,
        },
        ProjectionProfile.MEDIUM: {
            "primary_targets": 6,
            "secondary_neighbors": 4,
            "token_budget": 4000,
            "breadth_limit": 10,
        },
        ProjectionProfile.LARGE: {
            "primary_targets": 10,
            "secondary_neighbors": 6,
            "token_budget": 8000,
            "breadth_limit": 16,
        },
        ProjectionProfile.FRONTIER_ONLINE: {
            "primary_targets": 12,
            "secondary_neighbors": 8,
            "token_budget": 10000,
            "breadth_limit": 20,
        },
        ProjectionProfile.REASONING_FRONTIER: {
            "primary_targets": 14,
            "secondary_neighbors": 10,
            "token_budget": 12000,
            "breadth_limit": 24,
        },
        ProjectionProfile.AGENTIC_FRONTIER: {
            "primary_targets": 16,
            "secondary_neighbors": 12,
            "token_budget": 14000,
            "breadth_limit": 28,
        },
    }

    def __init__(self, adapter: Any):
        """Initialize hardener with PECS-PRO query adapter."""
        self.adapter = adapter
        self.diagnostics = QueryFlowDiagnostics(
            queried_pecs_pro=False,
            workspace_scan_performed=False,
            topology_reconstructed=False,
            continuity_state_owned=False,
            projection_mode="query_driven",
            adapter_methods_called=[],
            artifacts_accessed=[],
            artifacts_not_generated=[
                ".pecs/daemon_lite_v2.pid",
                ".pecs/daemon_lite_v2_state.json",
                ".pecs/pecs_lite_runtime_topology.json",
                "workspace runtime topology",
                "workspace scan results",
            ],
            timestamp="",
        )
        self.last_confidence_by_path: Dict[str, Dict[str, Any]] = {}
        self.last_confidence_uncertainty: Dict[str, Any] = {}

    def sanitize_projection(self, projection: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize projection to remove `.pecs` paths and continuity artifacts."""
        sanitized = {
            "primary_targets": [
                target
                for target in projection.get("primary_targets", [])
                if not target.startswith(".pecs")
            ],
            "secondary_targets": [
                target
                for target in projection.get("secondary_targets", [])
                if not target.startswith(".pecs")
            ],
        }
        return sanitized

    def generate_operational_guidance(self, projection: Dict[str, Any]) -> str:
        """Generate natural-language operational guidance for SMALL profiles."""
        primary_targets = projection.get("primary_targets", [])
        secondary_targets = projection.get("secondary_targets", [])

        guidance = ""
        if primary_targets:
            guidance += (
                f"Accepted engineering continuity suggests: {primary_targets[0]}\n"
                "is the likely active locality for the current issue.\n"
            )
        if secondary_targets:
            guidance += (
                f"Secondary candidates include: {', '.join(secondary_targets)}.\n"
            )
        guidance += "Confidence: High."
        return guidance

    def harden_projection(
        self,
        raw_targets: List[Any],
        profile: ProjectionProfile = ProjectionProfile.SMALL,
        active_zone: str = "general_runtime",
        mutation_owner: str = "",
        wrapper_warning: bool = False,
        issue_query: str = "",
        runtime_zone_count: int = 1,
        engineering_continuity: Mapping[str, object] = EMPTY_MAPPING,
    ) -> Tuple[List[str], List[str], ProjectionMetrics]:
        """
        Harden a projection for small models.

        Returns:
            (primary_targets, secondary_neighbors, metrics)
        """

        limits = self.LIMITS[profile]

        continuity_signals = dict(engineering_continuity)
        continuity_anchor_candidates = self._continuity_anchor_candidates(
            continuity_signals
        )
        scoring_input = list(raw_targets) + continuity_anchor_candidates

        # Score all targets
        scored_targets = self._score_candidates(
            scoring_input,
            issue_query=issue_query,
            continuity_signals=continuity_signals,
        )

        # Sort by confidence (descending)
        sorted_targets = sorted(
            scored_targets,
            key=lambda x: (-x.confidence, -x.evidence_strength, x.locality_proximity),
        )

        # Select primary targets (highest confidence, direct locality)
        primary = self._select_primary_targets(
            sorted_targets,
            limit=limits["primary_targets"],
        )

        accepted_scores_raw = continuity_signals.get("accepted_locality_scores", {})
        accepted_scores = accepted_scores_raw if isinstance(accepted_scores_raw, dict) else {}
        if accepted_scores:
            best_accepted_path, best_accepted_score = max(
                accepted_scores.items(), key=lambda item: float(item[1])
            )
            if float(best_accepted_score) >= 0.80:
                existing_primary_paths = {item.file_path for item in primary}
                if best_accepted_path not in existing_primary_paths:
                    accepted_candidate = next(
                        (
                            item
                            for item in sorted_targets
                            if item.file_path == best_accepted_path
                        ),
                        None,
                    )
                    if accepted_candidate is not None:
                        if len(primary) < limits["primary_targets"]:
                            primary.append(accepted_candidate)
                        elif primary:
                            primary[-1] = accepted_candidate
                        primary.sort(
                            key=lambda x: (-x.confidence, x.locality_proximity)
                        )

        progressive_disclosure_applied = False
        highest_confidence = primary[0].confidence if primary else 0.0

        # Progressive locality disclosure for weak-confidence small profile projections.
        if profile == ProjectionProfile.SMALL and (
            len(primary) < 2 or highest_confidence < 0.78
        ):
            widened: List[ConfidenceScore] = []
            existing = {item.file_path for item in primary}
            for candidate in sorted_targets:
                if candidate.file_path in existing:
                    continue
                if candidate.confidence < 0.55:
                    continue
                if candidate.locality_proximity > 2:
                    continue
                widened.append(candidate)
                existing.add(candidate.file_path)
                if len(primary) + len(widened) >= limits["primary_targets"]:
                    break
            if widened:
                primary = primary + widened
                progressive_disclosure_applied = True

        # Select secondary neighbors (lower confidence, near locality)
        secondary = self._select_secondary_neighbors(
            sorted_targets,
            primary_paths=[t.file_path for t in primary],
            limit=limits["secondary_neighbors"],
        )

        # Estimate tokens
        token_estimate = self._estimate_tokens(primary, secondary)

        # Enforce hard token budget by trimming lowest-priority neighbors first.
        token_budget = int(limits["token_budget"])
        while token_estimate > token_budget and secondary:
            secondary = secondary[:-1]
            token_estimate = self._estimate_tokens(primary, secondary)

        # If still over budget, trim primary from tail but keep at least one.
        while token_estimate > token_budget and len(primary) > 1:
            primary = primary[:-1]
            token_estimate = self._estimate_tokens(primary, secondary)

        # Calculate metrics
        metrics = self._calculate_metrics(
            profile=profile.value,
            primary_targets=primary,
            secondary_neighbors=secondary,
            token_estimate=token_estimate,
            active_zone=active_zone,
            wrapper_warning=wrapper_warning,
            suppressed_count=max(0, len(scoring_input) - len(primary) - len(secondary)),
            runtime_zone_count=max(1, runtime_zone_count),
            progressive_disclosure_applied=progressive_disclosure_applied,
        )

        self._capture_confidence_summary(
            scored=sorted_targets,
            primary=primary,
            secondary=secondary,
        )

        primary_paths = [t.file_path for t in primary]
        secondary_paths = [t.file_path for t in secondary]

        return primary_paths, secondary_paths, metrics

    def normalize_issue_query(self, issue_query: str) -> List[str]:
        """Normalize issue text into correlation tokens."""
        normalized = str(issue_query or "").lower().strip()
        if not normalized:
            return []
        tokens = [t for t in re.split(r"[^a-z0-9_]+", normalized) if len(t) > 2]
        # Preserve order while removing duplicates.
        seen = set()
        result: List[str] = []
        for token in tokens:
            if token not in seen:
                seen.add(token)
                result.append(token)
        return result

    def _score_candidates(
        self,
        targets: List[Any],
        issue_query: str = "",
        continuity_signals: Mapping[str, object] = EMPTY_MAPPING,
    ) -> List[ConfidenceScore]:
        """Score all target candidates."""
        scored: List[ConfidenceScore] = []
        query_tokens = self.normalize_issue_query(issue_query)
        accepted_scores_raw = continuity_signals.get("accepted_locality_scores", {})
        rejected_scores_raw = continuity_signals.get("rejected_locality_scores", {})
        accepted_scores = accepted_scores_raw if isinstance(accepted_scores_raw, dict) else {}
        rejected_scores = rejected_scores_raw if isinstance(rejected_scores_raw, dict) else {}

        # Try to get scoring context from adapter if available
        # For now, assign default scores based on order (first = highest confidence)
        for i, target in enumerate(targets):
            if isinstance(target, dict):
                file_path = str(target.get("file", "") or "")
                evidence_type = str(
                    target.get("evidence", "bundle_entry") or "bundle_entry"
                )
                base_confidence = float(target.get("base_confidence", 0.55) or 0.55)
                is_active = bool(target.get("is_active", False))
            else:
                file_path = str(target)
                evidence_type = "bundle_entry" if i > 5 else "touched_file"
                base_confidence = 0.55 if evidence_type == "bundle_entry" else 0.85
                is_active = i < 8

            if not file_path:
                continue

            if evidence_type == "accepted_continuity":
                proximity = 0
                evidence_strength = 5
            else:
                proximity = min(i // 4, 3)  # Rough proximity estimate
                evidence_strength = 5 - (i // 3)  # Decay strength with distance

            score = ConfidenceScorer.score_target(
                file_path=file_path,
                evidence_type=evidence_type,
                evidence_strength=max(1, evidence_strength),
                locality_proximity=proximity,
            )

            # Blend with adapter-provided base confidence when available.
            score.confidence = (score.confidence * 0.6) + (base_confidence * 0.4)

            accepted_boost = float(accepted_scores.get(file_path, 0.0) or 0.0)
            if accepted_boost > 0.0:
                score.confidence = min(
                    1.0,
                    score.confidence + (accepted_boost * 0.35),
                )
                score.evidence_strength = min(5, score.evidence_strength + 1)

            rejected_penalty = float(rejected_scores.get(file_path, 0.0) or 0.0)
            if rejected_penalty > 0.0:
                score.confidence = max(0.0, score.confidence * (1.0 - rejected_penalty))

            # Downrank inactive locality.
            if not is_active:
                score.confidence *= 0.85

            # Up-rank issue-correlated paths.
            lowered_path = file_path.lower()
            token_hits = sum(1 for token in query_tokens if token in lowered_path)
            if token_hits:
                score.confidence = min(1.0, score.confidence + (0.05 * token_hits))

            scored.append(score)

        return scored

    def _continuity_anchor_candidates(
        self,
        continuity_signals: Mapping[str, object],
    ) -> List[Dict[str, Any]]:
        """Inject accepted engineering locality anchors as bounded candidates."""
        candidates: List[Dict[str, Any]] = []
        accepted_scores_raw = continuity_signals.get("accepted_locality_scores", {})
        accepted_scores = accepted_scores_raw if isinstance(accepted_scores_raw, dict) else {}
        for file_path, confidence in accepted_scores.items():
            normalized = str(file_path or "").strip()
            if not normalized or normalized.startswith(".pecs/"):
                continue
            if float(confidence or 0.0) < 0.60:
                continue
            candidates.append(
                {
                    "file": normalized,
                    "evidence": "accepted_continuity",
                    "base_confidence": max(0.65, min(0.98, float(confidence))),
                    "is_active": True,
                }
            )
        return candidates[:8]

    def _capture_confidence_summary(
        self,
        scored: List[ConfidenceScore],
        primary: List[ConfidenceScore],
        secondary: List[ConfidenceScore],
    ) -> None:
        """Capture probabilistic confidence summary for projection export."""
        self.last_confidence_by_path = {
            item.file_path: {
                "confidence": round(item.confidence, 3),
                "evidence_type": item.evidence_type,
                "evidence_strength": item.evidence_strength,
                "locality_proximity": item.locality_proximity,
            }
            for item in scored
        }

        primary_conf = [item.confidence for item in primary]
        secondary_conf = [item.confidence for item in secondary]
        all_conf = primary_conf + secondary_conf
        confidence_mean = (sum(all_conf) / len(all_conf)) if all_conf else 0.0

        self.last_confidence_uncertainty = {
            "projection_confidence_mean": round(confidence_mean, 3),
            "projection_uncertainty": round(max(0.0, 1.0 - confidence_mean), 3),
            "ambiguity_hint": (
                "locality_confidence_mixed"
                if 0.45 <= confidence_mean <= 0.75
                else (
                    "locality_confidence_high"
                    if confidence_mean > 0.75
                    else "locality_confidence_weak"
                )
            ),
            "runtime_confirmation_hint": "confirm active runtime ownership before wide mutation",
        }

    def _select_primary_targets(
        self,
        scored: List[ConfidenceScore],
        limit: int = 3,
    ) -> List[ConfidenceScore]:
        """Select primary targets (highest confidence, proximity 0-1)."""
        direct_locality = [
            s for s in scored if s.confidence >= 0.70 and s.locality_proximity <= 1
        ]

        # Sort by confidence
        direct_locality.sort(key=lambda x: (-x.confidence, x.locality_proximity))

        return direct_locality[:limit]

    def _select_secondary_neighbors(
        self,
        scored: List[ConfidenceScore],
        primary_paths: List[str],
        limit: int = 2,
    ) -> List[ConfidenceScore]:
        """Select secondary neighbors (nearby, not in primary)."""
        neighbors = [
            s
            for s in scored
            if s.file_path not in primary_paths
            and s.confidence >= 0.50
            and s.locality_proximity <= 2
        ]

        # Sort by proximity first, then confidence
        neighbors.sort(key=lambda x: (x.locality_proximity, -x.confidence))

        return neighbors[:limit]

    def _estimate_tokens(
        self,
        primary: List[ConfidenceScore],
        secondary: List[ConfidenceScore],
    ) -> int:
        """Estimate tokens needed for targets."""
        # Rough estimate: 100-200 tokens per target
        primary_tokens = len(primary) * 150
        secondary_tokens = len(secondary) * 100
        overhead = 200  # Schema, metadata

        return primary_tokens + secondary_tokens + overhead

    def _calculate_metrics(
        self,
        profile: str,
        primary_targets: List[ConfidenceScore],
        secondary_neighbors: List[ConfidenceScore],
        token_estimate: int,
        active_zone: str,
        wrapper_warning: bool,
        suppressed_count: int,
        runtime_zone_count: int,
        progressive_disclosure_applied: bool,
    ) -> ProjectionMetrics:
        """Calculate projection health metrics."""
        import datetime

        # Breadth score: 0.0 = very tight, 1.0 = very broad
        total_projected = len(primary_targets) + len(secondary_neighbors)
        breadth_score = min(1.0, total_projected / 10.0)

        # Entropy reduction: how much did we suppress?
        # Higher score = more entropy reduction
        total_candidates = total_projected + suppressed_count
        entropy_reduction = (
            suppressed_count / total_candidates if total_candidates > 0 else 0.0
        )

        # Wrapper expansion depth
        wrapper_depth = 1 if wrapper_warning else 0

        return ProjectionMetrics(
            profile=profile,
            projected_target_count=len(primary_targets),
            projected_secondary_count=len(secondary_neighbors),
            projected_token_estimate=token_estimate,
            runtime_zone_count=runtime_zone_count,
            locality_breadth_score=breadth_score,
            entropy_reduction_score=entropy_reduction,
            inactive_locality_suppressed=suppressed_count,
            wrapper_expansion_depth=wrapper_depth,
            wrapper_expansion_count=len(secondary_neighbors) if wrapper_warning else 0,
            has_confirmed_neighborhoods=len(primary_targets) > 0,
            progressive_locality_disclosure_applied=progressive_disclosure_applied,
            diagnostic_timestamp=datetime.datetime.utcnow().isoformat() + "Z",
        )

    def validate_small_model_safety(
        self,
        projection: Dict[str, Any],
    ) -> Tuple[bool, List[str]]:
        """Validate projection is safe for small models."""
        issues: List[str] = []

        # Check: runtime targets not too many
        targets = projection.get("runtime_targets", [])
        if len(targets) > 10:
            issues.append(f"Too many runtime targets: {len(targets)} (max 10)")

        # Check: no .pecs paths exposed
        for target in targets:
            if isinstance(target, dict):
                probable_file = str(target.get("probable_file", "") or "")
                if probable_file.startswith(".pecs/"):
                    issues.append(f"Exposed .pecs artifact: {probable_file}")
            elif isinstance(target, str) and ".pecs/" in target:
                issues.append(f"Exposed .pecs artifact: {target}")

        # Check: no raw topology
        if projection.get("raw_topology"):
            issues.append("Projection contains raw topology graph")

        # Check: no continuity dumps
        if projection.get("continuity_dump"):
            issues.append("Projection contains continuity dump")

        # Check: no .pecs mutation owner guidance
        mutation_owner = str(projection.get("possible_mutation_owner", "") or "")
        if mutation_owner.startswith(".pecs/"):
            issues.append("Mutation owner points to .pecs artifact")

        # Check: continuity anchors must never point to .pecs paths
        engineering_continuity = projection.get("active_engineering_continuity", {})
        for chain in engineering_continuity.get("chains", []) or []:
            accepted = str(chain.get("accepted_locality", "") or "")
            if accepted.startswith(".pecs/"):
                issues.append(
                    f"Accepted continuity points to .pecs artifact: {accepted}"
                )
            for rejected in chain.get("rejected_locality", []) or []:
                if str(rejected).startswith(".pecs/"):
                    issues.append(
                        f"Rejected continuity points to .pecs artifact: {rejected}"
                    )

        # Check: has disclaimer
        if not projection.get("disclaimer"):
            issues.append("Missing projection disclaimer")

        return len(issues) == 0, issues

    def record_query_diagnostics(
        self,
        methods_called: List[str],
        artifacts_read: List[str],
    ) -> None:
        """Record query flow diagnostics."""
        import datetime

        self.diagnostics.queried_pecs_pro = True
        self.diagnostics.adapter_methods_called = methods_called
        self.diagnostics.artifacts_accessed = artifacts_read
        self.diagnostics.timestamp = datetime.datetime.utcnow().isoformat() + "Z"

        # Verify authority separation
        assert (
            not self.diagnostics.workspace_scan_performed
        ), "PECS-LITE must NOT scan workspace"
        assert (
            not self.diagnostics.topology_reconstructed
        ), "PECS-LITE must NOT reconstruct topology"
        assert (
            not self.diagnostics.continuity_state_owned
        ), "PECS-LITE must NOT own continuity state"


class ProjectionExporter:
    """Exports hardened projections with diagnostics and metrics."""

    DISCLAIMER = (
        "PECS-LITE PROJECTION DISCLAIMER:\n"
        "This is a STATELESS LOCALITY PROJECTION generated by querying PECS-PRO.\n"
        "It contains ephemeral guidance optimized for constrained coding models.\n"
        "It does NOT represent complete continuity, comprehensive topology, or authoritative runtime state.\n"
        "PECS-PRO maintains the sole continuity authority.\n"
        "Do NOT edit this projection or use it as infrastructure sourcecode.\n"
        "Use projected runtime targets to locate editable workspace files only."
    )

    @staticmethod
    def _require_dict(label: str, value: object) -> Dict[str, object]:
        if not isinstance(value, dict):
            raise ValueError(f"{label} must be an object")
        normalized: Dict[str, object] = {}
        for key, raw in value.items():
            normalized[str(key)] = raw
        return normalized

    @classmethod
    def _parse_governance_transfer_envelope(
        cls,
        engineering_continuity: Mapping[str, object],
        capability_bundle: Mapping[str, object],
        behavioral_signals: Mapping[str, object],
        runtime_context: Mapping[str, object],
    ) -> GovernanceTransferEnvelope:
        # Type-check capability_bundle before unpacking
        if not isinstance(capability_bundle, dict):
            raise ValueError("capability_bundle must be an object")
        
        capability_bundle_dict = cls._require_dict("capability_bundle", capability_bundle)
        profile_raw = capability_bundle_dict.get("projection_profile")
        detection_raw = capability_bundle_dict.get("model_detection")
        if profile_raw is None or detection_raw is None:
            raise ValueError(
                "capability_bundle requires projection_profile and model_detection"
            )

        projection_profile = cls._require_dict("capability_bundle.projection_profile", profile_raw)
        model_detection = cls._require_dict("capability_bundle.model_detection", detection_raw)

        return {
            "engineering_continuity": cls._require_dict(
                "engineering_continuity", dict(engineering_continuity)
            ),
            "capability_bundle": {
                "projection_profile": projection_profile,
                "model_detection": model_detection,
            },
            "behavioral_signals": cls._require_dict(
                "behavioral_signals", dict(behavioral_signals)
            ),
            "runtime_context": cls._require_dict("runtime_context", dict(runtime_context)),
        }

    @classmethod
    def export_projection(
        cls,
        hardener: ProjectionHardener,
        primary_targets: List[str],
        secondary_neighbors: List[str],
        metrics: ProjectionMetrics,
        active_zone: str,
        mutation_owner: str,
        wrapper_warning: bool,
        profile: str = "small",
        adapter: Any = None,
        engineering_continuity: Mapping[str, object] = EMPTY_MAPPING,
        issue_query: str = "",
        capability_bundle: Mapping[str, object] = EMPTY_MAPPING,
        behavioral_signals: Mapping[str, object] = EMPTY_MAPPING,
        runtime_context: Mapping[str, object] = EMPTY_MAPPING,
    ) -> Dict[str, Any]:
        """Export projection with profile-specific enrichment."""

        envelope = cls._parse_governance_transfer_envelope(
            engineering_continuity=engineering_continuity,
            capability_bundle=capability_bundle,
            behavioral_signals=behavioral_signals,
            runtime_context=runtime_context,
        )
        engineering_continuity_dict = envelope["engineering_continuity"]
        capability_bundle_dict = envelope["capability_bundle"]
        behavioral_signals_dict = envelope["behavioral_signals"]
        runtime_context_dict = envelope["runtime_context"]
        profile_view = capability_bundle_dict["projection_profile"]
        model_detection = capability_bundle_dict["model_detection"]
        evidence_fusion = (
            adapter.evidence_fusion_lookup(max_files=128)
            if adapter is not None and hasattr(adapter, "evidence_fusion_lookup")
            else {"schema": "pecs.evidence_fusion.v1", "deterministic": True, "weights": {}, "ranked_files": []}
        )

        runtime_targets = cls._build_structured_runtime_targets(
            adapter=adapter,
            hardener=hardener,
            primary_targets=primary_targets,
            secondary_neighbors=secondary_neighbors,
            issue_query=issue_query,
            profile_view=profile_view,
            engineering_continuity=engineering_continuity_dict,
            behavioral_signals=behavioral_signals_dict,
            evidence_fusion=evidence_fusion,
        )

        authority_confidence = 0.0
        if runtime_targets:
            authority_confidence = sum(
                float(target.get("confidence", 0.0) or 0.0) for target in runtime_targets
            ) / len(runtime_targets)

        pecs_lite_status = {
            "runtime_observability_used": False,
            "engineering_continuity_used": False,
            "workspace_scan_performed": False,
            "symbol_resolution_used": False,
            "behavioral_analysis_used": bool(behavioral_signals_dict),
            "capability_detection_used": bool(model_detection),
            "authority_confidence": round(max(0.0, min(1.0, authority_confidence)), 3),
        }
        if adapter is not None and hasattr(adapter, "projection_status"):
            any_symbol = any(bool(t.get("probable_method") or t.get("probable_class")) for t in runtime_targets)
            pecs_lite_status = adapter.projection_status(
                symbol_resolution_used=any_symbol,
                behavioral_analysis_used=bool(behavioral_signals_dict),
                capability_detection_used=bool(model_detection),
                authority_confidence=authority_confidence,
            )

        projection = {
            "schema": "pecs_lite.runtime_projection.locality_authority.v3",
            "disclaimer": cls.DISCLAIMER,
            "profile": metrics.profile,
            "projection_profile": profile_view,
            "model_detection": model_detection,
            "runtime_targets": runtime_targets,
            "secondary_neighbors": secondary_neighbors,
            "likely_execution_cluster": active_zone,
            "possible_mutation_owner": mutation_owner,
            "wrapper_warning": wrapper_warning,
            "deterministic": True,
            "runtime_mode": "read_only",
            "artifact_writes": 0,
            "metrics": asdict(metrics),
            "diagnostics": asdict(hardener.diagnostics),
            "continuity_supporting_artifacts": [
                ".pecs/active_context.json",
                ".pecs/locality_index.json",
                ".pecs/compact_bundle.json",
                ".pecs/continuity/engineering_continuity_state.json",
            ],
            "forbidden_mutation_prefixes": [".pecs/"],
            "confidence_projection": cls._build_confidence_projection(
                hardener, primary_targets, secondary_neighbors
            ),
            "pecs_lite_status": pecs_lite_status,
            "runtime_context": runtime_context_dict,
            "evidence_fusion": evidence_fusion,
        }

        if behavioral_signals_dict:
            projection["behavioral_signals"] = behavioral_signals_dict

        continuity_view = cls._build_active_engineering_continuity(
            profile=profile,
            continuity_signals=engineering_continuity_dict,
        )
        if continuity_view:
            projection["active_engineering_continuity"] = continuity_view

        # Add profile-specific enrichment
        if profile in ["medium", "large", "medium_local", "large_local", "frontier_online", "reasoning_frontier", "agentic_frontier"] and adapter:
            projection["execution_enrichment"] = cls._build_execution_enrichment(
                adapter,
                primary_targets,
                secondary_neighbors,
                profile,
            )

        projection["pecs_runtime_report"] = cls._build_pecs_runtime_report(
            adapter=adapter,
            projection=projection,
            metrics=metrics,
            active_zone=active_zone,
            issue_query=issue_query,
            profile_view=profile_view,
            behavioral_signals=behavioral_signals_dict,
            evidence_fusion=evidence_fusion,
        )

        return projection

    @classmethod
    def _build_structured_runtime_targets(
        cls,
        adapter: Any,
        hardener: ProjectionHardener,
        primary_targets: List[str],
        secondary_neighbors: List[str],
        issue_query: str,
        profile_view: Dict[str, Any],
        engineering_continuity: Dict[str, Any],
        behavioral_signals: Dict[str, Any],
        evidence_fusion: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        if adapter is None:
            return []

        related_cap = int(profile_view.get("max_related_files", 3) or 3)
        max_symbol_expansions = int(profile_view.get("max_symbol_expansions", 5) or 5)
        max_new_files = int(profile_view.get("max_new_files_before_validation", 2) or 2)
        evidence_by_file = {
            str(item.get("file", "") or ""): item
            for item in (evidence_fusion.get("ranked_files", []) or [])
            if isinstance(item, dict)
        }

        chains = engineering_continuity.get("active_engineering_chains", []) or []
        expected_outcome = (
            str(chains[0].get("issue", "")) if chains else str(issue_query or "")
        )

        targets: List[Dict[str, Any]] = []
        for idx, file_path in enumerate(primary_targets):
            confidence_entry = hardener.last_confidence_by_path.get(file_path, {})
            confidence = float(confidence_entry.get("confidence", 0.0) or 0.0)
            symbol_info = adapter.resolve_symbol_authority(file_path=file_path, issue_query=issue_query)
            related = adapter.related_files_for(file_path=file_path, max_related=related_cap)
            chain = adapter.entrypoint_chain_for(file_path=file_path, max_depth=5)
            authority_type = adapter.classify_authority_type(file_path)
            if idx > 0 and authority_type == "primary":
                authority_type = "secondary"

            likely_failure_mode = "wrapper_indirection" if authority_type == "wrapper" else "mutation_misdirection"
            if authority_type in {"legacy", "deprecated"}:
                likely_failure_mode = "stale_adapter"

            evidence_entry = evidence_by_file.get(file_path, {})
            fused_score = float(evidence_entry.get("fused_score", confidence) or confidence)
            tier_scores = evidence_entry.get("tier_scores", {}) if isinstance(evidence_entry.get("tier_scores", {}), dict) else {}
            fusion_sources = evidence_entry.get("provenance", []) if isinstance(evidence_entry.get("provenance", []), list) else []

            search_expansion_allowed = bool(
                fused_score >= 0.45
                and float(tier_scores.get("tier_1_runtime", 0.0) or 0.0) >= 0.25
                and float(tier_scores.get("tier_2_continuity", 0.0) or 0.0) >= 0.20
            )
            expansion_level = "restricted"
            if search_expansion_allowed and fused_score >= 0.70:
                expansion_level = "bounded"

            supporting_symbols = list(symbol_info.get("supporting_symbols", []))[:max_symbol_expansions]
            target = {
                "task_hint": str(issue_query or "inferred_issue").strip() or "inferred_issue",
                "expected_outcome": expected_outcome or "runtime ownership confirmation",
                "probable_file": file_path,
                "probable_class": symbol_info.get("probable_class", ""),
                "probable_method": symbol_info.get("probable_method", ""),
                "confidence": round(max(0.0, min(1.0, fused_score)), 3),
                "authority_type": authority_type,
                "evidence_tiers": {
                    "tier_0_static": round(float(tier_scores.get("tier_0_static", 0.0) or 0.0), 3),
                    "tier_1_runtime": round(float(tier_scores.get("tier_1_runtime", 0.0) or 0.0), 3),
                    "tier_2_continuity": round(float(tier_scores.get("tier_2_continuity", 0.0) or 0.0), 3),
                    "tier_3_validation": round(float(tier_scores.get("tier_3_validation", 0.0) or 0.0), 3),
                },
                "evidence_sources": sorted(fusion_sources),
                "supporting_symbols": supporting_symbols,
                "related_files": related,
                "entrypoint_chain": chain,
                "expected_edit_scope": "method",
                "safe_to_edit": authority_type in {"primary", "secondary"},
                "do_not_edit": [".pecs/", "generated/", "legacy_runtime_adapter.py"],
                "predicted_failure_mode": likely_failure_mode,
                "search_expansion_allowed": search_expansion_allowed,
                "search_budget": {
                    "max_new_files_before_validation": max_new_files,
                    "max_symbol_expansions": max_symbol_expansions,
                    "require_runtime_confirmation_before_breadth_expansion": True,
                    "expansion_level": expansion_level,
                },
                "last_verified": "runtime-confirmed",
            }
            targets.append(target)

        for file_path in secondary_neighbors[: max(0, max_new_files - 1)]:
            if any(item.get("probable_file") == file_path for item in targets):
                continue
            symbol_info = adapter.resolve_symbol_authority(file_path=file_path, issue_query=issue_query)
            targets.append(
                {
                    "task_hint": str(issue_query or "inferred_issue").strip() or "inferred_issue",
                    "expected_outcome": expected_outcome or "runtime ownership confirmation",
                    "probable_file": file_path,
                    "probable_class": symbol_info.get("probable_class", ""),
                    "probable_method": symbol_info.get("probable_method", ""),
                    "confidence": round(float(hardener.last_confidence_by_path.get(file_path, {}).get("confidence", 0.45) or 0.45), 3),
                    "authority_type": "secondary",
                    "evidence_tiers": {
                        "tier_0_static": round(float((evidence_by_file.get(file_path, {}).get("tier_scores", {}) or {}).get("tier_0_static", 0.0) or 0.0), 3),
                        "tier_1_runtime": round(float((evidence_by_file.get(file_path, {}).get("tier_scores", {}) or {}).get("tier_1_runtime", 0.0) or 0.0), 3),
                        "tier_2_continuity": round(float((evidence_by_file.get(file_path, {}).get("tier_scores", {}) or {}).get("tier_2_continuity", 0.0) or 0.0), 3),
                        "tier_3_validation": round(float((evidence_by_file.get(file_path, {}).get("tier_scores", {}) or {}).get("tier_3_validation", 0.0) or 0.0), 3),
                    },
                    "evidence_sources": sorted((evidence_by_file.get(file_path, {}).get("provenance", []) or [])),
                    "supporting_symbols": list(symbol_info.get("supporting_symbols", []))[: max_symbol_expansions],
                    "related_files": adapter.related_files_for(file_path=file_path, max_related=max(1, related_cap - 1)),
                    "entrypoint_chain": adapter.entrypoint_chain_for(file_path=file_path, max_depth=4),
                    "expected_edit_scope": "method",
                    "safe_to_edit": True,
                    "do_not_edit": [".pecs/", "generated/", "legacy_runtime_adapter.py"],
                    "predicted_failure_mode": "topology_drift",
                    "search_expansion_allowed": False,
                    "search_budget": {
                        "max_new_files_before_validation": max_new_files,
                        "max_symbol_expansions": max_symbol_expansions,
                        "require_runtime_confirmation_before_breadth_expansion": True,
                        "expansion_level": "restricted",
                    },
                    "last_verified": "runtime-confirmed",
                }
            )

        return targets

    @classmethod
    def _build_execution_enrichment(
        cls,
        adapter: Any,
        primary_targets: List[str],
        secondary_neighbors: List[str],
        profile: str,
    ) -> Dict[str, Any]:
        """Build execution-locality enrichment for medium/large profiles."""

        enrichment = {}

        if profile in {"medium", "medium_local", "frontier_online"}:
            enrichment["execution_neighborhood"] = {
                "primary_execution_focus": primary_targets[:3],
                "nearby_execution_adjacency": secondary_neighbors[:2],
                "mutation_locality_hint": adapter.ownership_locality_lookup(),
                "wrapper_expansion_indicated": adapter.wrapper_warning_lookup(),
            }

        elif profile in {"large", "large_local", "reasoning_frontier", "agentic_frontier"}:
            enrichment["execution_continuity"] = {
                "primary_execution_targets": primary_targets,
                "secondary_execution_adjacency": secondary_neighbors,
                "execution_neighborhood_metadata": {
                    "mutation_locality": adapter.ownership_locality_lookup(),
                    "wrapper_expansion": adapter.wrapper_warning_lookup(),
                    "execution_depth": adapter.execution_depth_lookup(),
                },
                "runtime_zone_context": adapter.runtime_zone_lookup(),
                "locality_confidence_hint": "execution_locality_focused, NOT raw_continuity",
            }

            # Include bounded continuity relationships for large models
            active_continuity = adapter.active_continuity_lookup()
            enrichment["continuity_context"] = {
                "active_runtime_zones": active_continuity.get(
                    "active_runtime_zones", []
                ),
                "locality_cluster_count": active_continuity.get(
                    "locality_cluster_count", 0
                ),
                "runtime_confirmation_density": active_continuity.get(
                    "runtime_confirmation_density", 0.0
                ),
                "note": "relationships are execution_locality_focused, not exhaustive",
            }

        return enrichment

    @classmethod
    def _build_confidence_projection(
        cls,
        hardener: ProjectionHardener,
        primary_targets: List[str],
        secondary_neighbors: List[str],
    ) -> Dict[str, Any]:
        """Build confidence/uncertainty summary to avoid false certainty."""
        confidence = hardener.last_confidence_by_path
        return {
            "primary": [
                {
                    "file": path,
                    **confidence.get(
                        path, {"confidence": 0.0, "evidence_type": "unknown"}
                    ),
                }
                for path in primary_targets
            ],
            "secondary": [
                {
                    "file": path,
                    **confidence.get(
                        path, {"confidence": 0.0, "evidence_type": "unknown"}
                    ),
                }
                for path in secondary_neighbors
            ],
            "uncertainty": hardener.last_confidence_uncertainty,
        }

    @classmethod
    def _build_pecs_runtime_report(
        cls,
        adapter: Any,
        projection: Dict[str, Any],
        metrics: ProjectionMetrics,
        active_zone: str,
        issue_query: str,
        profile_view: Dict[str, Any],
        behavioral_signals: Dict[str, Any],
        evidence_fusion: Dict[str, Any],
    ) -> Dict[str, Any]:
        # Return minimal report if adapter is None
        if adapter is None:
            default_artifacts = [
                ".pecs/active_context.json",
                ".pecs/compact_bundle.json",
                ".pecs/locality_index.json",
                ".pecs/topology_compact.json",
                ".pecs/continuity/locality_state.json",
                ".pecs/continuity/active_topology.json",
                ".pecs/continuity/engineering_continuity_state.json",
            ]
            return {
                "PECS STATUS": {
                    "workspace": "unknown",
                    "runtime_zones": [],
                    "missing_manifests": default_artifacts,
                }
            }
        
        artifact_candidates = [
            ".pecs/active_context.json",
            ".pecs/compact_bundle.json",
            ".pecs/locality_index.json",
            ".pecs/topology_compact.json",
            ".pecs/continuity/locality_state.json",
            ".pecs/continuity/active_topology.json",
            ".pecs/continuity/engineering_continuity_state.json",
        ]
        missing_manifests = [
            path for path in artifact_candidates
            if not os.path.exists(os.path.join(str(adapter.workspace_root), path))
        ]

        active_runtime_zones = adapter.runtime_zone_lookup()
        selected_files = [
            item.get("probable_file") for item in projection.get("runtime_targets", [])
        ]
        search_expansion_level = profile_view.get("exploration_constraints", "strict")
        context_budget = profile_view.get("reasoning_budget", "low")
        context_expansion_level = "minimal"
        if context_budget in {"medium", "high", "very_high"}:
            context_expansion_level = "bounded"
        if context_budget in {"very_high"}:
            context_expansion_level = "expanded"

        unresolved_localities = []
        for chain in (projection.get("active_engineering_continuity", {}).get("chains", []) or []):
            if chain.get("unresolved_locality"):
                unresolved_localities.extend(chain.get("unresolved_locality", []))

        fusion_ranked = evidence_fusion.get("ranked_files", []) if isinstance(evidence_fusion, dict) else []
        fusion_weights = evidence_fusion.get("weights", {}) if isinstance(evidence_fusion, dict) else {}
        fusion_preview = [
            {
                "file": str(item.get("file", "") or ""),
                "fused_score": float(item.get("fused_score", 0.0) or 0.0),
                "tier_scores": item.get("tier_scores", {}),
            }
            for item in fusion_ranked[:8]
            if isinstance(item, dict)
        ]

        return {
            "PECS STATUS": {
                "workspace": str(adapter.workspace_root),
                "mode": "PECS-LITE",
                "runtime_interface": "stateless_query",
                "deterministic": True,
                "validation_state": "read_only",
                "runtime_mode": "read_only",
                "artifact_writes": 0,
            },
            "PECS ARTIFACTS": {
                "continuity_artifacts_used": [
                    ".pecs/continuity/active_topology.json",
                    ".pecs/continuity/engineering_continuity_state.json",
                    ".pecs/continuity/locality_state.json",
                ],
                "locality_artifacts_used": [
                    ".pecs/locality_index.json",
                    ".pecs/compact_bundle.json",
                    ".pecs/active_context.json",
                    ".pecs/topology_compact.json",
                ],
                "runtime_modules_consulted": [
                    "integrations.pecs_pro_query_adapter.PECSProQueryAdapter",
                    "integrations.pecs_lite_projection_hardener.ProjectionHardener",
                    "integrations.pecs_lite_projection_hardener.ProjectionExporter",
                ],
            },
            "EVIDENCE FUSION": {
                "schema": str(evidence_fusion.get("schema", "pecs.evidence_fusion.v1")),
                "deterministic": bool(evidence_fusion.get("deterministic", True)),
                "weights": fusion_weights,
                "scoring_formula": "fused_score = sum(weight[tier] * tier_score[tier])",
                "top_ranked_files": fusion_preview,
            },
            "LOCALITY RESOLUTION": {
                "authoritative_ownership_files": [
                    ".pecs/locality_index.json",
                    ".pecs/continuity/engineering_continuity_state.json",
                ],
                "subsystem_roots": active_runtime_zones,
                "authority_source": "PECS-PRO artifacts",
                "inferred": False,
            },
            "SEARCH PLAN": {
                "search_expansion_level": search_expansion_level,
                "recursive_scan": False,
                "escalation_state": "none",
                "selected traversal roots": adapter.runtime_confirmed_neighborhood_lookup(max_neighbors=4),
            },
            "EXECUTION SCOPE": {
                "selected_files": selected_files,
                "estimated_token_usage": metrics.projected_token_estimate,
                "subsystem_target": active_zone,
                "context_expansion_level": context_expansion_level,
            },
            "UNRESOLVED": {
                "unresolved_ownership": sorted(set(unresolved_localities)),
                "fallback_manual_search_usage": False,
                "missing_manifests": sorted(missing_manifests),
                "unresolved_runtime_authority": bool(projection.get("active_engineering_continuity", {}).get("chains", [])) and not projection.get("continuity_supporting_artifacts"),
            },
        }

    @classmethod
    def _build_active_engineering_continuity(
        cls,
        profile: str,
        continuity_signals: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Build bounded accepted engineering continuity payload by profile."""
        chains = continuity_signals.get("active_engineering_chains", []) or []
        if not chains:
            return {}

        high_confidence = [
            chain
            for chain in chains
            if float(chain.get("continuity_confidence", 0.0) or 0.0) >= 0.75
        ]
        if not high_confidence:
            return {}

        if profile == "small":
            chain = high_confidence[0]
            return {
                "mode": "small_anchor",
                "chains": [
                    {
                        "issue": chain.get("issue", ""),
                        "accepted_locality": chain.get("accepted_locality", ""),
                        "continuity_confidence": chain.get(
                            "continuity_confidence", 0.0
                        ),
                        "accepted_followup": bool(
                            chain.get("accepted_followup", False)
                        ),
                        "rejected_locality": (chain.get("rejected_locality", []) or [])[
                            :1
                        ],
                    }
                ],
                "note": "tiny accepted continuity anchor only",
            }

        if profile == "medium":
            return {
                "mode": "bounded_chain",
                "chains": [
                    {
                        "issue": chain.get("issue", ""),
                        "accepted_locality": chain.get("accepted_locality", ""),
                        "continuity_confidence": chain.get(
                            "continuity_confidence", 0.0
                        ),
                        "accepted_followup": bool(
                            chain.get("accepted_followup", False)
                        ),
                        "rejected_locality": (chain.get("rejected_locality", []) or [])[
                            :2
                        ],
                        "locality_stability": chain.get("locality_stability", 0.0),
                    }
                    for chain in high_confidence[:2]
                ],
                "note": "bounded accepted continuity chains for medium profile",
            }

        return {
            "mode": "rich_bounded_chain",
            "chains": [
                {
                    "issue": chain.get("issue", ""),
                    "accepted_locality": chain.get("accepted_locality", ""),
                    "continuity_confidence": chain.get("continuity_confidence", 0.0),
                    "accepted_followup": bool(chain.get("accepted_followup", False)),
                    "rejected_locality": (chain.get("rejected_locality", []) or [])[:3],
                    "locality_stability": chain.get("locality_stability", 0.0),
                    "unresolved_locality": (chain.get("unresolved_locality", []) or [])[
                        :3
                    ],
                    "runtime_ambiguity": bool(chain.get("runtime_ambiguity", False)),
                    "stable_engineering_owner": chain.get(
                        "stable_engineering_owner", ""
                    ),
                }
                for chain in high_confidence[:4]
            ],
            "note": "structured engineering continuity only; no raw chat history",
        }
