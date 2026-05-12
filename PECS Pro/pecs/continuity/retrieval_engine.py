from __future__ import annotations

from pecs.continuity.object_engine import (
    ObjectEngine,
)


MAX_RUNTIME_OBJECTS = 5


class RetrievalEngine:
    def __init__(
        self,
        project_root: str,
    ):
        self.engine = ObjectEngine(
            project_root
        )

    def compact_context(
        self,
    ):
        objects = self.engine.objects(
            MAX_RUNTIME_OBJECTS
        )

        compact = []

        for obj in objects:
            compact.append(
                {
                    "object_id":
                        obj[
                            "object_id"
                        ],

                    "problem":
                        obj[
                            "problem"
                        ],

                    "expected":
                        obj[
                            "expected"
                        ],

                    "canonical":
                        obj[
                            "canonical"
                        ],
                }
            )

        return compact
