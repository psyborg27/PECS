from __future__ import annotations

import json
from pathlib import Path


class RuntimeCache:
    def __init__(
        self,
        project_root: str,
    ):
        self.project_root = Path(
            project_root
        )

        self.cache_root = (
            self.project_root
            / "pecs"
            / "cache"
        )

        self.cache_root.mkdir(
            parents=True,
            exist_ok=True,
        )

    def load(
        self,
        cache_name: str,
    ):
        path = (
            self.cache_root
            / f"{cache_name}.json"
        )

        if not path.exists():
            return {}

        return json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

    def save(
        self,
        cache_name: str,
        payload,
    ):
        path = (
            self.cache_root
            / f"{cache_name}.json"
        )

        path.write_text(
            json.dumps(
                payload,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
