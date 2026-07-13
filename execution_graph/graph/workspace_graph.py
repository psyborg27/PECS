from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class NodeType(str, Enum):
    """
    Language-agnostic workspace node categories.

    These describe execution-topological roles rather than
    source-language syntax, so the graph can later support
    Python, C#, Swift, Java, and other languages.
    """

    WORKSPACE = "workspace"
    MODULE = "module"
    CLASS = "class"
    METHOD = "method"
    FUNCTION = "function"
    SIGNAL = "signal"
    SLOT = "slot"
    CALLBACK = "callback"
    DISPATCH = "dispatch"
    EXECUTION = "execution"
    QACTION = "qaction"
    TOOLBAR = "toolbar"
    MENU = "menu"
    DIALOG = "dialog"
    VIEWER = "viewer"
    OVERLAY = "overlay"
    SUBPROCESS = "subprocess"
    UNKNOWN = "unknown"


class EdgeType(str, Enum):
    """
    Unified workspace edge types.

    Replaces the parallel ExecutionEdge/DispatchEdge/OwnershipEdge
    families with a single namespace while preserving all legacy
    semantic distinctions.
    """

    IMPORT = "import"
    METHOD_CALL = "method_call"
    SIGNAL_SLOT = "signal_slot"
    CALLBACK_EXECUTION = "callback_execution"
    QACTION_REGISTER = "qaction_register"
    QACTION_FACTORY_REGISTER = "qaction_factory_register"
    SHORTCUT_REGISTER = "shortcut_register"
    QACTION_OWNERSHIP = "qaction_ownership"
    SHORTCUT_OWNERSHIP = "shortcut_ownership"
    DIALOG_LAUNCH = "dialog_launch"
    SUBPROCESS_LAUNCH = "subprocess_launch"
    OVERLAY_PROPAGATION = "overlay_propagation"
    VIEWER_PROPAGATION = "viewer_propagation"
    STATE_PROPAGATION = "state_propagation"
    EXECUTION_CHAIN = "execution_chain"
    DISPATCH_CHAIN = "dispatch_chain"
    OWNERSHIP = "ownership"


class AuthorityLevel(str, Enum):
    """
    Confidence/authority hierarchy for a node or edge.
    """

    LIVE_RUNTIME = "live_runtime"
    EXECUTION_GRAPH = "execution_graph"
    WORKSPACE_STATE = "workspace_state"
    REGISTRY_STATE = "registry_state"
    HISTORICAL = "historical"


class EdgeDirection(str, Enum):
    """
    Directionality of an edge.
    """

    DIRECTED = "directed"
    BIDIRECTIONAL = "bidirectional"
    SELF = "self"


@dataclass
class Node:
    """
    A single node in the Workspace Graph.

    Nodes are stable, deterministic, language-agnostic continuity
    primitives identified by a PECS_ID-style anchor.
    """

    node_id: str
    node_type: NodeType
    canonical_name: str

    module_path: Optional[str] = None
    class_name: Optional[str] = None
    method_name: Optional[str] = None

    runtime_owner: Optional[str] = None
    execution_zone: Optional[str] = None

    authority_level: AuthorityLevel = AuthorityLevel.WORKSPACE_STATE
    confidence: float = 0.0

    language: Optional[str] = None
    source_file: Optional[str] = None
    line_number: Optional[int] = None

    tags: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)

    incoming_edges: Set[str] = field(default_factory=set)
    outgoing_edges: Set[str] = field(default_factory=set)

    duplicate_cluster_id: Optional[str] = None
    canonical_candidate: bool = False

    def register_outgoing_edge(self, edge_id: str) -> None:
        self.outgoing_edges.add(edge_id)

    def register_incoming_edge(self, edge_id: str) -> None:
        self.incoming_edges.add(edge_id)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type.value,
            "canonical_name": self.canonical_name,
            "module_path": self.module_path,
            "class_name": self.class_name,
            "method_name": self.method_name,
            "runtime_owner": self.runtime_owner,
            "execution_zone": self.execution_zone,
            "authority_level": self.authority_level.value,
            "confidence": self.confidence,
            "language": self.language,
            "source_file": self.source_file,
            "line_number": self.line_number,
            "tags": sorted(self.tags),
            "metadata": self.metadata,
            "incoming_edges": sorted(self.incoming_edges),
            "outgoing_edges": sorted(self.outgoing_edges),
            "duplicate_cluster_id": self.duplicate_cluster_id,
            "canonical_candidate": self.canonical_candidate,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Node":
        return cls(
            node_id=str(data.get("node_id", "")),
            node_type=NodeType(data.get("node_type", "unknown")),
            canonical_name=str(data.get("canonical_name", "")),
            module_path=data.get("module_path"),
            class_name=data.get("class_name"),
            method_name=data.get("method_name"),
            runtime_owner=data.get("runtime_owner"),
            execution_zone=data.get("execution_zone"),
            authority_level=AuthorityLevel(
                data.get("authority_level", "workspace_state")
            ),
            confidence=float(data.get("confidence", 0.0)),
            language=data.get("language"),
            source_file=data.get("source_file"),
            line_number=data.get("line_number"),
            tags=set(data.get("tags", [])),
            metadata=dict(data.get("metadata", {})),
            incoming_edges=set(data.get("incoming_edges", [])),
            outgoing_edges=set(data.get("outgoing_edges", [])),
            duplicate_cluster_id=data.get("duplicate_cluster_id"),
            canonical_candidate=bool(data.get("canonical_candidate", False)),
        )


