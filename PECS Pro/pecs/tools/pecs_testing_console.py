from __future__ import annotations

from pecs.core.registry import (
    PECSRegistry,
)


class PECSTestingConsole:
    def __init__(
        self,
        project_root: str,
    ):
        self.registry = PECSRegistry(
            project_root
        )

    def render(self):
        print("=" * 60)
        print("PECS TESTING CONSOLE")
        print("=" * 60)

        for obj in self.registry.objects(
            20
        ):
            object_id = obj[
                "object_id"
            ]

            print()
            print(
                f"OBJECT: {object_id}"
            )

            print(
                f"PROBLEM: "
                f"{obj['problem_to_solve']}"
            )

            print(
                f"EXPECTED: "
                f"{obj['expected_result']}"
            )

            print(
                f"CANONICAL: "
                f"{obj['canonical_locality']}"
            )

            print("LOCALITIES:")

            for locality in (
                self.registry.localities(
                    object_id
                )
            ):
                print(
                    f" - "
                    f"{locality['file_path']}"
                )

            print("RELATIONS:")

            for relation in (
                self.registry.relations(
                    object_id
                )
            ):
                print(
                    f" - "
                    f"{relation['target_object']}"
                )
