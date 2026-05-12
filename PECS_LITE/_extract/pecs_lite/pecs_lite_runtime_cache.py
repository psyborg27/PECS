
from __future__ import annotations
import json
from pathlib import Path

class PECSLiteRuntimeCache:
    def __init__(self, project_root: str):
        self.cache_file = (
            Path(project_root)
            / "pecs"
            / "cache"
            / "runtime_cache.json"
        )

    def load(self):
        if not self.cache_file.exists():
            return {}

        return json.loads(
            self.cache_file.read_text(
                encoding="utf-8"
            )
        )

    def save(self, payload):
        self.cache_file.write_text(
            json.dumps(
                payload,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
