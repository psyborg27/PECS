from __future__ import annotations

import unittest
from pathlib import Path

from evidence_correlation.models import EvidenceCluster, EvidenceBreakdown
from execution_graph.builders.workspace_graph_builder import WorkspaceGraphBuilder
from execution_graph.graph.workspace_graph import Edge, EdgeType, Graph, Node, NodeType
from navigation_builder.builders.navigation_graph_builder import (
    NavigationGraphBuilder,
)
from navigation_builder.line_range_resolver import LineRangeResolver
from validation.navigation_builder_validator import NavigationBuilderValidator


class TestNavigationBuilder(unittest.TestCase):
    """Smoke tests for the deterministic Navigation Builder."""

    def _build_graph(self) -> Graph:
        graph = Graph(workspace_root="/tmp/ws")

        nodes = [
            ("PECS_ID:app.main", NodeType.MODULE, "main", "app/main.py"),
            ("PECS_ID:app.daemon.worker", NodeType.MODULE, "worker", "app/daemon/worker.py"),
            ("PECS_ID:app.daemon.scheduler", NodeType.MODULE, "scheduler", "app/daemon/scheduler.py"),
            ("PECS_ID:lib.utils", NodeType.MODULE, "utils", "lib/utils.py"),
        ]
        for node_id, node_type, canonical_name, source_file in nodes:
            graph.register_node(
                Node(
                    node_id=node_id,
                    node_type=node_type,
                    canonical_name=canonical_name,
                    source_file=source_file,
                    module_path=node_id.replace("PECS_ID:", "").replace(".", "/"),
                )
            )

        graph.register_entrypoint("PECS_ID:app.main")

        edges = [
            ("PECS_ID:app.main", "PECS_ID:app.daemon.worker", EdgeType.IMPORT),
            ("PECS_ID:app.main", "PECS_ID:app.daemon.scheduler", EdgeType.IMPORT),
            ("PECS_ID:app.daemon.worker", "PECS_ID:lib.utils", EdgeType.IMPORT),
        ]
        for source, target, edge_type in edges:
            edge_id = f"{source}--{edge_type.value}--{target}"
            graph.register_edge(
                Edge(
                    edge_id=edge_id,
                    source_node_id=source,
                    target_node_id=target,
                    edge_type=edge_type,
                )
            )

        graph.update_graph_hash()
        return graph

    def _build_cluster(self, graph: Graph) -> EvidenceCluster:
        return EvidenceCluster(
            cluster_id="ec-app",
            primary_namespace="app",
            root_package="app",
            graph_nodes={"PECS_ID:app.main", "PECS_ID:app.daemon.worker"},
            imports={"PECS_ID:lib.utils"},
            evidence_breakdown=EvidenceBreakdown(),
            cumulative_correlation_score=1.0,
        )

    def test_navigation_graph_respects_budget(self) -> None:
        graph = self._build_graph()
        cluster = self._build_cluster(graph)
        builder = NavigationGraphBuilder(
            Path("/tmp/ws"), graph, max_nodes=3, max_depth=1
        )
        nav_graph = builder.build([cluster], query_terms=["daemon"])

        self.assertLessEqual(len(nav_graph.nodes), 3)

    def test_line_ranges_are_resolved(self) -> None:
        resolver = LineRangeResolver(Path("/tmp/ws"))
        # File does not exist, so fallback range is returned.
        start, end = resolver.resolve("app/main.py")
        self.assertEqual(start, 1)
        self.assertEqual(end, 1)

    def test_validator_passes(self) -> None:
        graph = self._build_graph()
        cluster = self._build_cluster(graph)
        builder = NavigationGraphBuilder(
            Path("/tmp/ws"), graph, max_nodes=10, max_depth=1
        )
        nav_graph = builder.build([cluster], query_terms=["daemon"])

        validator = NavigationBuilderValidator()
        report = validator.validate(nav_graph, ["daemon"], max_nodes=10)
        self.assertTrue(report.valid)

    def test_navigation_nodes_have_edges(self) -> None:
        graph = self._build_graph()
        cluster = self._build_cluster(graph)
        builder = NavigationGraphBuilder(
            Path("/tmp/ws"), graph, max_nodes=10, max_depth=1
        )
        nav_graph = builder.build([cluster], query_terms=["daemon"])

        main = nav_graph.nodes.get("PECS_ID:app.main")
        self.assertIsNotNone(main)
        self.assertTrue(main.outgoing_edges)


if __name__ == "__main__":
    unittest.main()
