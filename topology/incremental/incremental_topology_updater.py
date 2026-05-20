from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set

from execution_graph.indexes.graph_index import (
    GraphIndex,
)
from topology.indexing.locality_index import (
    LocalityIndex,
)
from topology.retrieval.topology_retriever import (
    TopologyRetriever,
)


@dataclass
class IncrementalTopologyUpdater:
    """
    Consolidated incremental continuity updater.

    Intentionally consolidates:
    - localized invalidation
    - topology refresh
    - continuity refresh
    - locality rebuild
    - selective re-indexing

    into ONE authority module.

    PECS avoids:
    - rebuild orchestration forests
    - invalidation managers
    - dependency daemons
    - sync pipelines
    - background mutation systems

    Incremental rebuilding remains:
    deterministic
    localized
    topology-aware
    continuity-safe
    """

    graph_index: GraphIndex
    locality_index: LocalityIndex
    topology_retriever: TopologyRetriever

    invalidated_objects: Set[str] = field(
        default_factory=set
    )

    invalidated_paths: Set[str] = field(
        default_factory=set
    )

    rebuild_metadata: Dict[str, object] = field(
        default_factory=dict
    )

    def invalidate_object(
        self,
        object_id: str,
    ) -> None:
        self.invalidated_objects.add(object_id)

    def invalidate_path(
        self,
        path_id: str,
    ) -> None:
        self.invalidated_paths.add(path_id)

    def refresh_object_locality(
        self,
        object_id: str,
        locality_nodes: List[str],
    ) -> None:
        self.locality_index.register_object_locality(
            object_id,
            locality_nodes,
        )

    def refresh_graph_node(
        self,
        node_id: str,
        node_data: Dict[str, object],
    ) -> None:
        self.graph_index.register_node(
            node_id,
            node_data,
        )

    def rebuild_minimal_context(
        self,
        object_id: str,
    ) -> Dict[str, object]:
        return (
            self.topology_retriever
            .build_minimal_context(object_id)
        )

    def selective_workspace_refresh(
        self,
        changed_files: List[Path],
    ) -> Dict[str, object]:
        refreshed = []

        for path in changed_files:
            refreshed.append(str(path))

        return {
            "refreshed_files": refreshed,
            "invalidated_objects": sorted(
                self.invalidated_objects
            ),
            "invalidated_paths": sorted(
                self.invalidated_paths
            ),
        }

    def refresh_locality_authority_evidence(
        self,
        evidence_by_object: Dict[str, Dict[str, object]],
        max_objects: int = 24,
    ) -> Dict[str, object]:
        """Return bounded evidence updates for invalidated objects only.

        This preserves incremental recomputation boundaries and avoids global rescans.
        """
        refreshed: Dict[str, Dict[str, object]] = {}
        invalidated = sorted(self.invalidated_objects)
        for object_id in invalidated[:max_objects]:
            payload = evidence_by_object.get(object_id)
            if isinstance(payload, dict):
                refreshed[object_id] = dict(payload)

        return {
            "refreshed_evidence": refreshed,
            "refreshed_count": len(refreshed),
            "invalidated_object_count": len(self.invalidated_objects),
            "bounded_max_objects": max_objects,
        }

    def clear_invalidations(self) -> None:
        self.invalidated_objects.clear()
        self.invalidated_paths.clear()

    def to_dict(self) -> Dict[str, object]:
        return {
            "invalidated_objects": sorted(
                self.invalidated_objects
            ),
            "invalidated_paths": sorted(
                self.invalidated_paths
            ),
            "rebuild_metadata": self.rebuild_metadata,
        }
