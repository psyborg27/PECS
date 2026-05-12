from __future__ import annotations

import json
from pathlib import Path

from pecs.core.workspace_scanner import (
    WorkspaceScanner,
)


CHAT_EXTENSIONS = {
    ".json",
    ".jsonl",
    ".md",
    ".txt",
}


class ChatIngestion:
    def __init__(
        self,
        project_root: str,
    ):
        self.project_root = Path(
            project_root
        )

        self.scanner = WorkspaceScanner(
            project_root
        )

    def candidate_chat_files(
        self,
    ):
        output = []

        for path in self.scanner.scan():
            lowered = str(path).lower()

            if (
                "continue" in lowered
                or "copilot" in lowered
                or "chat" in lowered
                or "conversation" in lowered
                or "session" in lowered
            ):
                if (
                    path.suffix.lower()
                    in CHAT_EXTENSIONS
                ):
                    output.append(path)

        return output

    def ingest(
        self,
    ):
        payload = []

        for path in (
            self.candidate_chat_files()
        ):
            try:
                content = path.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )

            except Exception:
                continue

            payload.append(
                {
                    "file":
                        str(path),

                    "size":
                        len(content),

                    "preview":
                        content[:500],
                }
            )

        return payload

    def export(
        self,
        payload,
    ):
        output = (
            self.project_root
            / "pecs"
            / "cache"
            / "chat_ingestion.json"
        )

        output.write_text(
            json.dumps(
                payload,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )


if __name__ == "__main__":
    root = Path.cwd()

    ingestion = ChatIngestion(
        str(root)
    )

    payload = ingestion.ingest()

    ingestion.export(
        payload
    )

    print(
        json.dumps(
            payload[:5],
            indent=2,
            ensure_ascii=False,
        )
    )
