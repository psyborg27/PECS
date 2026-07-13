from __future__ import annotations

import unittest
from pathlib import Path

from evidence_correlation.engines.evidence_correlator import EvidenceCorrelator
from execution_graph.builders.workspace_graph_builder import WorkspaceGraphBuilder
from execution_graph.graph.workspace_graph import Edge, EdgeType, Graph, Node, NodeType
from validation.evidence_correlation_validator import EvidenceCorrelationValidator


class TestEvidenceCorrelation(unittest.TestCase):
    """Smoke tests for the deterministic Evidence Correlation Engine."""

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

    def test_correlator_returns_ranked_clusters(self) -> None:
        graph = self._build_graph()
        correlator = EvidenceCorrelator(
            Path("/tmp/ws"),
            graph,
            None,
            {},
        )
        correlator.build_index()
        result = correlator.correlate(["daemon", "worker"], max_clusters=5)

        self.assertTrue(result.clusters)
        self.assertLessEqual(len(result.clusters), 5)
        # Top cluster should be app package because it contains daemon/worker.
        self.assertEqual(result.clusters[0].root_package, "app")

    def test_validation_passes(self) -> None:
        graph = self._build_graph()
        correlator = EvidenceCorrelator(
            Path("/tmp/ws"),
            graph,
            None,
            {},
        )
        correlator.build_index()
        result = correlator.correlate(["daemon"], max_clusters=5)

        validator = EvidenceCorrelationValidator()
        report = validator.validate(result, max_clusters=5)
        self.assertTrue(report.valid)

    def test_clusters_sorted_by_score(self) -> None:
        graph = self._build_graph()
        correlator = EvidenceCorrelator(
            Path("/tmp/ws"),
            graph,
            None,
            {},
        )
        correlator.build_index()
        result = correlator.correlate(["worker"], max_clusters=5)

        scores = [cluster.cumulative_correlation_score for cluster in result.clusters]
        self.assertEqual(scores, sorted(scores, reverse=True))


if __name__ == "__main__":
    unittest.main()
