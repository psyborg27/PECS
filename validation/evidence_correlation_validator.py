from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from evidence_correlation.models import CorrelationResult


@dataclass
class EvidenceCorrelationValidationReport:
    """Validation report for an Evidence Correlation result."""

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


class EvidenceCorrelationValidator:
    """
    Validate structural integrity of Evidence Correlation results.

    Checks are deterministic and advisory.
    """

    def validate(
        self,
        result: CorrelationResult,
        max_clusters: int,
    ) -> EvidenceCorrelationValidationReport:
        mismatches: List[str] = []

        if not result.query_terms:
            mismatches.append("query_terms is empty")

        if len(result.clusters) > max_clusters:
            mismatches.append(
                f"cluster count {len(result.clusters)} exceeds max {max_clusters}"
            )

        for index, cluster in enumerate(result.clusters):
            if not cluster.cluster_id:
                mismatches.append(f"cluster {index} missing cluster_id")
            if not cluster.primary_namespace:
                mismatches.append(f"cluster {index} missing primary_namespace")
            if not cluster.root_package:
                mismatches.append(f"cluster {index} missing root_package")
            if cluster.cumulative_correlation_score < 0.0:
                mismatches.append(
                    f"cluster {index} has negative score"
                )

        # Ensure clusters are sorted by descending score.
        scores = [cluster.cumulative_correlation_score for cluster in result.clusters]
        if scores != sorted(scores, reverse=True):
            mismatches.append("clusters are not sorted by descending score")

        summary = {
            "query_term_count": len(result.query_terms),
            "cluster_count": len(result.clusters),
            "top_score": result.clusters[0].cumulative_correlation_score
            if result.clusters
            else 0.0,
        }

        return EvidenceCorrelationValidationReport(
            valid=len(mismatches) == 0,
            mismatches=mismatches,
            summary=summary,
        )
