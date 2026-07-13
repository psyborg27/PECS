from __future__ import annotations

import ast
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple


@dataclass(frozen=True)
class _CacheKey:
    """Cache key combining file path and mtime."""

    path: str
    mtime: float


class LineRangeResolver:
    """
    Resolve current line ranges for code entities immediately before projection.

    Resolved ranges are never persisted. The resolver caches results only for
    the duration of a single build, keyed by file path and mtime, so modified
    files are always re-parsed.
    """

    def __init__(self, workspace_root: Path) -> None:
        self.workspace_root = workspace_root
        self._cache: Dict[_CacheKey, Dict[str, Tuple[int, int]]] = {}

    def resolve(
        self,
        file_path: str,
        class_name: Optional[str] = None,
        method_name: Optional[str] = None,
    ) -> Tuple[int, int]:
        """
        Return (start_line, end_line) for the requested entity.

        If class_name and method_name are both absent, the whole file range is
        returned. If only class_name is present, the class range is returned.
        If method_name is present, the method/function range is returned
        (optionally scoped to class_name).
        """
        absolute = self._absolute_path(file_path)
        if not absolute.exists():
            return (1, 1)

        try:
            mtime = absolute.stat().st_mtime
        except OSError:
            return (1, 1)

        key = _CacheKey(str(absolute), mtime)
        if key not in self._cache:
            self._cache[key] = self._parse_file(absolute)

        ranges = self._cache[key]

        if class_name and method_name:
            key_name = f"{class_name}.{method_name}"
            if key_name in ranges:
                return ranges[key_name]
            # Fall back to class range.
            if class_name in ranges:
                return ranges[class_name]
        if class_name and class_name in ranges:
            return ranges[class_name]
        if method_name and method_name in ranges:
            return ranges[method_name]

        # Whole file fallback.
        line_count = self._count_lines(absolute)
        return (1, max(1, line_count))

    def _parse_file(
        self,
        absolute: Path,
    ) -> Dict[str, Tuple[int, int]]:
        ranges: Dict[str, Tuple[int, int]] = {}
        try:
            source = absolute.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(source)
        except Exception:
            line_count = self._count_lines(absolute)
            ranges["__file__"] = (1, max(1, line_count))
            return ranges

        file_end = getattr(tree, "end_lineno", None) or self._count_lines(absolute)
        ranges["__file__"] = (1, file_end)

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                ranges[node.name] = (
                    node.lineno,
                    node.end_lineno or node.lineno,
                )
                for child in ast.iter_child_nodes(node):
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        key = f"{node.name}.{child.name}"
                        ranges[key] = (
                            child.lineno,
                            child.end_lineno or child.lineno,
                        )
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                ranges[node.name] = (
                    node.lineno,
                    node.end_lineno or node.lineno,
                )

        return ranges

    def _absolute_path(self, file_path: str) -> Path:
        candidate = Path(file_path)
        if candidate.is_absolute():
            return candidate
        return self.workspace_root / file_path

    def _count_lines(self, absolute: Path) -> int:
        try:
            with absolute.open("r", encoding="utf-8", errors="ignore") as handle:
                return sum(1 for _ in handle)
        except Exception:
            return 1
