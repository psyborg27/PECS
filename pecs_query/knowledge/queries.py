"""Deterministic knowledge access APIs for the Engineering Knowledge Layer.

These are NOT query-resolution APIs.  They are knowledge access APIs that
locate objects within the already-built knowledge base.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set

from pecs_query.knowledge.models import (
    ArchitectureDocumentKnowledge,
    ClassKnowledge,
    EngineeringConcept,
    EngineeringKnowledgeBase,
    FileKnowledge,
    MethodKnowledge,
    ModuleKnowledge,
    PackageKnowledge,
    RuntimeKnowledge,
)
from pecs_query.knowledge.relationships import (
    KnowledgeRelationship,
    RelationshipType,
)


class KnowledgeAccessAPI:
    """Deterministic access API over a built EngineeringKnowledgeBase."""

    def __init__(self, kb: EngineeringKnowledgeBase) -> None:
        self.kb = kb

    # ── find by PECS_ID ─────────────────────────────────────────────────

    def lookup_pecs_id(self, pecs_id: str) -> Optional[Dict[str, Any]]:
        """Look up any knowledge object by PECS_ID.

        Returns the object's ``to_dict()`` or ``None`` if not found.
        """
        if pecs_id in self.kb.packages:
            return self.kb.packages[pecs_id].to_dict()
        if pecs_id in self.kb.modules:
            return self.kb.modules[pecs_id].to_dict()
        if pecs_id in self.kb.classes:
            return self.kb.classes[pecs_id].to_dict()
        if pecs_id in self.kb.methods:
            return self.kb.methods[pecs_id].to_dict()
        if pecs_id in self.kb.runtime_objects:
            return self.kb.runtime_objects[pecs_id].to_dict()
        return None

    def pecs_id_type(self, pecs_id: str) -> Optional[str]:
        """Return the type tag for a PECS_ID ('module', 'class', etc.)."""
        return self.kb.pecs_id_index.get(pecs_id)

    # ── find by name / alias ────────────────────────────────────────────

    def find_package(self, name: str) -> Optional[PackageKnowledge]:
        """Find a package by exact name."""
        return self.kb.packages.get(name)

    def find_module(self, name: str) -> Optional[ModuleKnowledge]:
        """Find a module by exact PECS_ID."""
        return self.kb.modules.get(name)

    def find_file(self, file_path: str) -> Optional[FileKnowledge]:
        """Find a file by relative path."""
        return self.kb.files.get(file_path)

    def find_class(self, pecs_id: str) -> Optional[ClassKnowledge]:
        """Find a class by PECS_ID."""
        return self.kb.classes.get(pecs_id)

    def find_method(self, pecs_id: str) -> Optional[MethodKnowledge]:
        """Find a method/function by PECS_ID."""
        return self.kb.methods.get(pecs_id)

    def find_runtime_object(
        self, pecs_id: str
    ) -> Optional[RuntimeKnowledge]:
        """Find a runtime object by PECS_ID."""
        return self.kb.runtime_objects.get(pecs_id)

    def find_architecture_document(
        self, file_path: str
    ) -> Optional[ArchitectureDocumentKnowledge]:
        """Find an architecture document by file path."""
        return self.kb.arch_documents.get(file_path)

    def resolve_alias(self, alias: str) -> Optional[str]:
        """Resolve an alias/short name to a canonical PECS_ID."""
        return self.kb.alias_index.get(alias)

    # ── relationships ──────────────────────────────────────────────────

    def find_relationships(
        self,
        pecs_id: str,
        rel_type: Optional[RelationshipType] = None,
    ) -> List[KnowledgeRelationship]:
        """Find all relationships involving a PECS_ID, optionally filtered
        by relationship type."""
        results: List[KnowledgeRelationship] = []
        for rel in self.kb.relationships:
            if (
                rel.source_id == pecs_id or rel.target_id == pecs_id
            ):
                if rel_type is None or rel.relationship_type == rel_type:
                    results.append(rel)
        return results

    def find_outgoing(
        self, pecs_id: str, rel_type: Optional[RelationshipType] = None
    ) -> List[KnowledgeRelationship]:
        """Find relationships where the given PECS_ID is the source."""
        results: List[KnowledgeRelationship] = []
        for rel in self.kb.relationships:
            if rel.source_id == pecs_id:
                if rel_type is None or rel.relationship_type == rel_type:
                    results.append(rel)
        return results

    def find_incoming(
        self, pecs_id: str, rel_type: Optional[RelationshipType] = None
    ) -> List[KnowledgeRelationship]:
        """Find relationships where the given PECS_ID is the target."""
        results: List[KnowledgeRelationship] = []
        for rel in self.kb.relationships:
            if rel.target_id == pecs_id:
                if rel_type is None or rel.relationship_type == rel_type:
                    results.append(rel)
        return results

    def find_neighbors(
        self,
        pecs_id: str,
        rel_type: Optional[RelationshipType] = None,
    ) -> List[str]:
        """Find neighbor PECS_IDs (both incoming and outgoing)."""
        seen: Set[str] = set()
        for rel in self.kb.relationships:
            if rel_type is None or rel.relationship_type == rel_type:
                if rel.source_id == pecs_id:
                    seen.add(rel.target_id)
                elif rel.target_id == pecs_id:
                    seen.add(rel.source_id)
        return sorted(seen)

    # ── concepts ────────────────────────────────────────────────────────

    def concepts_for_pecs_id(self, pecs_id: str) -> List[EngineeringConcept]:
        """Find all engineering concepts that include this PECS ID.

        Engineering concepts are populated by the Ontology stage
        (Phase 2C).  Until then this returns an empty list.
        """
        return []

    # ── statistics ──────────────────────────────────────────────────────

    def statistics(self) -> Dict[str, int]:
        """Return knowledge base statistics."""
        return self.kb.statistics()
