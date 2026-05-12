from __future__ import annotations

from pecs.core.registry import (
    PECSRegistry,
)


class ObjectEngine:
    def __init__(
        self,
        project_root: str,
    ):
        self.registry = PECSRegistry(
            project_root
        )

    def objects(
        self,
        limit: int = 10,
    ):
        output = []

        for obj in self.registry.objects(
            limit
        ):
            object_id = obj[
                "object_id"
            ]

            output.append(
                {
                    "object_id":
                        object_id,

                    "problem":
                        obj[
                            "problem_to_solve"
                        ],

                    "expected":
                        obj[
                            "expected_result"
                        ],

                    "canonical":
                        obj[
                            "canonical_locality"
                        ],

                    "localities": [
                        dict(item)
                        for item in self.registry
                        .localities(
                            object_id
                        )
                    ],

                    "relations": [
                        dict(item)
                        for item in self.registry
                        .relations(
                            object_id
                        )
                    ],
                }
            )

        return output
