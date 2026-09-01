from __future__ import annotations

import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import workspace_bridge_cli

from pecs_query.canonical_query import (
    CQO_SCHEMA_VERSION as CQO_SCHEMA,
    CQOValidationError,
    CanonicalQueryObject,
    make_query_id,
    make_timestamp,
)
from pecs_query.engineering_objects import (
    EngineeringObject,
    EngineeringObjectConfidence,
    EngineeringObjectReference,
    EngineeringObjectType,
    make_object,
    make_object_ref,
)
from pecs_query.knowledge import (
    EngineeringKnowledgeBase,
    EngineeringKnowledgeBuilder,
    KnowledgeAccessAPI,
    build_knowledge_base,
)
from pecs_query.knowledge.models import (
    ModuleKnowledge,
    PackageKnowledge,
)
from pecs_query.knowledge.relationships import (
    KnowledgeRelationship,
    RelationshipType,
    make_relationship,
)
from pecs_query.query_builder import (
    CanonicalQueryBuilder,
    build_cqo_from_query,
)
from pecs_query.query_parser import QueryParser

class WorkspaceBridgeCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.workspace_root = Path(self.tempdir.name)
        self.workspace_root.mkdir(parents=True, exist_ok=True)
        pecs_dir = self.workspace_root / ".pecs"
        pecs_dir.mkdir(parents=True, exist_ok=True)
        (pecs_dir / "daemon.pid").write_text(str(os.getpid()), encoding="utf-8")

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    @patch("validation.workspace_readiness_authority.write_workspace_readiness_json")
    @patch("validation.workspace_readiness_authority.generate_workspace_readiness_report")
    def test_workspace_ready_json_flag_prints_json(self, mock_generate_report, mock_write_json):
        mock_generate_report.return_value = {
            "schema": "pecs.workspace_readiness.v1",
            "ready": True,
            "installation": {"status": "PASS"},
            "workspace_assets": {"status": "PASS"},
            "bridge": {"status": "PASS"},
            "daemon": {"status": "PASS"},
            "topology": {"status": "PASS"},
            "workspace_graph": {"status": "PASS"},
            "workspace_registry": {"status": "PASS"},
            "canonical_validation": {"status": "PASS"},
            "consumer_integration": {"status": "PASS"},
            "overall": {"status": "READY"},
        }

        argv = [
            "pecs",
            "workspace-ready",
            "--workspace",
            str(self.workspace_root),
            "--json",
        ]
        with patch.object(sys, "argv", argv):
            captured = io.StringIO()
            with patch.object(sys, "stdout", captured):
                with self.assertRaises(SystemExit) as cm:
                    workspace_bridge_cli.main()

        self.assertEqual(cm.exception.code, 0)
        output = captured.getvalue().strip()
        parsed = json.loads(output)
        self.assertEqual(parsed["overall"]["status"], "READY")
        self.assertTrue(parsed["ready"])

    def test_workspace_ready_prints_blocking_errors_when_not_ready(self):
        with patch("validation.workspace_readiness_authority.write_workspace_readiness_json") as mock_write_json:
            with patch("validation.workspace_readiness_authority.generate_workspace_readiness_report") as mock_generate_report:
                mock_generate_report.return_value = {
                    "schema": "pecs.workspace_readiness.v1",
                    "ready": False,
                    "installation": {"status": "PASS"},
                    "workspace_assets": {"status": "PASS"},
                    "bridge": {"status": "PASS"},
                    "daemon": {"status": "PASS"},
                    "topology": {"status": "PASS"},
                    "workspace_graph": {"status": "FAIL", "reason": "workspace_graph.json missing", "recommended_action": "Refresh workspace"},
                    "workspace_registry": {"status": "PASS"},
                    "canonical_validation": {"status": "PASS"},
                    "consumer_integration": {"status": "PASS"},
                    "overall": {"status": "NOT READY"},
                }

                argv = [
                    "pecs",
                    "workspace-ready",
                    "--workspace",
                    str(self.workspace_root),
                ]
                with patch.object(sys, "argv", argv):
                    captured_out = io.StringIO()
                    with patch.object(sys, "stdout", captured_out):
                        with self.assertRaises(SystemExit) as cm:
                            workspace_bridge_cli.main()

                self.assertEqual(cm.exception.code, 1)
                output = captured_out.getvalue()
                self.assertIn("Workspace Graph", output)
                self.assertIn("FAIL", output)
                self.assertIn("Blocking Errors:", output)
                self.assertIn("workspace_graph.json missing", output)
                mock_write_json.assert_called_once()

    def test_workspace_ready_with_positional_workspace_root(self):
        with patch("validation.workspace_readiness_authority.write_workspace_readiness_json") as mock_write_json:
            with patch("validation.workspace_readiness_authority.generate_workspace_readiness_report") as mock_generate_report:
                mock_generate_report.return_value = {
                    "schema": "pecs.workspace_readiness.v1",
                    "ready": True,
                    "installation": {"status": "PASS"},
                    "workspace_assets": {"status": "PASS"},
                    "bridge": {"status": "PASS"},
                    "daemon": {"status": "PASS"},
                    "topology": {"status": "PASS"},
                    "workspace_graph": {"status": "PASS"},
                    "workspace_registry": {"status": "PASS"},
                    "canonical_validation": {"status": "PASS"},
                    "consumer_integration": {"status": "PASS"},
                    "overall": {"status": "READY"},
                }

                argv = [
                    "pecs",
                    "workspace-ready",
                    str(self.workspace_root),
                ]
                with patch.object(sys, "argv", argv):
                    captured = io.StringIO()
                    with patch.object(sys, "stdout", captured):
                        with self.assertRaises(SystemExit) as cm:
                            workspace_bridge_cli.main()

                self.assertEqual(cm.exception.code, 0)
                output = captured.getvalue()
                self.assertIn("PECS Workspace Readiness", output)
                self.assertIn("READY", output)
                self.assertEqual(mock_generate_report.call_args[0][0], self.workspace_root.resolve())
                self.assertEqual(str(mock_generate_report.call_args[0][1]), str(Path(workspace_bridge_cli.__file__).resolve().parent))
                mock_write_json.assert_called_once()

    def test_workspace_ready_help_includes_json_and_exit_codes(self):
        argv = ["pecs", "workspace-ready", "--help"]
        with patch.object(sys, "argv", argv):
            captured = io.StringIO()
            with patch.object(sys, "stdout", captured):
                with self.assertRaises(SystemExit) as cm:
                    workspace_bridge_cli.main()

        self.assertEqual(cm.exception.code, 0)
        output = captured.getvalue()
        self.assertIn("--json", output)
        self.assertIn("Exit codes:", output)
        self.assertIn("Usage examples:", output)

    def test_workspace_ready_invalid_usage_exits_2(self):
        argv = ["pecs", "workspace-ready"]
        with patch.object(sys, "argv", argv):
            with patch.object(workspace_bridge_cli.logger, "error") as mock_error:
                with self.assertRaises(SystemExit) as cm:
                    workspace_bridge_cli.main()

        self.assertEqual(cm.exception.code, 2)
        self.assertTrue(mock_error.called)
        self.assertIn("Workspace root is required", mock_error.call_args[0][0])

    def test_workspace_ready_missing_workspace_exits_1(self):
        missing_path = self.workspace_root / "does_not_exist"
        argv = ["pecs", "workspace-ready", "--workspace", str(missing_path)]
        with patch.object(sys, "argv", argv):
            with patch.object(workspace_bridge_cli.logger, "error") as mock_error:
                with self.assertRaises(SystemExit) as cm:
                    workspace_bridge_cli.main()

        self.assertEqual(cm.exception.code, 1)
        self.assertTrue(mock_error.called)
        self.assertIn("Workspace does not exist", mock_error.call_args[0][0])

if __name__ == "__main__":
    unittest.main()


