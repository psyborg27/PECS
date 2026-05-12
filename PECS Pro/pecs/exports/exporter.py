from __future__ import annotations

import json
from pathlib import Path


class PECSExporter:
    def __init__(
        self,
        project_root: str,
    ):
        self.project_root = Path(
            project_root
        )

    def json_export(
        self,
        relative_path: str,
        payload,
    ):
        output = (
            self.project_root
            / relative_path
        )

        output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output.write_text(
            json.dumps(
                payload,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    def markdown_export(
        self,
        relative_path: str,
        sections,
    ):
        output = (
            self.project_root
            / relative_path
        )

        output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output.write_text(
            "\n".join(sections),
            encoding="utf-8",
        )
