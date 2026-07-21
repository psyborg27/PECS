import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from validation.workspace_readiness_authority import (
    generate_workspace_readiness_report,
    READINESS_FILENAME,
)


class WorkspaceReadinessAuthorityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.workspace_root = Path(self.tempdir.name)
        self.workspace_root.mkdir(parents=True, exist_ok=True)
        pecs_dir = self.workspace_root / ".pecs"
        pecs_dir.mkdir(parents=True, exist_ok=True)
        (pecs_dir / "daemon.pid").write_text(str(os.getpid()), encoding="utf-8")

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def _write_json(self, path: Path, payload: dict) -> None:
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @patch("validation.workspace_readiness_authority.health_check")
    @patch("validation.workspace_readiness_authority.WorkspaceAssetsManager")
    @patch("validation.workspace_readiness_authority.validate_workspace_continuity")
    def test_ready_when_all_stages_pass(
        self,
        mock_validate_workspace_continuity,
        mock_assets_manager_class,
        mock_health_check,
    ):
        self._write_json(
            self.workspace_root / ".pecs" / "daemon_health.json",
            {
                "status": "healthy",
                "retrieval_ready": True,
                "topology_ready": True,
                "continuity_ready": True,
            },
        )
        self._write_json(
            self.workspace_root / ".pecs" / "workspace_graph_validation.json",
            {"valid": True},
        )
        self._write_json(
            self.workspace_root / ".pecs" / "workspace_registry_validation.json",
            {"valid": True},
        )
        self._write_json(
            self.workspace_root / ".pecs" / "daemon_state.json",
            {
                "runtime_reachable_count": 1,
                "topology_edge_count": 0,
                "runtime_locality_payload_count": 1,
            },
        )
        self._write_json(
            self.workspace_root / ".pecs" / "workspace_graph.json",
            {"graph": []},
        )
        self._write_json(
            self.workspace_root / ".pecs" / "workspace_registry.json",
            {"registry": []},
        )

        mock_health_check.return_value = {
            "workspace_exists": True,
            "dependencies": {"watchdog": "ok"},
            "package_installed": True,
            "daemon_script_exists": True,
        }
        mock_manager = mock_assets_manager_class.return_value
        mock_manager.verify_installation.return_value = {"valid": True}
        mock_validate_workspace_continuity.return_value = {
            "success": True,
            "canonical_verification": {"valid": True, "checks": {"consumer_integrations": True, "consumer_compliance": True}},
        }

        report = generate_workspace_readiness_report(self.workspace_root)
        self.assertTrue(report["ready"])
        self.assertEqual(report["overall"]["status"], "READY")
        self.assertEqual(report["daemon"]["status"], "PASS")
        self.assertEqual(report["workspace_graph"]["status"], "PASS")
        self.assertEqual(report["workspace_registry"]["status"], "PASS")

    def test_missing_bridge_reports_not_ready(self):
        self._write_json(
            self.workspace_root / ".pecs" / "daemon_health.json",
            {
                "status": "healthy",
                "retrieval_ready": True,
                "topology_ready": True,
                "continuity_ready": True,
            },
        )
        self._write_json(
            self.workspace_root / ".pecs" / "workspace_graph_validation.json",
            {"valid": True},
        )
        self._write_json(
            self.workspace_root / ".pecs" / "workspace_registry_validation.json",
            {"valid": True},
        )
        (self.workspace_root / ".pecs" / "daemon.pid").write_text("not-a-number", encoding="utf-8")

        report = generate_workspace_readiness_report(self.workspace_root)
        self.assertFalse(report["ready"])
        self.assertEqual(report["daemon"]["status"], "FAIL")

    def test_daemon_unavailable_reports_not_ready(self):
        self._write_json(
            self.workspace_root / ".pecs" / "daemon_health.json",
            {
                "status": "healthy",
                "retrieval_ready": True,
                "topology_ready": True,
                "continuity_ready": True,
            },
        )
        (self.workspace_root / ".pecs" / "daemon.pid").write_text("999999", encoding="utf-8")

        report = generate_workspace_readiness_report(self.workspace_root)
        self.assertFalse(report["ready"])
        self.assertEqual(report["daemon"]["status"], "FAIL")

    def test_graph_validation_failure_reports_not_ready(self):
        self._write_json(
            self.workspace_root / ".pecs" / "daemon_health.json",
            {
                "status": "healthy",
                "retrieval_ready": True,
                "topology_ready": True,
                "continuity_ready": True,
            },
        )
        self._write_json(
            self.workspace_root / ".pecs" / "workspace_graph_validation.json",
            {"valid": False},
        )
        self._write_json(
            self.workspace_root / ".pecs" / "workspace_registry_validation.json",
            {"valid": True},
        )

        report = generate_workspace_readiness_report(self.workspace_root)
        self.assertFalse(report["ready"])
        self.assertEqual(report["workspace_graph"]["status"], "FAIL")

    def test_registry_validation_failure_reports_not_ready(self):
        self._write_json(
            self.workspace_root / ".pecs" / "daemon_health.json",
            {
                "status": "healthy",
                "retrieval_ready": True,
                "topology_ready": True,
                "continuity_ready": True,
            },
        )
        self._write_json(
            self.workspace_root / ".pecs" / "workspace_graph_validation.json",
            {"valid": True},
        )
        self._write_json(
            self.workspace_root / ".pecs" / "workspace_registry_validation.json",
            {"valid": False},
        )

        report = generate_workspace_readiness_report(self.workspace_root)
        self.assertFalse(report["ready"])
        self.assertEqual(report["workspace_registry"]["status"], "FAIL")

    def test_canonical_validation_failure_reports_not_ready(self):
        self._write_json(
            self.workspace_root / ".pecs" / "daemon_health.json",
            {
                "status": "healthy",
                "retrieval_ready": True,
                "topology_ready": True,
                "continuity_ready": True,
            },
        )
        self._write_json(
            self.workspace_root / ".pecs" / "workspace_graph_validation.json",
            {"valid": True},
        )
        self._write_json(
            self.workspace_root / ".pecs" / "workspace_registry_validation.json",
            {"valid": True},
        )
        self._write_json(
            self.workspace_root / ".pecs" / "daemon_state.json",
            {
                "runtime_reachable_count": 1,
                "topology_edge_count": 0,
                "runtime_locality_payload_count": 1,
            },
        )

        # Force canonical validation to fail by leaving missing required assets.
        report = generate_workspace_readiness_report(self.workspace_root)
        self.assertFalse(report["ready"])
        self.assertEqual(report["canonical_validation"]["status"], "FAIL")

    def test_consumer_validation_failure_reports_not_ready(self):
        self._write_json(
            self.workspace_root / ".pecs" / "daemon_health.json",
            {
                "status": "healthy",
                "retrieval_ready": True,
                "topology_ready": True,
                "continuity_ready": True,
            },
        )
        self._write_json(
            self.workspace_root / ".pecs" / "workspace_graph_validation.json",
            {"valid": True},
        )
        self._write_json(
            self.workspace_root / ".pecs" / "workspace_registry_validation.json",
            {"valid": True},
        )
        self._write_json(
            self.workspace_root / ".pecs" / "daemon_state.json",
            {
                "runtime_reachable_count": 1,
                "topology_edge_count": 0,
                "runtime_locality_payload_count": 1,
            },
        )

        report = generate_workspace_readiness_report(self.workspace_root)
        self.assertFalse(report["ready"])
        self.assertEqual(report["consumer_integration"]["status"], "FAIL")

    def test_malformed_validation_artifacts_are_handled(self):
        (self.workspace_root / ".pecs" / "workspace_graph_validation.json").write_text("not-json", encoding="utf-8")
        report = generate_workspace_readiness_report(self.workspace_root)
        self.assertFalse(report["ready"])
        self.assertEqual(report["workspace_graph"]["status"], "FAIL")

    @patch("validation.workspace_readiness_authority.health_check")
    @patch("validation.workspace_readiness_authority.WorkspaceAssetsManager")
    @patch("validation.workspace_readiness_authority.validate_workspace_continuity")
    def test_readiness_artifact_is_written(
        self,
        mock_validate_workspace_continuity,
        mock_assets_manager_class,
        mock_health_check,
    ):
        self._write_json(
            self.workspace_root / ".pecs" / "daemon_health.json",
            {
                "status": "healthy",
                "retrieval_ready": True,
                "topology_ready": True,
                "continuity_ready": True,
            },
        )
        self._write_json(
            self.workspace_root / ".pecs" / "workspace_graph_validation.json",
            {"valid": True},
        )
        self._write_json(
            self.workspace_root / ".pecs" / "workspace_registry_validation.json",
            {"valid": True},
        )
        self._write_json(
            self.workspace_root / ".pecs" / "daemon_state.json",
            {
                "runtime_reachable_count": 1,
                "topology_edge_count": 0,
                "runtime_locality_payload_count": 1,
            },
        )
        self._write_json(
            self.workspace_root / ".pecs" / "workspace_graph.json",
            {"graph": []},
        )
        self._write_json(
            self.workspace_root / ".pecs" / "workspace_registry.json",
            {"registry": []},
        )

        mock_health_check.return_value = {
            "workspace_exists": True,
            "dependencies": {"watchdog": "ok"},
            "package_installed": True,
            "daemon_script_exists": True,
        }
        mock_manager = mock_assets_manager_class.return_value
        mock_manager.verify_installation.return_value = {"valid": True}
        mock_validate_workspace_continuity.return_value = {
            "success": True,
            "canonical_verification": {"valid": True, "checks": {"consumer_integrations": True, "consumer_compliance": True}},
        }

        report = generate_workspace_readiness_report(self.workspace_root)
        artifact = self.workspace_root / ".pecs" / READINESS_FILENAME
        self.assertTrue(artifact.exists())
        artifacts = json.loads(artifact.read_text(encoding="utf-8"))
        self.assertEqual(artifacts["schema"], "pecs.workspace_readiness.v1")
        self.assertEqual(artifacts["overall"]["status"], report["overall"]["status"])
        report_artifact = self.workspace_root / ".pecs" / "workspace_readiness_report.json"
        self.assertTrue(report_artifact.exists())
        report_payload = json.loads(report_artifact.read_text(encoding="utf-8"))
        self.assertEqual(report_payload["workspace"], str(self.workspace_root.resolve()))
        self.assertIn("artifact_inventory", report_payload)
        self.assertEqual(report_payload["failures"], [])
        self.assertEqual(report_payload["warnings"], [])
        self.assertEqual(report_payload["recommendations"], [])


if __name__ == "__main__":
    unittest.main()