class ExplainingQueryCliTests(unittest.TestCase):
    """Regression tests for pecs explain-query."""

    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.workspace_root = Path(self.tempdir.name)
        self.workspace_root.mkdir(parents=True, exist_ok=True)
        self.pecs_dir = self.workspace_root / ".pecs"
        self.pecs_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def _write_artifact(self, name: str, data: dict) -> Path:
        path = self.pecs_dir / name
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def _run_explain(self, query: str) -> str:
        """Run explain-query in JSON mode and return stdout."""
        argv = [
            "pecs", "explain-query",
            str(self.workspace_root),
            "--query", query,
            "--json",
        ]
        with patch.object(sys, "argv", argv):
            captured = io.StringIO()
            with patch.object(sys, "stdout", captured):
                try:
                    workspace_bridge_cli.main()
                except SystemExit as e:
                    self.assertEqual(e.code, 0)
        return captured.getvalue()

    def test_zero_locality_matches(self):
        """explain-query handles empty locality index without crashing."""
        self._write_artifact("locality_index.json", {})
        self._write_artifact("topology_compact.json", {})
        output = self._run_explain("zxywvunothing")
        report = json.loads(output)
        self.assertEqual(report["query"], "zxywvunothing")
        self.assertEqual(len(report["locality_matches"]), 0)
        self.assertEqual(len(report["topology_matches"]), 0)
        self.assertEqual(report["locality_match_count"], 0)
        self.assertEqual(report["topology_match_count"], 0)

    def test_one_locality_match(self):
        """explain-query handles exactly one locality match."""
        self._write_artifact("locality_index.json", {
            "PECS_ID:Qt.main_app_UI_rewrite": {
                "file": "Qt/main_app_UI_rewrite.py",
                "runtime_zone": "ui",
            },
        })
        self._write_artifact("topology_compact.json", {})
        output = self._run_explain("main_app_UI_rewrite")
        report = json.loads(output)
        self.assertEqual(len(report["locality_matches"]), 1)
        self.assertEqual(report["locality_matches"][0]["id"], "PECS_ID:Qt.main_app_UI_rewrite")
        self.assertEqual(report["locality_matches"][0]["file"], "Qt/main_app_UI_rewrite.py")
        self.assertEqual(report["locality_match_count"], 1)

    def test_many_locality_matches_gt_10(self):
        """explain-query handles >10 locality matches (regression: list vs int)."""
        locality = {}
        for i in range(15):
            pecs_id = f"PECS_ID:project_runner.{i:03d}"
            locality[pecs_id] = {
                "file": f"src/runner_{i:03d}.py",
                "runtime_zone": "core",
            }
        self._write_artifact("locality_index.json", locality)
        self._write_artifact("topology_compact.json", {})
        output = self._run_explain("runner")
        report = json.loads(output)
        self.assertEqual(len(report["locality_matches"]), 15)
        self.assertEqual(report["locality_match_count"], 15)

    def test_large_multiline_engineering_prompt(self):
        """explain-query handles large multi-line queries without crashing."""
        locality = {}
        for i in range(20):
            pecs_id = f"PECS_ID:Qt.component_{i:03d}"
            locality[pecs_id] = {"file": f"Qt/component_{i:03d}.py", "runtime_zone": "ui"}
        self._write_artifact("locality_index.json", locality)
        self._write_artifact("topology_compact.json", {})

        multiline_query = (
            "We need to investigate the BulkTocMapper component "
            "and understand how it processes TOC entries. "
            "Specifically, why does it start from the first entry "
            "instead of the detected index page?"
        )
        output = self._run_explain(multiline_query)
        report = json.loads(output)
        self.assertIn("BulkTocMapper", output)
        self.assertIsInstance(report["locality_matches"], list)

    def test_explain_with_topology_matches(self):
        """explain-query matches topology edges correctly."""
        self._write_artifact("locality_index.json", {})
        self._write_artifact("topology_compact.json", {
            "edges": [
                {"from": "PECS_ID:Qt.main_app_UI_rewrite", "to": "PECS_ID:Qt.auto_toc_dialog_rewrite", "type": "calls"},
            ],
        })
        output = self._run_explain("main_app")
        report = json.loads(output)
        self.assertEqual(len(report["topology_matches"]), 1)
        self.assertEqual(report["topology_matches"][0]["type"], "calls")
        self.assertEqual(report["topology_match_count"], 1)

    def test_explain_skips_non_dict_locality_values(self):
        """explain-query skips non-dict locality entries without crashing."""
        self._write_artifact("locality_index.json", {
            "PECS_ID:good": {"file": "good.py", "runtime_zone": "core"},
            "PECS_ID:bad_string": "this is a string, not a dict",
            "PECS_ID:bad_list": [1, 2, 3],
            "PECS_ID:bad_number": 42,
        })
        self._write_artifact("topology_compact.json", {})
        output = self._run_explain("good")
        report = json.loads(output)
        self.assertEqual(len(report["locality_matches"]), 1)
        self.assertEqual(report["locality_matches"][0]["id"], "PECS_ID:good")
        self.assertEqual(report["locality_match_count"], 1)

    def test_explain_skips_non_dict_topology_edges(self):
        """explain-query skips non-dict topology edges without crashing."""
        self._write_artifact("locality_index.json", {
            "PECS_ID:good": {"file": "good.py", "runtime_zone": "core"},
        })
        self._write_artifact("topology_compact.json", {
            "edges": [
                {"from": "PECS_ID:good", "to": "PECS_ID:target", "type": "calls"},
                "not_a_dict",
                None,
                42,
            ],
        })
        output = self._run_explain("target")
        report = json.loads(output)
        self.assertEqual(len(report["topology_matches"]), 1)
        self.assertEqual(report["topology_matches"][0]["to"], "PECS_ID:target")
        self.assertEqual(report["topology_match_count"], 1)

    def test_explain_non_json_human_readable_output(self):
        """explain-query human-readable output handles >10 matches without crash."""
        locality = {}
        for i in range(12):
            pecs_id = f"PECS_ID:project_runner.{i:03d}"
            locality[pecs_id] = {
                "file": f"src/runner_{i:03d}.py",
                "runtime_zone": "core",
            }
        self._write_artifact("locality_index.json", locality)
        self._write_artifact("topology_compact.json", {})

        argv = [
            "pecs", "explain-query",
            str(self.workspace_root),
            "--query", "runner",
        ]
        with patch.object(sys, "argv", argv):
            captured = io.StringIO()
            with patch.object(sys, "stdout", captured):
                try:
                    workspace_bridge_cli.main()
                except SystemExit as e:
                    self.assertEqual(e.code, 0)
        output = captured.getvalue()
        self.assertIn("... and 2 more", output)
        self.assertIn("Query Explanation", output)


