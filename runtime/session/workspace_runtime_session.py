from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set

from execution_graph.indexes.execution_index import (
    ExecutionIndex,
)
from execution_graph.indexes.graph_index import (
    GraphIndex,
)
from topology.indexing.locality_index import (
    LocalityIndex,
)
from topology.retrieval.topology_retriever import (
    TopologyRetriever,
)
from topology.incremental.incremental_topology_updater import (
    IncrementalTopologyUpdater,
)


@dataclass
class WorkspaceRuntimeSession:
    """
    Consolidated live workspace continuity session.

    This intentionally consolidates:
    - active continuity locality
    - active topology zones
    - active engineering surfaces
    - runtime continuity state
    - active retrieval state
    - selective refresh coordination

    into ONE runtime session authority.

    PECS intentionally avoids:
    - runtime daemon forests
    - orchestration coordinators
    - background middleware systems
    - recursive session managers

    The session remains:
    deterministic
    lightweight
    topology-local
    continuity-oriented
    """

    workspace_root: Path

    graph_index: GraphIndex
    execution_index: ExecutionIndex
    locality_index: LocalityIndex

    topology_retriever: TopologyRetriever
    incremental_updater: IncrementalTopologyUpdater

    active_objects: Set[str] = field(
        default_factory=set
    )

    active_paths: Set[str] = field(
        default_factory=set
    )

    active_zones: Set[str] = field(
        default_factory=set
    )

    active_context_cache: Dict[str, Dict[str, object]] = field(
        default_factory=dict
    )

    session_metadata: Dict[str, object] = field(
        default_factory=dict
    )

    current_focus_object: Optional[str] = None

    def activate_object(
        self,
        object_id: str,
    ) -> None:
        self.active_objects.add(object_id)

    def activate_path(
        self,
        path_id: str,
    ) -> None:
        self.active_paths.add(path_id)

    def activate_zone(
        self,
        zone_id: str,
    ) -> None:
        self.active_zones.add(zone_id)

    def set_focus_object(
        self,
        object_id: str,
    ) -> None:
        self.current_focus_object = object_id
        self.activate_object(object_id)

    def build_focus_context(
        self,
    ) -> Dict[str, object]:
        if not self.current_focus_object:
            return {}

        path_id = next(iter(self.active_paths), None)
        owner_id = self.current_focus_object

        context = (
            self.topology_retriever
            .build_minimal_context(
                self.current_focus_object,
                path_id=path_id,
                owner_id=owner_id,
                enforce=False,
            )
        )

        self.active_context_cache[
            self.current_focus_object
        ] = context

        self.session_metadata["last_retrieval"] = context.get("telemetry", {})
        self.session_metadata["last_focus_context"] = {
            "object_id": self.current_focus_object,
            "path_id": path_id,
            "owner_id": owner_id,
            "retrieval_status": "success",
        }

        return context

    def refresh_changed_files(
        self,
        changed_files: List[Path],
    ) -> Dict[str, object]:
        return (
            self.incremental_updater
            .selective_workspace_refresh(
                changed_files
            )
        )

    def invalidate_object(
        self,
        object_id: str,
    ) -> None:
        self.incremental_updater.invalidate_object(
            object_id
        )

    def invalidate_path(
        self,
        path_id: str,
    ) -> None:
        self.incremental_updater.invalidate_path(
            path_id
        )

    def get_cached_context(
        self,
        object_id: str,
    ) -> Optional[Dict[str, object]]:
        return self.active_context_cache.get(
            object_id
        )

    def clear_context_cache(self) -> None:
        self.active_context_cache.clear()

    def export_session_state(
        self,
    ) -> Dict[str, object]:
        return {
            "workspace_root": str(
                self.workspace_root
            ),
            "active_objects": sorted(
                self.active_objects
            ),
            "active_paths": sorted(
                self.active_paths
            ),
            "active_zones": sorted(
                self.active_zones
            ),
            "current_focus_object": (
                self.current_focus_object
            ),
            "cached_contexts": list(
                self.active_context_cache.keys()
            ),
        }

    def to_dict(self) -> Dict[str, object]:
        return {
            "workspace_root": str(
                self.workspace_root
            ),
            "active_objects": sorted(
                self.active_objects
            ),
            "active_paths": sorted(
                self.active_paths
            ),
            "active_zones": sorted(
                self.active_zones
            ),
            "current_focus_object": (
                self.current_focus_object
            ),
            "session_metadata": (
                self.session_metadata
            ),
        }
