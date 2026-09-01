"""Deterministic query parser for PECS.

Tokenizes a raw prompt into clean search terms by:
- Removing stop words (English + prompt-structure noise)
- Stripping punctuation-only tokens
- Preserving file paths, PECS_ID references, task IDs, quoted identifiers
- Detecting semantic sections from line-oriented structure

This module is the single source of truth for query preprocessing
across all PECS query entry points (explain-query, consult, compare-query).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List


# ---------------------------------------------------------------------------
# Stop words
# ---------------------------------------------------------------------------

_STOP_WORDS: FrozenSet[str] = frozenset({
    # articles
    "a", "an", "the",
    # pronouns
    "i", "you", "he", "she", "it", "we", "they",
    "me", "him", "her", "us", "them",
    "my", "your", "his", "its", "our", "their",
    "mine", "yours", "hers", "ours", "theirs",
    "myself", "yourself", "himself", "herself", "itself",
    "ourselves", "yourselves", "themselves",
    "this", "that", "these", "those",
    "who", "whom", "which", "what", "whose", "how", "why",
    "someone", "something", "everyone", "everything",
    "anyone", "anything", "nothing", "nobody",
    # prepositions
    "about", "above", "across", "after", "against", "along", "among",
    "around", "at", "before", "behind", "below", "beneath", "beside",
    "between", "beyond", "by", "down", "during", "except", "for",
    "from", "in", "inside", "into", "near", "of", "off", "on",
    "onto", "out", "outside", "over", "past", "through", "throughout",
    "to", "toward", "under", "underneath", "until", "up", "upon",
    "with", "within", "without",
    # conjunctions
    "and", "but", "or", "nor", "for", "yet", "so",
    "because", "since", "although", "though", "while",
    "if", "unless", "once", "when", "where", "whereas",
    "whether", "until", "as",
    # modals / auxiliaries
    "can", "could", "may", "might", "will", "would", "shall", "should",
    "must", "need", "dare", "ought",
    "am", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "having",
    "do", "does", "did", "doing",
    # common verbs
    "get", "got", "gets", "getting",
    "make", "makes", "made", "making",
    "take", "takes", "took", "taking",
    "use", "uses", "used", "using",
    "see", "sees", "saw", "seen",
    "know", "knows", "knew", "known",
    "think", "thinks", "thought",
    "want", "wants", "wanted",
    "give", "gives", "gave", "given",
    "find", "finds", "found", "finding",
    "tell", "tells", "told",
    "ask", "asks", "asked",
    "work", "works", "worked", "working",
    "call", "calls", "called", "calling",
    "try", "tries", "tried", "trying",
    "let", "lets",
    "begin", "begins", "began", "begun",
    "keep", "keeps", "kept",
    "put", "puts",
    "set", "sets",
    "run", "runs", "ran",
    "go", "goes", "went", "gone", "going",
    "come", "comes", "came", "coming",
    "look", "looks", "looked", "looking",
    "show", "shows", "showed", "shown",
    "help", "helps", "helped",
    "start", "starts", "started",
    "stop", "stops", "stopped",
    "seem", "seems", "seemed",
    "say", "says", "said",
    "write", "writes", "wrote", "written",
    "add", "adds", "added",
    "change", "changes", "changed", "changing",
    "update", "updates", "updated",
    "remove", "removes", "removed",
    "check", "checks", "checked",
    # common adverbs
    "very", "really", "quite", "almost", "just", "only",
    "also", "too", "still", "already", "yet",
    "even", "then", "now", "here", "there",
    "always", "never", "often", "sometimes", "usually",
    "well", "so", "much", "more", "most", "less",
    "again", "ever", "once", "twice",
    "rather", "enough", "thus", "hence",
    "anyway", "somehow", "however", "therefore",
    "otherwise", "nonetheless", "nevertheless",
    "indeed", "instead", "perhaps", "maybe",
    # prompt-structure noise (also used as section markers)
    "mandatory", "read", "objective", "task", "id",
    "deliverables", "deliverable",
    "constraints", "constraint",
    "investigation", "investigate",
    "files",
    "requested",
    "architecture", "documents", "documentation",
    "return", "returns",
    "context", "additional",
    "background", "overview", "summary",
    "details", "detail", "description",
    "note", "notes",
    "example", "examples",
    "usage",
    "steps", "step",
    "status",
    "result", "results",
    "expected", "actual", "behavior",
    "reproduction", "reproduce",
    "acceptance", "criteria",
    "prerequisites", "prerequisite",
    "instructions",
    "questions", "question",
    "audit",
    # generic technical noise (overly broad)
    "method", "function", "class", "module",
    "file", "folder", "directory", "path",
    "route", "endpoint", "handler",
    "provider", "service", "manager", "factory", "builder",
    "config", "configuration",
    "setting", "settings",
    "property", "properties",
    "attribute", "attributes",
    "parameter", "parameters", "argument", "arguments",
    "variable", "constant",
    "value", "values",
    "type", "types",
    "data", "info", "information",
    "utils", "utility", "helper",
    "common", "shared", "base", "core", "main", "root",
    "default", "general", "standard", "normal",
    "simple", "complex", "advanced",
    # code keywords (useless as search terms)
    "def", "self", "cls", "super",
    "yield", "raise", "assert", "pass", "break", "continue",
    "true", "false", "none",
    "not", "and", "or", "in", "is",
    "if", "else", "elif",
    "for", "while",
    "try", "except", "finally",
    "with", "async", "await", "lambda",
    "global", "nonlocal", "del", "print",
    # boilerplate
    "please", "kindly",
    "thank", "thanks", "regards",
    "sincerely", "best", "cheers",
    "hello", "hi", "hey", "dear",
    "sure", "yes", "no", "ok", "okay", "well",
    # version / quantity
    "one", "two", "three", "four", "five",
    "six", "seven", "eight", "nine", "ten",
    "first", "second", "third",
    "last", "next", "previous",
    "few", "many", "several", "multiple",
    "all", "every", "each", "both",
    "some", "any",
    # length / scale
    "big", "small", "large", "tiny", "huge",
    "short", "long", "high", "low",
    "fast", "slow",
    "full", "partial",
    "new", "old",
    # relative / ordinal
    "top", "bottom", "left", "right",
    "front", "back", "side",
    "inner", "outer",
    "above", "below",
    "previous", "following",
    "current", "existing",
    # time
    "now", "today", "yesterday", "tomorrow",
    "recent", "recently",
    "early", "earlier", "late", "later",
    # prompt meta
    "action", "item", "items",
    "part", "parts",
    "section", "sections", "subsection",
    "list", "lists",
    "bullet", "point", "points",
    "key", "keys",
    "rule", "rules",
    "policy", "policies",
    "todo", "fixme", "xxx", "hack",
    "bug", "fix", "issue", "ticket",
    "story", "epic",
})

# ---------------------------------------------------------------------------
# Compiled patterns
# ---------------------------------------------------------------------------

# File path: absolute, relative, with known extensions
_RE_FILE_PATH = re.compile(
    r"(?:"
    r"/\S+"                                     # Unix absolute /a/b/c.py
    r"|"
    r"(?:\.\.?/)\S+"                            # Relative ./ ../ path/to/file
    r"|"
    r"\S+\.(?:py|js|ts|rs|go|cpp|h|hpp|java|kt|swift|rb|php|md)"  # known ext
    r")",
    re.IGNORECASE,
)

# PECS_ID reference
_RE_PECS_ID = re.compile(r"PECS_ID:[A-Za-z_][A-Za-z0-9_.]*")

# Task / RFC / ADR / ARCH IDs
_RE_TASK_ID = re.compile(
    r"(?:"
    r"[A-Z]+-\d+"                               # TASK-123, PROJ-42
    r"|"
    r"RFC[- ]?\d+"                              # RFC 042, RFC-042
    r"|"
    r"ADR[- ]?\d+"                              # ADR-007
    r"|"
    r"ARCH[- ]?\d+"                             # ARCH-99
    r")",
    re.IGNORECASE,
)

# Quoted identifiers (preserve the content inside quotes)
_RE_QUOTED = re.compile(r"""["']([^"']+)["']""")

# Punctuation-only or mostly-punctuation tokens
_RE_PUNCT_ONLY = re.compile(r"^[^a-zA-Z0-9_]+$")

# ---------------------------------------------------------------------------
# Section detection
# ---------------------------------------------------------------------------

_SECTION_HEADERS: Dict[str, str] = {
    "task id": "task_id",
    "task": "task_id",
    "mandatory read": "mandatory_reads",
    "mandatory reads": "mandatory_reads",
    "mandatory": "mandatory_reads",
    "constraints": "constraints",
    "constraint": "constraints",
    "objective": "objective",
    "investigation": "investigation",
    "deliverables": "deliverables",
    "deliverable": "deliverables",
    "files": "files",
    "architecture documents": "architecture_docs",
    "architecture document": "architecture_docs",
    "requested output": "requested_output",
    "background": "background",
    "overview": "overview",
    "summary": "summary",
    "notes": "notes",
    "note": "notes",
    "description": "description",
    "examples": "examples",
    "example": "examples",
    "usage": "usage",
    "steps to reproduce": "reproduction",
    "expected behavior": "expected",
    "actual behavior": "actual",
    "acceptance criteria": "acceptance",
    "acceptance": "acceptance",
    "prerequisites": "prerequisites",
    "prerequisite": "prerequisites",
    "context": "context",
    "additional context": "context",
    "questions": "questions",
    "question": "questions",
    "return": "return_info",
    "audit": "audit",
}


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------


@dataclass
class QueryParseResult:
    """Result of parsing a raw query into structured search terms."""

    terms: List[str] = field(default_factory=list)
    """Cleaned, deduplicated search terms (lowercased)."""

    sections: Dict[str, List[str]] = field(default_factory=dict)
    """Detected semantic sections: section_name -> list of raw items."""

    semantic_hints: Dict[str, bool] = field(default_factory=dict)
    """Boolean flags indicating what the query contains."""

    raw_query: str = ""
    """The original query string."""

    def to_dict(self) -> Dict[str, object]:
        return {
            "terms": self.terms,
            "sections": self.sections,
            "semantic_hints": self.semantic_hints,
            "term_count": len(self.terms),
        }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _strip_trailing_punctuation(token: str) -> str:
    """Remove common trailing punctuation from a regular token (not a file path)."""
    return token.rstrip(".,:;!?)]}>\"'·↓↑←→•◦·‣–—")


def _is_junk_token(token: str) -> bool:
    """True if token is only punctuation, digits, and separators (e.g. '1.', '-', '↓', '3.')."""
    return bool(re.match(r"^[\d.,:;!?\-_/()'\"·↓↑←→•◦·‣–—]+$", token))


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------


class QueryParser:
    """Deterministic query parser that produces cleaned search terms."""

    MIN_TERM_LENGTH = 2

    @classmethod
    def parse(cls, query: str) -> QueryParseResult:
        """Parse a raw query into structured search terms."""
        result = QueryParseResult(raw_query=query or "")

        if not query or not query.strip():
            return result

        # 1. Detect sections from line-oriented structure
        sections = cls._detect_sections(query)

        # 2. Extract preserved patterns (before tokenization of remaining text)
        preserved_terms: List[str] = []

        # File paths
        for match in _RE_FILE_PATH.finditer(query):
            preserved_terms.append(match.group(0).strip().lower())

        # PECS_ID references
        for match in _RE_PECS_ID.finditer(query):
            preserved_terms.append(match.group(0).lower())

        # Task IDs
        for match in _RE_TASK_ID.finditer(query):
            preserved_terms.append(match.group(0).lower().replace(" ", "-"))

        # Quoted identifiers
        for match in _RE_QUOTED.finditer(query):
            inner = match.group(1).strip()
            if inner:
                preserved_terms.append(inner.lower())

        # 3. Tokenize remaining text
        tokens = cls._tokenize(query)

        # 4. Filter tokens
        clean_terms: List[str] = []
        seen: set = set()

        for token in tokens:
            # Remove trailing punctuation
            token = _strip_trailing_punctuation(token)
            if not token:
                continue
            # Skip punctuation/numbered-only tokens
            if _is_junk_token(token):
                continue
            # Skip punctuation-only tokens
            if _RE_PUNCT_ONLY.match(token):
                continue
            # Skip short tokens
            if len(token) < cls.MIN_TERM_LENGTH:
                continue
            # Skip stop words
            if token in _STOP_WORDS:
                continue
            if token not in seen:
                seen.add(token)
                clean_terms.append(token)

        # 5. Add preserved terms (with dedup)
        for term in preserved_terms:
            if term not in seen:
                seen.add(term)
                clean_terms.append(term)

        # 6. Populate result
        result.terms = clean_terms
        result.sections = sections
        result.semantic_hints = {
            "has_file_paths": bool(_RE_FILE_PATH.search(query)),
            "has_pecs_ids": bool(_RE_PECS_ID.search(query)),
            "has_task_ids": bool(_RE_TASK_ID.search(query)),
            "has_quoted_identifiers": bool(_RE_QUOTED.search(query)),
            "has_sections": bool(sections),
        }

        return result

    @classmethod
    def _detect_sections(cls, query: str) -> Dict[str, List[str]]:
        """Parse line-oriented sections from the query.

        Only lines that start with a markdown header prefix (``#``/``##``/``###``)
        are treated as section headers.  Plain content lines that happen to start
        with a section keyword (e.g. "Audit ...") are *not* interpreted as headers.
        """
        sections: Dict[str, List[str]] = {}
        current_section: str | None = None
        current_items: List[str] = []

        for raw_line in query.split("\n"):
            line = raw_line.strip()
            if not line:
                continue

            # Only treat markdown header lines as section boundaries
            if line.startswith("#") or line.startswith("*"):
                stripped = line.strip("*# \t").rstrip(":").strip().lower()

                matched_section = None
                for header_key, section_name in _SECTION_HEADERS.items():
                    if (
                        stripped == header_key
                        or stripped.startswith(header_key + " ")
                        or stripped == header_key + ":"
                    ):
                        matched_section = section_name
                        break

                if matched_section:
                    # Flush previous section
                    if current_section and current_items:
                        sections[current_section] = current_items
                    current_section = matched_section
                    current_items = []
                    # Check if content follows on the same line after header
                    after_header = raw_line.strip()
                    after_header = after_header.strip("*# \t")
                    lower_line = after_header.lower()
                    for header_key in _SECTION_HEADERS:
                        if (
                            lower_line.startswith(header_key)
                            or lower_line.startswith(header_key.rstrip("s"))
                        ):
                            after_header = after_header[len(header_key) :].strip().lstrip(": ").strip()
                            if after_header:
                                current_items.append(after_header)
                            break
                    continue

            # Non-header line — add to current section if inside one
            if current_section:
                current_items.append(line)

        # Flush last section
        if current_section and current_items:
            sections[current_section] = current_items

        return sections

    @classmethod
    def _tokenize(cls, text: str) -> List[str]:
        """Split text into lowercased tokens."""
        tokens: List[str] = []
        for part in text.split():
            stripped = part.strip()
            if not stripped:
                continue
            tokens.append(stripped.lower())
        return tokens
