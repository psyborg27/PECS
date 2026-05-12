from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field


@dataclass
class PECSObject:
    object_id: str

    problem_to_solve: str

    expected_result: str

    canonical_locality: str

    localities: list = field(
        default_factory=list
    )

    relations: list = field(
        default_factory=list
    )
