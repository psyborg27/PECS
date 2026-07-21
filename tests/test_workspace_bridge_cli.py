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
