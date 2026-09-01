"""Deterministic ontology query APIs for the Engineering Ontology.

These APIs expose ontology data only.  They do not perform query resolution.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pecs_query.ontology.models import (
    ConceptRelationshipType,
    EngineeringOntology,
    OntologyConcept,
    OntologyConceptRelationship,
    OntologyStatistics,
)


class OntologyQueryAPI:
    """Deterministic query API over a built EngineeringOntology."""

    def __init__(self, ontology: EngineeringOntology) -> None:
        self.ontology = ontology

    # ── concept lookup ───────────────────────────────────────────────────

    def find_concept(self, concept_id: str) -> Optional[OntologyConcept]:
        """Find a concept by its canonical concept_id."""
        return self.ontology.concepts.get(concept_id)

    def lookup_alias(self, alias: str) -> List[OntologyConcept]:
        """Resolve an alias to its matching concepts."""
        concept_ids = self.ontology.alias_index.get(alias, [])
        return [
            self.ontology.concepts[cid]
            for cid in concept_ids
            if cid in self.ontology.concepts
        ]

    def lookup_canonical(self, canonical_name: str) -> List[OntologyConcept]:
        """Find all concepts with the given canonical_name."""
        cid = _make_concept_id(canonical_name)
        concept = self.ontology.concepts.get(cid)
        if concept:
            return [concept]
        return []

    def lookup_by_object(self, pecs_id: str) -> List[OntologyConcept]:
        """Find all concepts that contain the given PECS_ID."""
        concept_ids = self.ontology.pecs_id_index.get(pecs_id, [])
        return [
            self.ontology.concepts[cid]
            for cid in concept_ids
            if cid in self.ontology.concepts
        ]

    def lookup_by_pecs_id(self, pecs_id: str) -> List[OntologyConcept]:
        """Alias for lookup_by_object."""
        return self.lookup_by_object(pecs_id)

    # ── relationship queries ─────────────────────────────────────────────

    def related_concepts(self, concept_id: str) -> List[OntologyConcept]:
        """Find all concepts related to the given concept."""
        related_ids: set = set()
        for rel in self.ontology.concept_relationships:
            if rel.source_concept_id == concept_id:
                related_ids.add(rel.target_concept_id)
            elif rel.target_concept_id == concept_id:
                related_ids.add(rel.source_concept_id)
        return [
            self.ontology.concepts[cid]
            for cid in related_ids
            if cid in self.ontology.concepts
        ]

    def relationships_for_concept(
        self, concept_id: str
    ) -> List[OntologyConceptRelationship]:
        """Find all relationships involving a concept."""
        return [
            rel
            for rel in self.ontology.concept_relationships
            if rel.source_concept_id == concept_id
            or rel.target_concept_id == concept_id
        ]

    # ── search ───────────────────────────────────────────────────────────

    def search_prefix(self, prefix: str) -> List[OntologyConcept]:
        """Search concepts whose concept_id starts with the given prefix."""
        prefix = prefix.lower()
        return [
            c
            for cid, c in self.ontology.concepts.items()
            if cid.startswith(prefix)
        ]

    def search_exact(self, name: str) -> Optional[OntologyConcept]:
        """Find a concept by exact name or alias match."""
        # Try direct concept_id lookup
        cid = _make_concept_id(name)
        if cid in self.ontology.concepts:
            return self.ontology.concepts[cid]
        # Try alias lookup — return first match
        concepts = self.lookup_alias(name)
        if concepts:
            return concepts[0]
        return None

    # ── diagnostics ──────────────────────────────────────────────────────

    def statistics(self) -> OntologyStatistics:
        """Return ontology diagnostic statistics."""
        return self.ontology.statistics()

    def concept_count(self) -> int:
        return len(self.ontology.concepts)

    def alias_count(self) -> int:
        return len(self.ontology.alias_index)

    def relationship_count(self) -> int:
        return len(self.ontology.concept_relationships)


def _make_concept_id(name: str) -> str:
    """Create a deterministic concept_id from a name (mirrors builder logic)."""
    import re
    return re.sub(r"[^a-z0-9_]", "", name.lower().replace(" ", "_").replace("-", "_"))