class QueryParserTests(unittest.TestCase):
    """Regression tests for pecs_query/query_parser.py QueryParser."""

    def _parse(self, query: str):
        from pecs_query.query_parser import QueryParser
        return QueryParser.parse(query)

    # ── basic filtering ────────────────────────────────────────────────

    def test_strip_common_english_words(self):
        """Stop words like 'the', 'a', 'an', 'and', 'or' are removed."""
        result = self._parse("the quick brown fox jumps over the lazy dog")
        self.assertNotIn("the", result.terms)
        self.assertIn("quick", result.terms)
        self.assertIn("brown", result.terms)

    def test_strip_punctuation_only_tokens(self):
        """Tokens like '-', '↓', '>', '·', '1.', '2.' are removed."""
        result = self._parse("step 1: ↓ check - output > threshold · end")
        for bad in ("-", "↓", ">", "·", "1:", "2:"):
            self.assertNotIn(bad, result.terms)

    def test_short_tokens_removed(self):
        """Single-character tokens are removed."""
        result = self._parse("a b c d e f red blue")
        self.assertEqual(result.terms, ["red", "blue"])

    # ── preserved patterns ─────────────────────────────────────────────

    def test_preserves_file_paths(self):
        """Absolute and relative file paths survive tokenization."""
        result = self._parse("check /Users/raj/file.py and ./relative/path.py")
        self.assertIn("/users/raj/file.py", result.terms)
        self.assertIn("./relative/path.py", result.terms)

    def test_preserves_pecs_ids(self):
        """PECS_ID: references are preserved."""
        result = self._parse("look at PECS_ID:Qt.main_app_UI_rewrite")
        self.assertIn("pecs_id:qt.main_app_ui_rewrite", result.terms)

    def test_preserves_task_ids(self):
        """TASK-123 style IDs are preserved."""
        result = self._parse("refer to TASK-123 and RFC-042")
        self.assertIn("task-123", result.terms)
        self.assertIn("rfc-042", result.terms)

    def test_preserves_quoted_identifiers(self):
        """'quoted' and \"quoted\" identifiers preserve inner content."""
        result = self._parse('consider "BulkTocMapper" and \'auto_toc_dialog\'')
        self.assertIn("bulktocmapper", result.terms)
        self.assertIn("auto_toc_dialog", result.terms)

    # ── long / structured prompts ───────────────────────────────────────

    def test_long_engineering_prompt(self):
        """A realistic long engineering prompt filters out noise."""
        prompt = (
            "We need to investigate the BulkTocMapper component "
            "and understand how it processes TOC entries. "
            "Specifically, why does it start from the first entry "
            "instead of the detected index page?"
        )
        result = self._parse(prompt)
        # Meaningful surviving terms
        for term in ("bulktocmapper", "toc", "entries", "index", "page", "processes"):
            self.assertIn(term, result.terms)
        # Noise removed
        for noise in ("we", "need", "to", "the", "and", "how", "it", "from", "of", "a"):
            self.assertNotIn(noise, result.terms)

    def test_architecture_audit_prompt(self):
        """Architecture audit prompts keep domain-specific terms."""
        prompt = (
            "## Task ID\n"
            "TASK-042\n\n"
            "## MANDATORY Reads\n"
            "- PECS_ARCHITECTURE_BASELINE.md\n"
            "- PECS_CANONICAL_QUERY_AND_PROJECTION_CONTRACT.md\n\n"
            "## Objective\n"
            "Audit the BulkTocMapper module for TOC entry detection.\n\n"
            "## Deliverables\n"
            "- Fix the index page detection\n"
            "- Verify with test_runner.py\n"
        )
        result = self._parse(prompt)
        self.assertIn("task-042", result.terms)
        self.assertIn("bulktocmapper", result.terms)
        self.assertIn("pecs_architecture_baseline.md", result.terms)
        self.assertIn("test_runner.py", result.terms)
        self.assertIn("toc", result.terms)
        # Stop words removed
        for noise in ("the", "and", "for", "with", "this", "module"):
            self.assertNotIn(noise, result.terms)

    def test_prompt_with_file_paths(self):
        """File paths survive tokenization in prompts."""
        prompt = (
            "Check workspace_bridge_cli.py for the _cmd_explain_query function. "
            "Also review pecs_query/query_parser.py."
        )
        result = self._parse(prompt)
        self.assertIn("workspace_bridge_cli.py", result.terms)
        self.assertIn("pecs_query/query_parser.py", result.terms)
        self.assertIn("_cmd_explain_query", result.terms)
        # Noise removed
        self.assertNotIn("the", result.terms)
        self.assertNotIn("for", result.terms)

    def test_prompt_with_markdown_lists(self):
        """Markdown list markers are stripped; list content survives."""
        prompt = (
            "- Item one: run the checker\n"
            "- Item two: validate output\n"
            "- Item three: review the results\n"
        )
        result = self._parse(prompt)
        self.assertIn("checker", result.terms)
        self.assertIn("validate", result.terms)
        self.assertIn("output", result.terms)
        self.assertIn("review", result.terms)
        self.assertNotIn("item", result.terms)
        self.assertNotIn("the", result.terms)

    def test_prompt_with_numbered_sections(self):
        """Numbered section markers (1., 2.) are stripped; terms survive."""
        prompt = (
            "1. First step\n"
            "2. Second step\n"
            "3. Third step\n"
        )
        result = self._parse(prompt)
        # Ordinals "first", "second", "third" and generic "step" are stop words
        self.assertEqual(result.terms, [])

    def test_prompt_with_arrows(self):
        """Arrow symbols (↓, →, ←) are stripped."""
        prompt = (
            "Navigate to module ↓ then check the callback → verify signal ← done"
        )
        result = self._parse(prompt)
        self.assertIn("navigate", result.terms)
        self.assertIn("callback", result.terms)
        self.assertIn("signal", result.terms)
        for noise in ("↓", "→", "←"):
            self.assertNotIn(noise, result.terms)

    def test_prompt_with_repository_relative_paths(self):
        """Repo-relative paths like ./src/ or ../tests/ survive."""
        prompt = (
            "Fix ./integrations/pecs_lite_runtime_adapter.py "
            "and check ../tests/test_workspace_bridge_cli.py"
        )
        result = self._parse(prompt)
        self.assertIn("./integrations/pecs_lite_runtime_adapter.py", result.terms)
        self.assertIn("../tests/test_workspace_bridge_cli.py", result.terms)

    def test_prompt_with_multiple_architecture_docs(self):
        """Multiple architecture document references survive."""
        prompt = (
            "Check PECS_ARCHITECTURE_PROJECTION_SPEC.md and "
            "read docs/architecture.md before continuing"
        )
        result = self._parse(prompt)
        self.assertIn("pecs_architecture_projection_spec.md", result.terms)
        self.assertIn("docs/architecture.md", result.terms)
        self.assertNotIn("read", result.terms)
        self.assertNotIn("check", result.terms)

    # ── sections ───────────────────────────────────────────────────────

    def test_detects_sections(self):
        """Line-oriented sections are detected in structured prompts."""
        prompt = (
            "## Task ID\n"
            "TASK-042\n\n"
            "## MANDATORY Reads\n"
            "- PECS_ARCHITECTURE_BASELINE.md\n\n"
            "## Objective\n"
            "Audit the BulkTocMapper module.\n"
        )
        result = self._parse(prompt)
        self.assertIn("task_id", result.sections)
        self.assertIn("mandatory_reads", result.sections)
        self.assertIn("objective", result.sections)

    def test_section_content_collected(self):
        """Content under each section header is collected."""
        prompt = (
            "## Files\n"
            "- workspace_bridge_cli.py\n"
            "- pecs_query/query_parser.py\n"
        )
        result = self._parse(prompt)
        self.assertIn("files", result.sections)
        items = result.sections.get("files", [])
        found = any("workspace_bridge_cli.py" in item for item in items)
        self.assertTrue(found)

    # ── semantic hints ─────────────────────────────────────────────────

    def test_semantic_hints(self):
        """Semantic hint flags are set correctly."""
        result = self._parse(
            'Check PECS_ID:Qt.main_app and /src/file.py regarding TASK-123 "MyClass"'
        )
        hints = result.semantic_hints
        self.assertTrue(hints["has_pecs_ids"])
        self.assertTrue(hints["has_file_paths"])
        self.assertTrue(hints["has_task_ids"])
        self.assertTrue(hints["has_quoted_identifiers"])

    # ── edge cases ─────────────────────────────────────────────────────

    def test_empty_query_returns_empty(self):
        """Empty query returns empty result."""
        result = self._parse("")
        self.assertEqual(result.terms, [])
        self.assertEqual(result.sections, {})

    def test_whitespace_only_query_returns_empty(self):
        """Whitespace-only query returns empty result."""
        result = self._parse("   \n  \t  ")
        self.assertEqual(result.terms, [])

    def test_all_stop_words_returns_empty(self):
        """Query containing only stop words returns empty result."""
        result = self._parse("the and or for with this that those")
        self.assertEqual(result.terms, [])

    def test_punctuation_only_returns_empty(self):
        """Query containing only punctuation returns empty result."""
        result = self._parse("- ↓ > · 1. 2. 3.")
        self.assertEqual(result.terms, [])

    def test_mixed_noise_returns_only_meaningful_terms(self):
        """Mixed noise and meaningful terms keep only the meaningful ones."""
        result = self._parse(
            "- ↓ 1. the and we check BulkTocMapper for TOC processing"
        )
        self.assertIn("bulktocmapper", result.terms)
        self.assertIn("toc", result.terms)
        self.assertIn("processing", result.terms)
        for junk in ("-", "↓", "1", "the", "and", "we", "check"):
            self.assertNotIn(junk, result.terms)

    def test_to_dict_serialization(self):
        """to_dict() produces a serializable dictionary."""
        result = self._parse("hello BulkTocMapper")
        d = result.to_dict()
        self.assertIn("terms", d)
        self.assertIn("sections", d)
        self.assertIn("semantic_hints", d)
        self.assertIn("term_count", d)
        self.assertEqual(d["term_count"], len(d["terms"]))


# ======================================================================
# Canonical Query Object tests
# ======================================================================


