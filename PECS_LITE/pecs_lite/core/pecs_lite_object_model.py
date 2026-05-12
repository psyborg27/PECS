
from dataclasses import dataclass, field
from typing import List

@dataclass
class PECSLiteObject:
    object_id: str
    problem: str
    expected: str
    canonical: str

    files: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    related: List[str] = field(default_factory=list)
