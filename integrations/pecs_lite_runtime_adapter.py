from __future__ import annotations

import hashlib
import json
import sys
import time
import uuid
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from runtime.runtime_telemetry import emit_runtime_event

try:
    from integrations.pecs_lite_projection_hardener import ProjectionProfile
except Exception:
    ProjectionProfile = None  # type: ignore


def _ensure_pecs_lite_runtime_path() -> Optional[Path]:
    repo_root = Path(__file__).resolve().parents[1]
    pecs_lite_root = repo_root / "PECS_LITE v2" / "pecs_lite v2"
    if not pecs_lite_root.exists():
        return None

    repo_path = str(repo_root)
    if repo_path not in sys.path:
        sys.path.insert(0, repo_path)

    return pecs_lite_root


_pecs_lite_root = _ensure_pecs_lite_runtime_path()
PECSLiteRuntimeV2 = None
if _pecs_lite_root is not None:
    try:
        pecs_lite_package = str(_pecs_lite_root)
        if pecs_lite_package not in sys.path:
            sys.path.insert(0, pecs_lite_package)
        from pecs_lite_runtime.pecs_lite_runtime_v2 import PECSLiteRuntimeV2
    except Exception:
        PECSLiteRuntimeV2 = None


class PECSLiteRuntimeAdapter:
    @classmethod
    def _normalize_identity(
        cls,
        model_name: str,
        model_source: str,
        provider: str,
        profile_class: str,
        local_vs_frontier: str,
        reasoning_capability_class: str,
        model_size: str = "",
        context_window: int = 0,
    ) -> Dict[str, Any]:
        normalized = {
            "model_name": str(model_name or "").strip(),
            "model_source": str(model_source or "").strip(),
            "provider": str(provider or "").strip(),
            "profile_class": str(profile_class or "").strip().lower(),
            "local_vs_frontier": str(local_vs_frontier or "").strip().lower(),
            "reasoning_capability_class": str(reasoning_capability_class or "").strip().lower(),
        }

        # Infer missing identity hints from model_size and context_window.
        cloud_providers = {"openai", "anthropic", "azure", "cloud"}
        provider_key = normalized["provider"] or normalized["model_source"]
        is_cloud_frontier = (
            int(context_window or 0) >= 120000 and provider_key in cloud_providers
        )
        if not normalized["profile_class"]:
            if model_size == "small":
                normalized["profile_class"] = "small"
            elif model_size == "medium":
                normalized["profile_class"] = "medium"
            elif model_size == "large" and is_cloud_frontier:
                normalized["profile_class"] = "frontier"
        if not normalized["local_vs_frontier"]:
            cloud_providers = {"openai", "anthropic", "azure", "cloud"}
            provider_key = normalized["provider"] or normalized["model_source"]
            if int(context_window or 0) >= 120000 and provider_key in cloud_providers:
                normalized["local_vs_frontier"] = "frontier"
            else:
                normalized["local_vs_frontier"] = "local"
        if not normalized["reasoning_capability_class"]:
            if normalized["profile_class"] in {"large", "large_local", "frontier_online", "reasoning_frontier", "agentic_frontier"}:
                normalized["reasoning_capability_class"] = "very_high"
            elif normalized["profile_class"] in {"medium", "medium_local"}:
                normalized["reasoning_capability_class"] = "medium"
            else:
                normalized["reasoning_capability_class"] = "low"

        missing_fields = []
        if not normalized["model_name"]:
            missing_fields.append("model_name")
        if not (normalized["model_source"] or normalized["provider"]):
            missing_fields.append("provider_or_source")
        if not normalized["profile_class"]:
            missing_fields.append("profile_class")
        if not normalized["local_vs_frontier"]:
            missing_fields.append("local_vs_frontier")

        unknown_model_identity = bool(missing_fields)
        if not normalized["model_source"]:
            normalized["model_source"] = normalized["provider"]
        if not normalized["provider"]:
            normalized["provider"] = normalized["model_source"]

        if unknown_model_identity:
            if not normalized["profile_class"]:
                normalized["profile_class"] = "unknown"
            if not normalized["local_vs_frontier"]:
                normalized["local_vs_frontier"] = "unknown"
            if not normalized["model_source"]:
                normalized["model_source"] = "unknown"
            if not normalized["provider"]:
                normalized["provider"] = "unknown"

        normalized["missing_fields"] = missing_fields
        normalized["unknown_model_identity"] = unknown_model_identity
        return normalized

    @classmethod
    def _build_canonical_query_envelope(
        cls,
        workspace_root: str,
        query: str,
        model_name: str,
        model_source: str,
        context_window: int,
        provider: str,
        profile_class: str,
        local_vs_frontier: str,
        reasoning_capability_class: str,
        query_source: str,
        capability_bundle: Dict[str, Any],
    ) -> Dict[str, Any]:
        now = datetime.utcnow().isoformat() + "Z"
        workspace_id = hashlib.sha256(str(workspace_root).encode("utf-8")).hexdigest()
        query_id = str(uuid.uuid4())

        projection_profile = capability_bundle.get("projection_profile", {})
        normalized_profile = {
            "profile": projection_profile.get("profile", "small_local"),
            "reasoning_budget": projection_profile.get("reasoning_budget", "low"),
            "exploration_constraints": projection_profile.get("exploration_constraints", "strict"),
            "target_count": int(projection_profile.get("max_related_files", 3) or 3),
            "continuity_depth": "deep" if str(projection_profile.get("capability_class", "")).startswith("frontier") else "balanced",
            "include_advisories": True,
        }

        return {
            "query_id": query_id,
            "consumer": query_source,
            "workspace_id": f"sha256:{workspace_id}",
            "projection_profile": normalized_profile,
            "task_type": "inspection",
            "issue": query,
            "execution_mode": "analysis",
            "constraints": {
                "max_targets": int(projection_profile.get("max_related_files", 3) or 3),
                "max_token_budget": int(projection_profile.get("token_budget", 2000) or 2000),
                "allow_workspace_search": False,
            },
            "timestamp": now,
            "model": model_name or "unknown",
            "metadata": {
                "model_source": model_source or provider or "unknown",
                "profile_class": profile_class,
                "local_vs_frontier": local_vs_frontier,
                "reasoning_capability_class": reasoning_capability_class,
                "query_source": query_source,
            },
            "requested_authority": "strict" if normalized_profile["profile"] in {"small", "execution"} else "balanced" if normalized_profile["profile"] == "medium" else "exploratory",
            "requested_locality": "function",
            "requested_fields": [
                "runtime_targets",
                "authority_breakdown",
                "consulted_artifacts",
                "authority_inputs",
                "influential_artifacts",
            ],
        }

    @staticmethod
    def _build_canonical_response_snapshot(projection: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "schema": projection.get("schema"),
            "profile": projection.get("profile"),
            "projection_profile": projection.get("projection_profile"),
            "runtime_targets": projection.get("runtime_targets", []),
            "secondary_neighbors": projection.get("secondary_neighbors", []),
            "consulted_artifacts": projection.get("consulted_artifacts", []),
            "authority_inputs": projection.get("authority_inputs", {}),
            "authority_breakdown": projection.get("authority_breakdown", []),
            "influential_artifacts": projection.get("influential_artifacts", []),
            "consumer_decision": projection.get("consumer_decision", {}),
        }

    @classmethod
    def is_available(cls) -> bool:
        return True

    @classmethod
    def _derive_terms(cls, query: str) -> List[str]:
        from pecs_query.query_parser import QueryParser

        result = QueryParser.parse(str(query or ""))
        return result.terms

    @classmethod
    def _profile_limits(cls, profile_name: str) -> Dict[str, int]:
        from integrations.pecs_lite_projection_hardener import ProjectionHardener

        mapping = {
            "small": ProjectionHardener.LIMITS[ProjectionProfile.SMALL],
            "small_local": ProjectionHardener.LIMITS[ProjectionProfile.SMALL],
            "medium": ProjectionHardener.LIMITS[ProjectionProfile.MEDIUM],
            "medium_local": ProjectionHardener.LIMITS[ProjectionProfile.MEDIUM],
            "large": ProjectionHardener.LIMITS[ProjectionProfile.LARGE],
            "large_local": ProjectionHardener.LIMITS[ProjectionProfile.LARGE],
            "frontier_online": ProjectionHardener.LIMITS[ProjectionProfile.FRONTIER_ONLINE],
            "reasoning_frontier": ProjectionHardener.LIMITS[ProjectionProfile.REASONING_FRONTIER],
            "agentic_frontier": ProjectionHardener.LIMITS[ProjectionProfile.AGENTIC_FRONTIER],
        }
        return mapping.get(profile_name, mapping["small_local"])

    @classmethod
    def _map_profile_name(cls, profile_name: str) -> str:
        canonical = {
            "small": "small_local",
            "medium": "medium_local",
            "large": "large_local",
            "execution": "large_local",
            "frontier": "frontier_online",
        }
        return canonical.get(profile_name, profile_name)

    @classmethod
    def _build_projection_from_pipeline(
        cls,
        workspace_root: str,
        query: str,
        identity: Dict[str, Any],
        query_source: str,
        capability_bundle: Dict[str, Any],
        include_diagnostics: bool,
    ) -> Optional[Dict[str, Any]]:
        from pecs_query.pipeline import PECSQueryPipeline
        from integrations.pecs_lite_projection_hardener import (
            ProjectionExporter,
            ProjectionHardener,
            ProjectionMetrics,
            ProjectionProfile,
            QueryFlowDiagnostics,
        )

        workspace_path = Path(workspace_root).resolve()
        pipeline = PECSQueryPipeline(workspace_path)
        terms = cls._derive_terms(query)

        profile_name = capability_bundle.get("projection_profile", {}).get("profile", "small_local")
        profile_name = cls._map_profile_name(profile_name)
        limits = cls._profile_limits(profile_name)
        max_nodes = max(10, limits.get("primary_targets", 3) + limits.get("secondary_neighbors", 2) + 5)

        result = pipeline.query(
            terms=terms,
            max_clusters=1,
            max_nodes=max_nodes,
            max_depth=2,
        )

        if result.get("error") or not result.get("navigation_graph"):
            return None

        nav_graph = result.get("navigation_graph", {})
        nodes = nav_graph.get("nodes", {})

        # Sort nodes by confidence descending, then by node_id for determinism.
        scored_nodes = []
        for node_id, node in nodes.items():
            confidence = float(node.get("metadata", {}).get("confidence", 0.0) or 0.0)
            scored_nodes.append((confidence, node_id, node))
        scored_nodes.sort(key=lambda item: (-item[0], item[1]))

        primary_limit = limits.get("primary_targets", 3)
        secondary_limit = limits.get("secondary_neighbors", 2)

        primary_nodes = scored_nodes[:primary_limit]
        secondary_nodes = scored_nodes[primary_limit:primary_limit + secondary_limit]

        primary_targets: List[str] = []
        secondary_neighbors: List[str] = []
        runtime_targets: List[Dict[str, Any]] = []

        for idx, (confidence, node_id, node) in enumerate(primary_nodes):
            file_path = node.get("file_path") or node_id
            primary_targets.append(str(file_path))
            target = {
                "file": str(file_path),
                "confidence": round(max(0.0, min(1.0, confidence)), 3),
                "line_range": node.get("line_range", {"start": 1, "end": 1}),
                "node_type": node.get("node_type", "unknown"),
                "node_id": node_id,
                "authority_type": "primary" if idx == 0 else "secondary",
                "evidence_type": "graph_topology",
                "locality_proximity": 0,
            }
            runtime_targets.append(target)

        for _confidence, node_id, node in secondary_nodes:
            file_path = node.get("file_path") or node_id
            secondary_neighbors.append(str(file_path))
            runtime_targets.append({
                "file": str(file_path),
                "confidence": round(max(0.0, min(1.0, _confidence)), 3),
                "line_range": node.get("line_range", {"start": 1, "end": 1}),
                "node_type": node.get("node_type", "unknown"),
                "node_id": node_id,
                "authority_type": "neighbor",
                "evidence_type": "graph_topology",
                "locality_proximity": 1,
            })

        projected_target_count = len(primary_targets)
        projected_secondary_count = len(secondary_neighbors)
        total_nodes = len(scored_nodes)
        max_budget = limits.get("token_budget", 2000)
        projected_token_estimate = min(
            max_budget,
            sum(
                max(1, t.get("line_range", {}).get("end", 1) - t.get("line_range", {}).get("start", 0) + 1)
                for t in runtime_targets
            )
            * 8,
        )
        locality_breadth_score = round(min(1.0, len(runtime_targets) / max(1, max_nodes)), 3)
        entropy_reduction_score = round(1.0 - locality_breadth_score, 3)

        metrics = ProjectionMetrics(
            profile=profile_name,
            projected_target_count=projected_target_count,
            projected_secondary_count=projected_secondary_count,
            projected_token_estimate=projected_token_estimate,
            runtime_zone_count=0,
            locality_breadth_score=locality_breadth_score,
            entropy_reduction_score=entropy_reduction_score,
            inactive_locality_suppressed=max(0, total_nodes - len(runtime_targets)),
            wrapper_expansion_depth=0,
            wrapper_expansion_count=0,
            has_confirmed_neighborhoods=bool(runtime_targets),
            progressive_locality_disclosure_applied=True,
            diagnostic_timestamp=datetime.utcnow().isoformat() + "Z",
        )

        authority_confidence = 0.0
        if runtime_targets:
            authority_confidence = sum(t.get("confidence", 0.0) for t in runtime_targets) / len(runtime_targets)

        pecs_lite_status = {
            "runtime_observability_used": True,
            "engineering_continuity_used": False,
            "workspace_scan_performed": False,
            "symbol_resolution_used": any(t.get("node_type") in {"method", "function", "class"} for t in runtime_targets),
            "behavioral_analysis_used": False,
            "capability_detection_used": True,
            "authority_confidence": round(max(0.0, min(1.0, authority_confidence)), 3),
        }

        diagnostics = QueryFlowDiagnostics(
            queried_pecs_pro=True,
            workspace_scan_performed=False,
            topology_reconstructed=False,
            continuity_state_owned=False,
            projection_mode="query_driven",
            adapter_methods_called=["PECSQueryPipeline.query"],
            artifacts_accessed=[
                ".pecs/locality_index.json",
                ".pecs/topology_compact.json",
            ],
            artifacts_not_generated=[
                ".pecs/active_context.json",
                ".pecs/compact_bundle.json",
            ],
            timestamp=datetime.utcnow().isoformat() + "Z",
        )

        model_identity_input = {
            "model_name": identity["model_name"],
            "model_source": identity["model_source"],
            "provider": identity["provider"],
            "context_window": 0,
            "profile_class": identity["profile_class"],
            "local_vs_frontier": identity["local_vs_frontier"],
            "reasoning_capability_class": identity["reasoning_capability_class"],
        }

        projection = {
            "schema": "pecs_lite.runtime_projection.locality_authority.v3",
            "disclaimer": "PECS-LITE is a stateless projection adapter. Edit workspace runtime modules, not .pecs files.",
            "profile": profile_name,
            "projection_profile": capability_bundle.get("projection_profile", {}),
            "model_detection": capability_bundle.get("model_detection", {}),
            "runtime_targets": runtime_targets,
            "secondary_neighbors": secondary_neighbors,
            "likely_execution_cluster": "general_runtime",
            "possible_mutation_owner": "unknown",
            "wrapper_warning": False,
            "deterministic": True,
            "runtime_mode": "read_only",
            "artifact_writes": 0,
            "metrics": asdict(metrics),
            "diagnostics": asdict(diagnostics),
            "continuity_supporting_artifacts": [
                ".pecs/locality_index.json",
                ".pecs/topology_compact.json",
            ],
            "forbidden_mutation_prefixes": [".pecs/"],
            "confidence_projection": {},

            "pecs_lite_status": pecs_lite_status,
            "runtime_context": {
                "unknown_model_identity": identity.get("unknown_model_identity", False),
                "identity_missing_fields": identity.get("missing_fields", []),
                "model_identity_input": model_identity_input,
            },
            "evidence_fusion": {
                "schema": "pecs.evidence_fusion.v1",
                "deterministic": True,
                "weights": {},
                "ranked_files": [],
            },
            "authority_breakdown": [],
            "authority_inputs": {},
            "consulted_artifacts": [
                ".pecs/locality_index.json",
                ".pecs/topology_compact.json",
            ],
            "influential_artifacts": [],
            "query_pipeline": {
                "query_terms": result.get("query_terms", []),
                "correlation_cluster_count": result.get("correlation_cluster_count", 0),
                "selected_cluster_count": result.get("selected_cluster_count", 0),
                "navigation_graph_node_count": nav_graph.get("node_count", 0),
                "navigation_graph_edge_count": nav_graph.get("edge_count", 0),
            },
        }

        projection_payload = json.dumps(projection, sort_keys=True)
        elapsed_ms = 0  # computed by caller
        projection["pecs_lite_telemetry"] = {
            "runtime_invoked": True,
            "adapter_used": "PECSLiteRuntimeAdapter",
            "runtime_available": True,
            "projection_generated": True,
            "projection_schema": projection.get("schema"),
            "projection_generation_time_ms": elapsed_ms,
            "selected_projection_profile": profile_name,
            "model_detection": capability_bundle.get("model_detection", {}),
            "capability_classification": capability_bundle.get("projection_profile", {}),
            "profile_class": "frontier" if profile_name in {"frontier_online", "reasoning_frontier", "agentic_frontier", "large_local"} else "local",
            "reasoning_capability_class": (
                "small" if profile_name == "small_local" else "medium" if profile_name == "medium_local" else "frontier"
            ),
            "unknown_model_identity": identity.get("unknown_model_identity", False),
            "identity_missing_fields": identity.get("missing_fields", []),
            "model_identity_input": model_identity_input,
            "deterministic_narrowing_activated": True,
            "progressive_disclosure_activated": True,
            "token_budget_selected": max_budget,
            "candidate_count": len(runtime_targets),
            "primary_locality_selected": primary_targets,
            "secondary_locality_selected": secondary_neighbors,
            "payload_size": len(projection_payload),
            "export_mode": "in_memory",
            "compressed_continuity_size": 0,
            "topology_size": 0,
            "continuity_size": 0,
            "diagnostics_included": include_diagnostics,
            "projection_delivered": True,
            "fallback_triggered": False,
            "repository_search_allowed": False,
            "pecs_bypass_reason": "",
            "projection_rejected_reason": "",
        }

        projection["final_emission_observability"] = {
            "profile_class": projection["pecs_lite_telemetry"]["profile_class"],
            "reasoning_capability_class": projection["pecs_lite_telemetry"]["reasoning_capability_class"],
            "token_budget_selected": max_budget,
            "model_identity_input": model_identity_input,
            "locality_entropy_before": locality_breadth_score,
            "locality_entropy_after": max(0.0, locality_breadth_score - entropy_reduction_score),
            "authority_concentration_score": authority_confidence,
            "cognition_survivability_summary": {},
            "preserved_advisory_modes": [],
            "removed_advisory_modes": [],
            "suppression_reason_breakdown": {},
            "advisory_signal_priority": [],
            "authority_confidence_band": "high" if authority_confidence >= 0.7 else "medium" if authority_confidence >= 0.4 else "low",
            "cognition_density_score": 0.0,
            "topology_noise_ratio": 0.0,
        }

        return projection

    @classmethod
    def build_projection(
        cls,
        workspace_root: str,
        query: str,
        model_name: str = "",
        model_source: str = "",
        context_window: int = 0,
        model_size: str = "small",
        provider: str = "",
        profile_class: str = "",
        local_vs_frontier: str = "",
        reasoning_capability_class: str = "",
        query_source: str = "unknown",
        consumer_decision: Optional[Dict[str, Any]] = None,
        include_diagnostics: bool = True,
    ) -> Dict[str, Any]:
        from integrations.pecs_lite_projection_hardener import CapabilityClassifier, ProjectionProfile

        identity = cls._normalize_identity(
            model_name=model_name,
            model_source=model_source,
            provider=provider,
            profile_class=profile_class,
            local_vs_frontier=local_vs_frontier,
            reasoning_capability_class=reasoning_capability_class,
            model_size=model_size,
            context_window=context_window,
        )

        if identity["unknown_model_identity"]:
            emit_runtime_event(
                subsystem="PECS_LITE_ADAPTER",
                event="unknown_model_identity",
                payload={
                    "workspace": str(workspace_root),
                    "adapter_used": "PECSLiteRuntimeAdapter",
                    "query": query,
                    "query_source": query_source,
                    "missing_fields": identity.get("missing_fields", []),
                    "model_identity_input": {
                        "model_name": identity.get("model_name", ""),
                        "model_source": identity.get("model_source", ""),
                        "provider": identity.get("provider", ""),
                        "profile_class": identity.get("profile_class", "unknown"),
                        "local_vs_frontier": identity.get("local_vs_frontier", "unknown"),
                        "reasoning_capability_class": identity.get("reasoning_capability_class", "unknown"),
                    },
                    "conservative_shaping": True,
                },
                workspace_root=Path(workspace_root),
            )

        emit_runtime_event(
            subsystem="PECS_LITE",
            event="projection_request_received",
            payload={
                "query_source": query_source,
                "issue_query": query,
                "model_name": identity["model_name"],
                "model_source": identity["model_source"],
                "provider": identity["provider"],
                "context_window": context_window,
                "model_size": model_size,
                "profile_class": identity["profile_class"],
                "local_vs_frontier": identity["local_vs_frontier"],
                "reasoning_capability_class": identity["reasoning_capability_class"],
                "unknown_model_identity": identity["unknown_model_identity"],
                "identity_missing_fields": identity["missing_fields"],
                "model_identity_input": {
                    "model_name": identity["model_name"],
                    "model_source": identity["model_source"],
                    "provider": identity["provider"],
                    "context_window": context_window,
                    "local_vs_frontier": identity["local_vs_frontier"],
                    "profile_class": identity["profile_class"],
                    "reasoning_capability_class": identity["reasoning_capability_class"],
                },
            },
            workspace_root=Path(workspace_root),
        )

        start_time = time.perf_counter()
        classification_model_name = identity["model_name"] if identity["model_name"] else "unknown"
        classification_model_source = identity["model_source"] if identity["model_source"] else "unknown"
        classification_model_size = model_size if model_size else "small"
        capability_bundle = CapabilityClassifier.classify(
            model_name=classification_model_name,
            model_source=classification_model_source,
            context_window=context_window,
            model_size_hint=classification_model_size,
            profile_class_hint=identity["profile_class"],
            local_vs_frontier=identity["local_vs_frontier"],
            reasoning_capability_class=identity["reasoning_capability_class"],
        )

        emit_runtime_event(
            subsystem="PECS_LITE",
            event="capability_classification_completed",
            payload={
                "projection_profile": capability_bundle.get("projection_profile", {}),
                "model_detection": capability_bundle.get("model_detection", {}),
                "profile_class": "frontier" if capability_bundle.get("projection_profile", {}).get("profile") in {"frontier_online", "reasoning_frontier", "agentic_frontier", "large_local"} else "local",
                "reasoning_capability_class": (
                    "small"
                    if capability_bundle.get("projection_profile", {}).get("profile") == "small_local"
                    else "medium"
                    if capability_bundle.get("projection_profile", {}).get("profile") == "medium_local"
                    else "frontier"
                ),
            },
            workspace_root=Path(workspace_root),
        )

        profile_name = capability_bundle.get("projection_profile", {}).get("profile", "small_local")
        limits = cls._profile_limits(profile_name)

        # Primary path: canonical Query Pipeline.
        projection = None
        fallback_reason = ""
        try:
            projection = cls._build_projection_from_pipeline(
                workspace_root=workspace_root,
                query=query,
                identity=identity,
                query_source=query_source,
                capability_bundle=capability_bundle,
                include_diagnostics=include_diagnostics,
            )
        except Exception as exc:
            fallback_reason = f"query_pipeline_failed:{exc}"

        if projection is None and PECSLiteRuntimeV2 is not None:
            fallback_reason = fallback_reason or "query_pipeline_unavailable"
            runtime = PECSLiteRuntimeV2(str(workspace_root))
            projection = runtime.build_projection(
                model_size=model_size,
                include_diagnostics=include_diagnostics,
                issue_query=query,
                model_name=identity["model_name"],
                model_source=identity["model_source"],
                context_window=context_window,
                query_source=query_source,
                provider=identity["provider"],
                profile_class=identity["profile_class"],
                local_vs_frontier=identity["local_vs_frontier"],
                reasoning_capability_class=identity["reasoning_capability_class"],
            )
            projection["pecs_lite_telemetry"]["fallback_triggered"] = True
            projection["pecs_lite_telemetry"]["fallback_reason"] = fallback_reason
            if isinstance(projection.get("final_emission_observability"), dict):
                projection["final_emission_observability"]["fallback_triggered"] = True

        if projection is None:
            raise RuntimeError(
                "PECS-LITE unable to build projection: Query Pipeline failed and legacy runtime is unavailable."
            )

        elapsed_ms = int((time.perf_counter() - start_time) * 1000)
        projection["pecs_lite_telemetry"]["projection_generation_time_ms"] = elapsed_ms
        projection["pecs_lite_status"]["fallback_reason"] = fallback_reason if fallback_reason else ""

        emit_runtime_event(
            subsystem="PECS_LITE",
            event="projection_hardener_completed",
            payload={
                "profile_name": profile_name,
                "raw_targets": projection["pecs_lite_telemetry"].get("candidate_count", 0),
                "primary_targets": len(projection.get("runtime_targets", [])),
                "secondary_neighbors": len(projection.get("secondary_neighbors", [])),
                "token_budget_selected": limits.get("token_budget", 2000),
                "projected_token_estimate": projection.get("metrics", {}).get("projected_token_estimate", 0),
                "locality_breadth_score": projection.get("metrics", {}).get("locality_breadth_score", 0.0),
                "entropy_reduction_score": projection.get("metrics", {}).get("entropy_reduction_score", 0.0),
                "deterministic_narrowing_activated": True,
                "progressive_disclosure_activated": projection.get("metrics", {}).get("progressive_locality_disclosure_applied", False),
                "runtime_zone_count": projection.get("metrics", {}).get("runtime_zone_count", 0),
                "query_pipeline_active": not bool(fallback_reason),
                "fallback_reason": fallback_reason,
            },
            workspace_root=Path(workspace_root),
        )

        projection["consumer_decision"] = consumer_decision or {
            "query_source": query_source,
            "mode": "advisory_evidence",
            "hard_enforcement": False,
            "force_edit_destination": False,
        }
        projection["canonical_query"] = cls._build_canonical_query_envelope(
            workspace_root=workspace_root,
            query=query,
            query_source=query_source,
            model_name=identity["model_name"],
            model_source=identity["model_source"],
            context_window=context_window,
            provider=identity["provider"],
            profile_class=identity["profile_class"],
            local_vs_frontier=identity["local_vs_frontier"],
            reasoning_capability_class=identity["reasoning_capability_class"],
            capability_bundle=capability_bundle,
        )
        projection["canonical_response_snapshot"] = cls._build_canonical_response_snapshot(projection)

        emit_runtime_event(
            subsystem="PECS_LITE",
            event="projection_invocation_completed",
            payload={
                "query_source": query_source,
                "projection_profile": profile_name,
                "runtime_targets": len(projection.get("runtime_targets", [])),
                "secondary_neighbors": len(projection.get("secondary_neighbors", [])),
                "projected_token_estimate": projection.get("metrics", {}).get("projected_token_estimate", 0),
                "deterministic_narrowing_applied": True,
                "progressive_disclosure_applied": projection.get("metrics", {}).get("progressive_locality_disclosure_applied", False),
                "authority_confidence": projection.get("pecs_lite_status", {}).get("authority_confidence"),
                "payload_size": projection["pecs_lite_telemetry"].get("payload_size", 0),
                "token_budget_selected": limits.get("token_budget", 2000),
                "query_pipeline_active": not bool(fallback_reason),
                "fallback_reason": fallback_reason,
                "diagnostics_included": include_diagnostics,
            },
            workspace_root=Path(workspace_root),
        )

        return projection

    @classmethod
    def build_projection_safe(
        cls,
        workspace_root: str,
        query: str,
        model_name: str = "",
        model_source: str = "",
        context_window: int = 0,
        model_size: str = "small",
        provider: str = "",
        profile_class: str = "",
        local_vs_frontier: str = "",
        reasoning_capability_class: str = "",
        query_source: str = "unknown",
        consumer_decision: Optional[Dict[str, Any]] = None,
        include_diagnostics: bool = True,
    ) -> Dict[str, Any]:
        try:
            return cls.build_projection(
                workspace_root=workspace_root,
                query=query,
                model_name=model_name,
                model_source=model_source,
                context_window=context_window,
                model_size=model_size,
                provider=provider,
                profile_class=profile_class,
                local_vs_frontier=local_vs_frontier,
                reasoning_capability_class=reasoning_capability_class,
                query_source=query_source,
                include_diagnostics=include_diagnostics,
            )
        except Exception as exc:
            return {
                "schema": "pecs_lite.runtime_projection.error.v1",
                "adapter": "pecs_lite",
                "query": query,
                "model_name": model_name,
                "model_source": model_source or provider,
                "context_window": context_window,
                "model_size": model_size,
                "profile_class": profile_class,
                "local_vs_frontier": local_vs_frontier,
                "reasoning_capability_class": reasoning_capability_class,
                "query_source": query_source,
                "unknown_model_identity": not bool(model_name and (model_source or provider) and profile_class and local_vs_frontier),
                "error": str(exc),
                "fallback_allowed": True,
                "runtime_targets": [],
                "secondary_neighbors": [],
                "metrics": {
                    "projected_token_estimate": 0,
                    "projected_target_count": 0,
                    "projected_secondary_count": 0,
                },
                "pecs_lite_status": {
                    "runtime_observability_used": False,
                    "engineering_continuity_used": False,
                    "workspace_scan_performed": False,
                    "symbol_resolution_used": False,
                    "behavioral_analysis_used": False,
                    "capability_detection_used": False,
                    "authority_confidence": 0.0,
                    "fallback_reason": str(exc),
                },
                "pecs_lite_telemetry": {
                    "runtime_invoked": False,
                    "adapter_used": "PECSLiteRuntimeAdapter",
                    "runtime_available": True,
                    "projection_generated": False,
                    "fallback_triggered": True,
                    "fallback_reason": str(exc),
                },
                "consumer_decision": consumer_decision or {
                    "query_source": query_source,
                    "mode": "advisory_evidence",
                    "hard_enforcement": False,
                    "force_edit_destination": False,
                },
                "canonical_query": cls._build_canonical_query_envelope(
                    workspace_root=workspace_root,
                    query=query,
                    query_source=query_source,
                    model_name=model_name,
                    model_source=model_source,
                    context_window=context_window,
                    provider=provider,
                    profile_class=profile_class,
                    local_vs_frontier=local_vs_frontier,
                    reasoning_capability_class=reasoning_capability_class,
                    capability_bundle={
                        "projection_profile": {
                            "profile": "small_local",
                            "reasoning_budget": "low",
                            "exploration_constraints": "strict",
                            "max_related_files": 3,
                            "token_budget": 2000,
                            "capability_class": "weak_reasoning_local",
                        }
                    },
                ),
                "canonical_response_snapshot": {
                    "schema": "pecs_lite.runtime_projection.error.v1",
                    "runtime_targets": [],
                    "secondary_neighbors": [],
                },
            }
