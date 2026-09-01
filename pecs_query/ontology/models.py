"""Canonical ontology models for the PECS Engineering Ontology.

Every concept, alias, and relationship is derived deterministically from
existing PECS artifacts.  No NLP, embeddings, or probabilistic inference.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set


# ====================================================================
# Ontology Concept
# ====================================================================


@dataclass
class OntologyConcept:
    """A canonical engineering concept derived from repository knowledge.

    Each concept represents a named engineering idea (e.g. 'ocr_pipeline',
    'notes_canvas', 'bulktocmapper') and is tied to one or more PECS_IDs.
    """

    concept_id: str = ""
    """Canonical identifier (lowercase, underscore-separated)."""

    canonical_name: str = ""
    """Primary human-readable name."""

    aliases: List[str] = field(default_factory=list)
    """All known aliases for this concept."""

    engineering_object_ids: List[str] = field(default_factory=list)
    """PECS_IDs that belong to this concept."""

    object_types: List[str] = field(default_factory=list)
    """EngineeringObjectType values for the associated objects."""

    confidence: float = 1.0
    """Confidence that this concept is correctly identified in [0.0, 1.0]."""

    provenance: str = ""
    """How this concept was derived: 'package', 'module', 'class', 'method',
    'feature', 'file', 'pecs_id', 'architecture_document', or 'alias'."""

    documentation: str = ""
    """Human-readable description (empty by default; populated by later stages)."""

    metadata: Dict[str, Any] = field(default_factory=dict)
    """Additional metadata (source KnowledgeBase object key, etc.)."""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "concept_id": self.concept_id,
            "canonical_name": self.canonical_name,
            "aliases": sorted(self.aliases),
            "engineering_object_ids": sorted(self.engineering_object_ids),
            "object_types": sorted(self.object_types),
            "confidence": self.confidence,
            "provenance": self.provenance,
            "documentation": self.documentation,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> OntologyConcept:
        return cls(
            concept_id=str(data.get("concept_id", "")),
            canonical_name=str(data.get("canonical_name", "")),
            aliases=list(data.get("aliases", [])),
            engineering_object_ids=list(data.get("engineering_object_ids", [])),
            object_types=list(data.get("object_types", [])),
            confidence=float(data.get("confidence", 1.0)),
            provenance=str(data.get("provenance", "")),
            documentation=str(data.get("documentation", "")),
            metadata=dict(data.get("metadata", {})),
        )


# ====================================================================
# Ontology Relationship
# ====================================================================


class ConceptRelationshipType(str):
    """Canonical ontology relationship types between concepts."""

    SYNONYM = "synonym"
    PARENT = "parent"
    CHILD = "child"
    RELATED = "related"
    CONTAINS = "contains"
    BELONGS_TO = "belongs_to"
    REFERENCES = "references"
    ARCHITECTURE_REFERENCE = "architecture_reference"
    RUNTIME_REFERENCE = "runtime_reference"
    SAME_AS = "same_as"


@dataclass
class OntologyConceptRelationship:
    """A deterministic relationship between two ontology concepts."""

    source_concept_id: str = ""
    """Concept ID of the source."""

    target_concept_id: str = ""
    """Concept ID of the target."""

    relationship_type: str = ConceptRelationshipType.RELATED
    """Canonical relationship type."""

    evidence: str = ""
    """How this relationship was derived: 'knowledge_relationship',
    'alias_overlap', 'name_prefix', 'same_provenance', or 'manual'."""

    confidence: float = 1.0
    """Confidence in [0.0, 1.0]."""

    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.confidence = max(0.0, min(1.0, self.confidence))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_concept_id": self.source_concept_id,
            "target_concept_id": self.target_concept_id,
            "relationship_type": self.relationship_type,
            "evidence": self.evidence,
            "confidence": self.confidence,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> OntologyConceptRelationship:
        return cls(
            source_concept_id=str(data.get("source_concept_id", "")),
            target_concept_id=str(data.get("target_concept_id", "")),
            relationship_type=str(
                data.get("relationship_type", ConceptRelationshipType.RELATED)
            ),
            evidence=str(data.get("evidence", "")),
            confidence=float(data.get("confidence", 1.0)),
            metadata=dict(data.get("metadata", {})),
        )


# ====================================================================
# Engineering Ontology — top-level container
# ====================================================================


@dataclass
class EngineeringOntology:
    """Canonical deterministic engineering ontology for a PECS workspace.

    Built by :class:`OntologyBuilder` from the EngineeringKnowledgeBase.
    This is the authoritative vocabulary consumed by the Object Resolver.
    """

    # ── concepts and aliases ─────────────────────────────────────────────

    concepts: Dict[str, OntologyConcept] = field(default_factory=dict)
    """All concepts, keyed by concept_id."""

    alias_index: Dict[str, List[str]] = field(default_factory=dict)
    """Maps every alias to the list of concept_ids that match it."""

    # ── relationships ────────────────────────────────────────────────────

    concept_relationships: List[OntologyConceptRelationship] = field(
        default_factory=list
    )
    """Relationships between concepts."""

    # ── PECS ID index ────────────────────────────────────────────────────

    pecs_id_index: Dict[str, List[str]] = field(default_factory=dict)
    """Maps every PECS_ID to the list of concept_ids that contain it."""

    # ── diagnostics ──────────────────────────────────────────────────────

    build_diagnostics: Dict[str, Any] = field(default_factory=dict)
    """Builder metadata: sources consumed, counts, coverage."""

    # ── public helpers ───────────────────────────────────────────────────

    def statistics(self) -> OntologyStatistics:
        """Return ontology statistics."""
        orphans = [
            cid for cid, c in self.concepts.items()
            if not c.engineering_object_ids
        ]
        return OntologyStatistics(
            concept_count=len(self.concepts),
            alias_count=len(self.alias_index),
            relationship_count=len(self.concept_relationships),
            orphan_count=len(orphans),
            provenance_coverage=self._provenance_coverage(),
        )

    def ontology_hash(self) -> str:
        """Deterministic SHA-256 hash of ontology content."""
        payload = json.dumps(self.to_dict(), sort_keys=True, default=str)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "concept_count": len(self.concepts),
            "alias_count": len(self.alias_index),
            "relationship_count": len(self.concept_relationships),
            "build_diagnostics": dict(self.build_diagnostics),
        }

    def _provenance_coverage(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for concept in self.concepts.values():
            prov = concept.provenance or "unknown"
            counts[prov] = counts.get(prov, 0) + 1
        return counts


# ====================================================================
# Statistics
# ====================================================================


@dataclass
class OntologyStatistics:
    """Ontology diagnostic statistics."""

    concept_count: int = 0
    alias_count: int = 0
    relationship_count: int = 0
    orphan_count: int = 0
    provenance_coverage: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "concept_count": self.concept_count,
            "alias_count": self.alias_count,
            "relationship_count": self.relationship_count,
            "orphan_count": self.orphan_count,
            "provenance_coverage": dict(self.provenance_coverage),
        }
