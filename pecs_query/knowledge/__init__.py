"""Engineering Knowledge Layer for PECS.

This package provides the canonical deterministic engineering knowledge model
for a PECS workspace.  It is built entirely from existing PECS artifacts
(Workspace Graph, Workspace Registry, runtime locality/topology) without
repository rescans or duplicate indexes.

Components
----------
- models: canonical knowledge model dataclasses
- relationships: deterministic relationship types and model
- builder: EngineeringKnowledgeBuilder — builds the knowledge base from PECS artifacts
- queries: deterministic knowledge access APIs (find, lookup, search)
"""

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
from pecs_query.knowledge.builder import (
    EngineeringKnowledgeBuilder,
    build_knowledge_base,
)
from pecs_query.knowledge.queries import (
    KnowledgeAccessAPI,
)

__all__ = [
    "EngineeringKnowledgeBase",
    "EngineeringKnowledgeBuilder",
    "build_knowledge_base",
    "KnowledgeAccessAPI",
    "PackageKnowledge",
    "ModuleKnowledge",
    "FileKnowledge",
    "ClassKnowledge",
    "MethodKnowledge",
    "RuntimeKnowledge",
    "ArchitectureDocumentKnowledge",
    "EngineeringConcept",
    "KnowledgeRelationship",
    "RelationshipType",
]
