from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from navigation_builder.models import NavigationGraph


@dataclass
class NavigationBuilderValidationReport:
    """Validation report for a Navigation Graph."""

    valid: bool = False
    mismatches: List[str] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "valid": self.valid,
            "mismatch_count": len(self.mismatches),
            "mismatches": self.mismatches,
            "summary": self.summary,
        }


class NavigationBuilderValidator:
    """
    Validate structural integrity of a Navigation Graph.

    Checks are deterministic and advisory.
    """

    def validate(
        self,
        nav_graph: NavigationGraph,
        expected_query_terms: List[str],
        max_nodes: int,
    ) -> NavigationBuilderValidationReport:
        mismatches: List[str] = []

        if sorted(nav_graph.query_terms) != sorted(expected_query_terms):
            mismatches.append(
                f"query_terms mismatch: {nav_graph.query_terms}"
            )

        if len(nav_graph.nodes) > max_nodes:
            mismatches.append(
                f"node count {len(nav_graph.nodes)} exceeds max {max_nodes}"
            )

        for node_id, node in nav_graph.nodes.items():
            if node.line_range.start > node.line_range.end:
                mismatches.append(
                    f"node {node_id} has invalid line range "
                    f"{node.line_range.start}-{node.line_range.end}"
                )
            if node.line_range.start < 1:
                mismatches.append(
                    f"node {node_id} has non-positive start line"
                )

        for edge in nav_graph.edges.values():
            if edge.source_id not in nav_graph.nodes:
                mismatches.append(
                    f"edge {edge.edge_id} references missing source"
                )
            if edge.target_id not in nav_graph.nodes:
                mismatches.append(
                    f"edge {edge.edge_id} references missing target"
                )

        summary = {
            "node_count": len(nav_graph.nodes),
            "edge_count": len(nav_graph.edges),
            "query_term_count": len(nav_graph.query_terms),
        }

        return NavigationBuilderValidationReport(
            valid=len(mismatches) == 0,
            mismatches=mismatches,
            summary=summary,
        )
