from __future__ import annotations

import json
from pathlib import Path

from pecs.continuity.retrieval_engine import (
    RetrievalEngine,
)

from pecs.integrations.continue_adapter import (
    ContinueAdapter,
)


class RuntimeCore:
    def __init__(
        self,
        project_root: str,
    ):
        self.project_root = Path(
            project_root
        )

        self.retrieval = RetrievalEngine(
            str(project_root)
        )

        self.adapter = ContinueAdapter(
            str(project_root)
        )

    def run(self):
        compact = (
            self.retrieval
            .compact_context()
        )

        self.adapter.export(
            compact
        )

        output = (
            self.project_root
            / "pecs"
            / "logs"
            / "runtime.json"
        )

        output.write_text(
            json.dumps(
                compact,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        return compact


if __name__ == "__main__":
    root = Path.cwd()

    runtime = RuntimeCore(
        str(root)
    )

    payload = runtime.run()

    print(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
        )
    )
