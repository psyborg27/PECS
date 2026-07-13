from __future__ import annotations

import json
import unittest
from pathlib import Path

from execution_graph.builders.workspace_graph_builder import WorkspaceGraphBuilder
from evidence_correlation.engines.evidence_correlator import EvidenceCorrelator
from navigation_builder.builders.navigation_graph_builder import NavigationGraphBuilder
from workspace_registry.builders.workspace_registry_builder import WorkspaceRegistryBuilder


class TestQueryPipeline(unittest.TestCase):
    """End-to-end smoke tests for the CLI query pipeline flow."""

    def _create_minimal_workspace(self, root: Path) -> None:
        pecs_dir = root / ".pecs"
        pecs_dir.mkdir(parents=True, exist_ok=True)

        locality = {
            "PECS_ID:app.main": {
                "file": "app/main.py",
                "class": "",
                "method": "main",
                "runtime_zone": "general_runtime",
            },
            "PECS_ID:app.graph.builder": {
                "file": "app/graph/builder.py",
                "class": "GraphBuilder",
                "method": "build",
                "runtime_zone": "general_runtime",
            },
            "PECS_ID:app.correlator": {
                "file": "app/correlator.py",
                "class": "Correlator",
                "method": "correlate",
                "runtime_zone": "general_runtime",
            },
        }
        topology = {
            "entrypoints": ["PECS_ID:app.main"],
            "edges": [
                {"from": "PECS_ID:app.main", "to": "PECS_ID:app.graph.builder", "type": "import"},
                {"from": "PECS_ID:app.main", "to": "PECS_ID:app.correlator", "type": "import"},
            ],
        }

        (pecs_dir / "locality_index.json").write_text(
            json.dumps(locality, sort_keys=True), encoding="utf-8"
        )
        (pecs_dir / "topology_compact.json").write_text(
            json.dumps(topology, sort_keys=True), encoding="utf-8"
        )

    def test_pipeline_produces_navigation_graph(self) -> None:
        workspace_root = Path("/tmp/pecs-query-pipeline-test")
        workspace_root.mkdir(parents=True, exist_ok=True)
        self._create_minimal_workspace(workspace_root)

        locality = json.loads(
            (workspace_root / ".pecs" / "locality_index.json").read_text(encoding="utf-8")
        )
        topology = json.loads(
            (workspace_root / ".pecs" / "topology_compact.json").read_text(encoding="utf-8")
        )

        entrypoint_paths = []
        for ep in topology.get("entrypoints", []):
            body = ep[len("PECS_ID:") :] if ep.startswith("PECS_ID:") else ep
            candidate = workspace_root / (body.replace(".", "/") + ".py")
            if candidate.exists():
                entrypoint_paths.append(candidate)

        graph_builder = WorkspaceGraphBuilder(workspace_root)
        graph = graph_builder.build(
            reachable_files=set(),
            runtime_locality_payload=locality,
            runtime_topology_edges=topology.get("edges", []),
            entrypoints=entrypoint_paths,
        )

        registry_builder = WorkspaceRegistryBuilder(workspace_root)
        registry = registry_builder.build(graph)

        correlator = EvidenceCorrelator(
            workspace_root=workspace_root,
            graph=graph,
            registry=registry,
        )
        correlator.build_index()
        correlation_result = correlator.correlate(["graph", "correlator"], max_clusters=2)

        self.assertGreaterEqual(len(correlation_result.clusters), 1)

        nav_builder = NavigationGraphBuilder(
            workspace_root=workspace_root,
            graph=graph,
            max_nodes=20,
            max_depth=1,
        )
        nav_graph = nav_builder.build(
            clusters=correlation_result.clusters,
            query_terms=["graph", "correlator"],
        )

        self.assertGreaterEqual(len(nav_graph.nodes), 1)
        self.assertIn("query_terms", nav_graph.to_dict())

        # Navigation graph should be deterministic for unchanged inputs.
        nav_graph_2 = nav_builder.build(
            clusters=correlation_result.clusters,
            query_terms=["graph", "correlator"],
        )
        self.assertEqual(
            nav_graph.to_dict(),
            nav_graph_2.to_dict(),
        )


if __name__ == "__main__":
    unittest.main()
