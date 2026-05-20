from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from ..retrieval.topology_retriever import (
    TopologyRetriever,
)


@dataclass
class CompactContextBuilder:
    """
    Consolidated compact continuity reconstruction builder.

    This intentionally consolidates:
    - compact context generation
    - locality compression
    - minimal continuity reconstruction
    - token-budget-aware continuity export
    - execution-local context shaping

    into ONE authority module.

    PECS intentionally avoids:
    - summarization forests
    - compression middleware
    - recursive context pipelines
    - layered export coordinators

    The builder remains:
    probabilistic
    locality-oriented
    topology-aware
    low-token
    continuity-safe
    """

    topology_retriever: TopologyRetriever

    default_locality_limit: int = 12

    builder_metadata: Dict[str, object] = field(default_factory=dict)

    def build_compact_object_context(
        self,
        object_id: str,
        locality_limit: Optional[int] = None,
        continuity_signals: Optional[Dict[str, object]] = None,
    ) -> Dict[str, object]:
        retrieval = self.topology_retriever.retrieve_continuity_context(
            object_id=object_id,
            continuity_signals=continuity_signals,
        )

        limit = (
            locality_limit
            if locality_limit is not None
            else self.default_locality_limit
        )

        compact_anchors = retrieval["anchors"][:limit]

        return {
            "object_id": object_id,
            "anchors": compact_anchors,
            "locality": compact_anchors,
            "confidence": retrieval["scores"]["confidence"],
            "retrieval_score": retrieval["scores"],
            "duplicate_lineages": retrieval["duplicate_lineages"],
            "token_estimate": retrieval["token_estimate"],
            "anchor_count": len(compact_anchors),
            "retrieval_metadata": retrieval,
        }

    def build_multi_object_context(
        self,
        object_ids: List[str],
        locality_limit: Optional[int] = None,
    ) -> Dict[str, object]:
        compact_contexts = []

        for object_id in object_ids:
            compact_contexts.append(
                self.build_compact_object_context(
                    object_id=object_id,
                    locality_limit=locality_limit,
                )
            )

        return {
            "contexts": compact_contexts,
            "context_count": len(compact_contexts),
        }

    def build_execution_local_context(
        self,
        object_id: str,
        path_id: str,
        locality_limit: Optional[int] = None,
        continuity_signals: Optional[Dict[str, object]] = None,
    ) -> Dict[str, object]:
        retrieval = self.topology_retriever.retrieve_continuity_context(
            object_id=object_id,
            path_id=path_id,
            continuity_signals=continuity_signals,
        )

        limit = (
            locality_limit
            if locality_limit is not None
            else self.default_locality_limit
        )

        compact_anchors = retrieval["anchors"][:limit]

        return {
            "object_id": object_id,
            "execution_path": path_id,
            "anchors": compact_anchors,
            "execution_locality": retrieval["execution_locality"][:limit],
            "locality": compact_anchors,
            "confidence": retrieval["scores"]["confidence"],
            "retrieval_score": retrieval["scores"],
            "duplicate_lineages": retrieval["duplicate_lineages"],
            "token_estimate": retrieval["token_estimate"],
            "retrieval_metadata": retrieval,
        }

    def export_low_token_bundle(
        self,
        object_ids: List[str],
    ) -> Dict[str, object]:
        bundle = self.build_multi_object_context(
            object_ids=object_ids,
            locality_limit=self.default_locality_limit,
        )

        return {
            "bundle_type": "low_token_continuity",
            "bundle": bundle,
        }

    def to_dict(self) -> Dict[str, object]:
        return {
            "default_locality_limit": (self.default_locality_limit),
            "builder_metadata": self.builder_metadata,
        }
