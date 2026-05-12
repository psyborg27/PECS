from __future__ import annotations

import json
from pathlib import Path

from pecs.core.registry import (
    PECSRegistry,
)

from pecs.continuity.retrieval_engine import (
    RetrievalEngine,
)

from pecs.integrations.continue_adapter import (
    ContinueAdapter,
)

from pecs.runtime.runtime_cache import (
    RuntimeCache,
)

from pecs.runtime.pecs_incremental_update_engine import (
    IncrementalUpdateEngine,
)


class FinalRuntimeCore:
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

        self.retrieval = RetrievalEngine(
            project_root
        )

        self.adapter = ContinueAdapter(
            project_root
        )

        self.cache = RuntimeCache(
            project_root
        )

        self.incremental = (
            IncrementalUpdateEngine(
                project_root
            )
        )

    def cycle(
        self,
    ):
        updates = (
            self.incremental.run()
        )

        compact = (
            self.retrieval
            .compact_context()
        )

        self.cache.save(
            "runtime_context",
            compact,
        )

        self.adapter.export(
            compact
        )

        payload = {
            "updates":
                updates,

            "runtime":
                compact,
        }

        output = (
            Path(
                self.project_root
            )
            / "pecs"
            / "logs"
            / "final_runtime.json"
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


if __name__ == "__main__":
    root = Path.cwd()

    runtime = FinalRuntimeCore(
        str(root)
    )

    payload = runtime.cycle()

    print(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
        )
    )
