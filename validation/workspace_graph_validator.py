from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from execution_graph.graph.workspace_graph import EdgeType, Graph, NodeType
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
        EdgeType.SUBPROCESS_LAUNCH,
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
            # Handle already-prefixed PECS_ID: keys (runtime anchors)
            # same pattern as _validate_ownership_index
            if object_id.startswith("PECS_ID:"):
                pecs_id = object_id
            else:
                pecs_id = f"PECS_ID:{object_id}"
            derived = self._derive_anchors_transitive(graph, pecs_id)
            if self._is_runtime_owner_anchor(pecs_id, graph):
                derived = [anchor for anchor in derived if anchor != pecs_id]
            expected_set = set(expected)
            derived_set = set(derived)
            if not expected_set.issubset(derived_set):
                missing = sorted(expected_set - derived_set)
                self._mismatches.append(
                    f"object_locality mismatch for {object_id}: "
                    f"expected {sorted(expected)}, derived {sorted(derived)}, "
                    f"missing {missing}"
                )

    def _validate_execution_index(
        self,
        graph: Graph,
        execution_index: Optional[ExecutionIndex],
    ) -> None:
        if execution_index is None:
            return

        for path_id, expected in execution_index.execution_paths.items():
            if path_id.startswith("PECS_ID:"):
                pecs_id = path_id
            else:
                pecs_id = f"PECS_ID:{path_id}"
            derived = self._derive_anchors_transitive(graph, pecs_id)
            if self._is_runtime_owner_anchor(pecs_id, graph):
                derived = [anchor for anchor in derived if anchor != pecs_id]
            expected_set = set(expected)
            derived_set = set(derived)
            if not expected_set.issubset(derived_set):
                missing = sorted(expected_set - derived_set)
                self._mismatches.append(
                    f"execution_paths mismatch for {path_id}: "
                    f"expected {sorted(expected)}, derived {sorted(derived)}, "
                    f"missing {missing}"
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
            derived = self._derive_anchors_transitive(graph, pecs_id)
            if self._is_runtime_owner_anchor(pecs_id, graph):
                derived = [anchor for anchor in derived if anchor != pecs_id]
            expected_set = set(expected)
            derived_set = set(derived)
            if not expected_set.issubset(derived_set):
                missing = sorted(expected_set - derived_set)
                self._mismatches.append(
                    f"ownership_locality mismatch for {owner_id}: "
                    f"expected {sorted(expected)}, derived {sorted(derived)}, "
                    f"missing {missing}"
                )

    def _is_runtime_owner_anchor(self, pecs_id: str, graph: Optional[Graph] = None) -> bool:
        """
        Determine whether a PECS ID is a runtime interaction anchor
        (action, callback, signal source, dialog, etc.) as opposed to a
        workspace module node.

        Uses the graph node type when available; falls back to checking
        whether the first PECS_ID segment is a module-like path.
        """
        if graph is not None:
            node = graph.nodes.get(pecs_id)
            if node is not None:
                return node.node_type not in {
                    NodeType.WORKSPACE,
                    NodeType.MODULE,
                }

        # Fallback: module paths start with a workspace-local prefix like "Qt.",
        # while runtime anchors start with a single-word layer like "action.",
        # "callback.", "clicked.", "failed.", etc.
        if not pecs_id.startswith("PECS_ID:"):
            return False
        first_segment = pecs_id[len("PECS_ID:"):].split(".")[0]
        # Module paths are typically multi-segment Python paths —
        # single-word first segments are runtime anchor layers.
        return bool(first_segment) and first_segment[0].islower()

    def _validate_runtime_path_index(
        self,
        graph: Graph,
        runtime_path_index: Optional[RuntimePathIndex],
    ) -> None:
        if runtime_path_index is None:
            return

        for path_id, expected in runtime_path_index.runtime_paths.items():
            if path_id.startswith("PECS_ID:"):
                pecs_id = path_id
            else:
                pecs_id = f"PECS_ID:{path_id}"
            derived = self._derive_anchors_transitive(graph, pecs_id)
            if self._is_runtime_owner_anchor(pecs_id, graph):
                derived = [anchor for anchor in derived if anchor != pecs_id]
            expected_set = set(expected)
            derived_set = set(derived)
            if not expected_set.issubset(derived_set):
                missing = sorted(expected_set - derived_set)
                self._mismatches.append(
                    f"runtime_paths mismatch for {path_id}: "
                    f"expected {sorted(expected)}, derived {sorted(derived)}, "
                    f"missing {missing}"
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

    def _derive_anchors_transitive(
        self,
        graph: Graph,
        module_pecs_id: str,
    ) -> List[str]:
        """
        Derive all anchors reachable via transitive BFS over interaction edges.

        The locality index is authoritative and records transitive ownership:
        a module's anchor set includes all runtime anchors (callbacks, dialogs,
        actions, shortcuts, signals) reachable through the graph's interaction
        edge chain (e.g. module -> action -> callback).

        This method performs a BFS over *INTERACTION_EDGE_TYPES* edges to match
        the canonical locality index semantics.
        """
        start_node = graph.nodes.get(module_pecs_id)
        if start_node is None:
            return []

        anchors: Set[str] = {module_pecs_id}
        visited: Set[str] = set()
        queue: deque = deque()

        visited.add(module_pecs_id)
        queue.appendleft(module_pecs_id)

        while queue:
            current_id = queue.pop()
            current_node = graph.nodes.get(current_id)
            if current_node is None:
                continue

            # Add class/method metadata anchors
            if current_node.class_name and current_id == module_pecs_id:
                anchors.add(f"{module_pecs_id}.{current_node.class_name}")
            if current_node.method_name and current_id == module_pecs_id:
                anchors.add(f"{module_pecs_id}.{current_node.method_name}")

            # Traverse outgoing interaction edges
            for edge_id in current_node.outgoing_edges:
                edge = graph.edges.get(edge_id)
                if edge is None:
                    continue
                if edge.edge_type not in self._INTERACTION_EDGE_TYPES:
                    continue
                target_id = edge.target_node_id
                anchors.add(target_id)
                if target_id not in visited:
                    visited.add(target_id)
                    queue.appendleft(target_id)

            # Traverse incoming interaction edges
            for edge_id in current_node.incoming_edges:
                edge = graph.edges.get(edge_id)
                if edge is None:
                    continue
                if edge.edge_type not in self._INTERACTION_EDGE_TYPES:
                    continue
                source_id = edge.source_node_id
                anchors.add(source_id)
                if source_id not in visited:
                    visited.add(source_id)
                    queue.appendleft(source_id)

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
