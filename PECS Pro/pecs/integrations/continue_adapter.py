from __future__ import annotations

from pathlib import Path


class ContinueAdapter:
    def __init__(
        self,
        project_root: str,
    ):
        self.project_root = Path(
            project_root
        )

        self.output = (
            self.project_root
            / ".continue"
            / "rules"
            / "pecs_runtime.md"
        )

    def export(
        self,
        compact_context,
    ):
        sections = []

        sections.append(
            "# PECS RUNTIME"
        )

        sections.append("")

        for obj in compact_context:
            sections.append(
                f"OBJECT={obj['object_id']}"
            )

            sections.append(
                f"PROBLEM={obj['problem']}"
            )

            sections.append(
                f"EXPECTED={obj['expected']}"
            )

            sections.append(
                f"CANONICAL={obj['canonical']}"
            )

            sections.append("")

        self.output.write_text(
            "\n".join(sections),
            encoding="utf-8",
        )
