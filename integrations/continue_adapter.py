from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from topology.retrieval.topology_retriever import TopologyRetriever

from .consumer_integration_core import ConsumerIntegrationModel


@dataclass
class ContinueAdapter:
    """Thin wrapper around the shared canonical consumer integration model."""

    topology_retriever: TopologyRetriever
    workspace_root: Optional[Path] = None

    adapter_metadata: Dict[str, object] = field(
        default_factory=dict
    )

    def _resolved_workspace_root(self) -> Path:
        if self.workspace_root is not None:
            return self.workspace_root.resolve()
        return Path.cwd().resolve()

    def build_continue_context(
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
        model = ConsumerIntegrationModel(
            consumer="continue",
            topology_retriever=self.topology_retriever,
            workspace_root=self._resolved_workspace_root(),
        )
        return model.build_context(
            object_id=object_id,
            model_name=model_name,
            model_source=model_source,
            context_window=context_window,
            model_size=model_size,
            provider=provider,
            profile_class=profile_class,
            local_vs_frontier=local_vs_frontier,
            reasoning_capability_class=reasoning_capability_class,
        )

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
