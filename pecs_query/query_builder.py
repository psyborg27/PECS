"""CanonicalQueryBuilder — builds a CanonicalQueryObject from lexical analysis output.

Currently consumes ``QueryParseResult`` (from ``pecs_query.query_parser``)
together with consumer metadata and produces a fully validated CQO.

``candidate_objects`` is left empty — it will be populated by the Engineering
Object Resolution stage in a future phase.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pecs_query.canonical_query import (
    CQO_SCHEMA_VERSION,
    CanonicalQueryObject,
    make_query_id,
    make_timestamp,
)


class CanonicalQueryBuilder:
    """Builder for :class:`CanonicalQueryObject`.

    Usage::

        builder = CanonicalQueryBuilder()
        cqo = (
            builder
            .with_parse_result(parse_result)
            .with_consumer("commandcode")
            .with_profile("medium")
            .build()
        )
    """

    def __init__(self) -> None:
        self._query_id: str = ""
        self._raw_query: str = ""
        self._consumer: str = "other"
        self._profile: str = "medium"
        self._timestamp: str = ""
        self._parsed_terms: List[str] = []
        self._sections: Dict[str, List[str]] = {}
        self._semantic_hints: Dict[str, bool] = {}
        self._task_type: str = "other"
        self._execution_mode: str = "analysis"
        self._engineering_intents: List[str] = []
        self._constraints: Dict[str, Any] = {}
        self._requested_outcomes: List[str] = []
        self._candidate_objects: List[Dict[str, Any]] = []
        self._locality_hints: List[str] = []
        self._topology_hints: List[str] = []
        self._authority_hints: Dict[str, Any] = {}
        self._metadata: Dict[str, Any] = {}

    # ── setters ──────────────────────────────────────────────────────────

    def with_query_id(self, query_id: str) -> CanonicalQueryBuilder:
        self._query_id = query_id
        return self

    def with_raw_query(self, raw_query: str) -> CanonicalQueryBuilder:
        self._raw_query = raw_query
        return self

    def with_consumer(self, consumer: str) -> CanonicalQueryBuilder:
        self._consumer = consumer
        return self

    def with_profile(self, profile: str) -> CanonicalQueryBuilder:
        self._profile = profile
        return self

    def with_timestamp(self, timestamp: str) -> CanonicalQueryBuilder:
        self._timestamp = timestamp
        return self

    def with_parsed_terms(self, terms: List[str]) -> CanonicalQueryBuilder:
        self._parsed_terms = list(terms)
        return self

    def with_sections(self, sections: Dict[str, List[str]]) -> CanonicalQueryBuilder:
        self._sections = dict(sections)
        return self

    def with_semantic_hints(self, hints: Dict[str, bool]) -> CanonicalQueryBuilder:
        self._semantic_hints = dict(hints)
        return self

    def with_task_type(self, task_type: str) -> CanonicalQueryBuilder:
        self._task_type = task_type
        return self

    def with_execution_mode(self, mode: str) -> CanonicalQueryBuilder:
        self._execution_mode = mode
        return self

    def with_engineering_intents(
        self, intents: List[str]
    ) -> CanonicalQueryBuilder:
        self._engineering_intents = list(intents)
        return self

    def with_constraints(self, constraints: Dict[str, Any]) -> CanonicalQueryBuilder:
        self._constraints = dict(constraints)
        return self

    def with_requested_outcomes(
        self, outcomes: List[str]
    ) -> CanonicalQueryBuilder:
        self._requested_outcomes = list(outcomes)
        return self

    def with_candidate_objects(
        self, objects: List[Dict[str, Any]]
    ) -> CanonicalQueryBuilder:
        self._candidate_objects = list(objects)
        return self

    def with_locality_hints(self, hints: List[str]) -> CanonicalQueryBuilder:
        self._locality_hints = list(hints)
        return self

    def with_topology_hints(self, hints: List[str]) -> CanonicalQueryBuilder:
        self._topology_hints = list(hints)
        return self

    def with_authority_hints(
        self, hints: Dict[str, Any]
    ) -> CanonicalQueryBuilder:
        self._authority_hints = dict(hints)
        return self

    def with_metadata(self, metadata: Dict[str, Any]) -> CanonicalQueryBuilder:
        self._metadata = dict(metadata)
        return self

    # ── convenience: consume a QueryParseResult ──────────────────────────

    def with_parse_result(self, parse_result) -> CanonicalQueryBuilder:
        """Populate builder fields from a ``QueryParseResult`` instance."""
        self._raw_query = parse_result.raw_query
        self._parsed_terms = list(parse_result.terms)
        self._sections = dict(parse_result.sections)
        self._semantic_hints = dict(parse_result.semantic_hints)
        return self

    # ── build ────────────────────────────────────────────────────────────

    def build(self) -> CanonicalQueryObject:
        """Construct and return an immutable CanonicalQueryObject."""
        return CanonicalQueryObject(
            schema=CQO_SCHEMA_VERSION,
            query_id=self._query_id or make_query_id(),
            raw_query=self._raw_query,
            consumer=self._consumer,
            profile=self._profile,
            timestamp=self._timestamp or make_timestamp(),
            parsed_terms=self._parsed_terms,
            sections=self._sections,
            semantic_hints=self._semantic_hints,
            task_type=self._task_type,
            execution_mode=self._execution_mode,
            engineering_intents=self._engineering_intents,
            constraints=self._constraints,
            requested_outcomes=self._requested_outcomes,
            candidate_objects=self._candidate_objects,
            locality_hints=self._locality_hints,
            topology_hints=self._topology_hints,
            authority_hints=self._authority_hints,
            metadata=self._metadata,
        )


# ---------------------------------------------------------------------------
# Standalone helper
# ---------------------------------------------------------------------------


def build_cqo_from_query(
    query: str,
    consumer: str = "other",
    profile: str = "medium",
) -> CanonicalQueryObject:
    """One-shot convenience: parse a query string and build a CQO in one call."""
    from pecs_query.query_parser import QueryParser

    parse_result = QueryParser.parse(query)
    return (
        CanonicalQueryBuilder()
        .with_parse_result(parse_result)
        .with_consumer(consumer)
        .with_profile(profile)
        .build()
    )
