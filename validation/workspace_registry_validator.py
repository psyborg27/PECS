from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from execution_graph.graph.workspace_graph import Graph, NodeType
from workspace_registry.models import WorkspaceRegistry


@dataclass
class WorkspaceRegistryValidationReport:
    """Result of validating a Workspace Registry against its Workspace Graph."""

    valid: bool = False
    registry_hash: str = ""
    registry_hash_stable: bool = False
    mismatches: List[str] = field(default_factory=list)
    coverage_summary: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "valid": self.valid,
            "registry_hash": self.registry_hash,
            "registry_hash_stable": self.registry_hash_stable,
            "mismatch_count": len(self.mismatches),
            "mismatches": self.mismatches,
            "coverage_summary": self.coverage_summary,
        }


class WorkspaceRegistryValidator:
    """
    Validate that a Workspace Registry covers its Workspace Graph.

    Checks are advisory and do not raise.
    """

    def validate(
        self,
        registry: WorkspaceRegistry,
        graph: Graph,
    ) -> WorkspaceRegistryValidationReport:
        mismatches: List[str] = []

        module_nodes = {
            node_id
            for node_id, node in graph.nodes.items()
            if node.node_type == NodeType.MODULE
        }

        covered_nodes: Set[str] = set()
        for feature in registry.features.values():
            covered_nodes.update(feature.node_ids)
        for unit in registry.infrastructure_units.values():
            covered_nodes.update(unit.node_ids)

        uncovered = module_nodes - covered_nodes
        if uncovered:
            sample = sorted(uncovered)[:5]
            mismatches.append(
                f"module nodes not covered by any feature or unit: {sample}"
            )

        orphan_ui = self._find_orphan_ui_nodes(graph, covered_nodes)
        if orphan_ui:
            sample = sorted(orphan_ui)[:5]
            mismatches.append(f"UI anchor nodes not covered: {sample}")

        hash_stable = self._validate_hash_stability(registry)

        report = WorkspaceRegistryValidationReport(
            valid=len(mismatches) == 0,
            registry_hash=registry.metadata.registry_hash,
            registry_hash_stable=hash_stable,
            mismatches=mismatches,
            coverage_summary={
                "module_nodes": len(module_nodes),
                "covered_nodes": len(covered_nodes),
                "uncovered_nodes": len(uncovered),
                "feature_count": len(registry.features),
                "infrastructure_unit_count": len(registry.infrastructure_units),
            },
        )
        return report

    def _find_orphan_ui_nodes(
        self,
        graph: Graph,
        covered_nodes: Set[str],
    ) -> Set[str]:
        ui_types = {
            "qaction",
            "menu",
            "toolbar",
            "dialog",
            "viewer",
            "overlay",
        }
        orphans: Set[str] = set()
        for node_id, node in graph.nodes.items():
            if node.node_type.value in ui_types and node_id not in covered_nodes:
                orphans.add(node_id)
        return orphans

    def _validate_hash_stability(self, registry: WorkspaceRegistry) -> bool:
        original = registry.metadata.registry_hash
        registry.update_registry_hash()
        return registry.metadata.registry_hash == original and bool(original)
