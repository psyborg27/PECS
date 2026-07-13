from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from execution_graph.graph.workspace_graph import EdgeType, Graph, Node, NodeType


# UI anchor node types that can originate user-facing features.
_UI_NODE_TYPES: Set[NodeType] = {
    NodeType.QACTION,
    NodeType.MENU,
    NodeType.TOOLBAR,
    NodeType.DIALOG,
    NodeType.VIEWER,
    NodeType.OVERLAY,
}

# Ownership/register edge types that tie UI anchors to modules.
_UI_OWNERSHIP_EDGE_TYPES: Set[EdgeType] = {
    EdgeType.QACTION_OWNERSHIP,
    EdgeType.QACTION_REGISTER,
    EdgeType.QACTION_FACTORY_REGISTER,
    EdgeType.SHORTCUT_OWNERSHIP,
    EdgeType.SHORTCUT_REGISTER,
    EdgeType.DIALOG_LAUNCH,
}

# Controller identification is evidence-based: edges plus naming as support.
_CONTROLLER_EDGE_TYPES: Set[EdgeType] = {
    EdgeType.QACTION_OWNERSHIP,
    EdgeType.DIALOG_LAUNCH,
    EdgeType.SIGNAL_SLOT,
    EdgeType.DISPATCH_CHAIN,
}

# Naming patterns that strengthen controller evidence but do not create it.
_CONTROLLER_NAME_PATTERNS: Tuple[str, ...] = (
    "controller",
    "commands",
    "handlers",
    "actions",
)

# Utility/infrastructure naming patterns.
_INFRASTRUCTURE_NAME_PATTERNS: Tuple[str, ...] = (
    "utils",
    "utility",
    "service",
    "services",
    "helpers",
    "common",
    "framework",
    "core",
    "shared",
    "infrastructure",
)

# User-facing workflow naming patterns.
_USER_FACING_NAME_PATTERNS: Tuple[str, ...] = (
    "dialog",
    "view",
    "viewer",
    "feature",
    "tool",
    "wizard",
    "workflow",
    "command",
    "ribbon",
    "menu",
    "toolbar",
)


@dataclass
class FeatureCandidate:
    """
    Mutable candidate produced from deterministic evidence.

    Graph topology is used only to validate and expand boundaries.
    """

    candidate_id: str
    root_node_id: str
    node_ids: Set[str] = field(default_factory=set)
    edge_ids: Set[str] = field(default_factory=set)
    evidence_tags: Set[str] = field(default_factory=set)
    classification: str = "infrastructure"

    def add_node(self, node_id: str) -> None:
        self.node_ids.add(node_id)

    def add_edge(self, edge_id: str) -> None:
        self.edge_ids.add(edge_id)

    def add_evidence(self, tag: str) -> None:
        self.evidence_tags.add(tag)


