from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Set


@dataclass
class EvidenceBreakdown:
    """
    Correlation contribution from each deterministic evidence source.

    Scores are normalized per source before the weighted combination.
    """

    package_name: float = 0.0
    folder_hierarchy: float = 0.0
    module_file_name: float = 0.0
    import_locality: float = 0.0
    export_locality: float = 0.0
    class_name: float = 0.0
    function_method_name: float = 0.0
    decorator: float = 0.0
    controller_ownership: float = 0.0
    runtime_ownership: float = 0.0
    ui_registration: float = 0.0
    execution_graph_locality: float = 0.0
    graph_topology: float = 0.0
    continuity_artifact: float = 0.0

    def to_dict(self) -> Dict[str, float]:
        return {
            "package_name": self.package_name,
            "folder_hierarchy": self.folder_hierarchy,
            "module_file_name": self.module_file_name,
            "import_locality": self.import_locality,
            "export_locality": self.export_locality,
            "class_name": self.class_name,
            "function_method_name": self.function_method_name,
            "decorator": self.decorator,
            "controller_ownership": self.controller_ownership,
            "runtime_ownership": self.runtime_ownership,
            "ui_registration": self.ui_registration,
            "execution_graph_locality": self.execution_graph_locality,
            "graph_topology": self.graph_topology,
            "continuity_artifact": self.continuity_artifact,
        }


@dataclass
class EvidenceCluster:
    """
    A ranked cluster of deterministic architectural evidence correlated
    against a set of query terms.
    """

    cluster_id: str
    primary_namespace: str
    root_package: str
    participating_files: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    exports: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    methods_functions: List[str] = field(default_factory=list)
    runtime_nodes: List[str] = field(default_factory=list)
    ownership_nodes: List[str] = field(default_factory=list)
    graph_nodes: List[str] = field(default_factory=list)
    evidence_breakdown: EvidenceBreakdown = field(
        default_factory=EvidenceBreakdown
    )
    cumulative_correlation_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cluster_id": self.cluster_id,
            "primary_namespace": self.primary_namespace,
            "root_package": self.root_package,
            "participating_files": sorted(self.participating_files),
            "imports": sorted(self.imports),
            "exports": sorted(self.exports),
            "classes": sorted(self.classes),
            "methods_functions": sorted(self.methods_functions),
            "runtime_nodes": sorted(self.runtime_nodes),
            "ownership_nodes": sorted(self.ownership_nodes),
            "graph_nodes": sorted(self.graph_nodes),
            "evidence_breakdown": self.evidence_breakdown.to_dict(),
            "cumulative_correlation_score": self.cumulative_correlation_score,
            "metadata": self.metadata,
        }


@dataclass
class CorrelationResult:
    """Top-level result returned by the Evidence Correlation Engine."""

    query_terms: List[str]
    clusters: List[EvidenceCluster]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query_terms": sorted(self.query_terms),
            "cluster_count": len(self.clusters),
            "clusters": [cluster.to_dict() for cluster in self.clusters],
            "metadata": self.metadata,
        }