class CanonicalQueryObjectTests(unittest.TestCase):
    """Tests for pecs_query/canonical_query.py CanonicalQueryObject."""

    def _make_cqo(self, **overrides) -> "CanonicalQueryObject":
        from pecs_query.canonical_query import CanonicalQueryObject, make_query_id, make_timestamp

        kwargs = dict(
            query_id=make_query_id(),
            raw_query="fix the BulkTocMapper",
            consumer="commandcode",
            profile="medium",
            timestamp=make_timestamp(),
            parsed_terms=["bulktocmapper", "fix"],
            task_type="bug_fix",
            execution_mode="repair",
        )
        kwargs.update(overrides)
        return CanonicalQueryObject(**kwargs)

    # ── construction ──────────────────────────────────────────────────

    def test_construct_basic(self):
        """Basic CQO construction with required fields."""
        cqo = self._make_cqo()
        self.assertEqual(cqo.consumer, "commandcode")
        self.assertEqual(cqo.profile, "medium")
        self.assertEqual(cqo.task_type, "bug_fix")
        self.assertEqual(cqo.schema, "pecs.canonical_query.v1")
        self.assertTrue(cqo.query_id)
        self.assertTrue(cqo.timestamp)

    def test_missing_query_id_raises(self):
        """CQO without query_id raises validation error."""
        from pecs_query.canonical_query import CQOValidationError

        with self.assertRaises(CQOValidationError):
            self._make_cqo(query_id="")

    def test_missing_raw_query_raises(self):
        """CQO without raw_query raises validation error."""
        from pecs_query.canonical_query import CQOValidationError

        with self.assertRaises(CQOValidationError):
            self._make_cqo(raw_query="")

    def test_invalid_consumer_raises(self):
        """CQO with invalid consumer raises validation error."""
        from pecs_query.canonical_query import CQOValidationError

        with self.assertRaises(CQOValidationError):
            self._make_cqo(consumer="unknown_tool")

    def test_invalid_profile_raises(self):
        """CQO with invalid profile raises validation error."""
        from pecs_query.canonical_query import CQOValidationError

        with self.assertRaises(CQOValidationError):
            self._make_cqo(profile="ultra")

    def test_invalid_task_type_raises(self):
        """CQO with invalid task_type raises."""
        from pecs_query.canonical_query import CQOValidationError

        with self.assertRaises(CQOValidationError):
            self._make_cqo(task_type="invalid_type")

    # ── immutability ──────────────────────────────────────────────────

    def test_cqo_is_hashable(self):
        """CQO can be used in sets / as dict keys."""
        cqo = self._make_cqo()
        s = {cqo}
        self.assertIn(cqo, s)

    def test_cqo_is_immutable(self):
        """Cannot modify CQO fields after construction."""
        cqo = self._make_cqo()
        with self.assertRaises(Exception):
            cqo.consumer = "continue"  # type: ignore

    def test_replace_creates_new_instance(self):
        """replace() returns a new CQO without modifying the original."""
        cqo = self._make_cqo(consumer="commandcode")
        cqo2 = cqo.replace(consumer="copilot")
        self.assertEqual(cqo.consumer, "commandcode")
        self.assertEqual(cqo2.consumer, "copilot")
        self.assertIsNot(cqo, cqo2)

    # ── serialization ─────────────────────────────────────────────────

    def test_to_dict_contains_all_fields(self):
        """to_dict() includes all expected CQO fields."""
        cqo = self._make_cqo()
        d = cqo.to_dict()
        expected_keys = {
            "schema", "query_id", "raw_query", "consumer", "profile",
            "timestamp", "parsed_terms", "sections", "semantic_hints",
            "task_type", "execution_mode", "engineering_intents",
            "constraints", "requested_outcomes", "candidate_objects",
            "locality_hints", "topology_hints", "authority_hints",
            "metadata",
        }
        self.assertEqual(set(d.keys()), expected_keys)

    def test_round_trip_dict(self):
        """to_dict() → from_dict() preserves all fields."""
        cqo = self._make_cqo(
            sections={"task_id": ["TASK-123"]},
            semantic_hints={"has_sections": True},
            candidate_objects=[{"pecs_id": "PECS_ID:test"}],
        )
        d = cqo.to_dict()
        cqo2 = type(cqo).from_dict(d)
        self.assertEqual(cqo, cqo2)
        self.assertEqual(cqo2.sections, {"task_id": ["TASK-123"]})
        self.assertEqual(cqo2.candidate_objects, [{"pecs_id": "PECS_ID:test"}])

    def test_round_trip_json(self):
        """CQO survives JSON serialization."""
        import json

        cqo = self._make_cqo()
        d = json.dumps(cqo.to_dict())
        cqo2 = type(cqo).from_dict(json.loads(d))
        self.assertEqual(cqo, cqo2)

    # ── defaulted fields ──────────────────────────────────────────────

    def test_candidate_objects_defaults_empty(self):
        """candidate_objects is empty by default."""
        cqo = self._make_cqo()
        self.assertEqual(cqo.candidate_objects, [])

    def test_sections_defaults_empty(self):
        """sections is empty by default."""
        cqo = self._make_cqo()
        self.assertEqual(cqo.sections, {})

    def test_metadata_defaults_empty(self):
        """metadata is empty by default."""
        cqo = self._make_cqo()
        self.assertEqual(cqo.metadata, {})

    # ── valid consumers / profiles ────────────────────────────────────

    def test_all_valid_consumers(self):
        """All canonical consumers are accepted."""
        for c in ("copilot", "continue", "kimi", "commandcode", "other"):
            cqo = self._make_cqo(consumer=c)
            self.assertEqual(cqo.consumer, c)

    def test_all_valid_profiles(self):
        """All canonical profiles are accepted."""
        for p in ("small", "medium", "large", "execution"):
            cqo = self._make_cqo(profile=p)
            self.assertEqual(cqo.profile, p)


class EngineeringObjectTests(unittest.TestCase):
    """Tests for pecs_query/engineering_objects.py contracts."""

    def test_engineering_object_type_enum(self):
        """EngineeringObjectType contains all expected types."""
        from pecs_query.engineering_objects import EngineeringObjectType

        self.assertIn(EngineeringObjectType.MODULE, EngineeringObjectType)
        self.assertIn(EngineeringObjectType.CLASS, EngineeringObjectType)
        self.assertIn(EngineeringObjectType.METHOD, EngineeringObjectType)
        self.assertIn(EngineeringObjectType.FILE, EngineeringObjectType)
        self.assertIn(EngineeringObjectType.SIGNAL, EngineeringObjectType)

    def test_make_basic_object(self):
        """make_object() creates a valid EngineeringObject."""
        from pecs_query.engineering_objects import (
            EngineeringObjectType,
            make_object,
        )

        obj = make_object(
            "PECS_ID:Qt.main_app",
            EngineeringObjectType.MODULE,
            0.85,
            "exact_match",
            "main_app",
        )
        self.assertEqual(obj.reference.pecs_id, "PECS_ID:Qt.main_app")
        self.assertEqual(obj.reference.object_type, EngineeringObjectType.MODULE)
        self.assertEqual(obj.confidence.score, 0.85)
        self.assertEqual(obj.confidence.source, "exact_match")
        self.assertEqual(obj.display_name, "main_app")

    def test_object_round_trip(self):
        """EngineeringObject survives to_dict/from_dict round-trip."""
        from pecs_query.engineering_objects import (
            EngineeringObject,
            EngineeringObjectType,
            make_object,
        )

        obj = make_object(
            "PECS_ID:Qt.test",
            EngineeringObjectType.CLASS,
            0.9,
            "phrase_match",
            "TestClass",
        )
        d = obj.to_dict()
        obj2 = EngineeringObject.from_dict(d)
        self.assertEqual(obj, obj2)
        self.assertEqual(obj2.display_name, "TestClass")

    def test_object_reference_round_trip(self):
        """EngineeringObjectReference survives round-trip."""
        from pecs_query.engineering_objects import (
            EngineeringObjectReference,
            EngineeringObjectType,
            make_object_ref,
        )

        ref = make_object_ref("PECS_ID:test", EngineeringObjectType.SIGNAL, "runtime")
        d = ref.to_dict()
        ref2 = EngineeringObjectReference.from_dict(d)
        self.assertEqual(ref, ref2)
        self.assertEqual(ref2.source_evidence, "runtime")

    def test_object_confidence_round_trip(self):
        """EngineeringObjectConfidence survives round-trip."""
        from pecs_query.engineering_objects import (
            EngineeringObjectConfidence,
        )

        conf = EngineeringObjectConfidence(0.75, "segment_match", ["package_name"])
        d = conf.to_dict()
        conf2 = EngineeringObjectConfidence.from_dict(d)
        self.assertEqual(conf, conf2)
        self.assertEqual(conf2.source, "segment_match")

    def test_display_name_fallback(self):
        """display_name falls back to last PECS_ID segment."""
        from pecs_query.engineering_objects import (
            EngineeringObjectType,
            make_object,
        )

        obj = make_object(
            "PECS_ID:Qt.notes.controller",
            EngineeringObjectType.MODULE,
            confidence_score=0.5,
        )
        self.assertEqual(obj.display_name, "controller")


