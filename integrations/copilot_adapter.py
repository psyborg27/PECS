from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from ..topology.retrieval.topology_retriever import (
    TopologyRetriever,
)
from runtime.runtime_telemetry import emit_runtime_event


@dataclass
class CopilotAdapter:
    """
    Consolidated Copilot integration adapter.

    Designed for:
    - locality-directed retrieval
    - compact continuity reconstruction
    - low-token context delivery
    """

    topology_retriever: TopologyRetriever

    adapter_metadata: Dict[str, object] = field(
        default_factory=dict
    )

    def build_copilot_context(
        self,
        object_id: str,
    ) -> Dict[str, object]:
        emit_runtime_event(
            subsystem="DOWNSTREAM",
            event="copilot_request_intercepted",
            payload={"object_id": object_id},
        )
        continuity_context = (
            self.topology_retriever
            .build_minimal_context(object_id)
        )
        emit_runtime_event(
            subsystem="DOWNSTREAM",
            event="copilot_context_built",
            payload={
                "object_id": object_id,
                "anchors": continuity_context.get("anchors", []),
                "confidence": continuity_context.get("confidence"),
            },
        )

        return {
            "adapter": "copilot",
            "continuity_context": continuity_context,
        }

    def build_multi_object_context(
        self,
        object_ids: List[str],
    ) -> Dict[str, object]:
        reconstructed = []

        for object_id in object_ids:
            reconstructed.append(
                self.build_copilot_context(object_id)
            )

        return {
            "contexts": reconstructed,
        }

    def to_dict(self) -> Dict[str, object]:
        return {
            "adapter_metadata": self.adapter_metadata,
        }
