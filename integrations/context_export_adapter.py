from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from topology.retrieval.topology_retriever import TopologyRetriever


@dataclass
class ContextExportAdapter:
    """
    Consolidated continuity export adapter.

    Produces:
    - compact continuity exports
    - topology-local exports
    - execution-local exports
    - low-token reconstruction contexts

    PECS intentionally avoids export middleware proliferation.
    """

    topology_retriever: TopologyRetriever

    export_metadata: Dict[str, object] = field(
        default_factory=dict
    )

    def export_object_context(
        self,
        object_id: str,
    ) -> Dict[str, object]:
        return (
            self.topology_retriever
            .build_minimal_context(object_id)
        )

    def export_context_bundle(
        self,
        object_ids: List[str],
    ) -> Dict[str, object]:
        bundle = []

        for object_id in object_ids:
            bundle.append(
                self.export_object_context(object_id)
            )

        return {
            "bundle": bundle,
        }

    def to_dict(self) -> Dict[str, object]:
        return {
            "export_metadata": self.export_metadata,
        }
