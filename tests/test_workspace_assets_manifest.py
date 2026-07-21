import json
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

    def test_merge_json_merges_existing_target(self):
        repo_root = Path(__file__).resolve().parents[1]
        manager = WorkspaceAssetsManager(repo_root, Path(tempfile.mkdtemp()))

        source = manager.workspace_root / "source.json"
        target = manager.workspace_root / ".vscode" / "settings.json"
        target.parent.mkdir(parents=True, exist_ok=True)

        source.write_text(
            json.dumps({"pecs.contextPath": ".pecs/active_context.json", "newKey": "new"}, indent=2),
            encoding="utf-8",
        )
        target.write_text(
            json.dumps({"existing": "yes", "pecs.contextPath": "old"}, indent=2),
            encoding="utf-8",
        )

        manager._apply_merge_strategy(
            "test_json_merge",
            source,
            target,
            "merge_json",
            upgrade=True,
            merge_options={},
        )

        merged = json.loads(target.read_text(encoding="utf-8"))
        self.assertEqual(merged["existing"], "yes")
        self.assertEqual(merged["pecs.contextPath"], ".pecs/active_context.json")
        self.assertEqual(merged["newKey"], "new")

    def test_merge_vscode_tasks_merges_tasks_and_inputs(self):
        repo_root = Path(__file__).resolve().parents[1]
        manager = WorkspaceAssetsManager(repo_root, Path(tempfile.mkdtemp()))

        source = manager.workspace_root / "source_tasks.json"
        target = manager.workspace_root / ".vscode" / "tasks.json"
        target.parent.mkdir(parents=True, exist_ok=True)

        target.write_text(
            json.dumps({
                "version": "2.0.0",
                "tasks": [
                    {"label": "Existing Task", "type": "shell"}
                ],
                "inputs": [
                    {"id": "existingInput", "type": "promptString"}
                ]
            }, indent=2),
            encoding="utf-8",
        )
        source.write_text(
            json.dumps({
                "version": "2.0.0",
                "tasks": [
                    {"label": "Existing Task", "command": "echo hello"},
                    {"label": "New Task", "type": "shell"}
                ],
                "inputs": [
                    {"id": "existingInput", "description": "Prompt"},
                    {"id": "newInput", "type": "promptString"}
                ]
            }, indent=2),
            encoding="utf-8",
        )

        manager._apply_merge_strategy(
            "test_vscode_tasks",
            source,
            target,
            "merge_vscode_tasks",
            upgrade=True,
            merge_options={},
        )

        merged = json.loads(target.read_text(encoding="utf-8"))
        self.assertEqual(len(merged["tasks"]), 2)
        self.assertEqual(merged["tasks"][0]["label"], "Existing Task")
        self.assertEqual(merged["tasks"][0]["command"], "echo hello")
        self.assertEqual(merged["tasks"][1]["label"], "New Task")
        self.assertEqual(len(merged["inputs"]), 2)
        self.assertEqual(merged["inputs"][0]["id"], "existingInput")
        self.assertEqual(merged["inputs"][0]["description"], "Prompt")
        self.assertEqual(merged["inputs"][1]["id"], "newInput")

    def test_merge_yaml_extends_existing_list(self):
        repo_root = Path(__file__).resolve().parents[1]
        manager = WorkspaceAssetsManager(repo_root, Path(tempfile.mkdtemp()))

        source = manager.workspace_root / "source.yaml"
        target = manager.workspace_root / ".continue" / "config.yaml"
        target.parent.mkdir(parents=True, exist_ok=True)

        target.write_text(
            "rules:\n  - path: rules/pecs-first-routing.yaml\n    alwaysApply: true\n",
            encoding="utf-8",
        )
        source.write_text(
            "rules:\n  - path: rules/pecs-additional.yaml\n    alwaysApply: false\n",
            encoding="utf-8",
        )

        manager._apply_merge_strategy(
            "test_yaml_merge",
            source,
            target,
            "merge_yaml",
            upgrade=True,
            merge_options={
                "key_paths": ["rules"],
                "merge_mode": "extend",
                "create_if_missing_top_level": True,
            },
        )

        merged = target.read_text(encoding="utf-8")
        self.assertIn("rules:", merged)
        self.assertIn("path: rules/pecs-first-routing.yaml", merged)
        self.assertIn("path: rules/pecs-additional.yaml", merged)

    def test_append_or_merge_appends_markdown_when_target_exists(self):
        repo_root = Path(__file__).resolve().parents[1]
        manager = WorkspaceAssetsManager(repo_root, Path(tempfile.mkdtemp()))

        source = manager.workspace_root / "source.md"
        target = manager.workspace_root / "README.md"
        target.parent.mkdir(parents=True, exist_ok=True)

        target.write_text("# Existing\n\nOriginal content\n", encoding="utf-8")
        source.write_text("# PECS\n\nNew guidance\n", encoding="utf-8")

        manager._apply_merge_strategy(
            "test_append_or_merge",
            source,
            target,
            "append_or_merge",
            upgrade=True,
            merge_options={"append_section_marker": "<!-- PECS-PRO -->"},
        )

        merged = target.read_text(encoding="utf-8")
        self.assertIn("<!-- PECS-PRO -->", merged)
        self.assertIn("# PECS", merged)
