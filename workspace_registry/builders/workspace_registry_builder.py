from __future__ import annotations

import hashlib
import math
from pathlib import Path
from typing import Any, Dict, Set

from execution_graph.graph.workspace_graph import Graph
from workspace_registry.builders.feature_identification import (
    FeatureCandidate,
    FeatureIdentifier,
)
from workspace_registry.models import (
    WorkspaceEvidence,
    WorkspaceFeature,
    WorkspaceInfrastructureUnit,
    WorkspaceRegistry,
    WorkspaceRegistryMetadata,
)


# Evidence weights for confidence calculation. Sum is irrelevant because of
# tanh normalization, but relative magnitudes encode priority.
_EVIDENCE_WEIGHTS: Dict[str, float] = {
    "package_locality": 1.0,
    "module_naming_locality": 0.9,
    "public_ui_registration": 1.0,
    "controller_ownership": 0.8,
    "import_export_locality": 0.5,
    "runtime_evidence": 0.4,
    "graph_topology_validated": 0.2,
}

# Per-node-type bonus values.
_UI_ANCHOR_BONUS = 0.15
_CONTROLLER_BONUS = 0.15
_SUPPORT_MODULE_BONUS = 0.05


class WorkspaceRegistryBuilder:
    """
    Build a deterministic WorkspaceRegistry from a Workspace Graph.

    Feature candidates are identified from evidence first; the graph is
    used only to validate and expand boundaries.
    """

    def __init__(self, workspace_root: Path) -> None:
        self.workspace_root = workspace_root

    def build(
        self,
        graph: Graph,
        include_infrastructure: bool = True,
    ) -> WorkspaceRegistry:
        registry = WorkspaceRegistry(
            workspace_root=str(self.workspace_root),
            metadata=self._build_metadata(graph),
        )

        identifier = FeatureIdentifier(graph)
        candidates = identifier.identify()

        for candidate in sorted(candidates, key=lambda c: c.candidate_id):
            evidence = self._build_evidence(candidate)
            confidence = self._calculate_confidence(evidence)

            if candidate.classification == "user_facing":
                feature = WorkspaceFeature(
                    feature_id=candidate.candidate_id,
                    aliases=self._generate_aliases(candidate),
                    root_node_id=candidate.root_node_id,
                    node_ids=set(candidate.node_ids),
                    edge_ids=set(candidate.edge_ids),
                    evidence=evidence,
                    confidence=confidence,
                    classification=candidate.classification,
                    metadata={
                        "root_package": self._package_prefix(
                            candidate.root_node_id
                        ),
                    },
                )
                registry.register_feature(feature)
            elif include_infrastructure:
                unit = WorkspaceInfrastructureUnit(
                    unit_id=candidate.candidate_id,
                    aliases=self._generate_aliases(candidate),
                    root_node_id=candidate.root_node_id,
                    node_ids=set(candidate.node_ids),
                    edge_ids=set(candidate.edge_ids),
                    evidence=evidence,
                    confidence=confidence,
                    supported_features=set(),
                    metadata={
                        "root_package": self._package_prefix(
                            candidate.root_node_id
                        ),
                    },
                )
                registry.register_infrastructure_unit(unit)

        self._link_infrastructure_to_features(registry)
        registry.update_registry_hash()
        return registry

    def _build_metadata(self, graph: Graph) -> WorkspaceRegistryMetadata:
        workspace_hash = _workspace_hash(self.workspace_root)
        build_id = _deterministic_build_id(
            self.workspace_root,
            len(graph.nodes),
            len(graph.edges),
        )
        return WorkspaceRegistryMetadata(
            registry_version="1.0.0",
            workspace_hash=workspace_hash,
            build_id=build_id,
            created_at=_utc_now(),
            last_updated=_utc_now(),
            registry_hash="",
        )

    def _build_evidence(self, candidate: FeatureCandidate) -> WorkspaceEvidence:
        evidence = WorkspaceEvidence()
        evidence.graph_topology_validated = (
            "graph_topology_validated" in candidate.evidence_tags
        )
        evidence.package_locality = "package_locality" in candidate.evidence_tags
        evidence.module_naming_locality = (
            "module_naming_locality" in candidate.evidence_tags
        )
        evidence.public_ui_registration = (
            "public_ui_registration" in candidate.evidence_tags
        )
        evidence.controller_ownership = "controller_ownership" in candidate.evidence_tags
        evidence.import_export_locality = (
            "import_export_locality" in candidate.evidence_tags
        )
        evidence.runtime_evidence = "runtime_evidence" in candidate.evidence_tags

        evidence.package_depth = self._package_depth(candidate.root_node_id)
        evidence.ui_anchor_count = self._count_ui_anchors(candidate)
        evidence.controller_count = self._count_controllers(candidate)
        evidence.support_module_count = self._count_support_modules(candidate)
        evidence.observed_activation_count = self._count_activations(candidate)
        evidence.inbound_feature_count = 0  # Set during linking.
        return evidence

    def _calculate_confidence(self, evidence: WorkspaceEvidence) -> float:
        weighted = 0.0
        for tag, weight in _EVIDENCE_WEIGHTS.items():
            if getattr(evidence, tag, False):
                weighted += weight

        weighted += evidence.ui_anchor_count * _UI_ANCHOR_BONUS
        weighted += evidence.controller_count * _CONTROLLER_BONUS
        weighted += evidence.support_module_count * _SUPPORT_MODULE_BONUS

        return math.tanh(weighted / 3.0)

    def _generate_aliases(self, candidate: FeatureCandidate) -> list:
        canonical = f"feature:{candidate.root_node_id}"
        digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:12]
        readable = candidate.root_node_id.replace("PECS_ID:", "").replace(".", "-")
        evidence_input = "".join(sorted(candidate.node_ids)) + "".join(
            sorted(candidate.edge_ids)
        )
        evidence_hash = hashlib.sha256(evidence_input.encode("utf-8")).hexdigest()[:16]
        return sorted(
            {
                canonical,
                f"f-{digest}",
                readable,
                f"fh-{evidence_hash}",
            }
        )

    def _link_infrastructure_to_features(
        self,
        registry: WorkspaceRegistry,
    ) -> None:
        """
        Record which user-facing features each infrastructure unit supports
        based on shared node membership.
        """
        for unit in registry.infrastructure_units.values():
            supported: Set[str] = set()
            for node_id in unit.node_ids:
                for entry_id in registry.node_index.get(node_id, set()):
                    if entry_id in registry.features:
                        supported.add(entry_id)
            unit.supported_features = supported
            unit.evidence.inbound_feature_count = len(supported)

    def _package_prefix(self, node_id: str) -> str:
        body = node_id[len("PECS_ID:") :] if node_id.startswith("PECS_ID:") else node_id
        parts = body.split(".")
        return parts[0] if parts else ""

    def _package_depth(self, node_id: str) -> int:
        body = node_id[len("PECS_ID:") :] if node_id.startswith("PECS_ID:") else node_id
        return len(body.split("."))

    def _count_ui_anchors(self, candidate: FeatureCandidate) -> int:
        # Approximate: nodes that are not module nodes and are owned by the
        # root module via UI edges.
        count = 0
        for node_id in candidate.node_ids:
            if not node_id.startswith("PECS_ID:"):
                continue
            # A simple heuristic: non-module nodes in the candidate set.
            # The exact count is not critical for confidence ordering.
            if ".action." in node_id or ".dialog." in node_id:
                count += 1
        return count

    def _count_controllers(self, candidate: FeatureCandidate) -> int:
        return 1 if "controller_ownership" in candidate.evidence_tags else 0

    def _count_support_modules(self, candidate: FeatureCandidate) -> int:
        return 1 if "import_export_locality" in candidate.evidence_tags else 0

    def _count_activations(self, candidate: FeatureCandidate) -> int:
        return 1 if "runtime_evidence" in candidate.evidence_tags else 0


def _workspace_hash(workspace_root: Path) -> str:
    path_bytes = str(workspace_root.resolve()).encode("utf-8")
    return hashlib.sha256(path_bytes).hexdigest()[:16]


def _deterministic_build_id(
    workspace_root: Path,
    node_count: int,
    edge_count: int,
) -> str:
    payload = f"{workspace_root.resolve()}|{node_count}|{edge_count}"
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
    return f"wr-{digest}"


def _utc_now() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
