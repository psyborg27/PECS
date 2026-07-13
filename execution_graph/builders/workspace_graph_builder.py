from __future__ import annotations

import hashlib
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from execution_graph.graph.workspace_graph import (
    AuthorityLevel,
    Edge,
    EdgeDirection,
    EdgeType,
    Graph,
    GraphMetadata,
    Node,
    NodeType,
)
from execution_graph.indexes.execution_index import ExecutionIndex
from execution_graph.indexes.graph_index import GraphIndex
from execution_graph.indexes.ownership_index import OwnershipIndex
from execution_graph.indexes.runtime_path_index import RuntimePathIndex
from topology.indexing.locality_index import LocalityIndex


class WorkspaceGraphBuilder:
    """
    Build a single Workspace Graph from the same runtime data that
    currently populates PECS graph/index/registry structures.

    The builder is deterministic and read-only with respect to the
    legacy structures: it does not mutate indexes or registries.
    """

    _EDGE_TYPE_MAP: Dict[str, EdgeType] = {
        "import": EdgeType.IMPORT,
        "qaction_register": EdgeType.QACTION_REGISTER,
        "qaction_factory_register": EdgeType.QACTION_FACTORY_REGISTER,
        "shortcut_register": EdgeType.SHORTCUT_REGISTER,
        "signal_slot": EdgeType.SIGNAL_SLOT,
        "qaction_ownership": EdgeType.QACTION_OWNERSHIP,
        "shortcut_ownership": EdgeType.SHORTCUT_OWNERSHIP,
        "dialog_launch": EdgeType.DIALOG_LAUNCH,
        "subprocess_launch": EdgeType.SUBPROCESS_LAUNCH,
    }

    def __init__(self, workspace_root: Path) -> None:
        self.workspace_root = workspace_root
        self._graph = Graph(workspace_root=str(workspace_root))

    def build(
        self,
        reachable_files: Set[Path],
        runtime_locality_payload: Dict[str, Dict[str, Any]],
        runtime_topology_edges: List[Dict[str, str]],
        entrypoints: Optional[List[Path]] = None,
        graph_index: Optional[GraphIndex] = None,
        execution_index: Optional[ExecutionIndex] = None,
        ownership_index: Optional[OwnershipIndex] = None,
        locality_index: Optional[LocalityIndex] = None,
        runtime_path_index: Optional[RuntimePathIndex] = None,
    ) -> Graph:
        """
        Build the Workspace Graph from existing daemon/index data.

        All index arguments are optional and used only for validation
        comparisons; the graph is built primarily from
        `runtime_locality_payload` and `runtime_topology_edges`.
        """
        self._graph = Graph(workspace_root=str(self.workspace_root))
        self._graph.metadata = self._build_metadata(
            entrypoints=entrypoints,
            edge_count=len(runtime_topology_edges),
        )

        for pecs_id, meta in sorted(runtime_locality_payload.items()):
            node = self._node_from_payload(pecs_id, meta)
            self._graph.register_node(node)

        if entrypoints:
            for entrypoint in sorted(entrypoints):
                entry_id = self._pecs_id_from_path(entrypoint)
                self._graph.register_entrypoint(entry_id)
                if entry_id not in self._graph.nodes:
                    self._graph.register_node(
                        self._node_from_path(entrypoint)
                    )

        seen_edge_keys: Set[tuple] = set()
        for edge_data in runtime_topology_edges:
            edge = self._edge_from_dict(edge_data)
            key = (
                edge.source_node_id,
                edge.target_node_id,
                edge.edge_type.value,
            )
            if key in seen_edge_keys:
                continue
            seen_edge_keys.add(key)
            self._graph.register_edge(edge)

        for node_id, node in self._graph.nodes.items():
            if node.execution_zone:
                self._graph.register_zone(node.execution_zone, node_id)

        self._graph.update_graph_hash()
        return self._graph

    def _build_metadata(
        self,
        entrypoints: Optional[List[Path]],
        edge_count: int,
    ) -> GraphMetadata:
        workspace_hash = _workspace_hash(self.workspace_root)
        build_id = _deterministic_build_id(
            self.workspace_root,
            entrypoints or [],
            edge_count,
        )
        return GraphMetadata(
            graph_version="1.0.0",
            workspace_hash=workspace_hash,
            build_id=build_id,
            created_at=_utc_now(),
            last_updated=_utc_now(),
            graph_hash="",
        )

    def _node_from_payload(
        self,
        pecs_id: str,
        meta: Dict[str, Any],
    ) -> Node:
        node_type, canonical_name = _parse_pecs_id(pecs_id)
        class_name = meta.get("class")
        method_name = meta.get("method")
        if class_name and pecs_id.endswith(f".{class_name}"):
            node_type = NodeType.CLASS
            canonical_name = class_name
        elif method_name and pecs_id.endswith(f".{method_name}"):
            node_type = NodeType.METHOD
            canonical_name = method_name
        source_file = str(meta.get("file", ""))
        runtime_zone = meta.get("runtime_zone")

        module_path: Optional[str] = None
        if source_file:
            module_path = source_file.replace("/", ".").replace("\\", ".")
            if module_path.endswith(".py"):
                module_path = module_path[:-3]

        return Node(
            node_id=pecs_id,
            node_type=node_type,
            canonical_name=canonical_name,
            module_path=module_path,
            class_name=class_name,
            method_name=method_name,
            execution_zone=runtime_zone,
            authority_level=AuthorityLevel.WORKSPACE_STATE,
            confidence=1.0,
            source_file=source_file,
            language="python",
            metadata=dict(meta),
        )

    def _node_from_path(self, path: Path) -> Node:
        pecs_id = self._pecs_id_from_path(path)
        rel = path.relative_to(self.workspace_root)
        return Node(
            node_id=pecs_id,
            node_type=NodeType.MODULE,
            canonical_name=path.stem,
            source_file=str(rel),
            module_path=str(rel.with_suffix("")).replace("/", "."),
            language="python",
            confidence=1.0,
        )

    def _pecs_id_from_path(self, path: Path) -> str:
        rel = path.relative_to(self.workspace_root)
        object_id = ".".join(rel.with_suffix("").parts)
        return f"PECS_ID:{object_id}"

    def _edge_from_dict(self, edge_data: Dict[str, str]) -> Edge:
        source = edge_data.get("from", "")
        target = edge_data.get("to", "")
        edge_type_str = edge_data.get("type", "")
        edge_type = self._EDGE_TYPE_MAP.get(
            edge_type_str,
            EdgeType.METHOD_CALL,
        )
        edge_id = f"{source}--{edge_type.value}--{target}"
        return Edge(
            edge_id=edge_id,
            source_node_id=source,
            target_node_id=target,
            edge_type=edge_type,
            direction=EdgeDirection.DIRECTED,
            confidence=1.0,
        )


