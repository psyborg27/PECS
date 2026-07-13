from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from execution_graph.graph.workspace_graph import Graph


@dataclass
class ProjectionRequest:
    """
    Input parameters for a graph projection.

    Projections are generated on demand and are not persisted.
    """

    projection_name: str
    seed_node_ids: List[str] = None  # type: ignore[assignment]
    max_nodes: int = 40
    max_depth: int = 4
    focus_terms: List[str] = None  # type: ignore[assignment]
    metadata: Dict[str, Any] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.seed_node_ids is None:
            self.seed_node_ids = []
        if self.focus_terms is None:
            self.focus_terms = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ProjectionResult:
    """
    Output of a graph projection.

    Contains only references (node/edge ids) into the Workspace Graph;
    no separate copy of graph data is stored.
    """

    projection_name: str
    node_ids: List[str]
    edge_ids: List[str]
    metadata: Dict[str, Any]


class ProjectionEngine(ABC):
    """
    Abstract interface for Workspace Graph projections.

    This is a placeholder extension point. Concrete implementations
    can be added later for feature-specific projections (e.g., mutation
    owner projection, dispatch chain projection, dependency projection)
    without changing the core graph model.
    """

    @abstractmethod
    def project(
        self,
        graph: Graph,
        request: ProjectionRequest,
    ) -> ProjectionResult:
        """Generate a projection from the workspace graph."""
        raise NotImplementedError

    @abstractmethod
    def supported_projections(self) -> List[str]:
        """Return the names of projections this engine supports."""
        raise NotImplementedError