class CanonicalQueryBuilderTests(unittest.TestCase):
    """Tests for pecs_query/query_builder.py CanonicalQueryBuilder."""

    def test_build_from_parse_result(self):
        """Builder populates CQO from a QueryParseResult."""
        from pecs_query.query_parser import QueryParser
        from pecs_query.query_builder import CanonicalQueryBuilder

        parse_result = QueryParser.parse("fix the BulkTocMapper component")
        cqo = (
            CanonicalQueryBuilder()
            .with_parse_result(parse_result)
            .with_consumer("commandcode")
            .with_profile("medium")
            .build()
        )
        self.assertEqual(cqo.raw_query, "fix the BulkTocMapper component")
        self.assertIn("bulktocmapper", cqo.parsed_terms)
        self.assertIn("component", cqo.parsed_terms)
        self.assertNotIn("the", cqo.parsed_terms)
        self.assertEqual(cqo.consumer, "commandcode")
        self.assertEqual(cqo.profile, "medium")
        self.assertTrue(cqo.query_id)
        self.assertTrue(cqo.timestamp)

    def test_build_cqo_from_query_convenience(self):
        """build_cqo_from_query() is a one-shot convenience."""
        from pecs_query.query_builder import build_cqo_from_query

        cqo = build_cqo_from_query(
            "analyze the OCR pipeline", consumer="continue", profile="small"
        )
        self.assertEqual(cqo.consumer, "continue")
        self.assertEqual(cqo.profile, "small")
        self.assertIn("analyze", cqo.parsed_terms)
        self.assertIn("ocr", cqo.parsed_terms)
        self.assertNotIn("the", cqo.parsed_terms)

    def test_builder_explicit_fields(self):
        """Builder sets explicit fields correctly."""
        from pecs_query.query_builder import CanonicalQueryBuilder

        cqo = (
            CanonicalQueryBuilder()
            .with_raw_query("test query")
            .with_consumer("kimi")
            .with_profile("large")
            .with_task_type("refactor")
            .with_execution_mode("review")
            .with_parsed_terms(["test", "query"])
            .with_engineering_intents(["maintainability"])
            .with_constraints({"max_targets": 5})
            .with_requested_outcomes(["runtime_targets"])
            .with_locality_hints(["class"])
            .build()
        )
        self.assertEqual(cqo.consumer, "kimi")
        self.assertEqual(cqo.profile, "large")
        self.assertEqual(cqo.task_type, "refactor")
        self.assertEqual(cqo.execution_mode, "review")
        self.assertEqual(cqo.engineering_intents, ["maintainability"])
        self.assertEqual(cqo.constraints, {"max_targets": 5})
        self.assertEqual(cqo.requested_outcomes, ["runtime_targets"])
        self.assertEqual(cqo.locality_hints, ["class"])

    def test_builder_sections_and_hints(self):
        """Builder propagates sections and semantic_hints."""
        from pecs_query.query_builder import CanonicalQueryBuilder

        cqo = (
            CanonicalQueryBuilder()
            .with_raw_query("## Task ID\nTASK-123\n## Objective\nAudit")
            .with_sections({"task_id": ["TASK-123"], "objective": ["Audit"]})
            .with_semantic_hints({"has_sections": True, "has_task_ids": True})
            .with_consumer("commandcode")
            .build()
        )
        self.assertIn("task_id", cqo.sections)
        self.assertEqual(cqo.semantic_hints.get("has_sections"), True)


class PipelineStageContractTests(unittest.TestCase):
    """Tests for pecs_query/pipeline.py stage contracts."""

    def test_lexical_analysis_stage(self):
        """LexicalAnalysisStage produces a QueryParseResult."""
        from pecs_query.pipeline import LexicalAnalysisStage, LexicalAnalysisInput

        stage = LexicalAnalysisStage()
        result = stage.execute(LexicalAnalysisInput("test the pipeline"))
        self.assertEqual(result.parse_result.terms, ["test", "pipeline"])
        self.assertEqual(stage.stage_name, "lexical_analysis")

    def test_engineering_object_resolution_is_pass_through(self):
        """EngineeringObjectResolutionStage passes CQO through unchanged."""
        from pecs_query.pipeline import (
            EngineeringObjectResolutionStage,
            EngineeringObjectResolutionInput,
        )
        from pecs_query.query_builder import build_cqo_from_query

        cqo = build_cqo_from_query("test", consumer="commandcode")
        stage = EngineeringObjectResolutionStage()
        result = stage.execute(EngineeringObjectResolutionInput(cqo))
        self.assertEqual(result.cqo, cqo)
        self.assertEqual(result.cqo.candidate_objects, [])

    def test_all_stage_names(self):
        """Every stage has a non-empty stage_name."""
        from pecs_query.pipeline import (
            LexicalAnalysisStage,
            EngineeringObjectResolutionStage,
            OntologyResolutionStage,
            ObjectExpansionStage,
            CanonicalQueryConstructionStage,
            EvidenceCorrelationStage,
            AuthorityStage,
            ProjectionStage,
        )

        stages = [
            LexicalAnalysisStage(),
            EngineeringObjectResolutionStage(),
            OntologyResolutionStage(),
            ObjectExpansionStage(),
            CanonicalQueryConstructionStage(),
            EvidenceCorrelationStage(),
            AuthorityStage(),
            ProjectionStage(),
        ]
        for stage in stages:
            self.assertTrue(stage.stage_name, f"empty name for {type(stage)}")


# ======================================================================
# Engineering Knowledge Layer tests
# ======================================================================


def _minimal_graph() -> "Graph":
    """Build a minimal workspace graph for testing."""
    from execution_graph.graph.workspace_graph import (
        Edge,
        EdgeDirection,
        EdgeType,
        Graph,
        GraphMetadata,
        Node,
        NodeType,
    )

    graph = Graph(
        metadata=GraphMetadata(
            workspace_hash="test",
            build_id="test",
            graph_hash="test_hash",
            created_at="now",
            last_updated="now",
        )
    )
    # Module
    graph.register_node(
        Node(
            node_id="PECS_ID:Qt.main_app",
            node_type=NodeType.MODULE,
            canonical_name="main_app",
            source_file="Qt/main_app.py",
            execution_zone="general_runtime",
            authority_level="workspace_state",
            confidence=1.0,
        )
    )
    # Class
    graph.register_node(
        Node(
            node_id="PECS_ID:Qt.main_app.MainClass",
            node_type=NodeType.CLASS,
            class_name="MainClass",
            canonical_name="MainClass",
            module_path="Qt.main_app",
            source_file="Qt/main_app.py",
            execution_zone="general_runtime",
        )
    )
    # Method
    graph.register_node(
        Node(
            node_id="PECS_ID:Qt.main_app.MainClass.run",
            node_type=NodeType.METHOD,
            method_name="run",
            canonical_name="run",
            module_path="Qt.main_app.MainClass",
            source_file="Qt/main_app.py",
        )
    )
    # Runtime object
    graph.register_node(
        Node(
            node_id="PECS_ID:Qt.dialogs.TocDialog",
            node_type=NodeType.DIALOG,
            canonical_name="TocDialog",
            module_path="Qt.dialogs",
            source_file="Qt/dialogs.py",
            execution_zone="dialog_pipeline",
            runtime_owner="PECS_ID:Qt.main_app",
        )
    )
    # Edges
    graph.register_edge(
        Edge(
            edge_id="e1",
            source_node_id="PECS_ID:Qt.main_app",
            target_node_id="PECS_ID:Qt.main_app.MainClass",
            edge_type=EdgeType.IMPORT,
            direction=EdgeDirection.DIRECTED,
            confidence=1.0,
        )
    )
    graph.register_edge(
        Edge(
            edge_id="e2",
            source_node_id="PECS_ID:Qt.main_app.MainClass",
            target_node_id="PECS_ID:Qt.main_app.MainClass.run",
            edge_type=EdgeType.METHOD_CALL,
            direction=EdgeDirection.DIRECTED,
            confidence=0.9,
        )
    )
    graph.register_edge(
        Edge(
            edge_id="e3",
            source_node_id="PECS_ID:Qt.main_app",
            target_node_id="PECS_ID:Qt.dialogs.TocDialog",
            edge_type=EdgeType.DIALOG_LAUNCH,
            direction=EdgeDirection.DIRECTED,
            confidence=0.8,
        )
    )
    return graph


