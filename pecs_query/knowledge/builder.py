"""EngineeringKnowledgeBuilder — builds the canonical knowledge base from PECS artifacts.

Consumes the existing Workspace Graph and Workspace Registry to produce the
single authoritative ``EngineeringKnowledgeBase``.  No repository rescans, no
duplicate indexes, no source code scanning.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from execution_graph.graph.workspace_graph import (
    AuthorityLevel,
    EdgeType as GraphEdgeType,
    Graph,
    Node as GraphNode,
    NodeType as GraphNodeType,
)
from pecs_query.knowledge.models import (
    ArchitectureDocumentKnowledge,
    ClassKnowledge,
    EngineeringKnowledgeBase,
    FileKnowledge,
    MethodKnowledge,
    ModuleKnowledge,
    PackageKnowledge,
    RepositoryKnowledge,
    RuntimeKnowledge,
    WorkspaceKnowledge,
)
from pecs_query.knowledge.relationships import (
    KnowledgeRelationship,
    RelationshipType,
    make_relationship,
)
from workspace_registry.models import (
    WorkspaceRegistry,
)

LOG = logging.getLogger(__name__)

# Node types that map to "runtime" objects
_RUNTIME_NODE_TYPES = frozenset({
    GraphNodeType.QACTION,
    GraphNodeType.SIGNAL,
    GraphNodeType.SLOT,
    GraphNodeType.CALLBACK,
    GraphNodeType.DIALOG,
    GraphNodeType.VIEWER,
    GraphNodeType.OVERLAY,
    GraphNodeType.SUBPROCESS,
    GraphNodeType.DISPATCH,
    GraphNodeType.TOOLBAR,
    GraphNodeType.MENU,
})

# Edge types that map to specific relationship types
_EDGE_TO_RELATIONSHIP = {
    GraphEdgeType.IMPORT: RelationshipType.IMPORTS,
    GraphEdgeType.METHOD_CALL: RelationshipType.CALLS,
    GraphEdgeType.SIGNAL_SLOT: RelationshipType.SIGNAL_SLOT,
    GraphEdgeType.CALLBACK_EXECUTION: RelationshipType.CALLBACK_EXECUTION,
    GraphEdgeType.QACTION_REGISTER: RelationshipType.REGISTERS,
    GraphEdgeType.QACTION_FACTORY_REGISTER: RelationshipType.REGISTERS,
    GraphEdgeType.SHORTCUT_REGISTER: RelationshipType.REGISTERS,
    GraphEdgeType.QACTION_OWNERSHIP: RelationshipType.OWNS,
    GraphEdgeType.SHORTCUT_OWNERSHIP: RelationshipType.OWNS,
    GraphEdgeType.DIALOG_LAUNCH: RelationshipType.ACTIVATES,
    GraphEdgeType.SUBPROCESS_LAUNCH: RelationshipType.ACTIVATES,
    GraphEdgeType.OVERLAY_PROPAGATION: RelationshipType.RELATED_TO,
    GraphEdgeType.VIEWER_PROPAGATION: RelationshipType.RELATED_TO,
    GraphEdgeType.STATE_PROPAGATION: RelationshipType.RELATED_TO,
    GraphEdgeType.EXECUTION_CHAIN: RelationshipType.RUNTIME_NEIGHBOR,
    GraphEdgeType.DISPATCH_CHAIN: RelationshipType.RUNTIME_NEIGHBOR,
    GraphEdgeType.OWNERSHIP: RelationshipType.OWNS,
}


class EngineeringKnowledgeBuilder:
    """Builds an ``EngineeringKnowledgeBase`` from PECS artifacts.

    Usage::

        builder = EngineeringKnowledgeBuilder()
        knowledge = builder.build(graph, registry, workspace_root)
    """

    def __init__(self) -> None:
        self.kb = EngineeringKnowledgeBase()
        self._stats: Dict[str, int] = {}
        self._edges_processed: int = 0
        self._relationships_created: int = 0
        self._nodes_processed: int = 0
        self._package_map: Dict[str, List[str]] = {}  # package_name → pecs_ids
        self._file_map: Dict[str, List[str]] = {}  # file_path → pecs_ids

    # ── build ────────────────────────────────────────────────────────────

    def build(
        self,
        graph: Graph,
        registry: Optional[WorkspaceRegistry] = None,
        workspace_root: Optional[Path] = None,
    ) -> EngineeringKnowledgeBase:
        """Build the knowledge base from existing PECS artifacts."""
        self.kb = EngineeringKnowledgeBase()
        self._package_map = {}
        self._file_map = {}
        self._nodes_processed = 0
        self._edges_processed = 0
        self._relationships_created = 0

        # Phase 1: index graph nodes
        for node_id, node in graph.nodes.items():
            self._index_node(node)
            self._nodes_processed += 1

        # Phase 2: index graph edges
        for edge_id, edge in graph.edges.items():
            self._index_edge(edge)
            self._edges_processed += 1

        # Phase 3: add namespace-prefix relationships
        self._build_namespace_relationships()

        # Phase 4: build package knowledge
        self._build_package_knowledge()

        # Phase 5: consume registry
        if registry is not None:
            self._consume_registry(registry)

        # Phase 5: top-level knowledge
        self.kb.repository = self._build_repository(graph, workspace_root)
        self.kb.workspace = self._build_workspace(graph, registry)

        # Phase 6: build cross-reference indexes
        self._build_indexes()

        # Phase 7: populate diagnostics
        self.kb.build_diagnostics = {
            "graph_hash": graph.metadata.graph_hash if graph.metadata else "",
            "registry_hash": (
                registry.metadata.registry_hash
                if registry and registry.metadata
                else ""
            ),
            "nodes_processed": self._nodes_processed,
            "edges_processed": self._edges_processed,
            "relationships_created": self._relationships_created,
        }

        return self.kb

    # ── node indexing ────────────────────────────────────────────────────

    @staticmethod
    def _authority_value(node) -> str:
        val = node.authority_level
        if hasattr(val, "value"):
            return val.value
        return str(val)

    def _index_node(self, node: GraphNode) -> None:
        node_id = node.node_id
        node_type = node.node_type
        source_file = node.source_file or ""

        # Extract package name
        body = node_id
        if body.startswith("PECS_ID:"):
            body = body[8:]
        parts = body.split(".")
        package_name = parts[0] if parts else body

        # Accumulate package membership
        self._package_map.setdefault(package_name, []).append(node_id)

        # Accumulate file membership
        if source_file:
            self._file_map.setdefault(source_file, []).append(node_id)

        # Class knowledge
        if (
            node_type == GraphNodeType.CLASS
            and node.class_name
        ):
            self.kb.classes[node_id] = ClassKnowledge(
                pecs_id=node_id,
                class_name=node.class_name,
                module_path=node.module_path or "",
                source_file=source_file,
                execution_zone=node.execution_zone or "",
                authority_level=self._authority_value(node),
            )

        # Method / function knowledge
        if (
            node_type in (GraphNodeType.METHOD, GraphNodeType.FUNCTION)
            and node.method_name
        ):
            self.kb.methods[node_id] = MethodKnowledge(
                pecs_id=node_id,
                method_name=node.method_name,
                class_name=node.class_name or "",
                module_path=node.module_path or "",
                source_file=source_file,
                execution_zone=node.execution_zone or "",
                authority_level=self._authority_value(node),
            )

        # Module knowledge
        if node_type == GraphNodeType.MODULE:
            self.kb.modules[node_id] = ModuleKnowledge(
                pecs_id=node_id,
                module_path=node.module_path or body,
                node_type=node_type.value,
                source_file=source_file,
                execution_zone=node.execution_zone or "",
                authority_level=self._authority_value(node),
                confidence=node.confidence,
                class_names=self._collect_child_classes(node_id),
                method_names=self._collect_child_methods(node_id),
                line_count=node.line_number or 0,
            )

        # Runtime object knowledge
        if node_type in _RUNTIME_NODE_TYPES:
            self.kb.runtime_objects[node_id] = RuntimeKnowledge(
                pecs_id=node_id,
                node_type=node_type.value,
                canonical_name=node.canonical_name,
                module_path=node.module_path or "",
                source_file=source_file,
                execution_zone=node.execution_zone or "",
                runtime_owner=node.runtime_owner or "",
            )

    def _collect_child_classes(self, node_id: str) -> List[str]:
        """Collect class PECS_IDs that belong to this module."""
        result = []
        prefix = node_id + "."
        for cid in self.kb.classes:
            if cid.startswith(prefix) or cid.startswith(node_id):
                result.append(cid)
        return result

    def _collect_child_methods(self, node_id: str) -> List[str]:
        """Collect method PECS_IDs that belong to this module."""
        result = []
        prefix = node_id + "."
        for mid in self.kb.methods:
            if mid.startswith(prefix) or mid.startswith(node_id):
                result.append(mid)
        return result

    # ── edge indexing ────────────────────────────────────────────────────

    def _index_edge(self, edge) -> None:
        rel_type = _EDGE_TO_RELATIONSHIP.get(
            edge.edge_type, RelationshipType.RELATED_TO
        )
        rel = make_relationship(
            source_id=edge.source_node_id,
            target_id=edge.target_node_id,
            rel_type=rel_type,
            evidence="graph_edge",
            confidence=edge.confidence,
            edge_type=edge.edge_type.value,
            edge_id=edge.edge_id,
        )
        self.kb.relationships.append(rel)
        self._relationships_created += 1

    # ── namespace relationships ──────────────────────────────────────────

    def _build_namespace_relationships(self) -> None:
        """Create ``CONTAINS`` relationships from PECS_ID namespace prefixes."""
        for node_id in self.kb.modules:
            parts = node_id.split(".")
            # Module → class CONTAINS
            for cls_id in self.kb.classes:
                if cls_id.startswith(node_id + "."):
                    rel = make_relationship(
                        source_id=node_id,
                        target_id=cls_id,
                        rel_type=RelationshipType.CONTAINS,
                        evidence="namespace_prefix",
                        confidence=1.0,
                    )
                    self.kb.relationships.append(rel)
                    self._relationships_created += 1
            # Module → method CONTAINS
            for mid in self.kb.methods:
                if mid.startswith(node_id + "."):
                    rel = make_relationship(
                        source_id=node_id,
                        target_id=mid,
                        rel_type=RelationshipType.CONTAINS,
                        evidence="namespace_prefix",
                        confidence=1.0,
                    )
                    self.kb.relationships.append(rel)
                    self._relationships_created += 1

    # ── package knowledge ────────────────────────────────────────────────

    def _build_package_knowledge(self) -> None:
        for pkg_name, pecs_ids in self._package_map.items():
            modules_in_pkg = [
                pid for pid in pecs_ids if pid in self.kb.modules
            ]
            classes_in_pkg = [
                pid for pid in pecs_ids if pid in self.kb.classes
            ]
            methods_in_pkg = [
                pid for pid in pecs_ids if pid in self.kb.methods
            ]
            files_in_pkg = set()
            for pid in pecs_ids:
                if pid in self.kb.modules:
                    m = self.kb.modules[pid]
                    if m.source_file:
                        files_in_pkg.add(m.source_file)

            self.kb.packages[pkg_name] = PackageKnowledge(
                name=pkg_name,
                pecs_ids=pecs_ids,
                module_count=len(modules_in_pkg),
                file_count=len(files_in_pkg),
                class_count=len(classes_in_pkg),
                method_count=len(methods_in_pkg),
            )

    # ── registry consumption ─────────────────────────────────────────────

    def _consume_registry(self, registry: WorkspaceRegistry) -> None:
        """Incorporate registry classifications into knowledge."""
        # Build a set of user-facing PECS_IDs
        user_facing_ids: Set[str] = set()
        for feature in registry.features.values():
            user_facing_ids.update(feature.node_ids)
            # Register alias
            for alias in feature.aliases:
                for node_id in feature.node_ids:
                    self.kb.alias_index[alias] = node_id

        for unit in registry.infrastructure_units.values():
            for alias in unit.aliases:
                for node_id in unit.node_ids:
                    self.kb.alias_index[alias] = node_id

        # Mark packages as user-facing
        for pkg_name, pecs_ids in self._package_map.items():
            if any(pid in user_facing_ids for pid in pecs_ids):
                if pkg_name in self.kb.packages:
                    self.kb.packages[pkg_name].is_user_facing = True

        # Build registry relationships
        for feature in registry.features.values():
            for target_id in feature.node_ids:
                for node_id in feature.node_ids:
                    if node_id != target_id:
                        rel = make_relationship(
                            source_id=node_id,
                            target_id=target_id,
                            rel_type=RelationshipType.BELONGS_TO,
                            evidence="registry_structure",
                            confidence=feature.confidence,
                            feature_id=feature.feature_id,
                        )
                        self.kb.relationships.append(rel)
                        self._relationships_created += 1

        for unit in registry.infrastructure_units.values():
            for supported in unit.supported_features:
                for node_id in unit.node_ids:
                    rel = make_relationship(
                        source_id=node_id,
                        target_id=supported,
                        rel_type=RelationshipType.DEPENDS_ON,
                        evidence="registry_structure",
                        confidence=unit.confidence,
                    )
                    self.kb.relationships.append(rel)
                    self._relationships_created += 1

    # ── top-level knowledge ──────────────────────────────────────────────

    def _build_repository(
        self,
        graph: Graph,
        workspace_root: Optional[Path],
    ) -> RepositoryKnowledge:
        return RepositoryKnowledge(
            name=(
                graph.metadata.workspace_hash[:12]
                if graph.metadata and graph.metadata.workspace_hash
                else ""
            ),
            workspace_root=str(workspace_root) if workspace_root else "",
            graph_hash=graph.metadata.graph_hash if graph.metadata else "",
            registry_hash="",
        )

    def _build_workspace(
        self,
        graph: Graph,
        registry: Optional[WorkspaceRegistry],
    ) -> WorkspaceKnowledge:
        node_type_counts: Dict[str, int] = {}
        for node in graph.nodes.values():
            node_type_counts[node.node_type.value] = (
                node_type_counts.get(node.node_type.value, 0) + 1
            )
        return WorkspaceKnowledge(
            node_count=len(graph.nodes),
            edge_count=len(graph.edges),
            zone_count=len(graph.zones),
            cluster_count=len(graph.clusters),
            entrypoint_count=len(graph.entrypoints),
            feature_count=len(registry.features) if registry else 0,
            infrastructure_unit_count=(
                len(registry.infrastructure_units) if registry else 0
            ),
            zones=sorted(graph.zones.keys()),
            node_types=node_type_counts,
        )

    # ── cross-reference indexes ──────────────────────────────────────────

    def _build_indexes(self) -> None:
        """Build pecs_id_index after all knowledge objects are created."""
        pecs_id_index: Dict[str, str] = {}

        for pid in self.kb.modules:
            pecs_id_index[pid] = "module"
        for pid in self.kb.packages:
            pecs_id_index[pid] = "package"
        for pid in self.kb.classes:
            pecs_id_index[pid] = "class"
        for pid in self.kb.methods:
            pecs_id_index[pid] = "method"
        for pid in self.kb.runtime_objects:
            pecs_id_index[pid] = "runtime"
        for pid in self.kb.files:
            pecs_id_index[pid] = "file"

        self.kb.pecs_id_index = pecs_id_index

    # ── diagnostics ──────────────────────────────────────────────────────

    @property
    def statistics(self) -> Dict[str, int]:
        """Return current build statistics."""
        return self.kb.statistics()


def build_knowledge_base(
    graph: Graph,
    registry: Optional[WorkspaceRegistry] = None,
    workspace_root: Optional[Path] = None,
) -> EngineeringKnowledgeBase:
    """One-shot convenience: build the knowledge base from PECS artifacts."""
    builder = EngineeringKnowledgeBuilder()
    return builder.build(
        graph=graph,
        registry=registry,
        workspace_root=workspace_root,
    )
