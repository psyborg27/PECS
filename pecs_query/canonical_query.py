"""Canonical Query Object — the single intermediate representation for all PECS queries.

The CQO is produced by the CanonicalQueryBuilder from a QueryParseResult and
consumer metadata.  It is the input to every downstream pipeline stage:
Engineering Object Resolution → Evidence Correlation → Authority → Projection.

The CQO is immutable after construction.  Use the builder or dedicated factory
methods to create instances.
"""

from __future__ import annotations

import copy
import datetime
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# Schema version for serialisation.  Bump when the field set changes in a
# backward-incompatible way.
CQO_SCHEMA_VERSION = "pecs.canonical_query.v1"


# ---------------------------------------------------------------------------
# Field value constraints
# ---------------------------------------------------------------------------

_VALID_CONSUMERS = frozenset({
    "copilot", "continue", "kimi", "commandcode", "other",
})

_VALID_PROFILES = frozenset({
    "small", "medium", "large", "execution",
})

_VALID_TASK_TYPES = frozenset({
    "bug_fix", "feature_addition", "refactor", "inspection",
    "validation", "documentation", "other",
})

_VALID_EXECUTION_MODES = frozenset({
    "development", "inspection", "repair", "test", "review", "analysis",
})

_VALID_ENGINEERING_INTENTS = frozenset({
    "maintainability", "performance", "security", "ux",
    "compatibility", "reliability", "correctness", "other",
})


# ---------------------------------------------------------------------------
# CQO
# ---------------------------------------------------------------------------