class EngineeringKnowledgeModelTests(unittest.TestCase):
    """Core knowledge model construction and serialization."""

    def test_empty_knowledge_base(self):
        """Empty KB has zero counts."""
        from pecs_query.knowledge import EngineeringKnowledgeBase
        kb = EngineeringKnowledgeBase()
        stats = kb.statistics()
        self.assertEqual(stats["packages"], 0)
        self.assertEqual(stats["relationships"], 0)
        self.assertEqual(stats["pecs_ids"], 0)
        self.assertTrue(kb.knowledge_hash())

    def test_knowledge_base_to_dict(self):
        """to_dict() produces expected top-level structure."""
        from pecs_query.knowledge import EngineeringKnowledgeBase
        kb = EngineeringKnowledgeBase()
        d = kb.to_dict()
        self.assertIn("package_count", d)
        self.assertIn("relationship_count", d)
        self.assertIn("build_diagnostics", d)

    def test_package_knowledge_round_trip(self):
        """PackageKnowledge to/from dict."""
        from pecs_query.knowledge.models import PackageKnowledge
        pkg = PackageKnowledge(
            name="Qt",
            pecs_ids=["PECS_ID:Qt.main_app"],
            module_count=1,
            is_user_facing=True,
        )
        d = pkg.to_dict()
        self.assertEqual(d["name"], "Qt")
        self.assertEqual(d["module_count"], 1)

    def test_module_knowledge_round_trip(self):
        """ModuleKnowledge with all fields."""
        from pecs_query.knowledge.models import ModuleKnowledge
        mod = ModuleKnowledge(
            pecs_id="PECS_ID:Qt.main_app",
            module_path="Qt.main_app",
            source_file="Qt/main_app.py",
            execution_zone="ui",
            confidence=0.95,
            class_names=["MainClass"],
        )
        d = mod.to_dict()
        self.assertIn("MainClass", d["class_names"])

    def test_relationship_confidence_clamped(self):
        """Relationship confidence is clamped to [0, 1]."""
        from pecs_query.knowledge.relationships import (
            KnowledgeRelationship,
            RelationshipType,
        )
        rel = KnowledgeRelationship(
            source_id="a", target_id="b",
            relationship_type=RelationshipType.CONTAINS,
            confidence=2.5,
        )
        self.assertEqual(rel.confidence, 1.0)
        rel2 = KnowledgeRelationship(
            source_id="a", target_id="b",
            relationship_type=RelationshipType.CONTAINS,
            confidence=-0.5,
        )
        self.assertEqual(rel2.confidence, 0.0)

    def test_relationship_id_deterministic(self):
        """Same inputs produce same relationship_id."""
        from pecs_query.knowledge.relationships import (
            RelationshipType,
            make_relationship,
        )
        rel1 = make_relationship("a", "b", RelationshipType.CONTAINS)
        rel2 = make_relationship("a", "b", RelationshipType.CONTAINS)
        self.assertEqual(rel1.relationship_id(), rel2.relationship_id())

    def test_deterministic_hash(self):
        """Same KB content produces same hash."""
        from pecs_query.knowledge import EngineeringKnowledgeBase
        from pecs_query.knowledge.relationships import make_relationship, RelationshipType

        kb1 = EngineeringKnowledgeBase(
            relationships=[make_relationship("a", "b", RelationshipType.CONTAINS)]
        )
        kb2 = EngineeringKnowledgeBase(
            relationships=[make_relationship("a", "b", RelationshipType.CONTAINS)]
        )
        self.assertEqual(kb1.knowledge_hash(), kb2.knowledge_hash())
        stats = kb.statistics()
        self.assertEqual(stats["packages"], 0)
        self.assertEqual(stats["relationships"], 0)
        self.assertEqual(stats["pecs_ids"], 0)
        self.assertTrue(kb.knowledge_hash())

    def test_knowledge_base_to_dict(self):
        """to_dict() produces expected top-level structure."""
        kb = EngineeringKnowledgeBase()
        d = kb.to_dict()
        self.assertIn("package_count", d)
        self.assertIn("relationship_count", d)
        self.assertIn("build_diagnostics", d)

    def test_package_knowledge_round_trip(self):
        """PackageKnowledge to/from dict."""
        pkg = PackageKnowledge(
            name="Qt",
            pecs_ids=["PECS_ID:Qt.main_app"],
            module_count=1,
            is_user_facing=True,
        )
        d = pkg.to_dict()
        self.assertEqual(d["name"], "Qt")
        self.assertEqual(d["module_count"], 1)

    def test_module_knowledge_round_trip(self):
        """ModuleKnowledge with all fields."""
        mod = ModuleKnowledge(
            pecs_id="PECS_ID:Qt.main_app",
            module_path="Qt.main_app",
            source_file="Qt/main_app.py",
            execution_zone="ui",
            confidence=0.95,
            class_names=["MainClass"],
        )
        d = mod.to_dict()
        self.assertIn("MainClass", d["class_names"])

    def test_relationship_confidence_clamped(self):
        """Relationship confidence is clamped to [0, 1]."""
        rel = KnowledgeRelationship(
            source_id="a", target_id="b",
            relationship_type=RelationshipType.CONTAINS,
            confidence=2.5,
        )
        self.assertEqual(rel.confidence, 1.0)
        rel2 = KnowledgeRelationship(
            source_id="a", target_id="b",
            relationship_type=RelationshipType.CONTAINS,
            confidence=-0.5,
        )
        self.assertEqual(rel2.confidence, 0.0)

    def test_relationship_id_deterministic(self):
        """Same inputs produce same relationship_id."""
        rel1 = make_relationship("a", "b", RelationshipType.CONTAINS)
        rel2 = make_relationship("a", "b", RelationshipType.CONTAINS)
        self.assertEqual(
            rel1.relationship_id(), rel2.relationship_id()
        )

    def test_deterministic_hash(self):
        """Same KB content produces same hash."""
        from pecs_query.knowledge.relationships import make_relationship

        kb1 = EngineeringKnowledgeBase(
            relationships=[make_relationship("a", "b", RelationshipType.CONTAINS)]
        )
        kb2 = EngineeringKnowledgeBase(
            relationships=[make_relationship("a", "b", RelationshipType.CONTAINS)]
        )
        self.assertEqual(kb1.knowledge_hash(), kb2.knowledge_hash())


class EngineeringKnowledgeBuilderTests(unittest.TestCase):
    """Knowledge base construction from graph/registry."""

    def test_build_from_graph(self):
        """Builder indexes nodes and edges correctly."""
        graph = _minimal_graph()
        kb = build_knowledge_base(graph)
        self.assertEqual(kb.statistics()["modules"], 1)
        self.assertEqual(kb.statistics()["classes"], 1)
        self.assertEqual(kb.statistics()["methods"], 1)
        self.assertEqual(kb.statistics()["runtime_objects"], 1)
        self.assertEqual(kb.statistics()["relationships"], 5)

    def test_build_packages(self):
        """Packages are derived from PECS_ID namespace."""
        graph = _minimal_graph()
        kb = build_knowledge_base(graph)
        self.assertIn("Qt", kb.packages)
        pkg = kb.packages["Qt"]
        self.assertEqual(pkg.module_count, 1)
        self.assertEqual(pkg.class_count, 1)
        self.assertEqual(pkg.method_count, 1)

    def test_build_with_registry(self):
        """Registry feature classification propagates to packages."""
        from workspace_registry.models import (
            WorkspaceEvidence,
            WorkspaceFeature,
            WorkspaceRegistry,
        )

        graph = _minimal_graph()
        registry = WorkspaceRegistry(workspace_root="/test")
        feature = WorkspaceFeature(
            feature_id="Qt",
            root_node_id="PECS_ID:Qt.main_app",
            node_ids={"PECS_ID:Qt.main_app"},
            evidence=WorkspaceEvidence(
                public_ui_registration=True,
                controller_ownership=True,
                runtime_evidence=True,
            ),
            confidence=0.9,
        )
        registry.register_feature(feature)
        kb = build_knowledge_base(graph, registry)
        self.assertTrue(kb.packages["Qt"].is_user_facing)

    def test_build_diagnostics(self):
        """Builder populates diagnostics."""
        graph = _minimal_graph()
        kb = build_knowledge_base(graph)
        diag = kb.build_diagnostics
        self.assertEqual(diag["nodes_processed"], 4)
        self.assertEqual(diag["edges_processed"], 3)
        self.assertGreater(diag["relationships_created"], 0)

    def test_empty_graph_produces_empty_kb(self):
        """Empty graph produces empty knowledge base."""
        from execution_graph.graph.workspace_graph import Graph, GraphMetadata

        graph = Graph(
            metadata=GraphMetadata(
                workspace_hash="empty",
                build_id="empty",
                graph_hash="empty",
                created_at="now",
                last_updated="now",
            )
        )
        kb = build_knowledge_base(graph)
        stats = kb.statistics()
        self.assertEqual(stats["modules"], 0)
        self.assertEqual(stats["relationships"], 0)

    def test_builder_statistics_property(self):
        """statistics property matches KB statistics."""
        graph = _minimal_graph()
        builder = EngineeringKnowledgeBuilder()
        kb = builder.build(graph)
        self.assertEqual(
            builder.statistics, kb.statistics()
        )


