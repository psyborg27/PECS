"""Canonical engineering knowledge models for PECS.

Each model contains only canonical engineering information derived from
existing PECS artifacts.  No query-specific state or discovery logic.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from pecs_query.engineering_objects import EngineeringObjectType
from pecs_query.knowledge.relationships import (
    KnowledgeRelationship,
    RelationshipType,
)


# ====================================================================
# Engineering Knowledge Base — top-level container
# ====================================================================


@dataclass
class EngineeringKnowledgeBase:
    """Canonical deterministic engineering knowledge for a PECS workspace.

    Built by :class:`EngineeringKnowledgeBuilder` from existing PECS
    artifacts.  This is the single authoritative knowledge model consumed
    by the Ontology, Object Resolver, Authority Engine, and Projection
    Engine.
    """

    # ── top-level knowledge ────────────────────────────────────────────

    repository: Optional[RepositoryKnowledge] = None
    """Repository-level metadata."""

    workspace: Optional[WorkspaceKnowledge] = None
    """Workspace-level knowledge."""

    # ── source organisation ────────────────────────────────────────────

    packages: Dict[str, PackageKnowledge] = field(default_factory=dict)
    """All discovered packages, keyed by package name."""

    modules: Dict[str, ModuleKnowledge] = field(default_factory=dict)
    """All discovered modules, keyed by PECS_ID."""

    files: Dict[str, FileKnowledge] = field(default_factory=dict)
    """All discovered source files, keyed by relative file path."""

    # ── structural types ───────────────────────────────────────────────

    classes: Dict[str, ClassKnowledge] = field(default_factory=dict)
    """All discovered classes, keyed by PECS_ID."""

    methods: Dict[str, MethodKnowledge] = field(default_factory=dict)
    """All discovered methods/functions, keyed by PECS_ID."""

    # ── runtime / architecture ─────────────────────────────────────────

    runtime_objects: Dict[str, RuntimeKnowledge] = field(default_factory=dict)
    """All discovered runtime objects (QAction, Signal, Slot, etc.), keyed by PECS_ID."""

    arch_documents: Dict[str, ArchitectureDocumentKnowledge] = field(
        default_factory=dict
    )
    """Architecture documents discovered in the workspace."""

    # ── relationships ──────────────────────────────────────────────────

    relationships: List[KnowledgeRelationship] = field(default_factory=list)
    """All deterministic relationships between knowledge objects."""

    # ── cross-reference indexes ─────────────────────────────────────────

    pecs_id_index: Dict[str, str] = field(default_factory=dict)
    """Maps every PECS_ID to its knowledge object type tag
    ('package', 'module', 'file', 'class', 'method', 'runtime')."""

    alias_index: Dict[str, str] = field(default_factory=dict)
    """Maps aliases/short names to the canonical PECS_ID."""

    # ── diagnostics ────────────────────────────────────────────────────

    build_diagnostics: Dict[str, Any] = field(default_factory=dict)
    """Builder metadata: sources consumed, counts, coverage."""

    # ── public helpers ─────────────────────────────────────────────────

    def to_dict(self) -> Dict[str, Any]:
        return {
            "repository": self.repository.to_dict() if self.repository else None,
            "workspace": self.workspace.to_dict() if self.workspace else None,
            "package_count": len(self.packages),
            "module_count": len(self.modules),
            "file_count": len(self.files),
            "class_count": len(self.classes),
            "method_count": len(self.methods),
            "runtime_object_count": len(self.runtime_objects),
            "arch_document_count": len(self.arch_documents),
            "relationship_count": len(self.relationships),
            "pecs_id_count": len(self.pecs_id_index),
            "alias_count": len(self.alias_index),
            "build_diagnostics": dict(self.build_diagnostics),
        }

    def knowledge_hash(self) -> str:
        """Deterministic SHA-256 hash of the knowledge base content."""
        payload = json.dumps(self.to_dict(), sort_keys=True, default=str)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]

    def statistics(self) -> Dict[str, int]:
        """Return object and relationship counts."""
        return {
            "packages": len(self.packages),
            "modules": len(self.modules),
            "files": len(self.files),
            "classes": len(self.classes),
            "methods": len(self.methods),
            "runtime_objects": len(self.runtime_objects),
            "arch_documents": len(self.arch_documents),
            "relationships": len(self.relationships),
            "pecs_ids": len(self.pecs_id_index),
            "aliases": len(self.alias_index),
        }


# ====================================================================
# Top-level knowledge
# ====================================================================


@dataclass
class RepositoryKnowledge:
    """Repository-level knowledge."""

    name: str = ""
    """Repository name or identifier."""

    workspace_root: str = ""
    """Absolute path to the workspace root."""

    graph_hash: str = ""
    """SHA-256 hash of the workspace graph."""

    registry_hash: str = ""
    """SHA-256 hash of the workspace registry."""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "workspace_root": self.workspace_root,
            "graph_hash": self.graph_hash,
            "registry_hash": self.registry_hash,
        }


@dataclass
class WorkspaceKnowledge:
    """Workspace-level knowledge derived from the graph and registry."""

    node_count: int = 0
    edge_count: int = 0
    zone_count: int = 0
    cluster_count: int = 0
    entrypoint_count: int = 0

    feature_count: int = 0
    infrastructure_unit_count: int = 0

    zones: List[str] = field(default_factory=list)
    node_types: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "zone_count": self.zone_count,
            "cluster_count": self.cluster_count,
            "entrypoint_count": self.entrypoint_count,
            "feature_count": self.feature_count,
            "infrastructure_unit_count": self.infrastructure_unit_count,
            "zones": sorted(self.zones),
            "node_types": dict(self.node_types),
        }


# ====================================================================
# Source organisation
# ====================================================================


@dataclass
class PackageKnowledge:
    """Knowledge about a package (first segment of a PECS_ID)."""

    name: str = ""
    """Package name."""

    pecs_ids: List[str] = field(default_factory=list)
    """All PECS_IDs belonging to this package."""

    module_count: int = 0
    file_count: int = 0
    class_count: int = 0
    method_count: int = 0

    is_user_facing: bool = False
    """Whether the registry classifies this package as user-facing."""

    feature_id: str = ""
    """If this package maps to a WorkspaceFeature, its feature_id."""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "pecs_ids": list(self.pecs_ids),
            "module_count": self.module_count,
            "file_count": self.file_count,
            "class_count": self.class_count,
            "method_count": self.method_count,
            "is_user_facing": self.is_user_facing,
            "feature_id": self.feature_id,
        }


@dataclass
class ModuleKnowledge:
    """Knowledge about a module (PECS_ID with a MODULE node type)."""

    pecs_id: str = ""
    """Canonical PECS_ID."""

    module_path: str = ""
    """Dotted module path."""

    node_type: str = ""
    """The NodeType value."""

    source_file: str = ""
    """Relative source file path."""

    execution_zone: str = ""
    """Runtime execution zone."""

    authority_level: str = ""
    """Authority level from the graph."""

    confidence: float = 0.0
    """Confidence from the graph."""

    class_names: List[str] = field(default_factory=list)
    """Classes defined in this module."""

    method_names: List[str] = field(default_factory=list)
    """Methods/functions defined in this module."""

    line_count: int = 0
    """Line count of the source file."""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pecs_id": self.pecs_id,
            "module_path": self.module_path,
            "node_type": self.node_type,
            "source_file": self.source_file,
            "execution_zone": self.execution_zone,
            "authority_level": self.authority_level,
            "confidence": self.confidence,
            "class_names": sorted(self.class_names),
            "method_names": sorted(self.method_names),
            "line_count": self.line_count,
        }


@dataclass
class FileKnowledge:
    """Knowledge about a source file."""

    file_path: str = ""
    """Workspace-relative file path."""

    pecs_ids: List[str] = field(default_factory=list)
    """PECS_IDs belonging to this file."""

    module_paths: List[str] = field(default_factory=list)
    """Module paths discovered in this file."""

    class_names: List[str] = field(default_factory=list)
    """Class names defined in this file."""

    method_names: List[str] = field(default_factory=list)
    """Method/function names defined in this file."""

    line_count: int = 0
    """Total line count."""

    runtime_zone: str = ""
    """Runtime zone if this file has one."""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "pecs_ids": sorted(self.pecs_ids),
            "module_paths": sorted(self.module_paths),
            "class_names": sorted(self.class_names),
            "method_names": sorted(self.method_names),
            "line_count": self.line_count,
            "runtime_zone": self.runtime_zone,
        }


# ====================================================================
# Structural types
# ====================================================================


@dataclass
class ClassKnowledge:
    """Knowledge about a class."""

    pecs_id: str = ""
    """Canonical PECS_ID."""

    class_name: str = ""
    """Class name."""

    module_path: str = ""
    """Dotted module path containing this class."""

    source_file: str = ""
    """Relative source file path."""

    method_names: List[str] = field(default_factory=list)
    """Methods defined in this class."""

    execution_zone: str = ""
    """Runtime zone from the graph."""

    authority_level: str = ""
    """Authority level."""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pecs_id": self.pecs_id,
            "class_name": self.class_name,
            "module_path": self.module_path,
            "source_file": self.source_file,
            "method_names": sorted(self.method_names),
            "execution_zone": self.execution_zone,
            "authority_level": self.authority_level,
        }


@dataclass
class MethodKnowledge:
    """Knowledge about a method or function."""

    pecs_id: str = ""
    """Canonical PECS_ID."""

    method_name: str = ""
    """Method/function name."""

    class_name: str = ""
    """Containing class name (empty for module-level functions)."""

    module_path: str = ""
    """Dotted module path."""

    source_file: str = ""
    """Relative source file path."""

    execution_zone: str = ""
    """Runtime zone."""

    authority_level: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pecs_id": self.pecs_id,
            "method_name": self.method_name,
            "class_name": self.class_name,
            "module_path": self.module_path,
            "source_file": self.source_file,
            "execution_zone": self.execution_zone,
            "authority_level": self.authority_level,
        }


# ====================================================================
# Runtime / architecture
# ====================================================================


@dataclass
class RuntimeKnowledge:
    """Knowledge about a runtime object (QAction, Signal, Slot, etc.)."""

    pecs_id: str = ""
    """Canonical PECS_ID."""

    node_type: str = ""
    """The runtime NodeType value."""

    canonical_name: str = ""
    """Short canonical name."""

    module_path: str = ""
    """Dotted module path."""

    source_file: str = ""
    """Relative source file path."""

    execution_zone: str = ""
    """Runtime execution zone."""

    runtime_owner: str = ""
    """Owner PECS_ID if known."""

    is_active: bool = False
    """Whether the object has been observed as active."""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pecs_id": self.pecs_id,
            "node_type": self.node_type,
            "canonical_name": self.canonical_name,
            "module_path": self.module_path,
            "source_file": self.source_file,
            "execution_zone": self.execution_zone,
            "runtime_owner": self.runtime_owner,
            "is_active": self.is_active,
        }


@dataclass
class ArchitectureDocumentKnowledge:
    """Knowledge about an architecture or design document."""

    file_path: str = ""
    """Relative file path."""

    title: str = ""
    """Document title (from first heading or filename stem)."""

    referenced_objects: List[str] = field(default_factory=list)
    """PECS_IDs referenced in this document."""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "title": self.title,
            "referenced_objects": sorted(self.referenced_objects),
        }


# ====================================================================
# Engineering Concept (tag/category system)
# ====================================================================


@dataclass
class EngineeringConcept:
    """A named engineering concept that groups related knowledge objects.

    Concepts are derived from the ontology and are purely categorical.
    They contain no runtime state and no query context.
    """

    name: str = ""
    """Canonical concept name (e.g. 'ocr_pipeline', 'notes_canvas')."""

    aliases: List[str] = field(default_factory=list)
    """Alternative names for this concept."""

    pecs_ids: List[str] = field(default_factory=list)
    """PECS_IDs that belong to this concept."""

    description: str = ""
    """Human-readable description."""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "aliases": list(self.aliases),
            "pecs_ids": sorted(self.pecs_ids),
            "description": self.description,
        }
