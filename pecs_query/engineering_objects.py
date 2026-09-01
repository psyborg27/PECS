"""Engineering object contracts for PECS.

Defines canonical engineering object models.  These are the contracts that
EngineeringObjectResolution (Phase 2B) and the Engineering Ontology (Phase 2C)
will implement against.  No discovery logic is included here — only types.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Engineering Object Type
# ---------------------------------------------------------------------------


class EngineeringObjectType(str, enum.Enum):
    """Canonical classification of an engineering object in a PECS workspace."""

    # Workspace-level
    REPOSITORY = "repository"
    WORKSPACE = "workspace"
    FOLDER = "folder"

    # Source organisation
    PACKAGE = "package"
    MODULE = "module"
    FILE = "file"

    # Structural types
    CLASS = "class"
    INTERFACE = "interface"
    METHOD = "method"
    FUNCTION = "function"
    ENUM = "enum"
    CONSTANT = "constant"

    # Runtime / architecture
    SIGNAL = "signal"
    SLOT = "slot"
    CALLBACK = "callback"
    QACTION = "qaction"
    DIALOG = "dialog"
    VIEWER = "viewer"
    OVERLAY = "overlay"
    SUBPROCESS = "subprocess"
    DISPATCH = "dispatch"
    EXECUTION = "execution"

    # Graph entities
    WORKSPACE_GRAPH_NODE = "workspace_graph_node"
    EXECUTION_GRAPH_NODE = "execution_graph_node"
    TOPOLOGY_NODE = "topology_node"
    RUNTIME_OBJECT = "runtime_object"

    # Documentation / planning
    ARCHITECTURE_DOCUMENT = "architecture_document"
    WORK_PACKAGE = "work_package"
    TASK_ID = "task_id"

    # Authority / continuity
    AUTHORITY_SOURCE = "authority_source"
    CANONICAL_SOURCE = "canonical_source"

    # Episodes
    USER_EPISODE = "user_episode"
    USER_REACTION = "user_reaction"

    # Fallback
    UNKNOWN = "unknown"


# ---------------------------------------------------------------------------
# Confidence
# ---------------------------------------------------------------------------


@dataclass(frozen=True, unsafe_hash=True)
class EngineeringObjectConfidence:
    """Confidence that an engineering object was correctly identified."""

    score: float = 0.0
    """Confidence score in [0.0, 1.0]."""

    source: str = ""
    """How this confidence was derived: 'exact_match', 'segment_match',
    'phrase_match', 'partial_match', 'evidence_match', or 'fallback'."""

    evidence_sources: List[str] = field(default_factory=list)
    """Which evidence sources contributed to this confidence."""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "score": self.score,
            "source": self.source,
            "evidence_sources": list(self.evidence_sources),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> EngineeringObjectConfidence:
        return cls(
            score=float(data.get("score", 0.0)),
            source=str(data.get("source", "")),
            evidence_sources=list(data.get("evidence_sources", [])),
        )


# ---------------------------------------------------------------------------
# Reference
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EngineeringObjectReference:
    """A canonical reference to an engineering object.

    References are **identity** pointers, not data carriers.  The referenced
    object may be resolved from the Workspace Graph, registry, or locality
    index at projection time.
    """

    pecs_id: str = ""
    """Canonical PECS_ID for this object."""

    object_type: EngineeringObjectType = EngineeringObjectType.UNKNOWN
    """Type classification."""

    source_evidence: str = ""
    """Which evidence source produced this reference
    (e.g. 'package_name', 'class_name', 'continuity_artifact')."""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pecs_id": self.pecs_id,
            "object_type": self.object_type.value,
            "source_evidence": self.source_evidence,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> EngineeringObjectReference:
        return cls(
            pecs_id=str(data.get("pecs_id", "")),
            object_type=EngineeringObjectType(
                data.get("object_type", "unknown")
            ),
            source_evidence=str(data.get("source_evidence", "")),
        )


# ---------------------------------------------------------------------------
# Engineering Object
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EngineeringObject:
    """A resolved engineering object in the PECS workspace.

    Combines an identity reference with a confidence score.  The resolved
    details (file, class, function, line range) are available via the
    Workspace Graph for objects with an established PECS_ID.
    """

    reference: EngineeringObjectReference = field(
        default_factory=EngineeringObjectReference
    )
    """Canonical reference identifying this object."""

    confidence: EngineeringObjectConfidence = field(
        default_factory=EngineeringObjectConfidence
    )
    """Confidence that this identification is correct."""

    display_name: str = ""
    """Human-readable short name (e.g. 'BulkTocMapper', 'auto_toc_dialog')."""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "reference": self.reference.to_dict(),
            "confidence": self.confidence.to_dict(),
            "display_name": self.display_name,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> EngineeringObject:
        return cls(
            reference=EngineeringObjectReference.from_dict(
                data.get("reference", {})
            ),
            confidence=EngineeringObjectConfidence.from_dict(
                data.get("confidence", {})
            ),
            display_name=str(data.get("display_name", "")),
        )


# ---------------------------------------------------------------------------
# Convenience helpers
# ---------------------------------------------------------------------------


def make_object_ref(
    pecs_id: str,
    object_type: EngineeringObjectType = EngineeringObjectType.UNKNOWN,
    source_evidence: str = "",
) -> EngineeringObjectReference:
    """Quick constructor for an EngineeringObjectReference."""
    return EngineeringObjectReference(
        pecs_id=pecs_id,
        object_type=object_type,
        source_evidence=source_evidence,
    )


def make_object(
    pecs_id: str,
    object_type: EngineeringObjectType = EngineeringObjectType.UNKNOWN,
    confidence_score: float = 0.0,
    confidence_source: str = "",
    display_name: str = "",
) -> EngineeringObject:
    """Quick constructor for an EngineeringObject."""
    return EngineeringObject(
        reference=make_object_ref(
            pecs_id=pecs_id,
            object_type=object_type,
            source_evidence=confidence_source,
        ),
        confidence=EngineeringObjectConfidence(
            score=confidence_score,
            source=confidence_source,
        ),
        display_name=display_name or pecs_id.split(".")[-1],
    )
