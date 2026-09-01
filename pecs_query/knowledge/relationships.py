"""Deterministic relationship types for the Engineering Knowledge Layer.

Every relationship between knowledge objects has a canonical type, source,
target, evidence source, and confidence score.
"""

from __future__ import annotations

import enum
import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class RelationshipType(str, enum.Enum):
    """Canonical relationship types between engineering knowledge objects."""

    # ── structural ─────────────────────────────────────────────────
    CONTAINS = "contains"
    """Parent contains child (package → module, module → class)."""

    BELONGS_TO = "belongs_to"
    """Child belongs to parent (inverse of CONTAINS)."""

    # ── type hierarchy ─────────────────────────────────────────────
    INHERITS = "inherits"
    """Class inherits from another class."""

    IMPLEMENTS = "implements"
    """Class implements an interface."""

    # ── code dependencies ──────────────────────────────────────────
    IMPORTS = "imports"
    """Module imports another module."""

    REFERENCES = "references"
    """Code references another symbol."""

    CALLS = "calls"
    """Method/function calls another method/function."""

    DEPENDS_ON = "depends_on"
    """General dependency relationship."""

    # ── signal / slot ──────────────────────────────────────────────
    SIGNAL_SLOT = "signal_slot"
    """Signal connected to a slot."""

    CALLBACK_EXECUTION = "callback_execution"
    """Callback registered to execution path."""

    # ── ownership ──────────────────────────────────────────────────
    OWNS = "owns"
    """Owner relationship (qaction → dialog, module → subprocess)."""

    REGISTERS = "registers"
    """UI registration (module registers QAction)."""

    # ── runtime / activation ───────────────────────────────────────
    ACTIVATES = "activates"
    """Runtime object activates another."""

    RUNTIME_NEIGHBOR = "runtime_neighbor"
    """Objects are neighbours in runtime activation topology."""

    # ── topology ───────────────────────────────────────────────────
    TOPOLOGY_NEIGHBOR = "topology_neighbor"
    """Objects are neighbours in workspace topology."""

    CONTINUITY_NEIGHBOR = "continuity_neighbor"
    """Objects are neighbours in engineering continuity."""

    # ── documentation ──────────────────────────────────────────────
    DOCUMENTS = "documents"
    """Architecture document describes an object."""

    DOCUMENTED_BY = "documented_by"
    """Object is documented by an architecture document."""

    # ── validation ─────────────────────────────────────────────────
    VALIDATES = "validates"
    """Validation evidence confirms an object."""

    # ── fallback ───────────────────────────────────────────────────
    RELATED_TO = "related_to"
    """Generic related-to relationship."""


# ---------------------------------------------------------------------------
# Relationship model
# ---------------------------------------------------------------------------


@dataclass
class KnowledgeRelationship:
    """A deterministic relationship between two knowledge objects."""

    source_id: str = ""
    """PECS_ID of the source object."""

    target_id: str = ""
    """PECS_ID or external identifier of the target."""

    relationship_type: RelationshipType = RelationshipType.RELATED_TO
    """Canonical relationship type."""

    evidence: str = ""
    """How this relationship was derived:
    'graph_edge', 'registry_structure', 'runtime_activation', 'topology',
    'continuity', 'namespace_prefix', 'file_co_location', or 'manual'.
    """

    confidence: float = 1.0
    """Confidence in [0.0, 1.0]."""

    metadata: Dict[str, Any] = field(default_factory=dict)
    """Additional metadata (edge_id, source NodeType, etc.)."""

    def __post_init__(self) -> None:
        self.confidence = max(0.0, min(1.0, self.confidence))

    def relationship_id(self) -> str:
        """Deterministic ID for this relationship."""
        payload = f"{self.source_id}|{self.relationship_type.value}|{self.target_id}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "relationship_id": self.relationship_id(),
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relationship_type": self.relationship_type.value,
            "evidence": self.evidence,
            "confidence": self.confidence,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> KnowledgeRelationship:
        return cls(
            source_id=str(data.get("source_id", "")),
            target_id=str(data.get("target_id", "")),
            relationship_type=RelationshipType(
                data.get("relationship_type", "related_to")
            ),
            evidence=str(data.get("evidence", "")),
            confidence=float(data.get("confidence", 1.0)),
            metadata=dict(data.get("metadata", {})),
        )


# ---------------------------------------------------------------------------
# Convenience builders
# ---------------------------------------------------------------------------


def make_relationship(
    source_id: str,
    target_id: str,
    rel_type: RelationshipType,
    evidence: str = "",
    confidence: float = 1.0,
    **metadata: Any,
) -> KnowledgeRelationship:
    """Quick constructor for a KnowledgeRelationship."""
    return KnowledgeRelationship(
        source_id=source_id,
        target_id=target_id,
        relationship_type=rel_type,
        evidence=evidence,
        confidence=confidence,
        metadata=metadata,
    )
