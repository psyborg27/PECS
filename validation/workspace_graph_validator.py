from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from execution_graph.graph.workspace_graph import EdgeType, Graph
from execution_graph.indexes.execution_index import ExecutionIndex
from execution_graph.indexes.graph_index import GraphIndex
from execution_graph.indexes.ownership_index import OwnershipIndex
from execution_graph.indexes.runtime_path_index import RuntimePathIndex
from topology.indexing.locality_index import LocalityIndex


@dataclass
class WorkspaceGraphValidationReport:
    """
    Result of validating a Workspace Graph against legacy PECS indexes.
    """

    valid: bool = False
    graph_hash: str = ""
    graph_hash_stable: bool = False
    mismatches: List[str] = field(default_factory=list)
    legacy_index_summary: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "valid": self.valid,
            "graph_hash": self.graph_hash,
            "graph_hash_stable": self.graph_hash_stable,
            "mismatch_count": len(self.mismatches),
            "mismatches": self.mismatches,
            "legacy_index_summary": self.legacy_index_summary,
        }


class WorkspaceGraphValidator:
    """
    Compare legacy PECS graph/index/registry outputs against the Workspace
    Graph and verify deterministic hashing.

    The validator is additive and advisory: it reports mismatches but does
    not raise, so legacy consumers continue to work during migration.
    """

    _INTERACTION_EDGE_TYPES: Set[EdgeType] = {
        EdgeType.QACTION_REGISTER,
        EdgeType.QACTION_FACTORY_REGISTER,
        EdgeType.SHORTCUT_REGISTER,
        EdgeType.QACTION_OWNERSHIP,
        EdgeType.SHORTCUT_OWNERSHIP,
        EdgeType.DIALOG_LAUNCH,
        EdgeType.SIGNAL_SLOT,
    }

    def __init__(self) -> None:
        self._mismatches: List[str] = []

    def validate(
        self,
        graph: Graph,
        graph_index: Optional[GraphIndex] = None,
        execution_index: Optional[ExecutionIndex] = None,
        ownership_index: Optional[OwnershipIndex] = None,
        locality_index: Optional[LocalityIndex] = None,
        runtime_path_index: Optional[RuntimePathIndex] = None,
    ) -> WorkspaceGraphValidationReport:
        self._mismatches = []

        self._validate_graph_index(graph, graph_index)
        self._validate_locality_index(graph, locality_index)
        self._validate_execution_index(graph, execution_index)
        self._validate_ownership_index(graph, ownership_index)
        self._validate_runtime_path_index(graph, runtime_path_index)

        graph_hash_stable = self._validate_graph_hash_stability(graph)

        report = WorkspaceGraphValidationReport(
            valid=len(self._mismatches) == 0,
            graph_hash=graph.metadata.graph_hash,
            graph_hash_stable=graph_hash_stable,
            mismatches=self._mismatches,
            legacy_index_summary=_index_summary(
                graph_index,
                execution_index,
                ownership_index,
                locality_index,
                runtime_path_index,
            ),
        )
        return report

    def _validate_graph_index(
        self,
        graph: Graph,
        graph_index: Optional[GraphIndex],
    ) -> None:
        if graph_index is None:
            return

        legacy_node_keys = set(graph_index.node_index.keys())
        module_node_keys = {
            _strip_pecs_id(node_id)
            for node_id, node in graph.nodes.items()
            if node.node_type.value in {"module", "workspace"}
        }

        missing_in_graph = legacy_node_keys - module_node_keys
        if missing_in_graph:
            sample = sorted(missing_in_graph)[:5]
            self._mismatches.append(
                f"graph_index nodes missing in workspace graph: {sample}"
            )

        derived_zone_sets = {
            zone_id: {_strip_pecs_id(node_id) for node_id in node_ids}
            for zone_id, node_ids in graph.zones.items()
        }
        legacy_zone_sets = {
            zone_id: set(node_ids)
            for zone_id, node_ids in graph_index.zone_index.items()
        }
        # Legacy register_zone() replaces the zone list, so legacy zone
        # membership may be incomplete. Validate that every legacy node is
        # present in the workspace graph's zone.
        for zone_id, legacy_nodes in sorted(legacy_zone_sets.items()):
            derived = derived_zone_sets.get(zone_id, set())
            missing = legacy_nodes - derived
            if missing:
                self._mismatches.append(
                    f"zone '{zone_id}' missing legacy nodes in workspace graph: "
                    f"{sorted(missing)}"
                )

    def _validate_locality_index(
        self,
        graph: Graph,
        locality_index: Optional[LocalityIndex],
    ) -> None:
        if locality_index is None:
            return

        for object_id, expected in locality_index.object_locality.items():
            pecs_id = f"PECS_ID:{object_id}"
            derived = self._derive_anchors_for_module(graph, pecs_id)
            if sorted(expected) != sorted(derived):
                self._mismatches.append(
                    f"object_locality mismatch for {object_id}: "
                    f"expected {sorted(expected)}, derived {sorted(derived)}"
                )

    def _validate_execution_index(
        self,
        graph: Graph,
        execution_index: Optional[ExecutionIndex],
    ) -> None:
        if execution_index is None:
            return

        for path_id, expected in execution_index.execution_paths.items():
            pecs_id = f"PECS_ID:{path_id}"
            derived = self._derive_anchors_for_module(graph, pecs_id)
            if sorted(expected) != sorted(derived):
                self._mismatches.append(
                    f"execution_paths mismatch for {path_id}: "
                    f"expected {sorted(expected)}, derived {sorted(derived)}"
                )

    def _validate_ownership_index(
        self,
        graph: Graph,
        ownership_index: Optional[OwnershipIndex],
    ) -> None:
        if ownership_index is None:
            return

        for owner_id, expected in ownership_index.ownership_locality.items():
            if owner_id.startswith("PECS_ID:"):
                pecs_id = owner_id
            else:
                pecs_id = f"PECS_ID:{owner_id}"
            derived = self._derive_anchors_for_module(graph, pecs_id)
            if sorted(expected) != sorted(derived):
                self._mismatches.append(
                    f"ownership_locality mismatch for {owner_id}: "
                    f"expected {sorted(expected)}, derived {sorted(derived)}"
                )

    def _validate_runtime_path_index(
        self,
        graph: Graph,
        runtime_path_index: Optional[RuntimePathIndex],
    ) -> None:
        if runtime_path_index is None:
            return

        for path_id, expected in runtime_path_index.runtime_paths.items():
            pecs_id = f"PECS_ID:{path_id}"
            derived = self._derive_anchors_for_module(graph, pecs_id)
            if sorted(expected) != sorted(derived):
                self._mismatches.append(
                    f"runtime_paths mismatch for {path_id}: "
                    f"expected {sorted(expected)}, derived {sorted(derived)}"
                )

    def _derive_anchors_for_module(
        self,
        graph: Graph,
        module_pecs_id: str,
    ) -> List[str]:
        node = graph.nodes.get(module_pecs_id)
        if node is None:
            return []

        anchors: Set[str] = {module_pecs_id}
        if node.class_name:
            anchors.add(f"{module_pecs_id}.{node.class_name}")
        if node.method_name:
            anchors.add(f"{module_pecs_id}.{node.method_name}")

        for edge_id in node.outgoing_edges:
            edge = graph.edges.get(edge_id)
            if edge is None:
                continue
            if edge.edge_type in self._INTERACTION_EDGE_TYPES:
                anchors.add(edge.target_node_id)

        for edge_id in node.incoming_edges:
            edge = graph.edges.get(edge_id)
            if edge is None:
                continue
            if edge.edge_type in self._INTERACTION_EDGE_TYPES:
                anchors.add(edge.source_node_id)

        return sorted(anchors)

    def _validate_graph_hash_stability(self, graph: Graph) -> bool:
        """Verify that re-serializing the graph yields the same hash."""
        original = graph.metadata.graph_hash
        graph.update_graph_hash()
        return graph.metadata.graph_hash == original and bool(original)


def _strip_pecs_id(node_id: str) -> str:
    if node_id.startswith("PECS_ID:"):
        return node_id[len("PECS_ID:") :]
    return node_id


def _index_summary(
    graph_index: Optional[GraphIndex],
    execution_index: Optional[ExecutionIndex],
    ownership_index: Optional[OwnershipIndex],
    locality_index: Optional[LocalityIndex],
    runtime_path_index: Optional[RuntimePathIndex],
) -> Dict[str, Any]:
    return {
        "graph_index_nodes": len(graph_index.node_index) if graph_index else 0,
        "execution_index_paths": len(execution_index.execution_paths)
        if execution_index
        else 0,
        "ownership_index_entries": len(ownership_index.ownership_locality)
        if ownership_index
        else 0,
        "locality_index_objects": len(locality_index.object_locality)
        if locality_index
        else 0,
        "runtime_path_index_paths": len(runtime_path_index.runtime_paths)
        if runtime_path_index
        else 0,
    }
