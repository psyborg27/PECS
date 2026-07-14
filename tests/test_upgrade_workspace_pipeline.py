import json
import subprocess
import tempfile
import unittest
from pathlib import Path

import pecs_pro.upgrade_workspace_pipeline as upgrade_module
from pecs_pro.upgrade_workspace_pipeline import UpgradeWorkspacePipeline


class UpgradeWorkspacePipelineTests(unittest.TestCase):
    def test_inspect_workspace_populates_plan_fields(self):
        repo_root = Path.cwd()
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_root = Path(tmpdir)
            pipeline = UpgradeWorkspacePipeline(workspace_root, repo_root)
            plan = pipeline.inspect_workspace()

            self.assertIsNotNone(plan.installed_version)
            self.assertEqual(plan.installer_version, plan.installed_version)
            self.assertIn(".github/copilot-instructions.md", plan.managed_asset_status)
            self.assertIsInstance(plan.generated_artifact_status, dict)
            self.assertIn("copilot", plan.consumer_config_present)
            self.assertIsInstance(plan.legacy_artifacts, list)

    def test_classify_artifacts_assigns_expected_labels(self):
        repo_root = Path.cwd()
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_root = Path(tmpdir)
            pipeline = UpgradeWorkspacePipeline(workspace_root, repo_root)
            plan = pipeline.inspect_workspace()
            plan = pipeline.classify_artifacts(plan)

            self.assertIn(".github/copilot-instructions.md", plan.classified_artifacts)
            self.assertEqual(plan.classified_artifacts[".github/copilot-instructions.md"], "MERGE")
            self.assertIn(".pecs/active_context.json", plan.classified_artifacts)
            self.assertEqual(plan.classified_artifacts[".pecs/active_context.json"], "REGENERATE")

    def test_run_pipeline_reuses_existing_logic(self):
        repo_root = Path.cwd()
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_root = Path(tmpdir)
            pipeline = UpgradeWorkspacePipeline(workspace_root, repo_root)
            pipeline.manager.install_assets = lambda upgrade, verify: {
                "warnings": [],
                "status": "success",
            }
            pipeline._run_workspace_bridge = lambda command: {"success": True}
            pipeline._ensure_workspace_graph_and_registry = lambda: None
            pipeline._exercise_query_pipeline = lambda: None
            pipeline._start_workspace_daemon = lambda: None
            pipeline._wait_for_daemon_health = lambda: None
            pipeline._run_verify_workspace = lambda: True
            pipeline._run_validate_workspace = lambda: True
            pipeline._run_doctor = lambda: True
            pipeline._run_canonical_verification = lambda: {"valid": True}
            upgrade_module.install_workspace = lambda *args, **kwargs: None

            report = pipeline.run()

            self.assertTrue(report.success)
            self.assertEqual(
                Path(report.rollback_location).resolve(),
                (workspace_root / ".pecs" / "backups").resolve(),
            )
            self.assertIn(".github/copilot-instructions.md", report.merged_files)

    def test_upgrade_pipeline_detects_stale_local_runtime_copy(self):
        repo_root = Path.cwd()
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_root = Path(tmpdir)
            stale_runtime_dir = workspace_root / ".pecs" / "pecs_pro"
            stale_egg_info_dir = workspace_root / ".pecs" / "pecs_pro.egg-info"
            stale_runtime_dir.mkdir(parents=True, exist_ok=True)
            stale_egg_info_dir.mkdir(parents=True, exist_ok=True)

            pipeline = UpgradeWorkspacePipeline(workspace_root, repo_root)
            plan = pipeline.inspect_workspace()

            self.assertIn(".pecs/pecs_pro", plan.stale_workspace_runtime_paths)
            self.assertIn(".pecs/pecs_pro.egg-info", plan.stale_workspace_runtime_paths)

    def test_upgrade_pipeline_reads_install_root_binding(self):
        repo_root = Path.cwd()
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_root = Path(tmpdir)
            config_dir = workspace_root / ".pecs" / "config"
            config_dir.mkdir(parents=True, exist_ok=True)
            (config_dir / "install_root.json").write_text(
                json.dumps({"install_root": str(repo_root.resolve())}),
                encoding="utf-8",
            )

            pipeline = UpgradeWorkspacePipeline(workspace_root, repo_root)
            plan = pipeline.inspect_workspace()

            self.assertEqual(plan.workspace_install_root, repo_root.resolve())
            self.assertTrue(plan.workspace_install_root_matches_repo_root)

    def test_run_validate_workspace_accepts_bridge_json_without_success_key(self):
        repo_root = Path.cwd()
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_root = Path(tmpdir)
            pipeline = UpgradeWorkspacePipeline(workspace_root, repo_root)
            pipeline._run_workspace_bridge = lambda command: {"artifact_writes": 0, "returncode": 0}

            self.assertTrue(pipeline._run_validate_workspace())


if __name__ == "__main__":
    unittest.main()
