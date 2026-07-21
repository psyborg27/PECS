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
from execution_graph.indexes.runtime_path_index import RuntimePathIndex
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

    def test_validator_accepts_runtime_owner_locality_without_self_anchor(self) -> None:
        workspace_root = Path("/tmp/pecs-wg-runtime-owner")
        builder = WorkspaceGraphBuilder(workspace_root)
        payload = {
            "PECS_ID:module.file": {
                "file": "module/file.py",
                "runtime_zone": "general_runtime",
            },
            "PECS_ID:action.save": {
                "file": "module/file.py",
                "runtime_zone": "general_runtime",
            },
            "PECS_ID:dialog.open_file": {
                "file": "module/file.py",
                "runtime_zone": "general_runtime",
            },
            "PECS_ID:callback.save": {
                "file": "module/file.py",
                "runtime_zone": "general_runtime",
            },
            "PECS_ID:signal.changed": {
                "file": "module/file.py",
                "runtime_zone": "general_runtime",
            },
            "PECS_ID:shortcut.save": {
                "file": "module/file.py",
                "runtime_zone": "general_runtime",
            },
        }
        edges = [
            {
                "from": "PECS_ID:module.file",
                "to": "PECS_ID:action.save",
                "type": "qaction_ownership",
            },
            {
                "from": "PECS_ID:module.file",
                "to": "PECS_ID:dialog.open_file",
                "type": "dialog_launch",
            },
            {
                "from": "PECS_ID:callback.save",
                "to": "PECS_ID:module.file",
                "type": "signal_slot",
            },
            {
                "from": "PECS_ID:module.file",
                "to": "PECS_ID:shortcut.save",
                "type": "shortcut_ownership",
            },
            {
                "from": "PECS_ID:module.file",
                "to": "PECS_ID:signal.changed",
                "type": "signal_slot",
            },
        ]

        graph = builder.build(
            reachable_files=set(),
            runtime_locality_payload=payload,
            runtime_topology_edges=edges,
        )

        ownership_index = OwnershipIndex()
        ownership_index.register_ownership_locality(
            "PECS_ID:action.save",
            ["PECS_ID:module.file"],
        )
        ownership_index.register_ownership_locality(
            "PECS_ID:dialog.open_file",
            ["PECS_ID:module.file"],
        )
        ownership_index.register_ownership_locality(
            "PECS_ID:callback.save",
            ["PECS_ID:module.file"],
        )
        ownership_index.register_ownership_locality(
            "PECS_ID:signal.changed",
            ["PECS_ID:module.file"],
        )
        ownership_index.register_ownership_locality(
            "PECS_ID:shortcut.save",
            ["PECS_ID:module.file"],
        )

        validator = WorkspaceGraphValidator()
        report = validator.validate(
            graph,
            graph_index=GraphIndex(),
            execution_index=ExecutionIndex(),
            ownership_index=ownership_index,
            locality_index=LocalityIndex(),
        )

        self.assertTrue(report.valid)
        self.assertEqual(len(report.mismatches), 0)

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


