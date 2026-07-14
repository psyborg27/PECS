from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

from runtime.runtime_telemetry import emit_runtime_event

from .pecs_lite_runtime_adapter import PECSLiteRuntimeAdapter

CANONICAL_CONSUMER_RESPONSE_SCHEMA = "pecs.consumer_response_contract.v1"
SUPPORTED_CONSUMERS = ("continue", "copilot", "commandcode", "kimi")

_CANONICAL_CONTRACT_KEYS = {
    "schema",
    "adapter",
    "consumer",
    "consultation",
    "canonical_query",
    "projection",
    "continuity_context",
    "emitted_advisory_cognition",
    "discarded_cognition_summary",
    "shaping_losses",
    "final_emission_observability",
    "consumption_boundary",
}


@dataclass
class ConsultationPolicy:
    global_enabled: bool = True
    consumers: Dict[str, bool] = field(
        default_factory=lambda: {
            "continue": True,
            "copilot": True,
            "commandcode": True,
            "kimi": True,
        }
    )

    def enabled_for(self, consumer: str) -> bool:
        if not self.global_enabled:
            return False
        return bool(self.consumers.get(consumer, True))


class ConsumerIntegrationConfig:
    @staticmethod
    def load(workspace_root: Path) -> ConsultationPolicy:
        policy = ConsultationPolicy()
        config_path = (
            workspace_root
            / ".pecs"
            / "config"
            / "consumer_consultation.json"
        )

        if config_path.exists():
            try:
                payload = json.loads(config_path.read_text(encoding="utf-8"))
            except Exception:
                payload = {}
            if isinstance(payload, dict):
                policy.global_enabled = bool(
                    payload.get("global_enabled", policy.global_enabled)
                )
                raw_consumers = payload.get("consumers", {})
                if isinstance(raw_consumers, dict):
                    for name in SUPPORTED_CONSUMERS:
                        if name in raw_consumers:
                            policy.consumers[name] = bool(raw_consumers[name])

        env_global = os.environ.get("PECS_CONSULTATION_ENABLED", "").strip().lower()
        if env_global in {"0", "false", "off", "no"}:
            policy.global_enabled = False
        elif env_global in {"1", "true", "on", "yes"}:
            policy.global_enabled = True

        return policy


class CanonicalConsumerContract:
    @staticmethod
    def validate(payload: Mapping[str, Any]) -> Dict[str, Any]:
        keys = set(payload.keys())
        missing = sorted(_CANONICAL_CONTRACT_KEYS - keys)
        unknown = sorted(keys - (_CANONICAL_CONTRACT_KEYS | {"fallback_context"}))
        schema_ok = (
            str(payload.get("schema", "")) == CANONICAL_CONSUMER_RESPONSE_SCHEMA
        )

        consultation = payload.get("consultation", {})
        consultation_ok = isinstance(consultation, dict) and all(
            key in consultation
            for key in (
                "enabled",
                "consultation_appropriate",
                "query_issued",
                "response_received",
                "used",
                "reasoning",
            )
        )

        valid = schema_ok and not missing and not unknown and consultation_ok
        return {
            "valid": valid,
            "schema_ok": schema_ok,
            "consultation_ok": consultation_ok,
            "missing_keys": missing,
            "unknown_keys": unknown,
            "contract_keys": sorted(keys),
        }


