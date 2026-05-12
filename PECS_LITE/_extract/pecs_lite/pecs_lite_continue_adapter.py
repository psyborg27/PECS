
from __future__ import annotations
from pathlib import Path

class PECSLiteContinueAdapter:
    def __init__(self, project_root: str):
        self.output = (
            Path(project_root)
            / ".continue"
            / "rules"
            / "pecs_lite_runtime.md"
        )

    def export(self, markdown: str):
        self.output.write_text(
            markdown,
            encoding="utf-8",
        )
