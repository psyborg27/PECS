from __future__ import annotations

import hashlib
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from execution_graph.graph.workspace_graph import Graph, NodeType
from evidence_correlation.engines.evidence_extractor import EvidenceExtractor
from evidence_correlation.models import (
    CorrelationResult,
    EvidenceBreakdown,
    EvidenceCluster,
)
from workspace_registry.models import WorkspaceRegistry


# Weights for each evidence source. All weights are positive and fixed.
# No single source dominates because every source is normalized separately.
_EVIDENCE_WEIGHTS: Dict[str, float] = {
    "package_name": 1.0,
    "folder_hierarchy": 0.9,
    "module_file_name": 0.9,
    "import_locality": 0.7,
    "export_locality": 0.6,
    "class_name": 0.8,
    "function_method_name": 0.7,
    "decorator": 0.5,
    "controller_ownership": 0.6,
    "runtime_ownership": 0.6,
    "ui_registration": 0.8,
    "execution_graph_locality": 0.5,
    "graph_topology": 0.4,
    "continuity_artifact": 0.5,
}

# Minimum cumulative score for a cluster to be returned.
_MIN_CLUSTER_SCORE = 0.01


class EvidenceCorrelator:
    """
    Deterministic architectural evidence correlation engine.

    Given a list of query terms, correlates them against deterministic
    workspace evidence and returns ranked Evidence Clusters.

    Not semantic search. Not feature discovery. Not projection generation.
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
        self.extractor = EvidenceExtractor(
            workspace_root=workspace_root,
            graph=graph,
            registry=registry,
            locality_payload=locality_payload,
        )
        self._evidence: Optional[Dict[str, Dict[str, Set[str]]]] = None

    def build_index(self) -> None:
        """Build or rebuild the deterministic evidence index."""
        self._evidence = self.extractor.extract()

    def correlate(
        self,
        query_terms: List[str],
        max_clusters: int = 12,
    ) -> CorrelationResult:
        """
        Correlate query terms against evidence and return ranked clusters.
        """
        if self._evidence is None:
            self.build_index()

        normalized_terms = [self._normalize(term) for term in query_terms]

        node_scores: Dict[str, EvidenceBreakdown] = {}
        for node_id, node_evidence in self._evidence.items():
            breakdown = self._score_node(node_evidence, normalized_terms)
            cumulative = self._weighted_sum(breakdown)
            if cumulative >= _MIN_CLUSTER_SCORE:
                node_scores[node_id] = breakdown

        # Group nodes into clusters by primary namespace/root package.
        clusters = self._build_clusters(node_scores)
        clusters.sort(
            key=lambda cluster: (
                -cluster.cumulative_correlation_score,
                cluster.primary_namespace,
            )
        )

        return CorrelationResult(
            query_terms=query_terms,
            clusters=clusters[:max_clusters],
            metadata={
                "workspace_root": str(self.workspace_root),
                "indexed_nodes": len(self._evidence),
                "matched_nodes": len(node_scores),
                "evidence_source_count": len(_EVIDENCE_WEIGHTS),
            },
        )

    def _score_node(
        self,
        node_evidence: Dict[str, Set[str]],
        query_terms: List[str],
    ) -> EvidenceBreakdown:
        breakdown = EvidenceBreakdown()

        for source, weight in _EVIDENCE_WEIGHTS.items():
            terms = node_evidence.get(source, set())
            if not terms:
                continue

            normalized_terms = {self._normalize(term) for term in terms}
            matches = sum(
                1
                for query_term in query_terms
                if any(query_term in ev_term for ev_term in normalized_terms)
            )
            if matches:
                # Normalize by number of query terms and apply weight.
                setattr(
                    breakdown,
                    source,
                    min(1.0, matches / len(query_terms)) * weight,
                )

        return breakdown

    def _weighted_sum(self, breakdown: EvidenceBreakdown) -> float:
        total = 0.0
        for source, weight in _EVIDENCE_WEIGHTS.items():
            total += getattr(breakdown, source, 0.0) * weight
        # Normalize by sum of weights so score stays in [0, 1].
        return total / sum(_EVIDENCE_WEIGHTS.values())

    def _build_clusters(
        self,
        node_scores: Dict[str, EvidenceBreakdown],
    ) -> List[EvidenceCluster]:
        # Group by root package (first segment of PECS id).
        groups: Dict[str, List[str]] = {}
        for node_id in node_scores:
            root = self._root_package(node_id)
            groups.setdefault(root, []).append(node_id)

        clusters: List[EvidenceCluster] = []
        for root_package, node_ids in sorted(groups.items()):
            cluster = self._cluster_from_nodes(root_package, node_ids, node_scores)
            clusters.append(cluster)

        return clusters

    def _cluster_from_nodes(
        self,
        root_package: str,
        node_ids: List[str],
        node_scores: Dict[str, EvidenceBreakdown],
    ) -> EvidenceCluster:
        primary_namespace = root_package
        participating_files: Set[str] = set()
        imports: Set[str] = set()
        exports: Set[str] = set()
        classes: Set[str] = set()
        methods_functions: Set[str] = set()
        runtime_nodes: Set[str] = set()
        ownership_nodes: Set[str] = set()
        graph_nodes: Set[str] = set()
        aggregated = EvidenceBreakdown()

        for node_id in node_ids:
            node = self.graph.nodes.get(node_id)
            if node is None:
                continue

            graph_nodes.add(node_id)
            breakdown = node_scores[node_id]
            self._aggregate_breakdown(aggregated, breakdown)

            if node.source_file:
                participating_files.add(node.source_file)
            if node.class_name:
                classes.add(node.class_name)
            if node.method_name:
                methods_functions.add(node.method_name)

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
                runtime_nodes.add(node_id)
                ownership_nodes.add(node_id)

        # Aggregate imports/exports from cluster member outgoing/incoming edges.
        for node_id in node_ids:
            node = self.graph.nodes.get(node_id)
            if node is None:
                continue
            for edge_id in node.outgoing_edges:
                edge = self.graph.edges.get(edge_id)
                if edge and edge.target_node_id not in graph_nodes:
                    imports.add(edge.target_node_id)
            for edge_id in node.incoming_edges:
                edge = self.graph.edges.get(edge_id)
                if edge and edge.source_node_id not in graph_nodes:
                    exports.add(edge.source_node_id)

        cumulative = self._weighted_sum(aggregated)
        cluster_id = self._cluster_id(root_package, sorted(graph_nodes))

        return EvidenceCluster(
            cluster_id=cluster_id,
            primary_namespace=primary_namespace,
            root_package=root_package,
            participating_files=sorted(participating_files),
            imports=sorted(imports),
            exports=sorted(exports),
            classes=sorted(classes),
            methods_functions=sorted(methods_functions),
            runtime_nodes=sorted(runtime_nodes),
            ownership_nodes=sorted(ownership_nodes),
            graph_nodes=sorted(graph_nodes),
            evidence_breakdown=aggregated,
            cumulative_correlation_score=cumulative,
            metadata={"node_count": len(graph_nodes)},
        )

    def _aggregate_breakdown(
        self,
        target: EvidenceBreakdown,
        source: EvidenceBreakdown,
    ) -> None:
        for field_name in _EVIDENCE_WEIGHTS.keys():
            current = getattr(target, field_name, 0.0)
            addition = getattr(source, field_name, 0.0)
            setattr(target, field_name, max(current, addition))

    def _root_package(self, node_id: str) -> str:
        body = node_id[len("PECS_ID:") :] if node_id.startswith("PECS_ID:") else node_id
        parts = body.split(".")
        return parts[0] if parts else node_id

    def _normalize(self, term: str) -> str:
        return term.lower().strip().replace("_", "").replace("-", "")

    def _cluster_id(
        self,
        root_package: str,
        node_ids: List[str],
    ) -> str:
        payload = root_package + "|" + "|".join(node_ids)
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
        return f"ec-{root_package}-{digest}"


def _tanh_scale(value: float, scale: float = 1.0) -> float:
    """Optional deterministic non-linearity."""
    return math.tanh(value / scale)
