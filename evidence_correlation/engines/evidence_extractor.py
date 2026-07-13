from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from execution_graph.graph.workspace_graph import EdgeType, Graph, Node, NodeType
from workspace_registry.models import WorkspaceRegistry


class EvidenceExtractor:
    """
    Extract deterministic architectural evidence from the frozen Workspace
    Graph, Workspace Registry, and existing continuity artifacts.

    The extractor does not perform semantic matching; it only materializes
    the evidence sources that the correlator will match against query terms.
    """

    def __init__(
        self,
        workspace_root: Path,
        graph: Graph,
        registry: Optional[WorkspaceRegistry] = None,
        locality_payload: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> None:
        self.workspace_root = workspace_root
        self.graph = graph
        self.registry = registry
        self.locality_payload = locality_payload or {}

    def extract(self) -> Dict[str, Dict[str, Set[str]]]:
        """
        Return a mapping from PECS node id to evidence sets keyed by source.

        Evidence source keys mirror EvidenceBreakdown field names.
        """
        evidence: Dict[str, Dict[str, Set[str]]] = {}

        for node_id, node in self.graph.nodes.items():
            node_evidence: Dict[str, Set[str]] = {
                "package_name": set(),
                "folder_hierarchy": set(),
                "module_file_name": set(),
                "import_locality": set(),
                "export_locality": set(),
                "class_name": set(),
                "function_method_name": set(),
                "decorator": set(),
                "controller_ownership": set(),
                "runtime_ownership": set(),
                "ui_registration": set(),
                "execution_graph_locality": set(),
                "graph_topology": set(),
                "continuity_artifact": set(),
            }

            self._extract_node_identity(node, node_evidence)
            self._extract_graph_edges(node_id, node_evidence)
            self._extract_runtime_anchors(node, node_evidence)
            self._extract_continuity_artifacts(node_id, node_evidence)

            evidence[node_id] = node_evidence

        return evidence

    def _extract_node_identity(
        self,
        node: Node,
        node_evidence: Dict[str, Set[str]],
    ) -> None:
        body = (
            node.node_id[len("PECS_ID:") :]
            if node.node_id.startswith("PECS_ID:")
            else node.node_id
        )
        parts = body.split(".")

        # Package and folder hierarchy.
        if parts:
            node_evidence["package_name"].add(parts[0])
            for depth in range(1, len(parts) + 1):
                node_evidence["folder_hierarchy"].add(".".join(parts[:depth]))

        # Module/file name.
        if node.source_file:
            node_evidence["module_file_name"].add(
                Path(node.source_file).stem
            )
            node_evidence["module_file_name"].add(node.source_file)

        # Class and method names.
        if node.class_name:
            node_evidence["class_name"].add(node.class_name)
        if node.method_name:
            node_evidence["function_method_name"].add(node.method_name)

        # Graph topology: node type and canonical name.
        node_evidence["graph_topology"].add(node.node_type.value)
        node_evidence["graph_topology"].add(node.canonical_name)

        # Execution graph locality: runtime zone.
        if node.execution_zone:
            node_evidence["execution_graph_locality"].add(node.execution_zone)

    def _extract_graph_edges(
        self,
        node_id: str,
        node_evidence: Dict[str, Set[str]],
    ) -> None:
        for edge_id in self.graph.nodes[node_id].outgoing_edges:
            edge = self.graph.edges.get(edge_id)
            if edge is None:
                continue
            if edge.edge_type == EdgeType.IMPORT:
                node_evidence["import_locality"].add(edge.target_node_id)
                target = self.graph.nodes.get(edge.target_node_id)
                if target and target.source_file:
                    node_evidence["import_locality"].add(target.source_file)
            elif edge.edge_type in {
                EdgeType.QACTION_OWNERSHIP,
                EdgeType.QACTION_REGISTER,
                EdgeType.QACTION_FACTORY_REGISTER,
                EdgeType.SHORTCUT_OWNERSHIP,
                EdgeType.SHORTCUT_REGISTER,
                EdgeType.DIALOG_LAUNCH,
            }:
                node_evidence["ui_registration"].add(edge.target_node_id)
                node_evidence["runtime_ownership"].add(edge.target_node_id)
            elif edge.edge_type == EdgeType.SIGNAL_SLOT:
                node_evidence["controller_ownership"].add(edge.target_node_id)

        for edge_id in self.graph.nodes[node_id].incoming_edges:
            edge = self.graph.edges.get(edge_id)
            if edge is None:
                continue
            if edge.edge_type == EdgeType.IMPORT:
                node_evidence["export_locality"].add(edge.source_node_id)
                source = self.graph.nodes.get(edge.source_node_id)
                if source and source.source_file:
                    node_evidence["export_locality"].add(source.source_file)

    def _extract_runtime_anchors(
        self,
        node: Node,
        node_evidence: Dict[str, Set[str]],
    ) -> None:
        if node.node_type in {
            NodeType.QACTION,
            NodeType.MENU,
            NodeType.TOOLBAR,
            NodeType.DIALOG,
            NodeType.VIEWER,
            NodeType.OVERLAY,
            NodeType.SIGNAL,
            NodeType.SLOT,
            NodeType.CALLBACK,
        }:
            node_evidence["ui_registration"].add(node.node_id)
            node_evidence["runtime_ownership"].add(node.node_id)

    def _extract_continuity_artifacts(
        self,
        node_id: str,
        node_evidence: Dict[str, Set[str]],
    ) -> None:
        meta = self.locality_payload.get(node_id, {})
        if meta.get("file"):
            node_evidence["continuity_artifact"].add(str(meta["file"]))
        if meta.get("class"):
            node_evidence["continuity_artifact"].add(str(meta["class"]))
        if meta.get("method"):
            node_evidence["continuity_artifact"].add(str(meta["method"]))
        if meta.get("runtime_zone"):
            node_evidence["continuity_artifact"].add(
                str(meta["runtime_zone"])
            )

    def get_file_path(self, node_id: str) -> Optional[str]:
        node = self.graph.nodes.get(node_id)
        if node and node.source_file:
            return node.source_file
        meta = self.locality_payload.get(node_id, {})
        return meta.get("file")