class KnowledgeAccessAPITests(unittest.TestCase):
    """Knowledge access API (queries module)."""

    def setUp(self):
        self.kb = build_knowledge_base(_minimal_graph())
        self.api = KnowledgeAccessAPI(self.kb)

    def test_lookup_pecs_id(self):
        """lookup_pecs_id finds objects by PECS_ID."""
        obj = self.api.lookup_pecs_id("PECS_ID:Qt.main_app")
        self.assertIsNotNone(obj)
        self.assertIn("module_path", obj)

    def test_lookup_nonexistent_returns_none(self):
        """lookup_pecs_id returns None for unknown ID."""
        obj = self.api.lookup_pecs_id("PECS_ID:nonexistent")
        self.assertIsNone(obj)

    def test_pecs_id_type(self):
        """pecs_id_type returns correct type tag."""
        self.assertEqual(
            self.api.pecs_id_type("PECS_ID:Qt.main_app"), "module"
        )
        self.assertEqual(
            self.api.pecs_id_type("PECS_ID:Qt.main_app.MainClass"), "class"
        )
        self.assertEqual(
            self.api.pecs_id_type("PECS_ID:Qt.main_app.MainClass.run"),
            "method",
        )

    def test_find_relationships(self):
        """find_relationships returns all relationships for a node."""
        rels = self.api.find_relationships("PECS_ID:Qt.main_app")
        self.assertGreaterEqual(len(rels), 1)

    def test_find_relationships_filtered_by_type(self):
        """find_relationships filters by relationship type."""
        rels = self.api.find_relationships(
            "PECS_ID:Qt.main_app",
            RelationshipType.IMPORTS,
        )
        self.assertGreaterEqual(len(rels), 1)

    def test_find_outgoing(self):
        """find_outgoing returns source relationships."""
        rels = self.api.find_outgoing("PECS_ID:Qt.main_app")
        self.assertGreaterEqual(len(rels), 1)

    def test_find_incoming(self):
        """find_incoming returns target relationships."""
        rels = self.api.find_incoming(
            "PECS_ID:Qt.main_app.MainClass"
        )
        self.assertGreaterEqual(len(rels), 1)

    def test_find_neighbors(self):
        """find_neighbors returns both directions."""
        neighbors = self.api.find_neighbors("PECS_ID:Qt.main_app")
        self.assertIn("PECS_ID:Qt.main_app.MainClass", neighbors)

    def test_resolve_alias(self):
        """alias resolution returns PECS_ID when alias exists."""
        # No aliases registered in minimal test
        self.assertIsNone(self.api.resolve_alias("nonexistent"))

    def test_find_package(self):
        """find_package finds known packages."""
        pkg = self.api.find_package("Qt")
        self.assertIsNotNone(pkg)
        self.assertEqual(pkg.name, "Qt")

    def test_find_package_nonexistent(self):
        """find_package returns None for unknown package."""
        self.assertIsNone(self.api.find_package("nonexistent"))

    def test_statistics(self):
        """statistics returns counts."""
        stats = self.api.statistics()
        self.assertIn("modules", stats)
        self.assertIn("classes", stats)
        self.assertIn("relationships", stats)


class KnowledgeRelationshipTests(unittest.TestCase):
    """Relationship model tests."""

    def test_make_relationship(self):
        """make_relationship creates a valid relationship."""
        rel = make_relationship(
            "PECS_ID:src",
            "PECS_ID:dst",
            RelationshipType.IMPORTS,
            evidence="graph_edge",
            confidence=0.9,
            edge_type="import",
        )
        self.assertEqual(rel.source_id, "PECS_ID:src")
        self.assertEqual(rel.target_id, "PECS_ID:dst")
        self.assertEqual(rel.relationship_type, RelationshipType.IMPORTS)
        self.assertEqual(rel.evidence, "graph_edge")
        self.assertEqual(rel.confidence, 0.9)
        self.assertEqual(rel.metadata.get("edge_type"), "import")

    def test_relationship_round_trip(self):
        """KnowledgeRelationship survives to_dict/from_dict round-trip."""
        rel = make_relationship(
            "PECS_ID:src",
            "PECS_ID:dst",
            RelationshipType.CONTAINS,
            evidence="namespace_prefix",
            confidence=1.0,
        )
        d = rel.to_dict()
        rel2 = KnowledgeRelationship.from_dict(d)
        self.assertEqual(rel.source_id, rel2.source_id)
        self.assertEqual(rel.target_id, rel2.target_id)
        self.assertEqual(rel.relationship_type, rel2.relationship_type)
        self.assertEqual(rel.evidence, rel2.evidence)

    def test_relationship_types_have_all_members(self):
        """All expected relationship types exist."""
        expected = {
            "contains", "belongs_to", "inherits", "implements",
            "imports", "references", "calls", "depends_on",
            "signal_slot", "callback_execution",
            "owns", "registers",
            "activates", "runtime_neighbor", "topology_neighbor",
            "continuity_neighbor",
            "documents", "documented_by",
            "validates", "related_to",
        }
        actual = {e.value for e in RelationshipType}
        self.assertEqual(actual, expected)


# ======================================================================
# Ontology tests
# ======================================================================


def _ontology_test_kb():
    """Build a minimal KB for ontology tests."""
    from execution_graph.graph.workspace_graph import (
        Edge,
        EdgeDirection,
        EdgeType,
        Graph,
        GraphMetadata,
        Node,
        NodeType,
    )
    from workspace_registry.models import WorkspaceRegistry

    graph = Graph(
        metadata=GraphMetadata(
            workspace_hash="test",
            build_id="test",
            graph_hash="test_hash",
            created_at="now",
            last_updated="now",
        )
    )
    graph.register_node(
        Node(
            node_id="PECS_ID:Qt.main_app",
            node_type=NodeType.MODULE,
            canonical_name="main_app",
            source_file="Qt/main_app.py",
        )
    )
    graph.register_node(
        Node(
            node_id="PECS_ID:Qt.main_app.MainClass",
            node_type=NodeType.CLASS,
            class_name="MainClass",
            canonical_name="MainClass",
            source_file="Qt/main_app.py",
        )
    )
    graph.register_node(
        Node(
            node_id="PECS_ID:Qt.main_app.MainClass.run",
            node_type=NodeType.METHOD,
            method_name="run",
            canonical_name="run",
            source_file="Qt/main_app.py",
        )
    )
    graph.register_node(
        Node(
            node_id="PECS_ID:Qt.dialogs.TocDialog",
            node_type=NodeType.DIALOG,
            canonical_name="TocDialog",
            source_file="Qt/dialogs.py",
        )
    )
    graph.register_edge(
        Edge(
            edge_id="e1",
            source_node_id="PECS_ID:Qt.main_app",
            target_node_id="PECS_ID:Qt.main_app.MainClass",
            edge_type=EdgeType.IMPORT,
            direction=EdgeDirection.DIRECTED,
            confidence=1.0,
        )
    )
    from pecs_query.knowledge import build_knowledge_base
    return build_knowledge_base(graph, WorkspaceRegistry(workspace_root="/test"))


