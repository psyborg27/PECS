from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from execution_graph.builders.workspace_graph_builder import WorkspaceGraphBuilder
from evidence_correlation.engines.evidence_correlator import EvidenceCorrelator
from navigation_builder.builders.navigation_graph_builder import (
    NavigationGraphBuilder,
)
from workspace_registry.builders.workspace_registry_builder import (
    WorkspaceRegistryBuilder,
)

LOG = logging.getLogger(__name__)


class PECSQueryPipeline:
    """
    End-to-end deterministic PECS query pipeline.

    Transforms a list of architectural query terms into a Navigation Graph
    without prose, summarization, compression, or semantic search.
    """

    def __init__(self, workspace_root: Path) -> None:
        self.workspace_root = workspace_root.resolve()
        self.pecs_dir = self.workspace_root / ".pecs"

    def query(
        self,
        terms: List[str],
        max_clusters: int = 1,
        max_nodes: int = 40,
        max_depth: int = 2,
    ) -> Dict[str, Any]:
        """
        Execute the query pipeline and return a Navigation Graph response.
        """
        if not terms:
            return {
                "query_terms": [],
                "error": "no query terms provided",
                "navigation_graph": None,
            }

        locality_payload = self._load_json("locality_index.json")
        topology_compact = self._load_json("topology_compact.json")

        if not locality_payload or not topology_compact:
            return {
                "query_terms": terms,
                "error": "missing required .pecs artifacts",
                "navigation_graph": None,
            }

        try:
            graph = self._build_graph(locality_payload, topology_compact)
            registry = self._build_registry(graph)
            correlator = self._build_correlator(graph, registry, locality_payload)
            correlation_result = correlator.correlate(
                terms,
                max_clusters=max_clusters,
            )

            selected_clusters = correlation_result.clusters[:max_clusters]
            if not selected_clusters:
                return {
                    "query_terms": terms,
                    "error": "no evidence clusters correlated",
                    "navigation_graph": None,
                }

            nav_builder = NavigationGraphBuilder(
                workspace_root=self.workspace_root,
                graph=graph,
                max_nodes=max_nodes,
                max_depth=max_depth,
            )
            nav_graph = nav_builder.build(
                selected_clusters,
                query_terms=terms,
            )

            return {
                "query_terms": terms,
                "max_clusters": max_clusters,
                "max_nodes": max_nodes,
                "max_depth": max_depth,
                "correlation_cluster_count": len(correlation_result.clusters),
                "selected_cluster_count": len(selected_clusters),
                "navigation_graph": nav_graph.to_dict(),
            }
        except Exception as exc:
            LOG.warning("PECS query pipeline failed: %s", exc)
            return {
                "query_terms": terms,
                "error": str(exc),
                "navigation_graph": None,
            }

    def _build_graph(
        self,
        locality_payload: Dict[str, Any],
        topology_compact: Dict[str, Any],
    ) -> Any:
        builder = WorkspaceGraphBuilder(self.workspace_root)
        entrypoints = []
        for entry_id in topology_compact.get("entrypoints", []):
            rel = (
                entry_id.replace("PECS_ID:", "")
                .replace(".", "/")
                + ".py"
            )
            entrypoints.append(self.workspace_root / rel)

        return builder.build(
            reachable_files=set(),
            runtime_locality_payload=locality_payload,
            runtime_topology_edges=topology_compact.get("edges", []),
            entrypoints=entrypoints,
        )

    def _build_registry(self, graph: Any) -> Any:
        builder = WorkspaceRegistryBuilder(self.workspace_root)
        return builder.build(graph)

    def _build_correlator(
        self,
        graph: Any,
        registry: Any,
        locality_payload: Dict[str, Any],
    ) -> EvidenceCorrelator:
        correlator = EvidenceCorrelator(
            workspace_root=self.workspace_root,
            graph=graph,
            registry=registry,
            locality_payload=locality_payload,
        )
        correlator.build_index()
        return correlator

    def _load_json(self, filename: str) -> Optional[Dict[str, Any]]:
        path = self.pecs_dir / filename
        if not path.exists():
            return None
        try:
            with path.open("r", encoding="utf-8") as handle:
                return json.load(handle)
        except Exception:
            return None
