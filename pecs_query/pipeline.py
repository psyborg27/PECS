from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Generic, List, Optional, TypeVar

from execution_graph.builders.workspace_graph_builder import WorkspaceGraphBuilder
from evidence_correlation.engines.evidence_correlator import EvidenceCorrelator
from navigation_builder.builders.navigation_graph_builder import (
    NavigationGraphBuilder,
)
from workspace_registry.builders.workspace_registry_builder import (
    WorkspaceRegistryBuilder,
)

# Canonical query types used by stage contracts.
# Imported lazily inside stages to avoid circular dependency at module level.

LOG = logging.getLogger(__name__)


# ====================================================================
# Pipeline Stage Contracts (additive — do not affect existing class)
# ====================================================================

I = TypeVar("I")  # Stage input type
O = TypeVar("O")  # Stage output type


class PipelineStage(ABC, Generic[I, O]):
    """Abstract base for every stage in the PECS query pipeline.

    Each stage accepts a single input and produces a single output.
    Stages are composable: ``stage_n(stage_n_1(...stage_0(input)))``.
    """

    @abstractmethod
    def execute(self, input_data: I) -> O:
        """Execute this stage and return its output."""
        ...

    @property
    @abstractmethod
    def stage_name(self) -> str:
        """Human-readable stage name for observability."""
        ...


# ── Stage 1: Lexical Analysis ─────────────────────────────────────────────


class LexicalAnalysisInput:
    """Input to the lexical analysis stage: raw query text + consumer metadata."""

    def __init__(self, raw_query: str, consumer: str = "other",
                 profile: str = "medium") -> None:
        self.raw_query = raw_query
        self.consumer = consumer
        self.profile = profile


class LexicalAnalysisOutput:
    """Output of the lexical analysis stage: a QueryParseResult.

    The actual type is ``QueryParseResult`` from ``pecs_query.query_parser``.
    This type alias exists so the contract is explicit without forcing a direct
    import of the parser module at definition time.
    """

    def __init__(self, parse_result) -> None:
        self.parse_result = parse_result


class LexicalAnalysisStage(PipelineStage[LexicalAnalysisInput, LexicalAnalysisOutput]):
    """Tokenize, filter stop words, detect sections, extract preserved patterns."""

    @property
    def stage_name(self) -> str:
        return "lexical_analysis"

    def execute(self, input_data: LexicalAnalysisInput) -> LexicalAnalysisOutput:
        from pecs_query.query_parser import QueryParser
        result = QueryParser.parse(input_data.raw_query)
        return LexicalAnalysisOutput(result)


# ── Stage 2: Engineering Object Resolution (contract only) ────────────────


class EngineeringObjectResolutionInput:
    """Input: a fully constructed CanonicalQueryObject with parsed_terms populated."""

    def __init__(self, cqo) -> None:
        self.cqo = cqo


class EngineeringObjectResolutionOutput:
    """Output: the same CQO with candidate_objects populated."""

    def __init__(self, cqo) -> None:
        self.cqo = cqo


class EngineeringObjectResolutionStage(
    PipelineStage[EngineeringObjectResolutionInput, EngineeringObjectResolutionOutput]
):
    """Resolve lexical terms to candidate engineering objects.

    **Not yet implemented.**  This is an architectural placeholder.
    """

    @property
    def stage_name(self) -> str:
        return "engineering_object_resolution"

    def execute(
        self, input_data: EngineeringObjectResolutionInput
    ) -> EngineeringObjectResolutionOutput:
        # Pass-through: returns the CQO with empty candidate_objects.
        return EngineeringObjectResolutionOutput(input_data.cqo)


# ── Stage 3: Ontology Resolution (contract only) ──────────────────────────


class OntologyResolutionInput:
    def __init__(self, cqo) -> None:
        self.cqo = cqo


class OntologyResolutionOutput:
    def __init__(self, cqo) -> None:
        self.cqo = cqo


class OntologyResolutionStage(
    PipelineStage[OntologyResolutionInput, OntologyResolutionOutput]
):
    """Resolve repository vocabulary phrases to ontology-backed objects.

    **Not yet implemented.**  This is an architectural placeholder.
    """

    @property
    def stage_name(self) -> str:
        return "ontology_resolution"

    def execute(self, input_data: OntologyResolutionInput) -> OntologyResolutionOutput:
        return OntologyResolutionOutput(input_data.cqo)