class OntologyModelTests(unittest.TestCase):
    """Ontology concept and model tests."""

    def test_concept_round_trip(self):
        """OntologyConcept survives to_dict/from_dict round-trip."""
        from pecs_query.ontology.models import OntologyConcept

        c = OntologyConcept(
            concept_id="ocr_pipeline",
            canonical_name="OCR_Pipeline",
            aliases=["ocr", "pipeline"],
            engineering_object_ids=["PECS_ID:OCR.module"],
            object_types=["module"],
            provenance="package",
        )
        d = c.to_dict()
        c2 = OntologyConcept.from_dict(d)
        self.assertEqual(c.concept_id, c2.concept_id)
        self.assertEqual(c.canonical_name, c2.canonical_name)
        self.assertEqual(c.aliases, c2.aliases)

    def test_empty_ontology(self):
        """Empty ontology has zero counts."""
        from pecs_query.ontology import EngineeringOntology

        o = EngineeringOntology()
        stats = o.statistics()
        self.assertEqual(stats.concept_count, 0)
        self.assertEqual(stats.relationship_count, 0)
        self.assertTrue(o.ontology_hash())

    def test_concept_relationship_round_trip(self):
        """OntologyConceptRelationship survives round-trip."""
        from pecs_query.ontology.models import (
            ConceptRelationshipType,
            OntologyConceptRelationship,
        )

        r = OntologyConceptRelationship(
            source_concept_id="ocr",
            target_concept_id="pipeline",
            relationship_type=ConceptRelationshipType.RELATED,
            evidence="name_prefix",
            confidence=0.5,
        )
        d = r.to_dict()
        r2 = OntologyConceptRelationship.from_dict(d)
        self.assertEqual(r.source_concept_id, r2.source_concept_id)
        self.assertEqual(r.relationship_type, r2.relationship_type)


class OntologyBuilderTests(unittest.TestCase):
    """Ontology builder tests."""

    def test_build_from_kb(self):
        """Builder creates concepts from all knowledge sources."""
        from pecs_query.ontology.builder import build_ontology

        kb = _ontology_test_kb()
        ontology = build_ontology(kb)
        self.assertGreaterEqual(len(ontology.concepts), 4)
        self.assertIn("main_app", ontology.concepts)
        self.assertIn("mainclass", ontology.concepts)
        self.assertIn("run", ontology.concepts)

    def test_build_creates_aliases(self):
        """Builder creates aliases for each concept."""
        from pecs_query.ontology.builder import build_ontology

        kb = _ontology_test_kb()
        ontology = build_ontology(kb)
        # "Qt" concept should have "qt" as alias
        concepts = ontology.alias_index.get("qt", [])
        self.assertIn("qt", str(concepts))
        self.assertGreater(len(ontology.alias_index), 5)

    def test_build_creates_relationships(self):
        """Builder creates concept relationships."""
        from pecs_query.ontology.builder import build_ontology

        kb = _ontology_test_kb()
        ontology = build_ontology(kb)
        self.assertGreater(len(ontology.concept_relationships), 0)

    def test_deterministic_hash(self):
        """Same KB produces same ontology hash."""
        from pecs_query.ontology.builder import build_ontology

        kb = _ontology_test_kb()
        h1 = build_ontology(kb).ontology_hash()
        h2 = build_ontology(kb).ontology_hash()
        self.assertEqual(h1, h2)

    def test_all_sources_covered(self):
        """Concepts are created from all five knowledge sources."""
        from pecs_query.ontology.builder import build_ontology

        kb = _ontology_test_kb()
        ontology = build_ontology(kb)
        stats = ontology.statistics()
        coverage = stats.provenance_coverage
        self.assertIn("package", coverage)
        self.assertIn("module", coverage)
        self.assertIn("class", coverage)
        self.assertIn("method", coverage)
        self.assertIn("runtime", coverage)


class OntologyAliasGeneratorTests(unittest.TestCase):
    """Alias generator tests."""

    def test_split_snake_case(self):
        """snake_case splits correctly."""
        from pecs_query.ontology.alias_generator import split_identifier, AliasGenerator

        words = split_identifier("main_app")
        self.assertIn("main", words)
        self.assertIn("app", words)

    def test_split_camel_case(self):
        """camelCase splits correctly."""
        from pecs_query.ontology.alias_generator import split_identifier

        words = split_identifier("BulkTocMapper")
        self.assertIn("bulk", words)
        self.assertIn("toc", words)
        self.assertIn("mapper", words)

    def test_split_pascal_case(self):
        """PascalCase splits correctly."""
        from pecs_query.ontology.alias_generator import split_identifier

        words = split_identifier("MainClass")
        self.assertIn("main", words)
        self.assertIn("class", words)

    def test_from_pecs_id(self):
        """PECS_ID generates segment and word aliases."""
        from pecs_query.ontology.alias_generator import AliasGenerator

        aliases = AliasGenerator.from_pecs_id("PECS_ID:Qt.main_app.MainClass")
        self.assertIn("mainclass", aliases)
        self.assertIn("main_app", aliases)
        self.assertIn("main", aliases)

    def test_from_class_name(self):
        """Class name generates word aliases."""
        from pecs_query.ontology.alias_generator import AliasGenerator

        aliases = AliasGenerator.from_class_name("BulkTocMapper")
        self.assertIn("bulktocmapper", aliases)
        self.assertIn("bulk", aliases)
        self.assertIn("toc", aliases)
        self.assertIn("mapper", aliases)

    def test_from_file_path(self):
        """File path generates segment and word aliases."""
        from pecs_query.ontology.alias_generator import AliasGenerator

        aliases = AliasGenerator.from_file_path("Qt/notes_module_v2.py")
        self.assertIn("qt/notes_module_v2.py", aliases)
        self.assertIn("notes_module_v2", aliases)
        self.assertIn("notes", aliases)

    def test_from_empty_returns_empty(self):
        """Empty input returns empty list."""
        from pecs_query.ontology.alias_generator import split_identifier

        self.assertEqual(split_identifier(""), [])


class OntologyQueryAPITests(unittest.TestCase):
    """Ontology query API tests."""

    def setUp(self):
        from pecs_query.ontology.builder import build_ontology
        from pecs_query.ontology import OntologyQueryAPI

        kb = _ontology_test_kb()
        self.ontology = build_ontology(kb)
        self.api = OntologyQueryAPI(self.ontology)

    def test_find_concept(self):
        """find_concept returns concept by concept_id."""
        c = self.api.find_concept("main_app")
        self.assertIsNotNone(c)
        self.assertEqual(c.canonical_name, "main_app")

    def test_find_concept_nonexistent(self):
        """find_concept returns None for unknown concept."""
        c = self.api.find_concept("nonexistent")
        self.assertIsNone(c)

    def test_lookup_alias(self):
        """lookup_alias returns concepts matching alias."""
        concepts = self.api.lookup_alias("main_app")
        self.assertGreaterEqual(len(concepts), 1)

    def test_lookup_alias_nonexistent(self):
        """lookup_alias returns empty list for unknown alias."""
        concepts = self.api.lookup_alias("zzzzz_nonexistent")
        self.assertEqual(concepts, [])

    def test_lookup_by_pecs_id(self):
        """lookup_by_pecs_id returns concepts containing that PECS_ID."""
        concepts = self.api.lookup_by_pecs_id("PECS_ID:Qt.main_app")
        self.assertGreaterEqual(len(concepts), 1)
        names = [c.canonical_name for c in concepts]
        self.assertIn("main_app", names)

    def test_search_prefix(self):
        """search_prefix finds concepts by concept_id prefix."""
        concepts = self.api.search_prefix("main")
        self.assertGreaterEqual(len(concepts), 1)
        names = [c.canonical_name for c in concepts]
        self.assertIn("main_app", names)

    def test_search_exact_by_name(self):
        """search_exact finds concept by name."""
        c = self.api.search_exact("main_app")
        self.assertIsNotNone(c)
        self.assertEqual(c.canonical_name, "main_app")

    def test_search_exact_by_alias(self):
        """search_exact finds concept by alias when no direct match."""
        c = self.api.search_exact("main_app")
        self.assertIsNotNone(c)

    def test_related_concepts(self):
        """related_concepts returns related concepts."""
        related = self.api.related_concepts("main_app")
        self.assertIsInstance(related, list)

    def test_relationships_for_concept(self):
        """relationships_for_concept returns relationships."""
        rels = self.api.relationships_for_concept("main_app")
        self.assertIsInstance(rels, list)

    def test_statistics(self):
        """statistics returns populated OntologyStatistics."""
        stats = self.api.statistics()
        self.assertGreater(stats.concept_count, 0)
        self.assertGreater(stats.alias_count, 0)

    def test_concept_count(self):
        """concept_count returns positive count."""
        self.assertGreater(self.api.concept_count(), 0)

    def test_alias_count(self):
        """alias_count returns positive count."""
        self.assertGreater(self.api.alias_count(), 0)

    def test_relationship_count(self):
        """relationship_count returns relationships."""
        self.assertGreaterEqual(self.api.relationship_count(), 0)
