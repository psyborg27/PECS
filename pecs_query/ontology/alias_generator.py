"""Deterministic alias generator for the Engineering Ontology.

Derives aliases from existing identifiers using only deterministic
string transformations.  No NLP, embeddings, or synonym lookup.
"""

from __future__ import annotations

import re
from typing import List, Set


# Regex for splitting camelCase / PascalCase
_RE_CAMEL = re.compile(r"(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")


def split_identifier(ident: str) -> List[str]:
    """Split a camelCase, PascalCase, or snake_case identifier into words.

    Returns lowercased, deduplicated words preserving first-seen order.
    """
    if not ident:
        return []

    # 1. Split on underscores and hyphens
    parts: List[str] = []
    for segment in ident.replace("-", "_").split("_"):
        if not segment:
            continue
        # 2. Split on camelCase boundaries within each segment
        sub = _RE_CAMEL.split(segment)
        parts.extend(p for p in sub if p)

    # 3. Lowercase and deduplicate preserving order
    seen: Set[str] = set()
    result: List[str] = []
    for word in parts:
        w = word.lower().strip()
        if w and w not in seen and len(w) >= 2:
            seen.add(w)
            result.append(w)
    return result


class AliasGenerator:
    """Deterministic alias generator for ontology concepts.

    Generates aliases from identifiers using only deterministic string
    transformations.  Every alias retains provenance to its source.
    """

    @staticmethod
    def from_pecs_id(pecs_id: str) -> List[str]:
        """Generate aliases from a PECS_ID.

        Examples::

            PECS_ID:Qt.main_app
            → ["Qt", "main_app", "main app"]
            → split: ["qt", "main", "app"]
            → aliases: ["qt", "main", "app", "main_app"]

        PECS_ID:Qt.main_app.MainClass.run
        → last segment: "run"
        → aliases: ["run"]
        """
        aliases: List[str] = []
        body = pecs_id
        if body.startswith("PECS_ID:"):
            body = body[8:]

        # Full dotted path as alias
        aliases.append(body.lower())

        # Each segment as an alias
        segments = body.split(".")
        for seg in segments:
            if seg:
                aliases.append(seg.lower())
                # Split each segment into component words
                words = split_identifier(seg)
                aliases.extend(words)

        # Last segment is the most specific identifier
        if len(segments) > 1:
            last = segments[-1]
            if last:
                aliases.append(last.lower())

        return _dedup(aliases)

    @staticmethod
    def from_package_name(name: str) -> List[str]:
        """Generate aliases from a package name."""
        aliases: List[str] = [name.lower()]
        aliases.extend(split_identifier(name))
        return _dedup(aliases)

    @staticmethod
    def from_module_path(module_path: str) -> List[str]:
        """Generate aliases from a dotted module path."""
        aliases: List[str] = [module_path.lower()]
        for seg in module_path.split("."):
            if seg:
                aliases.append(seg.lower())
                aliases.extend(split_identifier(seg))
        return _dedup(aliases)

    @staticmethod
    def from_class_name(name: str) -> List[str]:
        """Generate aliases from a class name."""
        aliases: List[str] = [name.lower()]
        aliases.extend(split_identifier(name))
        return _dedup(aliases)

    @staticmethod
    def from_method_name(name: str) -> List[str]:
        """Generate aliases from a method/function name."""
        aliases: List[str] = [name.lower()]
        aliases.extend(split_identifier(name))
        return _dedup(aliases)

    @staticmethod
    def from_file_path(file_path: str) -> List[str]:
        """Generate aliases from a file path.

        Examples::

            Qt/main_app.py
            → ["qt", "main_app", "main app", "main_app.py"]
        """
        aliases: List[str] = [file_path.lower()]
        # Strip extension
        stem = file_path.rsplit(".", 1)[0] if "." in file_path else file_path
        aliases.append(stem.lower())
        # Split on path separators
        for part in stem.replace("\\", "/").split("/"):
            if part:
                aliases.append(part.lower())
                aliases.extend(split_identifier(part))
        return _dedup(aliases)

    @staticmethod
    def from_feature_name(name: str) -> List[str]:
        """Generate aliases from a feature name."""
        aliases: List[str] = [name.lower()]
        aliases.extend(split_identifier(name))
        return _dedup(aliases)

    @staticmethod
    def from_architecture_doc(file_path: str) -> List[str]:
        """Generate aliases from an architecture document reference."""
        aliases: List[str] = [file_path.lower()]
        # Strip extension
        stem = file_path.rsplit(".", 1)[0] if "." in file_path else file_path
        aliases.append(stem.lower())
        # Individual path components
        for part in stem.replace("\\", "/").split("/"):
            if part:
                aliases.append(part.lower())
                aliases.extend(split_identifier(part))
        return _dedup(aliases)

    @staticmethod
    def all_from_knowledge_object(
        obj_type: str,
        obj: object,
    ) -> List[str]:
        """Generate all aliases from a knowledge object based on its type.

        Dispatches to the appropriate specialized method.
        """
        from pecs_query.knowledge.models import (
            ClassKnowledge,
            MethodKnowledge,
            ModuleKnowledge,
            PackageKnowledge,
            RuntimeKnowledge,
        )

        if isinstance(obj, PackageKnowledge):
            return AliasGenerator.from_package_name(obj.name)
        elif isinstance(obj, ModuleKnowledge):
            result: List[str] = []
            result.extend(AliasGenerator.from_pecs_id(obj.pecs_id))
            if obj.module_path:
                result.extend(AliasGenerator.from_module_path(obj.module_path))
            if obj.source_file:
                result.extend(AliasGenerator.from_file_path(obj.source_file))
            return _dedup(result)
        elif isinstance(obj, ClassKnowledge):
            result = []
            result.extend(AliasGenerator.from_class_name(obj.class_name))
            result.extend(AliasGenerator.from_pecs_id(obj.pecs_id))
            return _dedup(result)
        elif isinstance(obj, MethodKnowledge):
            result = []
            result.extend(AliasGenerator.from_method_name(obj.method_name))
            result.extend(AliasGenerator.from_pecs_id(obj.pecs_id))
            return _dedup(result)
        elif isinstance(obj, RuntimeKnowledge):
            result = []
            result.extend(AliasGenerator.from_pecs_id(obj.pecs_id))
            if obj.canonical_name:
                result.append(obj.canonical_name.lower())
                result.extend(split_identifier(obj.canonical_name))
            return _dedup(result)
        return []


def _dedup(items: List[str]) -> List[str]:
    """Deduplicate preserving order."""
    seen: Set[str] = set()
    result: List[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
