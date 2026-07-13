from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set


class FeatureClassification(str):
    """Classification values for registry entries."""

    USER_FACING = "user_facing"
    INFRASTRUCTURE = "infrastructure"


@dataclass
class WorkspaceEvidence:
    """
    Deterministic evidence collected for a registry entry.

    Evidence is ordered by priority: package/module locality first,
    runtime evidence last.
    """

    package_locality: bool = False
    module_naming_locality: bool = False
    public_ui_registration: bool = False
    controller_ownership: bool = False
    import_export_locality: bool = False
    runtime_evidence: bool = False
    graph_topology_validated: bool = False

    package_depth: int = 0
    ui_anchor_count: int = 0
    controller_count: int = 0
    support_module_count: int = 0
    observed_activation_count: int = 0
    inbound_feature_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "package_locality": self.package_locality,
            "module_naming_locality": self.module_naming_locality,
            "public_ui_registration": self.public_ui_registration,
            "controller_ownership": self.controller_ownership,
            "import_export_locality": self.import_export_locality,
            "runtime_evidence": self.runtime_evidence,
            "graph_topology_validated": self.graph_topology_validated,
            "package_depth": self.package_depth,
            "ui_anchor_count": self.ui_anchor_count,
            "controller_count": self.controller_count,
            "support_module_count": self.support_module_count,
            "observed_activation_count": self.observed_activation_count,
            "inbound_feature_count": self.inbound_feature_count,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkspaceEvidence":
        return cls(
            package_locality=bool(data.get("package_locality", False)),
            module_naming_locality=bool(
                data.get("module_naming_locality", False)
            ),
            public_ui_registration=bool(
                data.get("public_ui_registration", False)
            ),
            controller_ownership=bool(
                data.get("controller_ownership", False)
            ),
            import_export_locality=bool(
                data.get("import_export_locality", False)
            ),
            runtime_evidence=bool(data.get("runtime_evidence", False)),
            graph_topology_validated=bool(
                data.get("graph_topology_validated", False)
            ),
            package_depth=int(data.get("package_depth", 0)),
            ui_anchor_count=int(data.get("ui_anchor_count", 0)),
            controller_count=int(data.get("controller_count", 0)),
            support_module_count=int(data.get("support_module_count", 0)),
            observed_activation_count=int(
                data.get("observed_activation_count", 0)
            ),
            inbound_feature_count=int(data.get("inbound_feature_count", 0)),
        )


@dataclass
class WorkspaceFeature:
    """
    A user-facing workspace feature identified from deterministic evidence.
    """

    feature_id: str
    aliases: List[str] = field(default_factory=list)
    root_node_id: str = ""
    node_ids: Set[str] = field(default_factory=set)
    edge_ids: Set[str] = field(default_factory=set)
    evidence: WorkspaceEvidence = field(default_factory=WorkspaceEvidence)
    confidence: float = 0.0
    classification: str = FeatureClassification.USER_FACING
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "feature_id": self.feature_id,
            "aliases": sorted(self.aliases),
            "root_node_id": self.root_node_id,
            "node_ids": sorted(self.node_ids),
            "edge_ids": sorted(self.edge_ids),
            "evidence": self.evidence.to_dict(),
            "confidence": self.confidence,
            "classification": self.classification,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkspaceFeature":
        return cls(
            feature_id=str(data.get("feature_id", "")),
            aliases=list(data.get("aliases", [])),
            root_node_id=str(data.get("root_node_id", "")),
            node_ids=set(data.get("node_ids", [])),
            edge_ids=set(data.get("edge_ids", [])),
            evidence=WorkspaceEvidence.from_dict(
                data.get("evidence", {}) or {}
            ),
            confidence=float(data.get("confidence", 0.0)),
            classification=str(
                data.get("classification", FeatureClassification.USER_FACING)
            ),
            metadata=dict(data.get("metadata", {})),
        )


@dataclass
class WorkspaceInfrastructureUnit:
    """
    An infrastructure unit that supports features but is not user-facing.
    """

    unit_id: str
    aliases: List[str] = field(default_factory=list)
    root_node_id: str = ""
    node_ids: Set[str] = field(default_factory=set)
    edge_ids: Set[str] = field(default_factory=set)
    evidence: WorkspaceEvidence = field(default_factory=WorkspaceEvidence)
    confidence: float = 0.0
    supported_features: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "unit_id": self.unit_id,
            "aliases": sorted(self.aliases),
            "root_node_id": self.root_node_id,
            "node_ids": sorted(self.node_ids),
            "edge_ids": sorted(self.edge_ids),
            "evidence": self.evidence.to_dict(),
            "confidence": self.confidence,
            "supported_features": sorted(self.supported_features),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkspaceInfrastructureUnit":
        return cls(
            unit_id=str(data.get("unit_id", "")),
            aliases=list(data.get("aliases", [])),
            root_node_id=str(data.get("root_node_id", "")),
            node_ids=set(data.get("node_ids", [])),
            edge_ids=set(data.get("edge_ids", [])),
            evidence=WorkspaceEvidence.from_dict(
                data.get("evidence", {}) or {}
            ),
            confidence=float(data.get("confidence", 0.0)),
            supported_features=set(data.get("supported_features", [])),
            metadata=dict(data.get("metadata", {})),
        )


