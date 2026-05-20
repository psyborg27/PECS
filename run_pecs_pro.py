from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict

from continuity.registry.continuity_registry import (
    ContinuityRegistry,
)
from continuity.registry.runtime_registry import (
    RuntimeRegistry,
)

from execution_graph.indexes.graph_index import (
    GraphIndex,
)
from execution_graph.indexes.execution_index import (
    ExecutionIndex,
)
from execution_graph.indexes.ownership_index import (
    OwnershipIndex,
)

from topology.indexing.locality_index import (
    LocalityIndex,
)

from topology.scoring.continuity_score_engine import (
    ContinuityScoreEngine,
)

from topology.retrieval.topology_retriever import (
    TopologyRetriever,
)

from topology.incremental.incremental_topology_updater import (
    IncrementalTopologyUpdater,
)

from runtime.session.workspace_runtime_session import (
    WorkspaceRuntimeSession,
)

from topology.compaction.compact_context_builder import (
    CompactContextBuilder,
)


@dataclass
class PECSProRuntime:
    """
    Canonical deterministic PECS-PRO v2 runtime.

    This intentionally remains:
    - deterministic
    - topology-first
    - continuity-oriented
    - lightweight
    - non-autonomous

    PECS intentionally avoids:
    - orchestration forests
    - runtime daemons
    - recursive AI systems
    - self-modifying infrastructure
    - autonomous engineering systems

    PECS exists to:
    - reconstruct continuity
    - preserve locality
    - reduce token overhead
    - stabilize long-running engineering
    """

    workspace_root: Path

    def initialize(self) -> Dict[str, object]:
        continuity_registry = ContinuityRegistry()
        runtime_registry = RuntimeRegistry()

        graph_index = GraphIndex()
        execution_index = ExecutionIndex()
        ownership_index = OwnershipIndex()

        locality_index = LocalityIndex()

        scoring_engine = ContinuityScoreEngine()

        topology_retriever = TopologyRetriever(
            locality_index=locality_index,
            execution_index=execution_index,
            ownership_index=ownership_index,
            scoring_engine=scoring_engine,
            mode="exploratory",
        )

        incremental_updater = IncrementalTopologyUpdater(
            graph_index=graph_index,
            locality_index=locality_index,
            topology_retriever=topology_retriever,
        )

        runtime_session = WorkspaceRuntimeSession(
            workspace_root=self.workspace_root,
            graph_index=graph_index,
            execution_index=execution_index,
            locality_index=locality_index,
            topology_retriever=topology_retriever,
            incremental_updater=incremental_updater,
        )

        compact_builder = CompactContextBuilder(
            topology_retriever=topology_retriever,
        )

        return {
            "continuity_registry": continuity_registry,
            "runtime_registry": runtime_registry,
            "graph_index": graph_index,
            "execution_index": execution_index,
            "ownership_index": ownership_index,
            "locality_index": locality_index,
            "scoring_engine": scoring_engine,
            "topology_retriever": topology_retriever,
            "incremental_updater": incremental_updater,
            "runtime_session": runtime_session,
            "compact_builder": compact_builder,
        }


def bootstrap_pecs_pro(
    workspace_root: str,
) -> PECSProRuntime:
    """
    Canonical PECS-PRO v2 bootstrap entrypoint.
    """

    runtime = PECSProRuntime(
        workspace_root=Path(workspace_root),
    )

    runtime.initialize()

    return runtime


if __name__ == "__main__":
    runtime = bootstrap_pecs_pro(".")
    print("PECS-PRO v2 initialized successfully.")