@dataclass
class Edge:
    """
    A single directed edge in the Workspace Graph.
    """

    edge_id: str
    source_node_id: str
    target_node_id: str
    edge_type: EdgeType

    direction: EdgeDirection = EdgeDirection.DIRECTED
    confidence: float = 0.0
    runtime_verified: bool = False
    dispatch_verified: bool = False
    propagation_verified: bool = False
    ownership_verified: bool = False

    execution_zone: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "edge_id": self.edge_id,
            "source_node_id": self.source_node_id,
            "target_node_id": self.target_node_id,
            "edge_type": self.edge_type.value,
            "direction": self.direction.value,
            "confidence": self.confidence,
            "runtime_verified": self.runtime_verified,
            "dispatch_verified": self.dispatch_verified,
            "propagation_verified": self.propagation_verified,
            "ownership_verified": self.ownership_verified,
            "execution_zone": self.execution_zone,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Edge":
        return cls(
            edge_id=str(data.get("edge_id", "")),
            source_node_id=str(data.get("source_node_id", "")),
            target_node_id=str(data.get("target_node_id", "")),
            edge_type=EdgeType(data.get("edge_type", "method_call")),
            direction=EdgeDirection(data.get("direction", "directed")),
            confidence=float(data.get("confidence", 0.0)),
            runtime_verified=bool(data.get("runtime_verified", False)),
            dispatch_verified=bool(data.get("dispatch_verified", False)),
            propagation_verified=bool(
                data.get("propagation_verified", False)
            ),
            ownership_verified=bool(data.get("ownership_verified", False)),
            execution_zone=data.get("execution_zone"),
            metadata=dict(data.get("metadata", {})),
        )


@dataclass
class GraphMetadata:
    """
    Deterministic metadata describing a Workspace Graph build.
    """

    graph_version: str = "1.0.0"
    workspace_hash: str = ""
    build_id: str = ""
    created_at: str = ""
    last_updated: str = ""
    graph_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "graph_version": self.graph_version,
            "workspace_hash": self.workspace_hash,
            "build_id": self.build_id,
            "created_at": self.created_at,
            "last_updated": self.last_updated,
            "graph_hash": self.graph_hash,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GraphMetadata":
        return cls(
            graph_version=str(data.get("graph_version", "1.0.0")),
            workspace_hash=str(data.get("workspace_hash", "")),
            build_id=str(data.get("build_id", "")),
            created_at=str(data.get("created_at", "")),
            last_updated=str(data.get("last_updated", "")),
            graph_hash=str(data.get("graph_hash", "")),
        )


