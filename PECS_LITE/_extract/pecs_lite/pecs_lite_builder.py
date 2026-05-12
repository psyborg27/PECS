from __future__ import annotations

import json
import shutil
import sqlite3
import zipfile
from pathlib import Path
from typing import Dict, List


# ============================================================
# PECS LITE BUILDER
# ============================================================
#
# PURPOSE:
#
# Build lightweight PECS runtime optimized for:
# - 8k models
# - 16k models
# - local inference
# - minimal orchestration
#
# ============================================================


LITE_ENGINES = [
    "pecs_context_pack_generator.py",
    "pecs_incremental_update_engine.py",
    "pecs_canonical_locality_enforcer.py",
    "pecs_live_continuity_daemon.py",
]


LITE_RULES = [
    "pecs_canonical_locality.md",
    "pecs_live_context.md",
]


class Registry:
    def __init__(
        self,
        db_path: Path,
    ):
        self.conn = sqlite3.connect(
            db_path
        )

        self.conn.row_factory = (
            sqlite3.Row
        )

    def object_count(
        self,
    ) -> int:
        result = self.conn.execute(
            """
            SELECT COUNT(*)
            FROM objects
            """
        ).fetchone()

        return int(result[0])

    def relation_count(
        self,
    ) -> int:
        result = self.conn.execute(
            """
            SELECT COUNT(*)
            FROM object_relations
            """
        ).fetchone()

        return int(result[0])

    def locality_count(
        self,
    ) -> int:
        result = self.conn.execute(
            """
            SELECT COUNT(*)
            FROM object_locality
            """
        ).fetchone()

        return int(result[0])


class LiteManifestBuilder:
    @staticmethod
    def build() -> Dict:
        return {
            "pecs_version":
                "LITE_1.0",

            "optimized_for":
                [
                    "8k_models",
                    "16k_models",
                    "local_llms",
                ],

            "runtime_principles":
                [
                    "minimal_context",
                    "deterministic_routing",
                    "canonical_locality",
                    "compact_objects",
                ],

            "max_runtime_objects":
                5,

            "engines":
                LITE_ENGINES,
        }


class LiteRuntimeBuilder:
    def __init__(
        self,
        project_root: str,
    ):
        self.project_root = Path(
            project_root
        )

        self.dist = (
            self.project_root
            / "pecs_dist"
        )

        self.bundle = (
            self.dist
            / "PECS_LITE"
        )

    def prepare(
        self,
    ):
        if self.bundle.exists():
            shutil.rmtree(
                self.bundle
            )

        self.bundle.mkdir(
            parents=True,
            exist_ok=True,
        )

    def copy_engines(
        self,
    ):
        source_root = (
            self.project_root
        )

        engine_dir = (
            self.bundle
            / "engines"
        )

        engine_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        for engine in (
            LITE_ENGINES
        ):
            source = (
                source_root
                / engine
            )

            if not source.exists():
                continue

            target = (
                engine_dir
                / engine
            )

            shutil.copy2(
                source,
                target,
            )

    def copy_rules(
        self,
    ):
        rules_dir = (
            self.bundle
            / ".continue"
            / "rules"
        )

        rules_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        for rule in (
            LITE_RULES
        ):
            source = (
                self.project_root
                / ".continue"
                / "rules"
                / rule
            )

            if not source.exists():
                continue

            target = (
                rules_dir
                / rule
            )

            shutil.copy2(
                source,
                target,
            )

    def create_manifest(
        self,
    ):
        output = (
            self.bundle
            / "manifest.json"
        )

        output.write_text(
            json.dumps(
                LiteManifestBuilder
                .build(),
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    def create_runtime_readme(
        self,
    ):
        output = (
            self.bundle
            / "README.md"
        )

        content = """
# PECS LITE

Minimal continuity runtime for local LLMs.

PRINCIPLES:
- deterministic routing
- canonical locality
- compact object retrieval
- minimal orchestration

WORKFLOW:
1. incremental update
2. canonical enforcement
3. compact context generation
4. live runtime export

OPTIMIZED FOR:
- Qwen
- DeepSeek local
- Codestral
- Gemma
- Phi
"""

        output.write_text(
            content,
            encoding="utf-8",
        )

    def create_launcher(
        self,
    ):
        output = (
            self.bundle
            / "run_lite.py"
        )

        launcher = r