@dataclass(frozen=True, unsafe_hash=True)
class CanonicalQueryObject:
    """Immutable canonical query object for the PECS query pipeline.

    Every field is read-only after construction.  Use :func:`replace` to
    produce a derived instance with selected fields changed.
    """

    # ── metadata ────────────────────────────────────────────────────────

    schema: str = CQO_SCHEMA_VERSION
    """Schema version identifier."""

    query_id: str = ""
    """Unique identifier for this query (UUID4)."""

    raw_query: str = ""
    """Original unmodified user prompt."""

    consumer: str = "other"
    """Canonical consumer identifier."""

    profile: str = "medium"
    """Projection profile: small, medium, large, execution."""

    timestamp: str = ""
    """ISO-8601 UTC timestamp of construction."""

    # ── lexical analysis output ─────────────────────────────────────────

    parsed_terms: List[str] = field(default_factory=list, hash=False)
    """Cleaned, deduplicated search terms from lexical analysis."""

    sections: Dict[str, List[str]] = field(default_factory=dict, hash=False)
    """Detected semantic sections (section_name -> raw items)."""

    semantic_hints: Dict[str, bool] = field(default_factory=dict, hash=False)
    """Boolean flags from lexical analysis."""

    # ── intent / framing ────────────────────────────────────────────────

    task_type: str = "other"
    """Classified task type."""

    execution_mode: str = "analysis"
    """Execution context."""

    engineering_intents: List[str] = field(default_factory=list, hash=False)
    """Engineering goals expressed in the prompt."""

    constraints: Dict[str, Any] = field(default_factory=dict, hash=False)
    """Hard constraints such as max targets, token budget, local-only."""

    requested_outcomes: List[str] = field(default_factory=list, hash=False)
    """What the consumer expects to receive."""

    # ── engineering objects (populated by later stages) ─────────────────

    candidate_objects: List[Dict[str, Any]] = field(
        default_factory=list, hash=False
    )
    """Resolved engineering objects.  Empty until object resolution stage."""

    # ── locality / topology / authority hints ─────────────────────────

    locality_hints: List[str] = field(default_factory=list, hash=False)
    """Suggested locality constraints derived from the prompt."""

    topology_hints: List[str] = field(default_factory=list, hash=False)
    """Suggested topology expansion hints."""

    authority_hints: Dict[str, Any] = field(default_factory=dict, hash=False)
    """Suggested authority constraints."""

    # ── extension slot ──────────────────────────────────────────────────

    metadata: Dict[str, Any] = field(default_factory=dict, hash=False)
    """Arbitrary consumer-specific or stage-specific metadata."""

    # ── private helpers ─────────────────────────────────────────────────

    def __post_init__(self) -> None:
        """Validate fields after construction."""
        _validate(self)

    # ── public helpers ──────────────────────────────────────────────────

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to a JSON-compatible dictionary."""
        return {
            "schema": self.schema,
            "query_id": self.query_id,
            "raw_query": self.raw_query,
            "consumer": self.consumer,
            "profile": self.profile,
            "timestamp": self.timestamp,
            "parsed_terms": list(self.parsed_terms),
            "sections": dict(self.sections),
            "semantic_hints": dict(self.semantic_hints),
            "task_type": self.task_type,
            "execution_mode": self.execution_mode,
            "engineering_intents": list(self.engineering_intents),
            "constraints": dict(self.constraints),
            "requested_outcomes": list(self.requested_outcomes),
            "candidate_objects": list(self.candidate_objects),
            "locality_hints": list(self.locality_hints),
            "topology_hints": list(self.topology_hints),
            "authority_hints": dict(self.authority_hints),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CanonicalQueryObject:
        """Deserialize from a dictionary (inverse of :meth:`to_dict`)."""
        return cls(
            schema=data.get("schema", CQO_SCHEMA_VERSION),
            query_id=data.get("query_id", ""),
            raw_query=data.get("raw_query", ""),
            consumer=data.get("consumer", "other"),
            profile=data.get("profile", "medium"),
            timestamp=data.get("timestamp", ""),
            parsed_terms=list(data.get("parsed_terms", [])),
            sections=dict(data.get("sections", {})),
            semantic_hints=dict(data.get("semantic_hints", {})),
            task_type=data.get("task_type", "other"),
            execution_mode=data.get("execution_mode", "analysis"),
            engineering_intents=list(data.get("engineering_intents", [])),
            constraints=dict(data.get("constraints", {})),
            requested_outcomes=list(data.get("requested_outcomes", [])),
            candidate_objects=list(data.get("candidate_objects", [])),
            locality_hints=list(data.get("locality_hints", [])),
            topology_hints=list(data.get("topology_hints", [])),
            authority_hints=dict(data.get("authority_hints", {})),
            metadata=dict(data.get("metadata", {})),
        )

    def replace(self, **changes: Any) -> CanonicalQueryObject:
        """Return a new CQO with selected fields replaced.

        This is the only supported mutation path.  The original instance is
        not modified.
        """
        current = self.to_dict()
        current.update(changes)
        return CanonicalQueryObject.from_dict(current)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


class CQOValidationError(ValueError):
    """Raised when a CQO field fails validation."""


def _validate(cqo: CanonicalQueryObject) -> None:
    """Validate CQO fields, raising on invalid values."""
    if not cqo.query_id:
        raise CQOValidationError("query_id is required")
    if not cqo.raw_query:
        raise CQOValidationError("raw_query is required")
    if cqo.consumer not in _VALID_CONSUMERS:
        raise CQOValidationError(
            f"invalid consumer '{cqo.consumer}'; must be one of {sorted(_VALID_CONSUMERS)}"
        )
    if cqo.profile not in _VALID_PROFILES:
        raise CQOValidationError(
            f"invalid profile '{cqo.profile}'; must be one of {sorted(_VALID_PROFILES)}"
        )
    if cqo.task_type not in _VALID_TASK_TYPES:
        raise CQOValidationError(
            f"invalid task_type '{cqo.task_type}'; must be one of {sorted(_VALID_TASK_TYPES)}"
        )
    if cqo.execution_mode not in _VALID_EXECUTION_MODES:
        raise CQOValidationError(
            f"invalid execution_mode '{cqo.execution_mode}'; must be one of {sorted(_VALID_EXECUTION_MODES)}"
        )
    for intent in cqo.engineering_intents:
        if intent not in _VALID_ENGINEERING_INTENTS:
            raise CQOValidationError(
                f"invalid engineering_intent '{intent}'; must be one of {sorted(_VALID_ENGINEERING_INTENTS)}"
            )
    if not cqo.timestamp:
        raise CQOValidationError("timestamp is required")


# ---------------------------------------------------------------------------
# Factory helpers
# ---------------------------------------------------------------------------


def make_query_id() -> str:
    """Generate a unique query ID."""
    return str(uuid.uuid4())


def make_timestamp() -> str:
    """Generate an ISO-8601 UTC timestamp."""
    return datetime.datetime.utcnow().isoformat() + "Z"
