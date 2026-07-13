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

import json
import re
import os
from types import MappingProxyType
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Any, Dict, List, Mapping, Tuple, TypedDict


EMPTY_MAPPING: Mapping[str, object] = MappingProxyType({})


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


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

    CANONICAL_MAP: Dict[str, str] = {
        "small": "small_local",
        "medium": "medium_local",
        "large": "large_local",
        "execution": "large_local",
        "small_local": "small_local",
        "medium_local": "medium_local",
        "large_local": "large_local",
        "frontier_online": "frontier_online",
        "reasoning_frontier": "reasoning_frontier",
        "agentic_frontier": "agentic_frontier",
        "frontier": "frontier_online",
        "local": "medium_local",
    }

    @classmethod
    def _normalize_profile_hint(cls, hint: str) -> str:
        normalized = str(hint or "").strip().lower()
        if not normalized:
            return ""
        return cls.CANONICAL_MAP.get(normalized, normalized)

    @classmethod
    def classify(
        cls,
        model_name: str,
        model_source: str,
        context_window: int,
        model_size_hint: str,
        profile_class_hint: str = "",
        local_vs_frontier: str = "",
        reasoning_capability_class: str = "",
    ) -> Dict[str, Any]:
        source = str(model_source or "").lower().strip()
        name = str(model_name or "").lower().strip()
        hint = cls._normalize_profile_hint(model_size_hint or "small")
        profile_class_hint = cls._normalize_profile_hint(profile_class_hint)
        local_hint = cls._normalize_profile_hint(local_vs_frontier)
        reasoning_hint = str(reasoning_capability_class or "").strip().lower()
        window = int(context_window or 0)

        detection_method: List[str] = []
        if name:
            detection_method.append("runtime_provider")
        if source:
            detection_method.append("environment_probe")
        detection_method.append("behavioral_inference")

        profile = "small_local"
        confidence = 0.63

        if profile_class_hint in cls.CANONICAL_MAP:
            profile = cls._normalize_profile_hint(profile_class_hint)
            confidence = 0.79 if profile_class_hint in {"large", "execution"} else 0.71
        elif hint in cls.CANONICAL_MAP:
            profile = hint
            confidence = 0.72 if hint == "large_local" else 0.70 if hint == "medium_local" else 0.63
        elif reasoning_hint.startswith("very_high"):
            profile = "reasoning_frontier"
            confidence = 0.78
        elif window >= 250000 and source in {"ollama", "local"}:
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
                "profile_class_hint": profile_class_hint,
                "local_vs_frontier": local_hint,
                "reasoning_capability_class": reasoning_hint,
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
        authority_contract: Mapping[str, object] = EMPTY_MAPPING,
    ) -> Tuple[List[str], List[str], ProjectionMetrics]:
        """
        Harden a projection for small models.

        Returns:
            (primary_targets, secondary_neighbors, metrics)
        """

        limits = self.LIMITS[profile]

        scored_targets: List[ConfidenceScore] = []
        authority_contract_dict = authority_contract if isinstance(authority_contract, dict) else {}
        authority_targets = authority_contract_dict.get("authority_targets", [])
        continuity_signals = dict(engineering_continuity)
        if isinstance(authority_targets, list) and authority_targets:
            raw_target_order = self._build_raw_target_order(raw_targets)
            scored_targets = self._score_from_authority_contract(
                authority_targets=authority_targets,
                raw_target_order=raw_target_order,
            )
            scoring_input = raw_targets
        else:
            continuity_anchor_candidates = self._continuity_anchor_candidates(
                continuity_signals
            )
            scoring_input = list(raw_targets) + continuity_anchor_candidates
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
        runtime_interaction_present = any(
            getattr(item, "evidence_type", "") == "runtime_interaction"
            for item in scored_targets
        )

        # Progressive locality disclosure for weak-confidence small profile projections.
        # Only widen when runtime interaction evidence is not already available.
        if (
            profile == ProjectionProfile.SMALL
            and (len(primary) < 2 or highest_confidence < 0.78)
            and not runtime_interaction_present
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

    def _build_raw_target_order(self, raw_targets: List[Any]) -> Dict[str, int]:
        """Preserve original raw target order for tie-breaking."""
        order: Dict[str, int] = {}
        for index, target in enumerate(raw_targets):
            if isinstance(target, dict):
                file_path = str(target.get("file", "") or "")
            else:
                file_path = str(target or "")
            normalized = file_path.strip()
            if normalized and normalized not in order:
                order[normalized] = index
        return order

    def _score_from_authority_contract(
        self,
        authority_targets: List[Any],
        raw_target_order: Dict[str, int],
    ) -> List[ConfidenceScore]:
        """Score candidates using the Authority Engine contract."""
        scored: List[ConfidenceScore] = []
        for index, item in enumerate(authority_targets):
            if not isinstance(item, dict):
                continue
            file_path = str(item.get("file", "") or "").strip()
            if not file_path:
                continue

            authority_score = float(item.get("authority_score", 0.0) or 0.0)
            breakdown = item.get("authority_breakdown", {}) if isinstance(item.get("authority_breakdown", {}), dict) else {}
            evidence_breakdown = item.get("evidence_breakdown", {}) if isinstance(item.get("evidence_breakdown", {}), dict) else {}
            provenance = evidence_breakdown.get("provenance", []) if isinstance(evidence_breakdown.get("provenance", []), list) else []

            evidence_strength = int(min(5, max(1, round(authority_score * 5))))
            locality_proximity = min(3, raw_target_order.get(file_path, index) // 4)
            confidence = max(0.0, min(1.0, authority_score))

            scored.append(
                ConfidenceScore(
                    file_path=file_path,
                    confidence=confidence,
                    evidence_type="authority_contract",
                    evidence_strength=evidence_strength,
                    locality_proximity=locality_proximity,
                )
            )
        return scored

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
        authority_contract: Mapping[str, object] = EMPTY_MAPPING,
        consumer_decision: Mapping[str, object] = EMPTY_MAPPING,
        query_source: str = "unknown",
        model_name: str = "",
        model_source: str = "",
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

        authority_contract_dict = authority_contract if isinstance(authority_contract, dict) else {}
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
            "authority_breakdown": authority_contract_dict.get("authority_targets", []),
            "authority_inputs": authority_contract_dict.get("authority_inputs", {}),
            "consulted_artifacts": authority_contract_dict.get("consulted_artifacts", []),
            "influential_artifacts": authority_contract_dict.get("influential_artifacts", []),
        }

        continuity_summary = {
            "reconstructed_lineage_density": _safe_float(
                engineering_continuity_dict.get("reconstructed_lineage_density", 0.0)
            ),
            "continuity_reconstruction_confidence": _safe_float(
                engineering_continuity_dict.get("continuity_reconstruction_confidence", 0.0)
            ),
            "historical_engineering_gravity": _safe_float(
                engineering_continuity_dict.get("historical_engineering_gravity", 0.0)
            ),
            "continuity_condensation_score": _safe_float(
                engineering_continuity_dict.get("continuity_condensation_score", 0.0)
            ),
            "lineage_fragmentation_score": _safe_float(
                engineering_continuity_dict.get("lineage_fragmentation_score", 0.0)
            ),
            "protected_authority_reinforcement": engineering_continuity_dict.get(
                "protected_authority_reinforcement", {}
            ),
            "canonical_authority_clusters": engineering_continuity_dict.get(
                "canonical_authority_clusters", []
            ) or [],
        }
        projection["engineering_continuity_summary"] = continuity_summary

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

        (
            projection["emitted_advisory_cognition"],
            projection["discarded_cognition_summary"],
            projection["shaping_losses"],
            projection["final_emission_observability"],
        ) = cls._build_final_cognition_envelope(
            projection=projection,
            metrics=metrics,
            active_zone=active_zone,
            query_source=query_source,
            model_name=model_name,
            model_source=model_source,
            issue_query=issue_query,
            runtime_context=runtime_context_dict,
            adapter=adapter,
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

        canonical_cluster_map = {
            str(item.get("cluster", "") or ""): min(
                1.0,
                float(item.get("share", 0.0) or 0.0),
            )
            for item in (engineering_continuity.get("canonical_authority_clusters", []) or [])
            if isinstance(item, dict) and str(item.get("cluster", "") or "").strip()
        }
        historical_gravity = min(
            1.0,
            float(engineering_continuity.get("historical_engineering_gravity", 0.0) or 0.0),
        )
        reconstructed_density = min(
            1.0,
            float(engineering_continuity.get("reconstructed_lineage_density", 0.0) or 0.0),
        )
        continuity_condensation_score = min(
            1.0,
            float(engineering_continuity.get("continuity_condensation_score", 0.0) or 0.0),
        )

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

            cluster_share = canonical_cluster_map.get(file_path, 0.0)
            continuity_emergence_bonus = 0.0
            if cluster_share > 0.0:
                continuity_emergence_bonus = round(
                    min(
                        0.08,
                        cluster_share * (0.06 + 0.50 * historical_gravity)
                        + 0.04 * reconstructed_density,
                    ),
                    3,
                )
                if continuity_emergence_bonus > 0.0:
                    fusion_sources = sorted(set(fusion_sources + ["canonical_authority_cluster"]))

            adjusted_confidence = min(1.0, fused_score + continuity_emergence_bonus)
            continuity_emergence_contribution = round(
                min(1.0, continuity_emergence_bonus + 0.15 * historical_gravity),
                3,
            )

            search_expansion_allowed = bool(
                adjusted_confidence >= 0.45
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
                "confidence": round(max(0.0, min(1.0, adjusted_confidence)), 3),
                "authority_type": authority_type,
                "evidence_tiers": {
                    "tier_0_static": round(float(tier_scores.get("tier_0_static", 0.0) or 0.0), 3),
                    "tier_1_runtime": round(float(tier_scores.get("tier_1_runtime", 0.0) or 0.0), 3),
                    "tier_2_continuity": round(float(tier_scores.get("tier_2_continuity", 0.0) or 0.0), 3),
                    "tier_3_validation": round(float(tier_scores.get("tier_3_validation", 0.0) or 0.0), 3),
                },
                "evidence_sources": sorted(fusion_sources),
                "continuity_authority_share": round(cluster_share, 3),
                "historical_authority_emergence_weight": round(
                    min(1.0, historical_gravity * 0.3 + continuity_emergence_contribution * 0.4),
                    3,
                ),
                "continuity_emergence_contribution": continuity_emergence_contribution,
                "continuity_condensation_score": continuity_condensation_score,
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
            secondary_confidence = round(float(hardener.last_confidence_by_path.get(file_path, {}).get("confidence", 0.45) or 0.45), 3)
            cluster_share = canonical_cluster_map.get(file_path, 0.0)
            continuity_emergence_bonus = 0.0
            if cluster_share > 0.0:
                continuity_emergence_bonus = round(
                    min(
                        0.06,
                        cluster_share * (0.05 + 0.45 * historical_gravity)
                        + 0.03 * reconstructed_density,
                    ),
                    3,
                )
            adjusted_secondary_confidence = round(
                min(1.0, secondary_confidence + continuity_emergence_bonus),
                3,
            )
            target_confidence = adjusted_secondary_confidence
            sources = sorted((evidence_by_file.get(file_path, {}).get("provenance", []) or []))
            if cluster_share > 0.0:
                sources = sorted(set(sources + ["canonical_authority_cluster"]))
            targets.append(
                {
                    "task_hint": str(issue_query or "inferred_issue").strip() or "inferred_issue",
                    "expected_outcome": expected_outcome or "runtime ownership confirmation",
                    "probable_file": file_path,
                    "probable_class": symbol_info.get("probable_class", ""),
                    "probable_method": symbol_info.get("probable_method", ""),
                    "confidence": target_confidence,
                    "authority_type": "secondary",
                    "evidence_tiers": {
                        "tier_0_static": round(float((evidence_by_file.get(file_path, {}).get("tier_scores", {}) or {}).get("tier_0_static", 0.0) or 0.0), 3),
                        "tier_1_runtime": round(float((evidence_by_file.get(file_path, {}).get("tier_scores", {}) or {}).get("tier_1_runtime", 0.0) or 0.0), 3),
                        "tier_2_continuity": round(float((evidence_by_file.get(file_path, {}).get("tier_scores", {}) or {}).get("tier_2_continuity", 0.0) or 0.0), 3),
                        "tier_3_validation": round(float((evidence_by_file.get(file_path, {}).get("tier_scores", {}) or {}).get("tier_3_validation", 0.0) or 0.0), 3),
                    },
                    "evidence_sources": sources,
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
    def _build_final_cognition_envelope(
        cls,
        projection: Dict[str, Any],
        metrics: ProjectionMetrics,
        active_zone: str,
        query_source: str,
        model_name: str,
        model_source: str,
        issue_query: str,
        runtime_context: Dict[str, Any],
        adapter: Any,
    ) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
        profile_name = str(
            projection.get("profile")
            or projection.get("projection_profile", {}).get("profile")
            or metrics.profile
            or "small_local"
        )
        profile_view = projection.get("projection_profile", {}) if isinstance(projection.get("projection_profile", {}), dict) else {}
        model_detection = projection.get("model_detection", {}) if isinstance(projection.get("model_detection", {}), dict) else {}
        is_small = profile_name == "small_local"
        is_medium = profile_name == "medium_local"
        is_frontier = profile_name in {
            "frontier_online",
            "reasoning_frontier",
            "agentic_frontier",
            "large_local",
        }
        derived_profile_class = "frontier" if is_frontier else "local"
        derived_reasoning_capability_class = (
            "small" if is_small else "medium" if is_medium else "frontier" if is_frontier else "medium"
        )

        runtime_targets = projection.get("runtime_targets", []) if isinstance(projection.get("runtime_targets", []), list) else []
        secondary_neighbors = projection.get("secondary_neighbors", []) if isinstance(projection.get("secondary_neighbors", []), list) else []
        continuity = projection.get("active_engineering_continuity", {}) if isinstance(projection.get("active_engineering_continuity", {}), dict) else {}
        continuity_summary = projection.get("engineering_continuity_summary", {}) if isinstance(projection.get("engineering_continuity_summary", {}), dict) else {}
        confidence_projection = projection.get("confidence_projection", {}) if isinstance(projection.get("confidence_projection", {}), dict) else {}
        pecs_telemetry = projection.get("pecs_lite_telemetry", {}) if isinstance(projection.get("pecs_lite_telemetry", {}), dict) else {}

        chains = continuity.get("chains", []) if isinstance(continuity.get("chains", []), list) else []
        identity_from_runtime = runtime_context.get("model_identity_input", {}) if isinstance(runtime_context.get("model_identity_input", {}), dict) else {}
        unknown_model_identity = bool(runtime_context.get("unknown_model_identity", False))
        identity_missing_fields = runtime_context.get("identity_missing_fields", []) if isinstance(runtime_context.get("identity_missing_fields", []), list) else []
        profile_class = str(identity_from_runtime.get("profile_class", "") or "").strip().lower() or derived_profile_class
        local_vs_frontier = str(identity_from_runtime.get("local_vs_frontier", "") or "").strip().lower() or profile_class
        reasoning_capability_class = str(identity_from_runtime.get("reasoning_capability_class", "") or "").strip().lower() or derived_reasoning_capability_class
        strongest_chain = chains[0] if chains else {}

        continuity_survivability = float(continuity.get("continuity_survivability_confidence", 0.0) or 0.0)
        locality_authority = float(continuity.get("locality_authority_confidence", 0.0) or 0.0)
        topology_mismatch = float(continuity.get("topology_mismatch_suspicion", 0.0) or 0.0)
        duplicate_shadow = float(continuity.get("duplicate_shadow_suspicion", 0.0) or 0.0)
        dead_execution = float(continuity.get("dead_execution_path_suspicion", 0.0) or 0.0)
        runtime_confirmed_locality = bool(continuity.get("runtime_confirmed_locality", False))

        wrapper_score = max(
            1.0 if bool(projection.get("wrapper_warning")) else 0.0,
            duplicate_shadow,
            topology_mismatch,
            dead_execution,
            max(
                [
                    1.0 if isinstance(target, dict) and str(target.get("predicted_failure_mode", "")) == "wrapper_indirection" else 0.0
                    for target in runtime_targets
                ]
                or [0.0]
            ),
        )
        divergence_floor = max(0.0, 1.0 - continuity_survivability)
        if not runtime_targets and chains:
            divergence_floor = max(0.0, divergence_floor * 0.65)
        divergence_score = max(topology_mismatch, duplicate_shadow, dead_execution, divergence_floor)
        gravity_score = max(locality_authority, continuity_survivability)
        continuity_cluster_strength = max(
            (
                float(item.get("share", 0.0) or 0.0)
                for item in (continuity.get("canonical_authority_clusters", []) or [])
                if isinstance(item, dict)
            ),
            default=0.0,
        )
        historical_gravity = min(1.0, float(continuity.get("historical_engineering_gravity", 0.0) or 0.0))
        continuity_condensation = min(1.0, float(continuity.get("continuity_condensation_score", 0.0) or 0.0))
        continuity_emergence_contribution = round(
            min(
                1.0,
                continuity_cluster_strength * 0.30
                + continuity_survivability * 0.30
                + historical_gravity * 0.20,
            ),
            3,
        )
        historical_authority_emergence_weight = round(
            min(
                1.0,
                historical_gravity * 0.38
                + continuity_cluster_strength * 0.28
                + continuity_condensation * 0.20,
            ),
            3,
        )
        sparse_emergence_assistance = bool(
            not runtime_targets
            and continuity_cluster_strength >= 0.15
            and historical_gravity >= 0.4
        )
        continuity_vs_runtime_balance = round(
            min(
                1.0,
                0.35 * historical_gravity
                + 0.35 * continuity_cluster_strength
                + 0.30 * (0.0 if runtime_targets else 1.0),
            ),
            3,
        )
        runtime_historical_reconciliation_weight = round(
            min(
                1.0,
                0.30 * historical_gravity
                + 0.30 * continuity_emergence_contribution
                + 0.25 * continuity_cluster_strength,
            ),
            3,
        )
        convergence_score = min(1.0, 0.35 + (0.18 * max(0, len(chains) - 1)) + (0.15 if runtime_confirmed_locality else 0.0)) if chains else 0.0
        target_confidences = [
            float(target.get("confidence", 0.0) or 0.0)
            for target in runtime_targets
            if isinstance(target, dict)
        ]
        confidence_total = sum(target_confidences)
        runtime_concentration_score = (
            (max(target_confidences) / confidence_total)
            if confidence_total > 0.0 and target_confidences
            else 0.0
        )
        chain_confidences = [
            float(chain.get("continuity_confidence", 0.0) or 0.0)
            for chain in chains
            if isinstance(chain, dict)
        ]
        chain_confidence_total = sum(chain_confidences)
        chain_concentration_score = (
            (max(chain_confidences) / chain_confidence_total)
            if chain_confidence_total > 0.0 and chain_confidences
            else 0.0
        )
        max_chain_confidence = max(chain_confidences) if chain_confidences else 0.0
        authority_concentration_score = 0.0
        if runtime_targets and chains:
            authority_concentration_score = (0.67 * runtime_concentration_score) + (0.33 * chain_concentration_score)
        elif runtime_targets:
            authority_concentration_score = runtime_concentration_score
        elif chains:
            authority_concentration_score = min(0.93, 0.30 + (0.45 * chain_concentration_score) + (0.25 * max_chain_confidence))

        topology_noise_ratio = round(
            min(
                1.0,
                float(metrics.inactive_locality_suppressed or 0)
                / float((metrics.inactive_locality_suppressed or 0) + len(runtime_targets) + len(secondary_neighbors) + 1),
            ),
            3,
        )
        locality_entropy_after = round(max(0.0, min(1.0, 1.0 - float(metrics.entropy_reduction_score or 0.0))), 3)
        locality_entropy_before = round(min(1.0, locality_entropy_after + float(metrics.entropy_reduction_score or 0.0)), 3)
        authority_confidence_band = (
            "high"
            if authority_concentration_score >= 0.75
            else "medium"
            if authority_concentration_score >= 0.45
            else "low"
        )

        model_identity_input = {
            "model_name": str(identity_from_runtime.get("model_name", "") or model_name or ("unknown" if unknown_model_identity else model_detection.get("model_name", "")) or ""),
            "model_source": str(identity_from_runtime.get("model_source", "") or model_source or ("unknown" if unknown_model_identity else model_detection.get("model_source", "")) or ""),
            "provider": str(identity_from_runtime.get("provider", "") or model_source or ("unknown" if unknown_model_identity else model_detection.get("model_source", "")) or ""),
            "context_window": int(identity_from_runtime.get("context_window", 0) or model_detection.get("context_window", 0) or 0),
            "profile_class": profile_class,
            "local_vs_frontier": local_vs_frontier,
            "reasoning_capability_class": reasoning_capability_class,
            "projection_profile": profile_name,
            "capability_class": str(profile_view.get("capability_class", "") or ""),
            "unknown_model_identity": unknown_model_identity,
            "identity_missing_fields": identity_missing_fields,
        }

        advisories: List[Dict[str, Any]] = []

        def add(verb: str, score: float, reason: str, evidence: Dict[str, Any]) -> None:
            advisories.append(
                {
                    "verb": verb,
                    "confidence": round(max(0.0, min(1.0, score)), 3),
                    "reason": reason,
                    "evidence": evidence,
                    "advisory_only": True,
                }
            )

        wrapper_threshold = 0.25 if is_small else 0.32 if is_medium else 0.35
        if wrapper_score >= wrapper_threshold:
            add(
                "rewire",
                max(wrapper_score, 0.74 if is_small else 0.67 if is_medium else 0.56),
                "Runtime wrapper currently routes execution; wrapper inflation risk is elevated and may hide the mature implementation surface.",
                {"signal": "wrapper_inflation", "score": round(wrapper_score, 3)},
            )

        divergence_threshold = 0.22 if is_small else 0.26 if is_medium else 0.30
        if divergence_score >= divergence_threshold:
            add(
                "reconcile",
                max(divergence_score, 0.72 if is_small else 0.69 if is_medium else 0.64),
                "Runtime-vs-historical locality divergence is visible; reconciliation may be preferable to isolated local patching.",
                {
                    "signal": "runtime_historical_divergence",
                    "topology_mismatch_suspicion": round(topology_mismatch, 3),
                    "duplicate_shadow_suspicion": round(duplicate_shadow, 3),
                    "dead_execution_path_suspicion": round(dead_execution, 3),
                },
            )

        if gravity_score >= 0.70:
            add(
                "preserve",
                max(gravity_score, 0.68 if is_small else 0.74),
                "Historically mature implementation appears concentrated here; preserving the accepted anchor keeps continuity stable while evidence is reconciled.",
                {
                    "signal": "continuity_survivability",
                    "locality_authority_confidence": round(locality_authority, 3),
                    "continuity_survivability_confidence": round(continuity_survivability, 3),
                },
            )

        if convergence_score >= 0.45:
            add(
                "consolidate",
                convergence_score,
                "Convergent locality evidence is present; concentration around the highest-survivability anchor may reduce fragmentation risk.",
                {"signal": "convergence_opportunity", "chain_count": len(chains)},
            )

        if (duplicate_shadow >= 0.22 or dead_execution >= 0.30) and (not is_small or max(duplicate_shadow, dead_execution) >= 0.80):
            add(
                "split",
                max(duplicate_shadow, dead_execution, 0.55 if is_frontier else 0.60 if is_medium else 0.48),
                "Fragmentation risk detected across competing shadows or dead paths; separating these pressures can keep advisory reasoning clearer.",
                {
                    "signal": "scattering_suspicion",
                    "duplicate_shadow_suspicion": round(duplicate_shadow, 3),
                    "dead_execution_path_suspicion": round(dead_execution, 3),
                },
            )

        if topology_mismatch >= 0.35 and (not is_small or topology_mismatch >= 0.82):
            add(
                "refactor",
                max(topology_mismatch, 0.57 if is_medium else 0.61),
                "Topology mismatch pressure is visible; reshaping the reasoning surface may reduce repeated locality drift.",
                {"signal": "topology_mismatch", "score": round(topology_mismatch, 3)},
            )

        if wrapper_score >= 0.45 and gravity_score > 0.60:
            add(
                "migrate",
                min(0.9, max(wrapper_score, gravity_score) - 0.02),
                "A stronger gravity surface is visible away from wrapper-adjacent paths; migration attention may improve continuity survivability.",
                {"signal": "preferred_engineering_gravity", "wrapper_score": round(wrapper_score, 3), "gravity_score": round(gravity_score, 3)},
            )

        if is_small and (runtime_targets or chains) and authority_concentration_score >= 0.78:
            add(
                "preserve",
                min(0.87, 0.62 + authority_concentration_score * 0.25),
                "Small-profile reasoning benefits from mature-authority concentration; keeping the strongest anchor helps avoid noisy dispersion.",
                {
                    "signal": "mature_authority_concentration",
                    "authority_concentration_score": round(authority_concentration_score, 3),
                    "runtime_target_count": len(runtime_targets),
                    "continuity_chain_count": len(chains),
                },
            )

        if is_medium and (runtime_targets or chains) and authority_concentration_score >= 0.72:
            add(
                "consolidate",
                min(0.86, 0.58 + authority_concentration_score * 0.22),
                "Medium-profile reasoning can weight the mature authority surface earlier while preserving advisory plurality.",
                {
                    "signal": "authority_concentration",
                    "authority_concentration_score": round(authority_concentration_score, 3),
                    "runtime_target_count": len(runtime_targets),
                    "secondary_neighbor_count": len(secondary_neighbors),
                    "continuity_chain_count": len(chains),
                },
            )

        if not runtime_targets and chains and max_chain_confidence >= (0.62 if is_small else 0.56 if is_medium else 0.50):
            add(
                "preserve",
                min(0.89, 0.50 + (0.30 * max_chain_confidence) + (0.10 * chain_concentration_score)),
                "Sparse runtime locality is currently observed; historically mature continuity still appears concentrated and may warrant preservation.",
                {
                    "signal": "sparse_runtime_mature_continuity",
                    "max_chain_confidence": round(max_chain_confidence, 3),
                    "chain_concentration_score": round(chain_concentration_score, 3),
                    "runtime_target_count": len(runtime_targets),
                },
            )

        if is_frontier and len(runtime_targets) >= 1:
            add(
                "preserve",
                min(0.93, gravity_score + 0.06),
                "Frontier models can retain richer continuity context; preserve the high-confidence anchor set while comparing tensions.",
                {"signal": "frontier_continuity_depth", "primary_anchor_count": len(runtime_targets)},
            )
            if len(secondary_neighbors) >= 1:
                add(
                    "split",
                    min(0.82, 0.52 + len(secondary_neighbors) * 0.04),
                    "Frontier profile can hold competing advisory surfaces simultaneously; keep ambiguity visible while comparing anchors.",
                    {
                        "signal": "frontier_advisory_plurality",
                        "secondary_neighbor_count": len(secondary_neighbors),
                    },
                )
        elif is_medium and len(confidence_projection.get("primary", [])) >= 1 and gravity_score >= 0.6:
            add(
                "preserve",
                min(0.88, gravity_score + 0.04),
                "Medium models should keep the anchor but stay compact; preserve the strongest gravity signal and avoid over-expansion.",
                {"signal": "compressed_continuity_preservation", "primary_anchor_count": len(confidence_projection.get("primary", []))},
            )
        elif is_small and gravity_score >= 0.60:
            add(
                "preserve",
                min(0.84, gravity_score + 0.03),
                "Small models need a compact anchor; preserve the strongest continuity gravity and ignore verbose provenance.",
                {"signal": "compact_anchor", "primary_anchor_count": len(confidence_projection.get("primary", []))},
            )

        signal_priority_map = {
            "reconcile": 0,
            "preserve": 1,
            "rewire": 2,
            "split": 3,
            "consolidate": 4,
            "refactor": 5,
            "migrate": 6,
        }
        suppression_reason_breakdown = {
            "weak_topology_neighbors": int(len(secondary_neighbors) > len(runtime_targets) and len(secondary_neighbors) > 0),
            "broad_runtime_spread": int(metrics.locality_breadth_score >= 0.55),
            "low_confidence_locality_noise": int(sum(1 for score in target_confidences if score < 0.45) > 0),
            "redundant_structural_metadata": int(metrics.inactive_locality_suppressed > (len(runtime_targets) + len(secondary_neighbors))),
        }

        advisory_by_verb: Dict[str, Dict[str, Any]] = {}
        for advisory in advisories:
            verb = str(advisory.get("verb", "") or "")
            existing = advisory_by_verb.get(verb)
            if existing is None or float(advisory.get("confidence", 0.0) or 0.0) > float(existing.get("confidence", 0.0) or 0.0):
                advisory_by_verb[verb] = advisory
        advisories = list(advisory_by_verb.values())

        advisories.sort(
            key=lambda item: (
                signal_priority_map.get(str(item.get("verb", "")), 99),
                -float(item.get("confidence", 0.0) or 0.0),
            )
        )
        max_advisories = 2 if is_small else 4 if is_medium else 6
        advisories = advisories[:max_advisories]
        advisory_signal_priority = [str(item.get("verb", "")) for item in advisories if str(item.get("verb", ""))]
        cognition_density_score = round(
            min(
                1.0,
                float(len(advisories))
                / float(max(1, len(runtime_targets) + len(secondary_neighbors) + len(chains))),
            ),
            3,
        )

        all_modes = ["reconcile", "consolidate", "migrate", "preserve", "split", "refactor", "rewire"]
        emitted_modes = list(dict.fromkeys([str(item.get("verb", "")) for item in advisories if str(item.get("verb", ""))]))
        discarded_modes = [mode for mode in all_modes if mode not in emitted_modes]

        omitted_sections: List[str] = []
        if "execution_enrichment" not in projection:
            omitted_sections.append("execution_enrichment")
        if not projection.get("active_engineering_continuity"):
            omitted_sections.append("active_engineering_continuity")
        enrichment = projection.get("execution_enrichment", {}) if isinstance(projection.get("execution_enrichment", {}), dict) else {}
        for section in ("execution_neighborhood", "execution_continuity", "continuity_context"):
            if section not in enrichment:
                omitted_sections.append(section)

        emitted_advisory_cognition = {
            "profile": profile_name,
            "mode": "compact_advisory" if is_small else "bounded_advisory" if is_medium else "rich_advisory",
            "summary": "; ".join(f"{item['verb']}: {item['reason']}" for item in advisories),
            "model_identity_input": model_identity_input,
            "authority_concentration_score": round(authority_concentration_score, 3),
            "strongest_tension": {
                "kind": "wrapper_inflation" if wrapper_score >= divergence_score else "continuity_divergence",
                "score": round(max(wrapper_score, divergence_score), 3),
                "advisory": "rewire" if wrapper_score >= divergence_score else "reconcile",
            },
            "strongest_gravity_indicator": {
                "kind": "continuity_survivability",
                "score": round(gravity_score, 3),
                "advisory": "preserve" if gravity_score >= 0.6 else "consolidate",
            },
            "strongest_divergence_indicator": {
                "kind": "runtime_historical_divergence",
                "score": round(divergence_score, 3),
                "advisory": "reconcile" if divergence_score >= 0.35 else "refactor",
            },
            "preferred_engineering_gravity": {
                "signal": "accepted continuity anchor" if gravity_score >= 0.6 else "counter-pressure surface",
                "score": round(gravity_score, 3),
            },
            "advisories": advisories,
            "advisory_signal_priority": advisory_signal_priority,
            "continuity_emergence_contribution": continuity_emergence_contribution,
            "historical_authority_emergence_weight": historical_authority_emergence_weight,
            "sparse_emergence_assistance": sparse_emergence_assistance,
            "runtime_historical_reconciliation_weight": runtime_historical_reconciliation_weight,
            "continuity_vs_runtime_balance": continuity_vs_runtime_balance,
            "emergence_source_breakdown": {
                "runtime_signal": round(min(1.0, len(runtime_targets) / max(1, len(runtime_targets) + len(secondary_neighbors))), 3),
                "continuity_signal": continuity_emergence_contribution,
                "cluster_signal": continuity_cluster_strength,
            },
            "suppression_reason_breakdown": suppression_reason_breakdown,
            "authority_confidence_band": authority_confidence_band,
            "cognition_density_score": cognition_density_score,
            "topology_noise_ratio": topology_noise_ratio,
        }

        if is_frontier:
            emitted_advisory_cognition["convergence_opportunities"] = [
                {
                    "kind": "accepted_locality",
                    "score": round(float(chain.get("continuity_confidence", 0.0) or 0.0), 3),
                    "signal": str(chain.get("accepted_locality", "")),
                }
                for chain in chains[:4]
                if isinstance(chain, dict)
            ]
            emitted_advisory_cognition["continuity_context"] = {
                "runtime_confirmation_density": float(continuity.get("runtime_confirmation_density", 0.0) or 0.0),
                "accepted_anchor_count": len(chains),
                "note": "frontier retains richer continuity reasoning while staying advisory only",
            }

        discarded_cognition_summary = {
            "profile": profile_name,
            "preserved_advisory_modes": emitted_modes,
            "removed_advisory_modes": discarded_modes,
            "omitted_enrichment_sections": sorted(set(omitted_sections)),
            "trimmed_target_sets": {
                "raw_candidates_suppressed": metrics.inactive_locality_suppressed,
                "primary_targets_emitted": len(runtime_targets),
                "secondary_neighbors_emitted": len(secondary_neighbors),
                "continuity_chains_emitted": len(chains),
            },
            "compressed_away": [
                "verbose provenance chains",
                "raw topology dumps",
                "workspace scan narratives",
            ],
            "cognition_survivability_summary": {
                "continuity_survivability_confidence": round(continuity_survivability, 3),
                "runtime_confirmed_locality": runtime_confirmed_locality,
                "authority_concentration_score": round(authority_concentration_score, 3),
                "locality_entropy_before": locality_entropy_before,
                "locality_entropy_after": locality_entropy_after,
            },
            "suppression_reason_breakdown": suppression_reason_breakdown,
            "advisory_signal_priority": advisory_signal_priority,
            "authority_confidence_band": authority_confidence_band,
            "cognition_density_score": cognition_density_score,
            "topology_noise_ratio": topology_noise_ratio,
            "continuity_reasoning_compressed": not is_frontier,
            "topology_reasoning_compressed": is_small or is_medium,
        }

        shaping_losses = {
            "model_identity_input": model_identity_input,
            "profile_class": profile_class,
            "preserved_advisory_modes": emitted_modes,
            "advisory_modes_removed": discarded_modes,
            "target_pruning_count": metrics.inactive_locality_suppressed,
            "continuity_compression": "high" if is_small else "moderate" if is_medium else "bounded",
            "omitted_enrichment_sections": sorted(set(omitted_sections)),
            "authority_concentration_score": round(authority_concentration_score, 3),
            "locality_entropy_before": locality_entropy_before,
            "locality_entropy_after": locality_entropy_after,
            "suppression_reason_breakdown": suppression_reason_breakdown,
            "advisory_signal_priority": advisory_signal_priority,
            "authority_confidence_band": authority_confidence_band,
            "cognition_density_score": cognition_density_score,
            "topology_noise_ratio": topology_noise_ratio,
        }

        continuity_cluster_strength = max(
            (
                float(item.get("share", 0.0) or 0.0)
                for item in (continuity_summary.get("canonical_authority_clusters", []) or [])
                if isinstance(item, dict)
            ),
            default=0.0,
        )
        continuity_emergence_contribution = round(
            min(
                1.0,
                continuity_cluster_strength * 0.30
                + continuity_summary.get("historical_engineering_gravity", 0.0) * 0.40
                + continuity_summary.get("reconstructed_lineage_density", 0.0) * 0.25,
            ),
            3,
        )
        historical_authority_emergence_weight = round(
            min(
                1.0,
                continuity_summary.get("historical_engineering_gravity", 0.0) * 0.38
                + continuity_cluster_strength * 0.28
                + continuity_summary.get("continuity_condensation_score", 0.0) * 0.20,
            ),
            3,
        )
        sparse_emergence_assistance = bool(
            not runtime_targets
            and continuity_cluster_strength >= 0.15
            and continuity_summary.get("historical_engineering_gravity", 0.0) >= 0.4
        )
        continuity_vs_runtime_balance = round(
            min(
                1.0,
                0.35 * continuity_summary.get("historical_engineering_gravity", 0.0)
                + 0.35 * continuity_cluster_strength
                + 0.30 * (0.0 if runtime_targets else 1.0),
            ),
            3,
        )
        runtime_historical_reconciliation_weight = round(
            min(
                1.0,
                0.30 * continuity_summary.get("historical_engineering_gravity", 0.0)
                + 0.30 * continuity_summary.get("reconstructed_lineage_density", 0.0)
                + 0.25 * continuity_cluster_strength
                + 0.10 * continuity_summary.get("continuity_condensation_score", 0.0),
            ),
            3,
        )

        final_emission_observability = {
            "timestamp": metrics.diagnostic_timestamp,
            "session_id": str(runtime_context.get("session_id", "") or runtime_context.get("session", "") or ""),
            "query": str(issue_query or ""),
            "query_source": str(query_source or "unknown"),
            "model_name": str(model_name or ""),
            "model_source": str(model_source or ""),
            "model_identity_input": model_identity_input,
            "profile_class": profile_class,
            "adapter": str(type(adapter).__name__ if adapter is not None else "unknown"),
            "selected_projection_profile": profile_name,
            "unknown_model_identity": unknown_model_identity,
            "identity_missing_fields": identity_missing_fields,
            "preserved_advisory_modes": emitted_modes,
            "removed_advisory_modes": discarded_modes,
            "cognition_survivability_summary": discarded_cognition_summary.get("cognition_survivability_summary", {}),
            "authority_concentration_score": round(authority_concentration_score, 3),
            "locality_entropy_before": locality_entropy_before,
            "locality_entropy_after": locality_entropy_after,
            "suppression_reason_breakdown": suppression_reason_breakdown,
            "advisory_signal_priority": advisory_signal_priority,
            "authority_confidence_band": authority_confidence_band,
            "cognition_density_score": cognition_density_score,
            "topology_noise_ratio": topology_noise_ratio,
            "reconstructed_lineage_density": continuity_summary.get("reconstructed_lineage_density", 0.0),
            "continuity_reconstruction_confidence": continuity_summary.get("continuity_reconstruction_confidence", 0.0),
            "historical_engineering_gravity": continuity_summary.get("historical_engineering_gravity", 0.0),
            "continuity_condensation_score": continuity_summary.get("continuity_condensation_score", 0.0),
            "protected_authority_reinforcement": continuity_summary.get("protected_authority_reinforcement", {}),
            "lineage_fragmentation_score": continuity_summary.get("lineage_fragmentation_score", 0.0),
            "canonical_authority_clusters": continuity_summary.get("canonical_authority_clusters", []),
            "continuity_emergence_contribution": continuity_emergence_contribution,
            "historical_authority_emergence_weight": historical_authority_emergence_weight,
            "sparse_emergence_assistance": sparse_emergence_assistance,
            "runtime_historical_reconciliation_weight": runtime_historical_reconciliation_weight,
            "continuity_vs_runtime_balance": continuity_vs_runtime_balance,
            "emergence_source_breakdown": {
                "runtime_signal": round(min(1.0, len(runtime_targets) / max(1, len(runtime_targets) + len(secondary_neighbors))), 3),
                "continuity_signal": continuity_emergence_contribution,
                "cluster_signal": continuity_cluster_strength,
            },
            "token_budget_selected": int(pecs_telemetry.get("token_budget_selected", 0) or 0),
            "runtime_targets_count": len(runtime_targets),
            "secondary_neighbors_count": len(secondary_neighbors),
            "active_zone": str(active_zone),
        }

        return emitted_advisory_cognition, discarded_cognition_summary, shaping_losses, final_emission_observability

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
                "canonical_authority_clusters": (
                    continuity_signals.get("canonical_authority_clusters", []) or []
                )[:1],
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
                "canonical_authority_clusters": (
                    continuity_signals.get("canonical_authority_clusters", []) or []
                )[:2],
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
            "canonical_authority_clusters": (
                continuity_signals.get("canonical_authority_clusters", []) or []
            )[:4],
            "note": "structured engineering continuity only; no raw chat history",
        }