@dataclass
class Graph:
    """
    Single in-memory Workspace Graph.

    Replaces the parallel RuntimeGraph/ExecutionGraph/OwnershipGraph
    families and the parallel GraphIndex/ExecutionIndex/OwnershipIndex
    families with one canonical container.
    """

    workspace_root: Optional[str] = None
    nodes: Dict[str, Node] = field(default_factory=dict)
    edges: Dict[str, Edge] = field(default_factory=dict)
    zones: Dict[str, Set[str]] = field(default_factory=dict)
    clusters: Dict[str, Set[str]] = field(default_factory=dict)
    entrypoints: Set[str] = field(default_factory=set)
    metadata: GraphMetadata = field(default_factory=GraphMetadata)

    def register_node(self, node: Node) -> None:
        self.nodes[node.node_id] = node

    def register_edge(self, edge: Edge) -> None:
        if edge.edge_id in self.edges:
            return
        self.edges[edge.edge_id] = edge
        if edge.source_node_id in self.nodes:
            self.nodes[edge.source_node_id].register_outgoing_edge(edge.edge_id)
        if edge.target_node_id in self.nodes:
            self.nodes[edge.target_node_id].register_incoming_edge(edge.edge_id)

    def register_zone(self, zone_id: str, node_id: str) -> None:
        if zone_id not in self.zones:
            self.zones[zone_id] = set()
        self.zones[zone_id].add(node_id)

    def register_cluster(self, cluster_id: str, node_id: str) -> None:
        if cluster_id not in self.clusters:
            self.clusters[cluster_id] = set()
        self.clusters[cluster_id].add(node_id)

    def register_entrypoint(self, node_id: str) -> None:
        self.entrypoints.add(node_id)

    def update_graph_hash(self) -> None:
        """Recompute deterministic hash over stable graph content."""
        self.metadata.graph_hash = _compute_content_hash(self)
        self.metadata.last_updated = _utc_now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workspace_root": self.workspace_root,
            "metadata": self.metadata.to_dict(),
            "nodes": {
                node_id: node.to_dict()
                for node_id, node in sorted(self.nodes.items())
            },
            "edges": {
                edge_id: edge.to_dict()
                for edge_id, edge in sorted(self.edges.items())
            },
            "zones": {
                zone_id: sorted(node_ids)
                for zone_id, node_ids in sorted(self.zones.items())
            },
            "clusters": {
                cluster_id: sorted(node_ids)
                for cluster_id, node_ids in sorted(self.clusters.items())
            },
            "entrypoints": sorted(self.entrypoints),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Graph":
        graph = cls(
            workspace_root=data.get("workspace_root"),
            metadata=GraphMetadata.from_dict(
                data.get("metadata", {}) or {}
            ),
        )
        for node_id, node_data in sorted(
            (data.get("nodes") or {}).items()
        ):
            graph.register_node(Node.from_dict(node_data))
        for edge_id, edge_data in sorted(
            (data.get("edges") or {}).items()
        ):
            graph.register_edge(Edge.from_dict(edge_data))
        for zone_id, node_ids in sorted(
            (data.get("zones") or {}).items()
        ):
            for node_id in node_ids:
                graph.register_zone(zone_id, node_id)
        for cluster_id, node_ids in sorted(
            (data.get("clusters") or {}).items()
        ):
            for node_id in node_ids:
                graph.register_cluster(cluster_id, node_id)
        for node_id in sorted(data.get("entrypoints", [])):
            graph.register_entrypoint(node_id)
        return graph


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _compute_content_hash(graph: Graph) -> str:
    """
    Compute a deterministic SHA-256 hash of stable graph content.

    Excludes mutable metadata timestamps so the hash is stable across
    re-serialization of the same workspace topology.
    """
    data = {
        "workspace_root": graph.workspace_root,
        "nodes": {
            node_id: node.to_dict()
            for node_id, node in sorted(graph.nodes.items())
        },
        "edges": {
            edge_id: edge.to_dict()
            for edge_id, edge in sorted(graph.edges.items())
        },
        "zones": {
            zone_id: sorted(node_ids)
            for zone_id, node_ids in sorted(graph.zones.items())
        },
        "clusters": {
            cluster_id: sorted(node_ids)
            for cluster_id, node_ids in sorted(graph.clusters.items())
        },
        "entrypoints": sorted(graph.entrypoints),
        "metadata": {
            "graph_version": graph.metadata.graph_version,
            "workspace_hash": graph.metadata.workspace_hash,
            "build_id": graph.metadata.build_id,
        },
    }
    canonical = json.dumps(
        data,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        default=str,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _compute_graph_hash(graph: Graph) -> str:
    """Deprecated alias; use _compute_content_hash."""
    return _compute_content_hash(graph)