def _parse_pecs_id(pecs_id: str) -> tuple:
    """
    Infer NodeType and canonical name from a PECS_ID anchor.

    Examples:
        PECS_ID:module.path.file          -> MODULE, file
        PECS_ID:module.path.file.Class    -> CLASS, Class
        PECS_ID:action.save               -> QACTION, save
        PECS_ID:shortcut.quit             -> UNKNOWN, quit
        PECS_ID:callback.on_click         -> CALLBACK, on_click
        PECS_ID:dialog.open_settings      -> DIALOG, open_settings
        PECS_ID:subprocess.launch         -> SUBPROCESS, launch
    """
    if not pecs_id.startswith("PECS_ID:"):
        return NodeType.UNKNOWN, pecs_id

    body = pecs_id[len("PECS_ID:") :]
    parts = body.split(".")

    if len(parts) >= 2 and parts[-1] and parts[-1][0].isupper():
        return NodeType.CLASS, parts[-1]

    layer = parts[0] if parts else ""
    canonical_name = parts[-1] if parts else ""

    mapping = {
        "action": NodeType.QACTION,
        "signal": NodeType.SIGNAL,
        "slot": NodeType.SLOT,
        "callback": NodeType.CALLBACK,
        "dialog": NodeType.DIALOG,
        "subprocess": NodeType.SUBPROCESS,
        "overlay": NodeType.OVERLAY,
        "viewer": NodeType.VIEWER,
    }

    node_type = mapping.get(layer, NodeType.MODULE)
    return node_type, canonical_name


def _workspace_hash(workspace_root: Path) -> str:
    path_bytes = str(workspace_root.resolve()).encode("utf-8")
    return hashlib.sha256(path_bytes).hexdigest()[:16]


def _deterministic_build_id(
    workspace_root: Path,
    entrypoints: List[Path],
    edge_count: int,
) -> str:
    parts = [
        str(workspace_root.resolve()),
        str(edge_count),
    ]
    for entry in sorted(entrypoints):
        parts.append(str(entry))
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]
    return f"wg-{digest}"


def _utc_now() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