# ── Stage 4: Object Expansion (contract only) ─────────────────────────────


class ObjectExpansionInput:
    def __init__(self, cqo) -> None:
        self.cqo = cqo


class ObjectExpansionOutput:
    def __init__(self, cqo) -> None:
        self.cqo = cqo


class ObjectExpansionStage(PipelineStage[ObjectExpansionInput, ObjectExpansionOutput]):
    """Expand seed objects through graph topology to find related objects.

    **Not yet implemented.**  This is an architectural placeholder.
    """

    @property
    def stage_name(self) -> str:
        return "object_expansion"

    def execute(self, input_data: ObjectExpansionInput) -> ObjectExpansionOutput:
        return ObjectExpansionOutput(input_data.cqo)


# ── Stage 5: Canonical Query Construction (contract only) ─────────────────


class CanonicalQueryConstructionInput:
    def __init__(self, cqo) -> None:
        self.cqo = cqo


class CanonicalQueryConstructionOutput:
    def __init__(self, cqo) -> None:
        self.cqo = cqo


class CanonicalQueryConstructionStage(
    PipelineStage[CanonicalQueryConstructionInput, CanonicalQueryConstructionOutput]
):
    """Finalise the CQO with defaulted fields, validated constraints, metadata.

    **Not yet implemented.**  This is an architectural placeholder.
    """

    @property
    def stage_name(self) -> str:
        return "canonical_query_construction"

    def execute(
        self, input_data: CanonicalQueryConstructionInput
    ) -> CanonicalQueryConstructionOutput:
        return CanonicalQueryConstructionOutput(input_data.cqo)


# ── Stage 6: Evidence Correlation (contract only) ─────────────────────────


class EvidenceCorrelationInput:
    def __init__(self, cqo, graph=None, registry=None,
                 locality_payload=None) -> None:
        self.cqo = cqo
        self.graph = graph
        self.registry = registry
        self.locality_payload = locality_payload


class EvidenceCorrelationOutput:
    def __init__(self, cqo, clusters=None) -> None:
        self.cqo = cqo
        self.clusters = clusters or []


class EvidenceCorrelationStage(
    PipelineStage[EvidenceCorrelationInput, EvidenceCorrelationOutput]
):
    """Correlate query terms against deterministic workspace evidence.

    **Not yet implemented as a stage.**  The existing ``EvidenceCorrelator``
    is called directly by ``PECSQueryPipeline`` and continues to work unchanged.
    """

    @property
    def stage_name(self) -> str:
        return "evidence_correlation"

    def execute(
        self, input_data: EvidenceCorrelationInput
    ) -> EvidenceCorrelationOutput:
        return EvidenceCorrelationOutput(input_data.cqo)


# ── Stage 7: Authority (contract only) ────────────────────────────────────


class AuthorityInput:
    def __init__(self, cqo, clusters=None, graph=None, registry=None) -> None:
        self.cqo = cqo
        self.clusters = clusters or []
        self.graph = graph
        self.registry = registry


class AuthorityOutput:
    def __init__(self, cqo, authority_report=None) -> None:
        self.cqo = cqo
        self.authority_report = authority_report


class AuthorityStage(PipelineStage[AuthorityInput, AuthorityOutput]):
    """Produce per-target authority scores with evidence breakdown.

    **Not yet implemented.**  This is an architectural placeholder.
    """

    @property
    def stage_name(self) -> str:
        return "authority"

    def execute(self, input_data: AuthorityInput) -> AuthorityOutput:
        return AuthorityOutput(input_data.cqo)


# ── Stage 8: Projection (contract only) ───────────────────────────────────


class ProjectionInput:
    def __init__(self, cqo, authority_report=None, graph=None) -> None:
        self.cqo = cqo
        self.authority_report = authority_report
        self.graph = graph


class ProjectionOutput:
    def __init__(self, cqo, projection=None) -> None:
        self.cqo = cqo
        self.projection = projection


class ProjectionStage(PipelineStage[ProjectionInput, ProjectionOutput]):
    """Shape the final projection response from authority and profile selection.

    **Not yet implemented.**  This is an architectural placeholder.
    """

    @property
    def stage_name(self) -> str:
        return "projection"

    def execute(self, input_data: ProjectionInput) -> ProjectionOutput:
        return ProjectionOutput(input_data.cqo)


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
