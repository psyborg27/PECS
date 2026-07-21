from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from integrations.commandcode_adapter import CommandCodeAdapter
from integrations.consumer_integration_core import (
    CANONICAL_CONSUMER_RESPONSE_SCHEMA,
    CanonicalConsumerContract,
    ConsumerIntegrationConfig,
)
from integrations.continue_adapter import ContinueAdapter
from integrations.copilot_adapter import CopilotAdapter
from integrations.kimi_adapter import KimiAdapter
from integrations.pecs_lite_runtime_adapter import PECSLiteRuntimeAdapter


@dataclass
class ConsumerConsultationComplianceResult:
    consumer: str
    valid: bool
    query: str
    adapter: str
    contract_valid: bool
    consultation: Dict[str, Any]
    canonical_query: Dict[str, Any]
    projection_schema: str
    response_received: bool
    response_used: bool
    files_returned: List[str]
    classes_returned: List[str]
    methods_returned: List[str]
    runtime_objects_returned: List[str]
    report_errors: List[str] = field(default_factory=list)
    compliance: Dict[str, str] = field(default_factory=dict)
    details: Dict[str, Any] = field(default_factory=dict)


class ConsumerConsultationComplianceValidator:
    CONSUMER_ADAPTERS: Dict[str, Tuple[Type[Any], str]] = {
        "copilot": (CopilotAdapter, "build_copilot_context"),
        "continue": (ContinueAdapter, "build_continue_context"),
        "kimi": (KimiAdapter, "build_kimi_context"),
        "commandcode": (CommandCodeAdapter, "build_commandcode_context"),
    }

    DEFAULT_MODEL_METADATA: Dict[str, Any] = {
        "model_name": "gpt-4o",
        "model_source": "openai",
        "context_window": 250000,
        "model_size": "large",
        "provider": "openai",
        "profile_class": "frontier",
        "local_vs_frontier": "frontier",
        "reasoning_capability_class": "very_high",
    }

    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root.resolve()
        self.policy = ConsumerIntegrationConfig.load(self.workspace_root)

    def validate_consumer(
        self,
        consumer: str,
        object_id: str = "PECS_ID:consultation_test",
    ) -> ConsumerConsultationComplianceResult:
        errors: List[str] = []
        consumer = consumer.lower().strip()
        if consumer not in self.CONSUMER_ADAPTERS:
            raise ValueError(f"Unsupported consumer: {consumer}")

        adapter_class, build_method_name = self.CONSUMER_ADAPTERS[consumer]
        adapter = adapter_class(
            topology_retriever=self._dummy_topology_retriever(),
            workspace_root=self.workspace_root,
        )

        enabled = self.policy.enabled_for(consumer)
        result_payload: Dict[str, Any] = {}

        try:
            build_method = getattr(adapter, build_method_name)
            result_payload = build_method(
                object_id=object_id,
                **self.DEFAULT_MODEL_METADATA,
            )
        except Exception as exc:
            errors.append(f"consumer invocation raised exception: {exc}")
            return ConsumerConsultationComplianceResult(
                consumer=consumer,
                valid=False,
                query=object_id,
                adapter=adapter_class.__name__,
                contract_valid=False,
                consultation={},
                canonical_query={},
                projection_schema="",
                response_received=False,
                response_used=False,
                files_returned=[],
                classes_returned=[],
                methods_returned=[],
                runtime_objects_returned=[],
                report_errors=errors,
                compliance={
                    "query": "FAIL",
                    "response": "FAIL",
                    "context_injection": "FAIL",
                    "consultation_report": "FAIL",
                    "enable_disable": "FAIL",
                },
                details={
                    "exception": str(exc),
                },
            )

        contract_validation = CanonicalConsumerContract.validate(result_payload)
        if not contract_validation.get("valid", False):
            errors.append(
                f"canonical contract validation failed: missing={contract_validation.get('missing_keys')} unknown={contract_validation.get('unknown_keys')}"
            )

        consultation = result_payload.get("consultation", {})
        canonical_query = result_payload.get("canonical_query", {})
        projection = result_payload.get("projection", {})
        response_received = bool(consultation.get("response_received", False))
        response_used = bool(consultation.get("used", False))

        projection_schema = str(projection.get("schema", ""))
        response_present = isinstance(projection, dict)
        context_injected = bool(
            result_payload.get("projection") is not None
            and result_payload.get("continuity_context") is not None
        )

        query_emitted = bool(
            canonical_query
            and canonical_query.get("consumer") == consumer
            and canonical_query.get("issue") == object_id
        )
        if not query_emitted:
            errors.append("canonical_query missing or consumer/issue mismatch")

        if enabled and not consultation.get("query_issued", False):
            errors.append("consultation should be issued when enabled and query is present")

        if not enabled and consultation.get("query_issued", False):
            errors.append("consultation should not be issued when disabled")

        if enabled and consultation.get("consultation_appropriate") is False:
            errors.append("consultation should be appropriate when enabled and query exists")

        if enabled and not response_received:
            errors.append("enabled consultation did not receive a response")

        if not response_present:
            errors.append("projection response is not present")

        final_observability = result_payload.get("final_emission_observability", {})
        if not isinstance(final_observability, dict):
            errors.append("final_emission_observability missing or invalid")

        files_returned = self._extract_files_returned(projection)
        classes_returned = self._extract_classes_returned(projection)
        methods_returned = self._extract_methods_returned(projection)
        runtime_objects_returned = self._extract_runtime_object_ids(projection)

        enable_disable_status = "PASS"
        if enabled and consultation.get("enabled") is not True:
            enable_disable_status = "FAIL"
        if not enabled and consultation.get("enabled") is not False:
            enable_disable_status = "FAIL"

        return ConsumerConsultationComplianceResult(
            consumer=consumer,
            valid=not bool(errors),
            query=object_id,
            adapter=adapter_class.__name__,
            contract_valid=contract_validation.get("valid", False),
            consultation=consultation,
            canonical_query=canonical_query,
            projection_schema=projection_schema,
            response_received=response_received,
            response_used=response_used,
            files_returned=files_returned,
            classes_returned=classes_returned,
            methods_returned=methods_returned,
            runtime_objects_returned=runtime_objects_returned,
            report_errors=errors,
            compliance={
                "query": "PASS" if query_emitted else "FAIL",
                "response": "PASS" if response_received else "FAIL",
                "context_injection": "PASS" if context_injected else "FAIL",
                "consultation_report": "PASS" if contract_validation.get("valid", False) else "FAIL",
                "enable_disable": enable_disable_status,
            },
            details={
                "projection_schema": projection_schema,
                "final_emission_observability": final_observability,
                "response_present": response_present,
                "projection_payload": projection,
            },
        )

    def validate_all(self) -> List[ConsumerConsultationComplianceResult]:
        results: List[ConsumerConsultationComplianceResult] = []
        for consumer in self.CONSUMER_ADAPTERS:
            results.append(self.validate_consumer(consumer))
        return results

    @staticmethod
    def _extract_files_returned(projection: Dict[str, Any]) -> List[str]:
        runtime_targets = projection.get("runtime_targets") or []
        return [str(item.get("file", "")) for item in runtime_targets if item.get("file")]

    @staticmethod
    def _extract_classes_returned(projection: Dict[str, Any]) -> List[str]:
        runtime_targets = projection.get("runtime_targets") or []
        return [
            item.get("node_id")
            for item in runtime_targets
            if item.get("node_type") == "class" and item.get("node_id")
        ]

    @staticmethod
    def _extract_methods_returned(projection: Dict[str, Any]) -> List[str]:
        runtime_targets = projection.get("runtime_targets") or []
        methods: List[str] = []
        for item in runtime_targets:
            node_type = str(item.get("node_type", ""))
            node_id = item.get("node_id")
            if node_type in {"method", "function"} and node_id:
                methods.append(node_id)
            elif isinstance(node_id, str) and "." in node_id:
                methods.append(node_id)
        return methods

    @staticmethod
    def _extract_runtime_object_ids(projection: Dict[str, Any]) -> List[str]:
        runtime_targets = projection.get("runtime_targets") or []
        return [item.get("node_id") for item in runtime_targets if item.get("node_id")]

    class _dummy_topology_retriever:
        @staticmethod
        def build_minimal_context(object_id: str) -> Dict[str, Any]:
            return {"object_id": object_id}
