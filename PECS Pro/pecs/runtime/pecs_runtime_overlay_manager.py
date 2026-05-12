from __future__ import annotations

import json
from pathlib import Path


class RuntimeOverlayManager:
    def __init__(
        self,
        project_root: str,
    ):
        self.project_root = Path(
            project_root
        )

        self.runtime_root = (
            self.project_root
            / "pecs"
            / "runtime"
        )

    def bootstrap(self):
        (
            self.runtime_root
            / "pro"
        ).mkdir(
            parents=True,
            exist_ok=True,
        )

        (
            self.runtime_root
            / "lite"
        ).mkdir(
            parents=True,
            exist_ok=True,
        )

    def write_overlay(
        self,
        runtime_name: str,
        payload,
    ):
        output = (
            self.runtime_root
            / runtime_name
            / "overlay.json"
        )

        output.write_text(
            json.dumps(
                payload,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    def run(self):
        self.bootstrap()

        self.write_overlay(
            "pro",
            {
                "authority":
                    "high",

                "writes":
                    True,
            },
        )

        self.write_overlay(
            "lite",
            {
                "authority":
                    "restricted",

                "writes":
                    False,
            },
        )

        return {
            "pro":
                str(
                    self.runtime_root
                    / "pro"
                ),

            "lite":
                str(
                    self.runtime_root
                    / "lite"
                ),
        }
