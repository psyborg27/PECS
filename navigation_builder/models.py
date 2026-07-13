from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class LineRange:
    """
    Current line range resolved immediately before projection.

    Never persisted; recalculated for modified files on every build.
    """

    start: int = 1
    end: int = 1

    def to_dict(self) -> Dict[str, int]:
        return {"start": self.start, "end": self.end}


@dataclass
class NavigationEdge:
    """A deterministic relationship in the Navigation Graph."""

    edge_id: str
    source_id: str
    target_id: str
    edge_type: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "edge_id": self.edge_id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "edge_type": self.edge_type,
            "metadata": self.metadata,
        }


@dataclass
class NavigationNode:
    """
    A node in the Navigation Graph with current navigation metadata.
    """

    node_id: str
    node_type: str
    file_path: Optional[str] = None
    line_range: LineRange = field(default_factory=LineRange)
    parent_node_id: Optional[str] = None
    child_node_ids: List[str] = field(default_factory=list)
    incoming_edges: List[str] = field(default_factory=list)
    outgoing_edges: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "file_path": self.file_path,
            "line_range": self.line_range.to_dict(),
            "parent_node_id": self.parent_node_id,
            "child_node_ids": sorted(self.child_node_ids),
            "incoming_edges": sorted(self.incoming_edges),
            "outgoing_edges": sorted(self.outgoing_edges),
            "metadata": self.metadata,
        }


@dataclass
class NavigationGraph:
    """
    Deterministic bounded Navigation Graph built from Evidence Clusters.
    """

    query_terms: List[str] = field(default_factory=list)
    nodes: Dict[str, NavigationNode] = field(default_factory=dict)
    edges: Dict[str, NavigationEdge] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def register_node(self, node: NavigationNode) -> None:
        self.nodes[node.node_id] = node

    def register_edge(self, edge: NavigationEdge) -> None:
        if edge.edge_id in self.edges:
            return
        self.edges[edge.edge_id] = edge
        if edge.source_id in self.nodes:
            self.nodes[edge.source_id].outgoing_edges.append(edge.edge_id)
        if edge.target_id in self.nodes:
            self.nodes[edge.target_id].incoming_edges.append(edge.edge_id)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query_terms": sorted(self.query_terms),
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "nodes": {
                node_id: node.to_dict()
                for node_id, node in sorted(self.nodes.items())
            },
            "edges": {
                edge_id: edge.to_dict()
                for edge_id, edge in sorted(self.edges.items())
            },
            "metadata": self.metadata,
        }
