from __future__ import annotations

from pathlib import Path


SUPPORTED_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".json",
    ".jsonl",
    ".md",
    ".txt",
}


IGNORED_DIRECTORIES = {
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "dist",
    "build",
}


class WorkspaceScanner:
    def __init__(
        self,
        project_root: str,
    ):
        self.project_root = Path(
            project_root
        )

    def scan(self):
        output = []

        for path in self.project_root.rglob("*"):
            if not path.is_file():
                continue

            if (
                path.suffix.lower()
                not in SUPPORTED_EXTENSIONS
            ):
                continue

            lowered = {
                part.lower()
                for part in path.parts
            }

            if lowered.intersection(
                IGNORED_DIRECTORIES
            ):
                continue

            output.append(path)

        return output