@dataclass
class ConsumerIntegrationModel:
    consumer: str
    topology_retriever: Any
    workspace_root: Optional[Path] = None

    def _resolved_workspace_root(self) -> Path:
        if self.workspace_root is not None:
            return self.workspace_root.resolve()
        return Path.cwd().resolve()

    def _build_consultation_report(
        self,
        enabled: bool,
        consultation_appropriate: bool,
        query_issued: bool,
        response_received: bool,
        used: bool,
        reasoning: str,
    ) -> Dict[str, Any]:
        return {
            "enabled": enabled,
            "consultation_appropriate": consultation_appropriate,
            "query_issued": query_issued,
            "response_received": response_received,
            "used": used,
            "reasoning": reasoning,
        }

    def build_context(
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
    ) -> Dict[str, Any]:
        workspace_root = self._resolved_workspace_root()
        policy = ConsumerIntegrationConfig.load(workspace_root)
        enabled = policy.enabled_for(self.consumer)
        query = str(object_id or "").strip()
        consultation_appropriate = enabled and bool(query)

        continuity_context = self.topology_retriever.build_minimal_context(object_id)

        emit_runtime_event(
            subsystem="DOWNSTREAM",
            event=f"{self.consumer}_consultation_started",
            payload={
                "consumer": self.consumer,
                "enabled": enabled,
                "consultation_appropriate": consultation_appropriate,
                "query": query,
            },
            workspace_root=workspace_root,
        )

        projection: Dict[str, Any] = {}
        fallback_context: Optional[Dict[str, Any]] = None
        reasoning = "consultation disabled by policy"
        query_issued = False
        response_received = False
        used = False

        if consultation_appropriate:
            query_issued = True
            projection = PECSLiteRuntimeAdapter.build_projection_safe(
                workspace_root=str(workspace_root),
                query=query,
                model_name=model_name,
                model_source=model_source,
                context_window=context_window,
                model_size=model_size,
                provider=provider,
                profile_class=str(profile_class or "").strip().lower() or "unknown",
                local_vs_frontier=str(local_vs_frontier or "").strip().lower()
                or "unknown",
                reasoning_capability_class=str(reasoning_capability_class or "")
                .strip()
                .lower()
                or "unknown",
                query_source=self.consumer,
            )
            response_received = True
            used = not str(projection.get("schema", "")).startswith(
                "pecs_lite.runtime_projection.error"
            )
            if used:
                reasoning = "projection delivered and accepted as advisory evidence"
            else:
                fallback_context = continuity_context
                reasoning = "projection unavailable; fallback continuity context used"
        elif enabled and not query:
            reasoning = "consultation skipped: empty query"

        consultation = self._build_consultation_report(
            enabled=enabled,
            consultation_appropriate=consultation_appropriate,
            query_issued=query_issued,
            response_received=response_received,
            used=used,
            reasoning=reasoning,
        )

        canonical_response: Dict[str, Any] = {
            "schema": CANONICAL_CONSUMER_RESPONSE_SCHEMA,
            "adapter": self.consumer,
            "consumer": self.consumer,
            "consultation": consultation,
            "canonical_query": projection.get(
                "canonical_query", {"consumer": self.consumer, "issue": query}
            ),
            "projection": projection,
            "continuity_context": continuity_context,
            "emitted_advisory_cognition": projection.get(
                "emitted_advisory_cognition", {}
            ),
            "discarded_cognition_summary": projection.get(
                "discarded_cognition_summary", {}
            ),
            "shaping_losses": projection.get("shaping_losses", {}),
            "final_emission_observability": projection.get(
                "final_emission_observability", {}
            ),
            "consumption_boundary": {
                "mode": "advisory_evidence",
                "hard_enforcement": False,
                "force_edit_destination": False,
            },
        }

        if fallback_context is not None:
            canonical_response["fallback_context"] = fallback_context

        contract_validation = CanonicalConsumerContract.validate(canonical_response)
        if not contract_validation.get("valid", False):
            raise ValueError(
                "Canonical consumer contract validation failed: "
                + json.dumps(contract_validation, sort_keys=True)
            )

        emit_runtime_event(
            subsystem="DOWNSTREAM",
            event=f"{self.consumer}_consultation_completed",
            payload={
                "consumer": self.consumer,
                "query_issued": query_issued,
                "response_received": response_received,
                "used": used,
                "reasoning": reasoning,
                "contract_schema": CANONICAL_CONSUMER_RESPONSE_SCHEMA,
            },
            workspace_root=workspace_root,
        )

        return canonical_response
