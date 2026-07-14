import tempfile
import unittest
from pathlib import Path

from pecs_pro.install_workspace_integration import install_workspace
from pecs_pro.workspace_assets_manager import WorkspaceAssetsManager


class WorkspaceAssetsManifestTests(unittest.TestCase):
    def test_manifest_sources_exist(self):
        repo_root = Path(__file__).resolve().parents[1]
        manager = WorkspaceAssetsManager(repo_root, repo_root)

        missing_sources = []
        for asset in manager.manifest.get("assets", []):
            source_path = repo_root / "workspace_assets" / asset["source"]
            if not source_path.exists():
                missing_sources.append(asset["source"])

        self.assertEqual(
            missing_sources,
            [],
            f"Workspace asset manifest contains missing source files: {missing_sources}",
        )

    def test_manifest_assets_define_policy_metadata(self):
        repo_root = Path(__file__).resolve().parents[1]
        manager = WorkspaceAssetsManager(repo_root, repo_root)
        required = {
            "asset_version",
            "ownership",
            "replacement_policy",
            "merge_policy",
            "upgrade_behavior",
        }
        missing = {}
        for asset in manager.manifest.get("assets", []):
            absent = sorted(field for field in required if field not in asset)
            if absent:
                missing[asset.get("id", "unknown")] = absent
        self.assertEqual(missing, {}, f"Asset policy metadata missing: {missing}")

    def test_consumer_guidance_assets_install_and_verify(self):
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_root = Path(tmpdir) / "workspace"
            workspace_root.mkdir()

            manager = WorkspaceAssetsManager(repo_root, workspace_root)
            manager.install_assets(upgrade=True, verify=False)
            install_workspace(workspace_root, repo_root, preserve_existing=True)

            expected_paths = [
                workspace_root / ".pecs" / "PECS_CONSUMER_PROTOCOL.md",
                workspace_root / ".pecs" / "config" / "consumer_consultation.json",
                workspace_root / ".kimi" / "instructions.md",
                workspace_root / ".commandcode" / "instructions.md",
            ]
            for path in expected_paths:
                self.assertTrue(
                    path.exists(),
                    f"Expected installed asset missing: {path.relative_to(workspace_root)}",
                )

            verification = manager.verify_installation()
            self.assertTrue(
                verification["valid"],
                f"Workspace verification failed after install: {verification.get('errors')}",
            )


if __name__ == "__main__":
    unittest.main()
