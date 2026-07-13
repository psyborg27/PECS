from __future__ import annotations

import unittest
from pathlib import Path

from execution_graph.builders.workspace_graph_builder import WorkspaceGraphBuilder
from execution_graph.graph.workspace_graph import Edge, EdgeType, Graph, Node, NodeType
from validation.workspace_registry_validator import WorkspaceRegistryValidator
from workspace_registry.builders.workspace_registry_builder import (
    WorkspaceRegistryBuilder,
)
from workspace_registry.models import WorkspaceRegistry


class TestWorkspaceRegistry(unittest.TestCase):
    """Smoke tests for the deterministic Workspace Registry."""

    def _build_graph(self) -> Graph:
        graph = Graph(workspace_root="/tmp/ws")

        modules = [
            "PECS_ID:app.main",
            "PECS_ID:app.dialogs.settings",
            "PECS_ID:app.commands.save",
            "PECS_ID:app.utils.helpers",
            "PECS_ID:lib.shared.constants",
        ]
        for module_id in modules:
            graph.register_node(
                Node(
                    node_id=module_id,
                    node_type=NodeType.MODULE,
                    canonical_name=module_id.split(".")[-1],
                    module_path=module_id.replace("PECS_ID:", "").replace(".", "/"),
                )
            )

        graph.register_entrypoint("PECS_ID:app.main")

        edges = [
            ("PECS_ID:app.main", "PECS_ID:app.dialogs.settings", EdgeType.IMPORT),
            ("PECS_ID:app.main", "PECS_ID:app.commands.save", EdgeType.IMPORT),
            ("PECS_ID:app.dialogs.settings", "PECS_ID:app.utils.helpers", EdgeType.IMPORT),
            ("PECS_ID:app.commands.save", "PECS_ID:app.utils.helpers", EdgeType.IMPORT),
            ("PECS_ID:app.utils.helpers", "PECS_ID:lib.shared.constants", EdgeType.IMPORT),
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

    def test_registry_builds_features_and_units(self) -> None:
        graph = self._build_graph()
        builder = WorkspaceRegistryBuilder(Path("/tmp/ws"))
        registry = builder.build(graph)

        self.assertGreater(len(registry.features), 0)
        self.assertGreater(len(registry.infrastructure_units), 0)
        self.assertTrue(registry.metadata.registry_hash)

    def test_entrypoints_are_user_facing(self) -> None:
        graph = self._build_graph()
        builder = WorkspaceRegistryBuilder(Path("/tmp/ws"))
        registry = builder.build(graph)

        entrypoint_features = [
            f
            for f in registry.features.values()
            if f.root_node_id == "PECS_ID:app.main"
        ]
        self.assertEqual(len(entrypoint_features), 1)
        self.assertEqual(entrypoint_features[0].classification, "user_facing")

    def test_validation_passes(self) -> None:
        graph = self._build_graph()
        builder = WorkspaceRegistryBuilder(Path("/tmp/ws"))
        registry = builder.build(graph)

        validator = WorkspaceRegistryValidator()
        report = validator.validate(registry, graph)

        self.assertTrue(report.valid)
        self.assertTrue(report.registry_hash_stable)

    def test_registry_hash_is_deterministic(self) -> None:
        graph = self._build_graph()
        builder = WorkspaceRegistryBuilder(Path("/tmp/ws"))

        registry1 = builder.build(graph)
        registry2 = builder.build(graph)

        self.assertEqual(
            registry1.metadata.registry_hash,
            registry2.metadata.registry_hash,
        )

    def test_registry_from_dict_roundtrip_preserves_hash(self) -> None:
        graph = self._build_graph()
        builder = WorkspaceRegistryBuilder(Path("/tmp/ws"))
        registry = builder.build(graph)
        original_hash = registry.metadata.registry_hash

        rebuilt = WorkspaceRegistry.from_dict(registry.to_dict())
        self.assertEqual(rebuilt.metadata.registry_hash, original_hash)
        self.assertEqual(len(rebuilt.features), len(registry.features))
        self.assertEqual(
            len(rebuilt.infrastructure_units),
            len(registry.infrastructure_units),
        )


if __name__ == "__main__":
    unittest.main()
