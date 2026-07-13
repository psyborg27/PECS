from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from execution_graph.graph.workspace_graph import Graph
from evidence_correlation.models import EvidenceCluster
from navigation_builder.line_range_resolver import LineRangeResolver
from navigation_builder.models import (
    LineRange,
    NavigationEdge,
    NavigationGraph,
    NavigationNode,
)


class NavigationGraphBuilder:
    """
    Build a deterministic, bounded Navigation Graph from ranked Evidence
    Clusters.

    Current line ranges are resolved immediately before projection and are
    never persisted.
    """

    def __init__(
        self,
        workspace_root: Path,
        graph: Graph,
        max_nodes: int = 40,
        max_depth: int = 2,
    ) -> None:
        self.workspace_root = workspace_root
        self.graph = graph
        self.max_nodes = max_nodes
        self.max_depth = max_depth
        self.line_resolver = LineRangeResolver(workspace_root)

    def build(
        self,
        clusters: List[EvidenceCluster],
        query_terms: Optional[List[str]] = None,
    ) -> NavigationGraph:
        """
        Build a Navigation Graph from the provided Evidence Clusters.

        Projection boundary is determined by the cluster nodes plus graph
        locality expansion up to max_nodes/max_depth.
        """
        nav_graph = NavigationGraph(
            query_terms=query_terms or [],
            metadata={
                "workspace_root": str(self.workspace_root),
                "max_nodes": self.max_nodes,
                "max_depth": self.max_depth,
            },
        )

        seed_ids: Set[str] = set()
        for cluster in clusters:
            seed_ids.update(cluster.graph_nodes)
            seed_ids.update(cluster.imports)
            seed_ids.update(cluster.exports)

        # Cap seed set before expansion to respect the node budget.
        seed_ids = set(sorted(seed_ids)[: self.max_nodes])
        selected_ids = self._expand_boundary(seed_ids)

        # Create navigation nodes for all selected graph nodes.
        for node_id in sorted(selected_ids):
            graph_node = self.graph.nodes.get(node_id)
            if graph_node is None:
                continue
            nav_node = self._build_navigation_node(graph_node)
            nav_graph.register_node(nav_node)

        # Create navigation edges for relationships between selected nodes.
        for edge in self.graph.edges.values():
            if (
                edge.source_node_id in selected_ids
                and edge.target_node_id in selected_ids
                and edge.source_node_id in self.graph.nodes
                and edge.target_node_id in self.graph.nodes
            ):
                nav_edge = NavigationEdge(
                    edge_id=edge.edge_id,
                    source_id=edge.source_node_id,
                    target_id=edge.target_node_id,
                    edge_type=edge.edge_type.value,
                    metadata={"execution_zone": edge.execution_zone},
                )
                nav_graph.register_edge(nav_edge)

        # Wire parent/child relationships.
        self._wire_parent_child(nav_graph)

        return nav_graph

    def _expand_boundary(self, seed_ids: Set[str]) -> Set[str]:
        """Expand seed nodes via graph locality up to budget limits."""
        selected: Set[str] = set(seed_ids)
        frontier: Set[str] = set(seed_ids)
        depth = 0

        while frontier and depth < self.max_depth and len(selected) < self.max_nodes:
            next_frontier: Set[str] = set()
            for node_id in frontier:
                node = self.graph.nodes.get(node_id)
                if node is None:
                    continue
                for edge_id in node.outgoing_edges:
                    edge = self.graph.edges.get(edge_id)
                    if edge and edge.target_node_id not in selected:
                        next_frontier.add(edge.target_node_id)
                for edge_id in node.incoming_edges:
                    edge = self.graph.edges.get(edge_id)
                    if edge and edge.source_node_id not in selected:
                        next_frontier.add(edge.source_node_id)

            # Respect node budget.
            remaining = self.max_nodes - len(selected)
            added = sorted(next_frontier)[:remaining]
            selected.update(added)
            frontier = set(added)
            depth += 1

        return selected

    def _build_navigation_node(self, graph_node: Any) -> NavigationNode:
        file_path = graph_node.source_file
        start, end = self.line_resolver.resolve(
            file_path or "",
            class_name=graph_node.class_name,
            method_name=graph_node.method_name,
        )

        return NavigationNode(
            node_id=graph_node.node_id,
            node_type=graph_node.node_type.value,
            file_path=file_path,
            line_range=LineRange(start=start, end=end),
            metadata={
                "canonical_name": graph_node.canonical_name,
                "module_path": graph_node.module_path,
                "execution_zone": graph_node.execution_zone,
                "authority_level": graph_node.authority_level.value,
                "confidence": graph_node.confidence,
            },
        )

    def _wire_parent_child(self, nav_graph: NavigationGraph) -> None:
        """
        Establish parent/child relationships based on module path nesting.

        A node is a parent of another if its module path is a prefix and it
        represents a broader scope (e.g., module vs class vs method).
        """
        node_ids = sorted(nav_graph.nodes.keys())
        for node_id in node_ids:
            node = nav_graph.nodes[node_id]
            node_module = node.metadata.get("module_path", "")
            if not node_module:
                continue

            for other_id in node_ids:
                if other_id == node_id:
                    continue
                other = nav_graph.nodes[other_id]
                other_module = other.metadata.get("module_path", "")
                if not other_module:
                    continue

                # Parent module path must be a proper prefix.
                if other_module.startswith(node_module + "."):
                    if other.parent_node_id == node_id:
                        continue
                    # Prefer the longest prefix parent already set.
                    current_parent = other.parent_node_id
                    if current_parent is None:
                        other.parent_node_id = node_id
                        node.child_node_ids.append(other_id)
                    else:
                        current = nav_graph.nodes[current_parent]
                        current_module = current.metadata.get(
                            "module_path", ""
                        )
                        if len(node_module) > len(current_module):
                            other.parent_node_id = node_id
                            node.child_node_ids.append(other_id)

        # Deduplicate child lists.
        for node in nav_graph.nodes.values():
            node.child_node_ids = sorted(set(node.child_node_ids))