class TestWorkspaceGraphTransitiveValidation(unittest.TestCase):
    """Regression tests for transitive ownership/locality validation."""

    def _build_graph(self, payload, edges):
        builder = WorkspaceGraphBuilder(Path("/tmp/pecs-transitive"))
        return builder.build(
            reachable_files=set(),
            runtime_locality_payload=payload,
            runtime_topology_edges=edges,
        )

    def test_callback_reachable_via_module_action_callback(self):
        """module -> action -> callback: transitive BFS must capture callback."""
        payload = {
            "PECS_ID:module.file": {
                "file": "module/file.py",
                "runtime_zone": "general_runtime",
            },
            "PECS_ID:action.save": {
                "file": "module/file.py",
                "runtime_zone": "general_runtime",
            },
            "PECS_ID:callback.on_save": {
                "file": "module/file.py",
                "runtime_zone": "general_runtime",
            },
        }
        edges = [
            {"from": "PECS_ID:module.file", "to": "PECS_ID:action.save", "type": "qaction_ownership"},
            {"from": "PECS_ID:action.save", "to": "PECS_ID:callback.on_save", "type": "signal_slot"},
        ]
        graph = self._build_graph(payload, edges)

        # Locality index: module owns action AND transitive callback
        locality_index = LocalityIndex()
        locality_index.register_object_locality(
            "module.file",
            ["PECS_ID:module.file", "PECS_ID:action.save", "PECS_ID:callback.on_save"],
        )

        validator = WorkspaceGraphValidator()
        report = validator.validate(
            graph,
            graph_index=GraphIndex(),
            execution_index=ExecutionIndex(),
            ownership_index=OwnershipIndex(),
            locality_index=locality_index,
        )
        self.assertTrue(report.valid, f"locality mismatches: {report.mismatches}")

    def test_already_prefixed_pecs_id_no_double_prefix(self):
        """Runtime anchor keys already start with PECS_ID: must not get double-prefixed."""
        payload = {
            "PECS_ID:module.file": {
                "file": "module/file.py",
                "runtime_zone": "general_runtime",
            },
            "PECS_ID:action.save": {
                "file": "module/file.py",
                "runtime_zone": "general_runtime",
            },
        }
        edges = [
            {"from": "PECS_ID:module.file", "to": "PECS_ID:action.save", "type": "qaction_ownership"},
        ]
        graph = self._build_graph(payload, edges)

        # Locality index with already-prefixed key (as daemon produces for runtime anchors)
        locality_index = LocalityIndex()
        locality_index.register_object_locality(
            "PECS_ID:action.save",
            ["PECS_ID:module.file"],
        )

        validator = WorkspaceGraphValidator()
        report = validator.validate(
            graph,
            graph_index=GraphIndex(),
            execution_index=ExecutionIndex(),
            ownership_index=OwnershipIndex(),
            locality_index=locality_index,
        )
        self.assertTrue(report.valid, f"locality mismatches: {report.mismatches}")

    def test_execution_index_with_transitive_callback(self):
        """execution_paths must validate with transitive anchor derivation."""
        payload = {
            "PECS_ID:module.file": {
                "file": "module/file.py",
                "runtime_zone": "general_runtime",
            },
            "PECS_ID:dialog.open_file": {
                "file": "module/file.py",
                "runtime_zone": "general_runtime",
            },
            "PECS_ID:callback.on_open": {
                "file": "module/file.py",
                "runtime_zone": "general_runtime",
            },
        }
        edges = [
            {"from": "PECS_ID:module.file", "to": "PECS_ID:dialog.open_file", "type": "dialog_launch"},
            {"from": "PECS_ID:dialog.open_file", "to": "PECS_ID:callback.on_open", "type": "signal_slot"},
        ]
        graph = self._build_graph(payload, edges)

        execution_index = ExecutionIndex()
        execution_index.register_execution_path(
            "module.file",
            ["PECS_ID:module.file", "PECS_ID:dialog.open_file", "PECS_ID:callback.on_open"],
        )

        validator = WorkspaceGraphValidator()
        report = validator.validate(
            graph,
            graph_index=GraphIndex(),
            execution_index=execution_index,
            ownership_index=OwnershipIndex(),
            locality_index=LocalityIndex(),
        )
        self.assertTrue(report.valid, f"execution mismatches: {report.mismatches}")

    def test_runtime_path_index_with_transitive_callback(self):
        """runtime_paths must validate with transitive anchor derivation."""
        payload = {
            "PECS_ID:module.file": {
                "file": "module/file.py",
                "runtime_zone": "general_runtime",
            },
            "PECS_ID:shortcut.ctrl_s": {
                "file": "module/file.py",
                "runtime_zone": "general_runtime",
            },
            "PECS_ID:callback.on_ctrl_s": {
                "file": "module/file.py",
                "runtime_zone": "general_runtime",
            },
        }
        edges = [
            {"from": "PECS_ID:module.file", "to": "PECS_ID:shortcut.ctrl_s", "type": "shortcut_ownership"},
            {"from": "PECS_ID:shortcut.ctrl_s", "to": "PECS_ID:callback.on_ctrl_s", "type": "signal_slot"},
        ]
        graph = self._build_graph(payload, edges)

        runtime_path_index = RuntimePathIndex()
        runtime_path_index.register_runtime_path(
            "module.file",
            ["PECS_ID:module.file", "PECS_ID:shortcut.ctrl_s", "PECS_ID:callback.on_ctrl_s"],
        )

        validator = WorkspaceGraphValidator()
        report = validator.validate(
            graph,
            graph_index=GraphIndex(),
            execution_index=ExecutionIndex(),
            ownership_index=OwnershipIndex(),
            locality_index=LocalityIndex(),
            runtime_path_index=runtime_path_index,
        )
        self.assertTrue(report.valid, f"runtime_path mismatches: {report.mismatches}")

    def test_transitive_bfs_does_not_explode_with_cycles(self):
        """BFS must handle cycles in the interaction edge graph."""
        payload = {
            "PECS_ID:module.file": {
                "file": "module/file.py",
                "runtime_zone": "general_runtime",
            },
            "PECS_ID:action.a": {"file": "module/file.py", "runtime_zone": "general_runtime"},
            "PECS_ID:action.b": {"file": "module/file.py", "runtime_zone": "general_runtime"},
            "PECS_ID:callback.c": {"file": "module/file.py", "runtime_zone": "general_runtime"},
        }
        # action.a -> callback.c, callback.c -> action.a (cycle), both owned by module
        edges = [
            {"from": "PECS_ID:module.file", "to": "PECS_ID:action.a", "type": "qaction_ownership"},
            {"from": "PECS_ID:module.file", "to": "PECS_ID:action.b", "type": "qaction_ownership"},
            {"from": "PECS_ID:action.a", "to": "PECS_ID:callback.c", "type": "signal_slot"},
            {"from": "PECS_ID:callback.c", "to": "PECS_ID:action.a", "type": "signal_slot"},
        ]
        graph = self._build_graph(payload, edges)

        locality_index = LocalityIndex()
        locality_index.register_object_locality(
            "module.file",
            ["PECS_ID:module.file", "PECS_ID:action.a", "PECS_ID:action.b", "PECS_ID:callback.c"],
        )

        validator = WorkspaceGraphValidator()
        report = validator.validate(
            graph,
            graph_index=GraphIndex(),
            execution_index=ExecutionIndex(),
            ownership_index=OwnershipIndex(),
            locality_index=locality_index,
        )
        self.assertTrue(report.valid, f"locality mismatches: {report.mismatches}")

    def test_runtime_owner_self_anchor_excluded_after_transitive_bfs(self):
        """Runtime owner anchors (action/dialog/callback/shortcut/signal) must have self excluded."""
        payload = {
            "PECS_ID:module.file": {
                "file": "module/file.py",
                "runtime_zone": "general_runtime",
            },
            "PECS_ID:callback.on_save": {
                "file": "module/file.py",
                "runtime_zone": "general_runtime",
            },
            "PECS_ID:dialog.open_file": {
                "file": "module/file.py",
                "runtime_zone": "general_runtime",
            },
        }
        edges = [
            {"from": "PECS_ID:module.file", "to": "PECS_ID:dialog.open_file", "type": "dialog_launch"},
            {"from": "PECS_ID:dialog.open_file", "to": "PECS_ID:callback.on_save", "type": "signal_slot"},
        ]
        graph = self._build_graph(payload, edges)

        locality_index = LocalityIndex()
        locality_index.register_object_locality(
            "PECS_ID:callback.on_save",
            ["PECS_ID:module.file", "PECS_ID:dialog.open_file"],
        )

        validator = WorkspaceGraphValidator()
        report = validator.validate(
            graph,
            graph_index=GraphIndex(),
            execution_index=ExecutionIndex(),
            ownership_index=OwnershipIndex(),
            locality_index=locality_index,
        )
        self.assertTrue(report.valid, f"locality mismatches: {report.mismatches}")

    def test_subset_semantics_accepts_superset_in_graph(self):
        """The graph can discover more anchors than the legacy index (subset check)."""
        payload = {
            "PECS_ID:module.a": {
                "file": "module/a.py",
                "runtime_zone": "general_runtime",
            },
            "PECS_ID:module.b": {
                "file": "module/b.py",
                "runtime_zone": "general_runtime",
            },
            "PECS_ID:action.save": {
                "file": "module/a.py",
                "runtime_zone": "general_runtime",
            },
            "PECS_ID:callback.on_save": {
                "file": "module/a.py",
                "runtime_zone": "general_runtime",
            },
        }
        # Both modules own the action, and it connects to a callback
        edges = [
            {"from": "PECS_ID:module.a", "to": "PECS_ID:action.save", "type": "qaction_ownership"},
            {"from": "PECS_ID:module.b", "to": "PECS_ID:action.save", "type": "qaction_ownership"},
            {"from": "PECS_ID:action.save", "to": "PECS_ID:callback.on_save", "type": "signal_slot"},
        ]
        graph = self._build_graph(payload, edges)

        # Locality index only records module.a as owner (canonical),
        # but the graph also finds module.b
        locality_index = LocalityIndex()
        locality_index.register_object_locality(
            "module.a",
            ["PECS_ID:module.a", "PECS_ID:action.save"],
        )

        validator = WorkspaceGraphValidator()
        report = validator.validate(
            graph,
            graph_index=GraphIndex(),
            execution_index=ExecutionIndex(),
            ownership_index=OwnershipIndex(),
            locality_index=locality_index,
        )
        # Should pass because expected ⊆ derived (graph found action.save + callback too)
        self.assertTrue(report.valid, f"mismatches: {report.mismatches}")

    def test_clicked_signal_source_reaches_callback(self):
        """clicked.* intermediate source must anchor its callback via BFS."""
        payload = {
            "PECS_ID:module.file": {"file": "module/file.py", "runtime_zone": "general_runtime"},
            "PECS_ID:clicked.save_btn": {"file": "module/file.py", "runtime_zone": "general_runtime"},
            "PECS_ID:callback.on_save": {"file": "module/file.py", "runtime_zone": "general_runtime"},
        }
        edges = [
            {"from": "PECS_ID:module.file", "to": "PECS_ID:clicked.save_btn", "type": "signal_slot"},
            {"from": "PECS_ID:clicked.save_btn", "to": "PECS_ID:callback.on_save", "type": "signal_slot"},
        ]
        graph = self._build_graph(payload, edges)

        locality_index = LocalityIndex()
        locality_index.register_object_locality(
            "module.file",
            ["PECS_ID:module.file", "PECS_ID:clicked.save_btn", "PECS_ID:callback.on_save"],
        )

        validator = WorkspaceGraphValidator()
        report = validator.validate(
            graph,
            graph_index=GraphIndex(),
            execution_index=ExecutionIndex(),
            ownership_index=OwnershipIndex(),
            locality_index=locality_index,
        )
        self.assertTrue(report.valid, f"mismatches: {report.mismatches}")

    def test_failed_signal_source_reaches_callback(self):
        """failed.* intermediate source must anchor its callback via BFS."""
        payload = {
            "PECS_ID:module.file": {"file": "module/file.py", "runtime_zone": "general_runtime"},
            "PECS_ID:failed.worker": {"file": "module/file.py", "runtime_zone": "general_runtime"},
            "PECS_ID:callback.on_worker_failed": {"file": "module/file.py", "runtime_zone": "general_runtime"},
        }
        edges = [
            {"from": "PECS_ID:module.file", "to": "PECS_ID:failed.worker", "type": "signal_slot"},
            {"from": "PECS_ID:failed.worker", "to": "PECS_ID:callback.on_worker_failed", "type": "signal_slot"},
        ]
        graph = self._build_graph(payload, edges)

        locality_index = LocalityIndex()
        locality_index.register_object_locality(
            "module.file",
            ["PECS_ID:module.file", "PECS_ID:failed.worker", "PECS_ID:callback.on_worker_failed"],
        )

        validator = WorkspaceGraphValidator()
        report = validator.validate(
            graph,
            graph_index=GraphIndex(),
            execution_index=ExecutionIndex(),
            ownership_index=OwnershipIndex(),
            locality_index=locality_index,
        )
        self.assertTrue(report.valid, f"mismatches: {report.mismatches}")

    def test_timeout_signal_source_reaches_callback(self):
        """timeout.* intermediate source must anchor its callback via BFS."""
        payload = {
            "PECS_ID:module.file": {"file": "module/file.py", "runtime_zone": "general_runtime"},
            "PECS_ID:timeout.refresh_timer": {"file": "module/file.py", "runtime_zone": "general_runtime"},
            "PECS_ID:callback.on_refresh": {"file": "module/file.py", "runtime_zone": "general_runtime"},
        }
        edges = [
            {"from": "PECS_ID:module.file", "to": "PECS_ID:timeout.refresh_timer", "type": "signal_slot"},
            {"from": "PECS_ID:timeout.refresh_timer", "to": "PECS_ID:callback.on_refresh", "type": "signal_slot"},
        ]
        graph = self._build_graph(payload, edges)

        locality_index = LocalityIndex()
        locality_index.register_object_locality(
            "module.file",
            ["PECS_ID:module.file", "PECS_ID:timeout.refresh_timer", "PECS_ID:callback.on_refresh"],
        )

        validator = WorkspaceGraphValidator()
        report = validator.validate(
            graph,
            graph_index=GraphIndex(),
            execution_index=ExecutionIndex(),
            ownership_index=OwnershipIndex(),
            locality_index=locality_index,
        )
        self.assertTrue(report.valid, f"mismatches: {report.mismatches}")

    def test_unknown_future_signal_source_reaches_callback(self):
        """A future/invented signal prefix must work without any allowlist changes."""
        payload = {
            "PECS_ID:module.file": {"file": "module/file.py", "runtime_zone": "general_runtime"},
            "PECS_ID:phaseChange.detector": {"file": "module/file.py", "runtime_zone": "general_runtime"},
            "PECS_ID:callback.on_phase_change": {"file": "module/file.py", "runtime_zone": "general_runtime"},
        }
        edges = [
            {"from": "PECS_ID:module.file", "to": "PECS_ID:phaseChange.detector", "type": "signal_slot"},
            {"from": "PECS_ID:phaseChange.detector", "to": "PECS_ID:callback.on_phase_change", "type": "signal_slot"},
        ]
        graph = self._build_graph(payload, edges)

        locality_index = LocalityIndex()
        locality_index.register_object_locality(
            "module.file",
            ["PECS_ID:module.file", "PECS_ID:phaseChange.detector", "PECS_ID:callback.on_phase_change"],
        )

        validator = WorkspaceGraphValidator()
        report = validator.validate(
            graph,
            graph_index=GraphIndex(),
            execution_index=ExecutionIndex(),
            ownership_index=OwnershipIndex(),
            locality_index=locality_index,
        )
        self.assertTrue(report.valid, f"mismatches: {report.mismatches}")


if __name__ == "__main__":
    unittest.main()
