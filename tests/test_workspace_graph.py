from __future__ import annotations

import unittest
from pathlib import Path

from execution_graph.builders.workspace_graph_builder import (
    WorkspaceGraphBuilder,
)
from execution_graph.graph.workspace_graph import (
    Edge,
    EdgeType,
    Graph,
    Node,
    NodeType,
)
from execution_graph.indexes.execution_index import ExecutionIndex
from execution_graph.indexes.graph_index import GraphIndex
from execution_graph.indexes.ownership_index import OwnershipIndex
from topology.indexing.locality_index import LocalityIndex
from validation.workspace_graph_validator import (
    WorkspaceGraphValidator,
)


class TestWorkspaceGraph(unittest.TestCase):
    """Smoke tests for the incremental Workspace Graph."""

    def test_node_creation(self) -> None:
        node = Node(
            node_id="PECS_ID:module.example",
            node_type=NodeType.MODULE,
            canonical_name="example",
        )
        self.assertEqual(node.node_id, "PECS_ID:module.example")
        self.assertEqual(node.node_type, NodeType.MODULE)

    def test_graph_registers_edge_between_nodes(self) -> None:
        graph = Graph()
        source = Node(
            node_id="PECS_ID:module.a",
            node_type=NodeType.MODULE,
            canonical_name="a",
        )
        target = Node(
            node_id="PECS_ID:module.b",
            node_type=NodeType.MODULE,
            canonical_name="b",
        )
        graph.register_node(source)
        graph.register_node(target)
        edge = graph.edges.get("PECS_ID:module.a--import--PECS_ID:module.b")
        self.assertIsNone(edge)

        edge = Edge(
            edge_id="PECS_ID:module.a--import--PECS_ID:module.b",
            source_node_id="PECS_ID:module.a",
            target_node_id="PECS_ID:module.b",
            edge_type=EdgeType.IMPORT,
        )
        graph.register_edge(edge)
        self.assertIn(edge.edge_id, source.outgoing_edges)
        self.assertIn(edge.edge_id, target.incoming_edges)

    def test_builder_produces_deterministic_hash(self) -> None:
        workspace_root = Path("/tmp/pecs-wg-test")
        builder = WorkspaceGraphBuilder(workspace_root)
        payload = {
            "PECS_ID:module.file": {
                "file": "module/file.py",
                "class": "Klass",
                "method": "method",
                "runtime_zone": "general_runtime",
            },
            "PECS_ID:module.file.Klass": {
                "file": "module/file.py",
                "class": "Klass",
                "method": "method",
                "runtime_zone": "general_runtime",
            },
            "PECS_ID:module.file.method": {
                "file": "module/file.py",
                "class": "Klass",
                "method": "method",
                "runtime_zone": "general_runtime",
            },
        }
        edges = [
            {
                "from": "PECS_ID:module.file",
                "to": "PECS_ID:module.file.Klass",
                "type": "qaction_register",
            }
        ]

        graph1 = builder.build(
            reachable_files=set(),
            runtime_locality_payload=payload,
            runtime_topology_edges=edges,
        )
        graph2 = builder.build(
            reachable_files=set(),
            runtime_locality_payload=payload,
            runtime_topology_edges=edges,
        )

        self.assertTrue(graph1.metadata.graph_hash)
        self.assertEqual(
            graph1.metadata.graph_hash,
            graph2.metadata.graph_hash,
        )

    def test_validator_reports_valid_for_equivalent_indexes(self) -> None:
        workspace_root = Path("/tmp/pecs-wg-test")
        builder = WorkspaceGraphBuilder(workspace_root)
        payload = {
            "PECS_ID:module.file": {
                "file": "module/file.py",
                "class": "",
                "method": "",
                "runtime_zone": "general_runtime",
            },
        }
        edges: list = []
        graph = builder.build(
            reachable_files=set(),
            runtime_locality_payload=payload,
            runtime_topology_edges=edges,
        )

        graph_index = GraphIndex()
        graph_index.register_node(
            "module.file",
            {"object_id": "module.file", "path": "module/file.py"},
        )

        execution_index = ExecutionIndex()
        execution_index.register_execution_path(
            "module.file",
            ["PECS_ID:module.file"],
        )

        ownership_index = OwnershipIndex()
        ownership_index.register_ownership_locality(
            "module.file",
            ["PECS_ID:module.file"],
        )

        locality_index = LocalityIndex()
        locality_index.register_object_locality(
            "module.file",
            ["PECS_ID:module.file"],
        )

        validator = WorkspaceGraphValidator()
        report = validator.validate(
            graph,
            graph_index=graph_index,
            execution_index=execution_index,
            ownership_index=ownership_index,
            locality_index=locality_index,
        )

        self.assertTrue(report.valid)
        self.assertTrue(report.graph_hash_stable)

    def test_graph_from_dict_roundtrip_preserves_hash(self) -> None:
        workspace_root = Path("/tmp/pecs-wg-roundtrip")
        builder = WorkspaceGraphBuilder(workspace_root)
        payload = {
            "PECS_ID:module.file": {
                "file": "module/file.py",
                "class": "Klass",
                "method": "method",
                "runtime_zone": "general_runtime",
            },
            "PECS_ID:module.file.Klass": {
                "file": "module/file.py",
                "class": "Klass",
                "method": "method",
                "runtime_zone": "general_runtime",
            },
        }
        edges = [
            {
                "from": "PECS_ID:module.file",
                "to": "PECS_ID:module.file.Klass",
                "type": "import",
            }
        ]
        graph = builder.build(
            reachable_files=set(),
            runtime_locality_payload=payload,
            runtime_topology_edges=edges,
        )
        original_hash = graph.metadata.graph_hash

        rebuilt = Graph.from_dict(graph.to_dict())
        self.assertEqual(rebuilt.metadata.graph_hash, original_hash)
        self.assertEqual(len(rebuilt.nodes), len(graph.nodes))
        self.assertEqual(len(rebuilt.edges), len(graph.edges))


if __name__ == "__main__":
    unittest.main()