class FeatureIdentifier:
    """
    Evidence-first feature identification.

    Candidates originate from package/module locality, UI registrations,
    controller ownership, import/export locality, and runtime evidence.
    The Workspace Graph validates and expands candidates but never
    originates them.
    """

    def __init__(self, graph: Graph) -> None:
        self.graph = graph
        self._module_nodes: Dict[str, Node] = {
            node_id: node
            for node_id, node in graph.nodes.items()
            if node.node_type == NodeType.MODULE
        }
        self._ui_nodes: Dict[str, Node] = {
            node_id: node
            for node_id, node in graph.nodes.items()
            if node.node_type in _UI_NODE_TYPES
        }
        self._import_adjacency: Dict[str, Set[str]] = self._build_import_adjacency()
        self._reverse_import_adjacency: Dict[str, Set[str]] = (
            self._build_reverse_import_adjacency()
        )

    def identify(self) -> List[FeatureCandidate]:
        candidates: Dict[str, FeatureCandidate] = {}

        # Phase 1: Package-level locality candidates.
        package_candidates = self._package_candidates()
        for candidate in package_candidates:
            candidates[candidate.candidate_id] = candidate

        # Phase 2: Entrypoint candidates (individual user-facing entry surfaces).
        for entry_id in sorted(self.graph.entrypoints):
            entry_node = self._module_nodes.get(entry_id)
            if entry_node is None:
                continue
            candidate = self._entrypoint_candidate(entry_node)
            if candidate is not None:
                candidates[candidate.candidate_id] = candidate

        # Phase 3: Module-level UI registration evidence (strengthens only).
        for module_id, module in sorted(self._module_nodes.items()):
            candidate = self._candidate_from_module(module)
            if candidate is not None:
                if candidate.candidate_id in candidates:
                    self._merge_candidates(
                        candidates[candidate.candidate_id],
                        candidate,
                    )
                else:
                    candidates[candidate.candidate_id] = candidate

        # Phase 3b: Standalone modules that are not part of any candidate
        # become infrastructure unit candidates.
        covered_modules = set()
        for candidate in candidates.values():
            covered_modules.update(
                nid
                for nid in candidate.node_ids
                if nid in self._module_nodes
            )
        for module_id, module in sorted(self._module_nodes.items()):
            if module_id in covered_modules:
                continue
            if module_id in self.graph.entrypoints:
                continue
            candidate = FeatureCandidate(
                candidate_id=self._candidate_id(module_id),
                root_node_id=module_id,
            )
            candidate.add_node(module_id)
            candidate.add_evidence("package_locality")
            candidates[candidate.candidate_id] = candidate

        # Phase 4: Controller ownership evidence strengthens/expands candidates.
        for module_id, module in sorted(self._module_nodes.items()):
            if self._is_controller(module):
                self._attach_controller(candidates, module)

        # Phase 5: Import/export locality attaches support modules.
        for candidate in list(candidates.values()):
            self._attach_support_modules(candidate)

        # Phase 6: Runtime evidence confirms and expands candidates.
        for candidate in list(candidates.values()):
            self._apply_runtime_evidence(candidate)

        # Phase 7: Graph topology validation and expansion.
        for candidate in list(candidates.values()):
            self._validate_and_expand(candidate)

        # Phase 8: Classification.
        for candidate in candidates.values():
            candidate.classification = self._classify(candidate)

        # Merge overlapping user-facing candidates that share a module root.
        merged = self._merge_overlapping_candidates(list(candidates.values()))
        return merged

    def _candidate_from_module(
        self,
        module: Node,
    ) -> Optional[FeatureCandidate]:
        has_naming = self._has_feature_naming(module)
        ui_anchor_ids = self._ui_anchors_for_module(module)

        if not has_naming and not ui_anchor_ids:
            return None

        candidate = FeatureCandidate(
            candidate_id=self._candidate_id(module.node_id),
            root_node_id=module.node_id,
        )
        candidate.add_node(module.node_id)
        candidate.add_evidence("package_locality")

        if has_naming:
            candidate.add_evidence("module_naming_locality")

        for anchor_id in sorted(ui_anchor_ids):
            candidate.add_node(anchor_id)
            candidate.add_evidence("public_ui_registration")
            # Add the ownership/register edge if present.
            for edge_id in module.outgoing_edges:
                edge = self.graph.edges.get(edge_id)
                if edge and edge.target_node_id == anchor_id:
                    candidate.add_edge(edge_id)

        return candidate

    def _package_candidates(self) -> List[FeatureCandidate]:
        """
        Create candidates from package locality and module naming consistency.

        A package with >=2 modules always becomes a candidate:
        - If at least one module matches a user-facing naming pattern, it is
          tagged with module_naming_locality (may become user-facing).
        - Otherwise it is an infrastructure unit candidate.
        """
        packages: Dict[str, List[Node]] = {}
        for module in self._module_nodes.values():
            package = self._package_prefix(module.node_id)
            if package:
                packages.setdefault(package, []).append(module)

        candidates: List[FeatureCandidate] = []
        for package, modules in sorted(packages.items()):
            if len(modules) < 2:
                continue

            has_feature_naming = any(
                self._has_feature_naming(module) for module in modules
            )

            root = self._select_package_root(modules)
            candidate = FeatureCandidate(
                candidate_id=self._candidate_id(root.node_id),
                root_node_id=root.node_id,
            )
            candidate.add_evidence("package_locality")
            if has_feature_naming:
                candidate.add_evidence("module_naming_locality")

            for module in sorted(modules, key=lambda m: m.node_id):
                candidate.add_node(module.node_id)

            candidates.append(candidate)

        return candidates

    def _entrypoint_candidate(
        self,
        entry_node: Node,
    ) -> Optional[FeatureCandidate]:
        """
        Entrypoint modules are user-facing surfaces; create a candidate for
        each one unless it is already covered by a package candidate.
        """
        candidate = FeatureCandidate(
            candidate_id=self._candidate_id(entry_node.node_id),
            root_node_id=entry_node.node_id,
        )
        candidate.add_node(entry_node.node_id)
        candidate.add_evidence("package_locality")
        candidate.add_evidence("runtime_evidence")
        return candidate

    def _merge_candidates(
        self,
        target: FeatureCandidate,
        source: FeatureCandidate,
    ) -> None:
        """Merge source candidate evidence and nodes into target."""
        target.node_ids.update(source.node_ids)
        target.edge_ids.update(source.edge_ids)
        target.evidence_tags.update(source.evidence_tags)

    def _select_package_root(self, modules: List[Node]) -> Node:
        """Pick the most representative module in a package as the root."""
        # Prefer entrypoints, then highest out-degree, then lexicographically.
        for module in sorted(modules, key=lambda m: m.node_id):
            if module.node_id in self.graph.entrypoints:
                return module
        return max(
            modules,
            key=lambda m: (len(m.outgoing_edges), m.node_id),
        )

    def _ui_anchors_for_module(self, module: Node) -> Set[str]:
        anchors: Set[str] = set()
        for edge_id in module.outgoing_edges:
            edge = self.graph.edges.get(edge_id)
            if not edge:
                continue
            if (
                edge.edge_type in _UI_OWNERSHIP_EDGE_TYPES
                and edge.target_node_id in self._ui_nodes
            ):
                anchors.add(edge.target_node_id)
        return anchors

    def _is_controller(self, module: Node) -> bool:
        # Primary criterion: outgoing edges to UI anchors/dispatch targets.
        edge_based = False
        controlled_anchors = 0
        for edge_id in module.outgoing_edges:
            edge = self.graph.edges.get(edge_id)
            if not edge:
                continue
            if edge.edge_type in _CONTROLLER_EDGE_TYPES:
                edge_based = True
                if edge.target_node_id in self._ui_nodes:
                    controlled_anchors += 1

        # Naming strengthens but is never primary.
        naming_based = any(
            pattern in module.canonical_name.lower()
            for pattern in _CONTROLLER_NAME_PATTERNS
        )

        return edge_based and (controlled_anchors >= 1 or naming_based)

    def _attach_controller(
        self,
        candidates: Dict[str, FeatureCandidate],
        controller: Node,
    ) -> None:
        # Prefer same-package candidate.
        same_package = self._same_package_candidate(candidates, controller)
        if same_package is not None:
            same_package.add_node(controller.node_id)
            same_package.add_evidence("controller_ownership")
            for edge_id in controller.outgoing_edges:
                edge = self.graph.edges.get(edge_id)
                if edge and edge.edge_type in _CONTROLLER_EDGE_TYPES:
                    same_package.add_edge(edge_id)
                    same_package.add_node(edge.target_node_id)
            return

        # No matching candidate: controller alone does not create a feature.

    def _same_package_candidate(
        self,
        candidates: Dict[str, FeatureCandidate],
        node: Node,
    ) -> Optional[FeatureCandidate]:
        node_package = self._package_prefix(node.node_id)
        for candidate in candidates.values():
            if candidate.classification != "infrastructure":
                continue
            root = self.graph.nodes.get(candidate.root_node_id)
            if root and self._package_prefix(root.node_id) == node_package:
                return candidate
        return None

    def _attach_support_modules(self, candidate: FeatureCandidate) -> None:
        root = self.graph.nodes.get(candidate.root_node_id)
        if root is None:
            return

        root_package = self._package_prefix(root.node_id)
        to_attach: Set[str] = set()

        for node_id in list(candidate.node_ids):
            for neighbor in self._import_adjacency.get(node_id, set()):
                neighbor_node = self.graph.nodes.get(neighbor)
                if (
                    neighbor_node
                    and neighbor_node.node_type == NodeType.MODULE
                    and self._package_prefix(neighbor) == root_package
                    and neighbor not in candidate.node_ids
                    and not self._has_ui_anchors(neighbor_node)
                ):
                    to_attach.add(neighbor)

            for neighbor in self._reverse_import_adjacency.get(node_id, set()):
                neighbor_node = self.graph.nodes.get(neighbor)
                if (
                    neighbor_node
                    and neighbor_node.node_type == NodeType.MODULE
                    and self._package_prefix(neighbor) == root_package
                    and neighbor not in candidate.node_ids
                    and not self._has_ui_anchors(neighbor_node)
                ):
                    to_attach.add(neighbor)

        for node_id in sorted(to_attach):
            candidate.add_node(node_id)
            candidate.add_evidence("import_export_locality")

    def _apply_runtime_evidence(self, candidate: FeatureCandidate) -> None:
        if candidate.root_node_id in self.graph.entrypoints:
            candidate.add_evidence("runtime_evidence")

        # Any observed activation bonus on member nodes counts as runtime evidence.
        activation_count = 0
        for node_id in candidate.node_ids:
            node = self.graph.nodes.get(node_id)
            if node and node.metadata.get("observed_activation_count"):
                activation_count += int(node.metadata["observed_activation_count"])
        if activation_count > 0:
            candidate.add_evidence("runtime_evidence")

    def _validate_and_expand(self, candidate: FeatureCandidate) -> None:
        # Validate connectedness within the same top-level package.
        root = self.graph.nodes.get(candidate.root_node_id)
        if root is None:
            return

        root_package = self._package_prefix(root.node_id)
        expanded: Set[str] = set(candidate.node_ids)

        for node_id in list(candidate.node_ids):
            for edge_id in self.graph.nodes[node_id].outgoing_edges:
                edge = self.graph.edges.get(edge_id)
                if not edge:
                    continue
                target = self.graph.nodes.get(edge.target_node_id)
                if (
                    target
                    and target.node_type == NodeType.MODULE
                    and self._package_prefix(target.node_id) == root_package
                    and edge.target_node_id not in expanded
                ):
                    expanded.add(edge.target_node_id)
                    candidate.add_edge(edge_id)

        candidate.node_ids = expanded
        candidate.add_evidence("graph_topology_validated")

    def _classify(self, candidate: FeatureCandidate) -> str:
        if "public_ui_registration" in candidate.evidence_tags:
            return "user_facing"
        if (
            "controller_ownership" in candidate.evidence_tags
            and "runtime_evidence" in candidate.evidence_tags
        ):
            return "user_facing"

        root = self.graph.nodes.get(candidate.root_node_id)
        if root is not None:
            name_lower = root.canonical_name.lower()
            if any(pattern in name_lower for pattern in _USER_FACING_NAME_PATTERNS):
                return "user_facing"
            if any(pattern in name_lower for pattern in _INFRASTRUCTURE_NAME_PATTERNS):
                return "infrastructure"

        # Entrypoints are user-facing surfaces by definition.
        if candidate.root_node_id in self.graph.entrypoints:
            return "user_facing"

        # Default: infrastructure unless runtime-confirmed controller-owned.
        if (
            "controller_ownership" in candidate.evidence_tags
            and "runtime_evidence" in candidate.evidence_tags
        ):
            return "user_facing"

        return "infrastructure"

    def _merge_overlapping_candidates(
        self,
        candidates: List[FeatureCandidate],
    ) -> List[FeatureCandidate]:
        # Group by root node id; keep the most evidence-rich candidate per root.
        by_root: Dict[str, FeatureCandidate] = {}
        for candidate in candidates:
            existing = by_root.get(candidate.root_node_id)
            if existing is None or len(candidate.evidence_tags) > len(
                existing.evidence_tags
            ):
                by_root[candidate.root_node_id] = candidate
        return list(by_root.values())

    def _build_import_adjacency(self) -> Dict[str, Set[str]]:
        adjacency: Dict[str, Set[str]] = {}
        for edge in self.graph.edges.values():
            if edge.edge_type == EdgeType.IMPORT:
                adjacency.setdefault(edge.source_node_id, set()).add(
                    edge.target_node_id
                )
        return adjacency

    def _build_reverse_import_adjacency(self) -> Dict[str, Set[str]]:
        adjacency: Dict[str, Set[str]] = {}
        for edge in self.graph.edges.values():
            if edge.edge_type == EdgeType.IMPORT:
                adjacency.setdefault(edge.target_node_id, set()).add(
                    edge.source_node_id
                )
        return adjacency

    def _has_feature_naming(self, module: Node) -> bool:
        name_lower = module.canonical_name.lower()
        return any(pattern in name_lower for pattern in _USER_FACING_NAME_PATTERNS)

    def _has_ui_anchors(self, module: Node) -> bool:
        return len(self._ui_anchors_for_module(module)) > 0

    def _package_prefix(self, node_id: str) -> str:
        if not node_id.startswith("PECS_ID:"):
            return node_id.split(".")[0] if "." in node_id else node_id
        body = node_id[len("PECS_ID:") :]
        parts = body.split(".")
        return parts[0] if parts else ""

    def _candidate_id(self, node_id: str) -> str:
        stable = f"feature:{node_id}"
        digest = hashlib.sha256(stable.encode("utf-8")).hexdigest()[:12]
        return f"{stable}:{digest}"


def _tanh_normalize(value: float, scale: float = 3.0) -> float:
    """Deterministic normalization to [0.0, 1.0]."""
    return math.tanh(value / scale)