@dataclass
class WorkspaceRegistryMetadata:
    """Deterministic metadata for a Workspace Registry build."""

    registry_version: str = "1.0.0"
    workspace_hash: str = ""
    build_id: str = ""
    created_at: str = ""
    last_updated: str = ""
    registry_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "registry_version": self.registry_version,
            "workspace_hash": self.workspace_hash,
            "build_id": self.build_id,
            "created_at": self.created_at,
            "last_updated": self.last_updated,
            "registry_hash": self.registry_hash,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkspaceRegistryMetadata":
        return cls(
            registry_version=str(
                data.get("registry_version", "1.0.0")
            ),
            workspace_hash=str(data.get("workspace_hash", "")),
            build_id=str(data.get("build_id", "")),
            created_at=str(data.get("created_at", "")),
            last_updated=str(data.get("last_updated", "")),
            registry_hash=str(data.get("registry_hash", "")),
        )


@dataclass
class WorkspaceRegistry:
    """
    Single in-memory deterministic Workspace Registry.

    Holds user-facing features and infrastructure units, indexed by
    stable identifiers and by node membership.
    """

    workspace_root: Optional[str] = None
    features: Dict[str, WorkspaceFeature] = field(default_factory=dict)
    infrastructure_units: Dict[str, WorkspaceInfrastructureUnit] = field(
        default_factory=dict
    )
    aliases: Dict[str, str] = field(default_factory=dict)
    node_index: Dict[str, Set[str]] = field(default_factory=dict)
    metadata: WorkspaceRegistryMetadata = field(
        default_factory=WorkspaceRegistryMetadata
    )

    def register_feature(self, feature: WorkspaceFeature) -> None:
        self.features[feature.feature_id] = feature
        self._index_entry(feature.feature_id, feature.node_ids)
        for alias in feature.aliases:
            self.aliases[alias] = feature.feature_id

    def register_infrastructure_unit(
        self,
        unit: WorkspaceInfrastructureUnit,
    ) -> None:
        self.infrastructure_units[unit.unit_id] = unit
        self._index_entry(unit.unit_id, unit.node_ids)
        for alias in unit.aliases:
            self.aliases[alias] = unit.unit_id

    def _index_entry(self, entry_id: str, node_ids: Set[str]) -> None:
        for node_id in node_ids:
            if node_id not in self.node_index:
                self.node_index[node_id] = set()
            self.node_index[node_id].add(entry_id)

    def update_registry_hash(self) -> None:
        self.metadata.registry_hash = _compute_registry_hash(self)
        self.metadata.last_updated = _utc_now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workspace_root": self.workspace_root,
            "metadata": self.metadata.to_dict(),
            "features": {
                fid: feature.to_dict()
                for fid, feature in sorted(self.features.items())
            },
            "infrastructure_units": {
                uid: unit.to_dict()
                for uid, unit in sorted(self.infrastructure_units.items())
            },
            "aliases": dict(sorted(self.aliases.items())),
            "node_index": {
                node_id: sorted(entry_ids)
                for node_id, entry_ids in sorted(self.node_index.items())
            },
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkspaceRegistry":
        registry = cls(
            workspace_root=data.get("workspace_root"),
            metadata=WorkspaceRegistryMetadata.from_dict(
                data.get("metadata", {}) or {}
            ),
        )
        for feature_id, feature_data in sorted(
            (data.get("features") or {}).items()
        ):
            registry.register_feature(
                WorkspaceFeature.from_dict(feature_data)
            )
        for unit_id, unit_data in sorted(
            (data.get("infrastructure_units") or {}).items()
        ):
            registry.register_infrastructure_unit(
                WorkspaceInfrastructureUnit.from_dict(unit_data)
            )
        return registry


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _compute_registry_hash(registry: WorkspaceRegistry) -> str:
    """
    Compute deterministic SHA-256 hash of stable registry content.
    """
    data = {
        "workspace_root": registry.workspace_root,
        "features": {
            fid: feature.to_dict()
            for fid, feature in sorted(registry.features.items())
        },
        "infrastructure_units": {
            uid: unit.to_dict()
            for uid, unit in sorted(registry.infrastructure_units.items())
        },
        "metadata": {
            "registry_version": registry.metadata.registry_version,
            "workspace_hash": registry.metadata.workspace_hash,
            "build_id": registry.metadata.build_id,
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
