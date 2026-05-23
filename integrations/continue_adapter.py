from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from ..topology.retrieval.topology_retriever import (
    TopologyRetriever,
)
from runtime.runtime_telemetry import emit_runtime_event


@dataclass
class ContinueAdapter:
    """
    Consolidated Continue integration adapter.

    Intentionally consolidates:
    - context preparation
    - continuity export
    - locality reconstruction
    - compact context generation

    into ONE integration authority.

    PECS avoids integration fragmentation deliberately.
    """

    topology_retriever: TopologyRetriever

    adapter_metadata: Dict[str, object] = field(
        default_factory=dict
    )

    def build_continue_context(
        self,
        object_id: str,
    ) -> Dict[str, object]:
        emit_runtime_event(
            subsystem="DOWNSTREAM",
            event="continue_request_intercepted",
            payload={"object_id": object_id},
        )
        continuity_context = (
            self.topology_retriever
            .build_minimal_context(object_id)
        )
        emit_runtime_event(
            subsystem="DOWNSTREAM",
            event="continue_context_built",
            payload={
                "object_id": object_id,
                "anchors": continuity_context.get("anchors", []),
                "confidence": continuity_context.get("confidence"),
            },
        )

        return {
            "adapter": "continue",
            "continuity_context": continuity_context,
        }

    def build_compact_context_window(
        self,
        object_ids: List[str],
    ) -> Dict[str, object]:
        reconstructed = []

        for object_id in object_ids:
            reconstructed.append(
                self.build_continue_context(object_id)
            )

        return {
            "contexts": reconstructed,
        }

    def to_dict(self) -> Dict[str, object]:
        return {
            "adapter_metadata": self.adapter_metadata,
        }
