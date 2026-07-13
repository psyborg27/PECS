from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

from topology.retrieval.topology_retriever import TopologyRetriever
from runtime.runtime_telemetry import emit_runtime_event
from .pecs_lite_runtime_adapter import PECSLiteRuntimeAdapter


@dataclass
class CommandCodeAdapter:
    """
    Command Code runtime adapter.

    This adapter consumes PECS context exclusively through the PECS-LITE compatibility layer.
    """

    topology_retriever: TopologyRetriever
    workspace_root: Optional[Path] = None
    adapter_metadata: Dict[str, object] = field(default_factory=dict)

    def _resolved_workspace_root(self) -> Path:
        if self.workspace_root is not None:
            return self.workspace_root.resolve()
        return Path.cwd().resolve()

    def build_commandcode_context(
        self,
        object_id: str,
        model_name: str = "",
        model_source: str = "",
        context_window: int = 0,
        model_size: str = "small",
        provider: str = "",
        profile_class: str = "",
        local_vs_frontier: str = "",
        reasoning_capability_class: str = "",
    ) -> Dict[str, object]:
        query = str(object_id or "")
        workspace_root = self._resolved_workspace_root()
        emit_runtime_event(
            subsystem="DOWNSTREAM",
            event="commandcode_query_received",
            payload={
                "query": query,
                "model_name": model_name,
                "model_source": model_source or provider,
                "context_window": context_window,
                "model_size": model_size,
            },
            workspace_root=workspace_root,
        )

        normalized_profile_class = str(profile_class or "").strip().lower()
        normalized_locality_class = str(local_vs_frontier or "").strip().lower()
        normalized_reasoning_class = str(reasoning_capability_class or "").strip().lower()
        missing_identity_fields = []
        if not str(model_name or "").strip():
            missing_identity_fields.append("model_name")
        if not str(model_source or provider or "").strip():
            missing_identity_fields.append("provider_or_source")
        if not normalized_profile_class:
            missing_identity_fields.append("profile_class")
        if not normalized_locality_class:
            missing_identity_fields.append("local_vs_frontier")

        unknown_model_identity = bool(missing_identity_fields)
        if unknown_model_identity:
            emit_runtime_event(
                subsystem="DOWNSTREAM",
                event="unknown_model_identity",
                payload={
                    "adapter": "commandcode",
                    "query": query,
                    "query_source": "commandcode",
                    "missing_fields": missing_identity_fields,
                    "conservative_shaping": True,
                },
                workspace_root=workspace_root,
            )

        if not normalized_profile_class:
            normalized_profile_class = "unknown"
        if not normalized_locality_class:
            normalized_locality_class = "unknown"
        if not normalized_reasoning_class:
            normalized_reasoning_class = "unknown"

        projection = PECSLiteRuntimeAdapter.build_projection_safe(
            workspace_root=str(workspace_root),
            query=query,
            model_name=model_name,
            model_source=model_source,
            context_window=context_window,
            model_size=model_size,
            provider=provider,
            profile_class=normalized_profile_class,
            local_vs_frontier=normalized_locality_class,
            reasoning_capability_class=normalized_reasoning_class,
            query_source="commandcode",
        )

        fallback_context = None
        if projection.get("schema", "").startswith("pecs_lite.runtime_projection.error"):
            fallback_context = self.topology_retriever.build_minimal_context(object_id)

        telemetry = projection.get("pecs_lite_telemetry", {})
        emit_runtime_event(
            subsystem="DOWNSTREAM",
            event="commandcode_projection_finalized",
            payload={
                "query": query,
                "projection_schema": projection.get("schema"),
                "authority_confidence": projection.get("pecs_lite_status", {}).get("authority_confidence"),
                "runtime_targets": len(projection.get("runtime_targets", [])),
                "fallback_used": fallback_context is not None,
                "pecs_runtime_invoked": telemetry.get("runtime_invoked", False),
                "adapter_used": telemetry.get("adapter_used", "PECSLiteRuntimeAdapter"),
                "runtime_available": telemetry.get("runtime_available", PECSLiteRuntimeAdapter.is_available()),
                "projection_generated": telemetry.get("projection_generated", not fallback_context),
                "projection_generation_time_ms": telemetry.get("projection_generation_time_ms"),
                "selected_projection_profile": telemetry.get("selected_projection_profile"),
                "profile_class": projection.get("final_emission_observability", {}).get("profile_class", "local"),
                "deterministic_narrowing_activated": telemetry.get("deterministic_narrowing_activated"),
                "progressive_disclosure_activated": telemetry.get("progressive_disclosure_activated"),
                "token_budget_selected": telemetry.get("token_budget_selected") or telemetry.get("selected_token_budget"),
                "projection_delivered": telemetry.get("projection_delivered", fallback_context is None),
                "fallback_triggered": telemetry.get("fallback_triggered", fallback_context is not None),
                "consumption_mode": "advisory_evidence",
                "hard_enforcement": False,
                "unknown_model_identity": unknown_model_identity,
                "identity_missing_fields": missing_identity_fields,
                "final_payload_size": len(json.dumps(projection, sort_keys=True, default=str)),
                "model_identity_input": projection.get("final_emission_observability", {}).get("model_identity_input", {}),
                "emitted_advisory_cognition": projection.get("emitted_advisory_cognition", {}),
                "discarded_cognition_summary": projection.get("discarded_cognition_summary", {}),
                "shaping_losses": projection.get("shaping_losses", {}),
                "final_emission_observability": projection.get("final_emission_observability", {}),
                "cognition_survivability_summary": projection.get("final_emission_observability", {}).get("cognition_survivability_summary", {}),
                "preserved_advisory_modes": projection.get("final_emission_observability", {}).get("preserved_advisory_modes", []),
                "removed_advisory_modes": projection.get("final_emission_observability", {}).get("removed_advisory_modes", []),
                "authority_concentration_score": projection.get("final_emission_observability", {}).get("authority_concentration_score", 0.0),
                "locality_entropy_before": projection.get("final_emission_observability", {}).get("locality_entropy_before", 0.0),
                "locality_entropy_after": projection.get("final_emission_observability", {}).get("locality_entropy_after", 0.0),
                "suppression_reason_breakdown": projection.get("final_emission_observability", {}).get("suppression_reason_breakdown", {}),
                "advisory_signal_priority": projection.get("final_emission_observability", {}).get("advisory_signal_priority", []),
                "authority_confidence_band": projection.get("final_emission_observability", {}).get("authority_confidence_band", "low"),
                "cognition_density_score": projection.get("final_emission_observability", {}).get("cognition_density_score", 0.0),
                "topology_noise_ratio": projection.get("final_emission_observability", {}).get("topology_noise_ratio", 0.0),
            },
            workspace_root=workspace_root,
        )

        result: Dict[str, object] = {
            "adapter": "commandcode",
            "continuity_context": self.topology_retriever.build_minimal_context(object_id),
            "projection": projection,
            "emitted_advisory_cognition": projection.get("emitted_advisory_cognition", {}),
            "discarded_cognition_summary": projection.get("discarded_cognition_summary", {}),
            "shaping_losses": projection.get("shaping_losses", {}),
            "final_emission_observability": projection.get("final_emission_observability", {}),
            "consumption_boundary": {
                "mode": "advisory_evidence",
                "hard_enforcement": False,
                "force_edit_destination": False,
            },
        }
        if fallback_context is not None:
            result["fallback_context"] = fallback_context

        return result

    def to_dict(self) -> Dict[str, object]:
        return {
            "adapter_metadata": self.adapter_metadata,
        }
