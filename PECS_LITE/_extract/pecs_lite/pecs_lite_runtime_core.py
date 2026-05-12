
from __future__ import annotations

import json
from pathlib import Path

from pecs_lite_registry import (
    PECSLiteRegistry,
)

from pecs_lite_runtime_cache import (
    PECSLiteRuntimeCache,
)

from pecs_lite_continue_adapter import (
    PECSLiteContinueAdapter,
)


MAX_OBJECTS = 5


class PECSLiteRuntimeCore:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)

        self.registry = PECSLiteRegistry(
            str(project_root)
        )

        self.cache = PECSLiteRuntimeCache(
            str(project_root)
        )

        self.adapter = (
            PECSLiteContinueAdapter(
                str(project_root)
            )
        )

    def objects(self):
        return self.registry.fetchall(
            """
            SELECT *
            FROM objects
            ORDER BY
                recurrence_weight DESC,
                locality_confidence DESC
            LIMIT ?
            """,
            (MAX_OBJECTS,),
        )

    def build_payload(self):
        output = []

        for obj in self.objects():
            output.append(
                {
                    "object_id":
                        obj["object_id"],

                    "problem":
                        obj["problem_to_solve"],

                    "expected":
                        obj["expected_result"],

                    "canonical":
                        obj["canonical_locality"],
                }
            )

        return {
            "runtime_objects":
                output
        }

    def markdown(self, payload):
        sections = []

        sections.append(
            "# PECS LITE RUNTIME"
        )

        sections.append("")

        for obj in payload[
            "runtime_objects"
        ]:
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

        return "\n".join(sections)

    def run(self):
        payload = self.build_payload()

        self.cache.save(payload)

        self.adapter.export(
            self.markdown(payload)
        )

        return payload


if __name__ == "__main__":
    root = Path.cwd()

    runtime = PECSLiteRuntimeCore(
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
