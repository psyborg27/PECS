from __future__ import annotations

import hashlib
import json
from pathlib import Path

from pecs.core.workspace_scanner import (
    WorkspaceScanner,
)

from pecs.core.registry import (
    PECSRegistry,
)


class IncrementalUpdateEngine:
    def __init__(
        self,
        project_root: str,
    ):
        self.project_root = Path(
            project_root
        )

        self.registry = PECSRegistry(
            project_root
        )

        self.scanner = WorkspaceScanner(
            project_root
        )

    @staticmethod
    def file_hash(
        path: Path,
    ) -> str:
        return hashlib.sha256(
            path.read_bytes()
        ).hexdigest()

    def changed(
        self,
        file_path: str,
        file_hash: str,
    ) -> bool:
        existing = self.registry.fetchone(
            """
            SELECT *
            FROM incremental_file_state
            WHERE file_path = ?
            """,
            (file_path,),
        )

        if existing is None:
            return True

        return (
            existing["file_hash"]
            != file_hash
        )

    def upsert(
        self,
        file_path: str,
        file_hash: str,
    ):
        existing = self.registry.fetchone(
            """
            SELECT *
            FROM incremental_file_state
            WHERE file_path = ?
            """,
            (file_path,),
        )

        if existing:
            self.registry.execute(
                """
                UPDATE incremental_file_state
                SET file_hash = ?
                WHERE file_path = ?
                """,
                (
                    file_hash,
                    file_path,
                ),
            )

        else:
            self.registry.execute(
                """
                INSERT INTO incremental_file_state (
                    file_path,
                    file_hash
                )
                VALUES (?, ?)
                """,
                (
                    file_path,
                    file_hash,
                ),
            )

    def run(self):
        payload = []

        for path in self.scanner.scan():
            file_hash = self.file_hash(
                path
            )

            changed = self.changed(
                str(path),
                file_hash,
            )

            if changed:
                self.upsert(
                    str(path),
                    file_hash,
                )

            payload.append(
                {
                    "file":
                        str(path),

                    "changed":
                        changed,

                    "hash":
                        file_hash,
                }
            )

        output = (
            self.project_root
            / "pecs"
            / "logs"
            / "incremental_updates.json"
        )

        output.write_text(
            json.dumps(
                payload,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        return payload
