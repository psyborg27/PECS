import json
import hashlib
import tempfile
import unittest
from pathlib import Path

import install_workspace_integration
from pecs_pro.install_workspace_integration import install_workspace
from pecs_pro.workspace_assets_manager import WorkspaceAssetsManager


class WorkspaceAssetsManifestTests(unittest.TestCase):
    def test_canonical_windows_tasks_use_installed_pecs_paths(self):
        repo_root = Path(__file__).resolve().parents[1]
        tasks = json.loads(
            (repo_root / "workspace_assets" / ".vscode" / "tasks.json").read_text(
                encoding="utf-8"
            )
        )

        for task in tasks["tasks"]:
            windows = task["windows"]
            serialized = json.dumps(windows)
            self.assertNotIn("&&", serialized)
            self.assertNotIn(".\\pecs\\", serialized)
            self.assertEqual(windows["options"]["cwd"], "${workspaceFolder}")

        launcher_commands = {
            task["windows"]["command"]
            for task in tasks["tasks"]
            if task["label"]
            in {
                "PECS: Start Daemon",
                "PECS: Auto Start Daemon On Folder Open",
                "PECS: Append Chat Event",
                "PECS: Manual Update Chat History",
                "PECS: Refresh Continuity State",
                "PECS: Validate Continuity State",
                "PECS: Observation Snapshot (Opt-In)",
                "PECS: Observation Daemon (Opt-In)",
            }
        }
        self.assertTrue(all(command.startswith(".\\.pecs\\") for command in launcher_commands))

    def test_windows_launcher_templates_use_powershell_51_join_path_form(self):
        repo_root = Path(__file__).resolve().parents[1]
        for launcher_name in ("run_pecs.ps1", "run_pecs_daemon.ps1"):
            content = (
                repo_root / "workspace_assets" / ".pecs" / launcher_name
            ).read_text(encoding="utf-8")
            self.assertIn(
                '$ConfigFile = Join-Path $ScriptDir (Join-Path "config" "install_root.json")',
                content,
            )
            self.assertNotIn(
                '$ConfigFile = Join-Path $ScriptDir "config" "install_root.json"',
                content,
            )

    def test_fresh_install_deploys_corrected_tasks_and_launcher(self):
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(prefix="pecs workspace ") as tmpdir:
            workspace_root = Path(tmpdir) / "fresh workspace"
            workspace_root.mkdir()

            manager = WorkspaceAssetsManager(repo_root, workspace_root)
            manager.install_assets(upgrade=True, verify=False)
            install_workspace(workspace_root, repo_root, preserve_existing=True)

            installed_tasks = json.loads(
                (workspace_root / ".vscode" / "tasks.json").read_text(encoding="utf-8")
            )
            start_task = next(
                task for task in installed_tasks["tasks"] if task["label"] == "PECS: Start Daemon"
            )
            self.assertEqual(start_task["windows"]["command"], ".\\.pecs\\run_pecs_daemon.cmd")
            self.assertEqual(start_task["windows"]["args"], ["${workspaceFolder}"])
            self.assertTrue((workspace_root / ".pecs" / "run_pecs_daemon.ps1").is_file())

    def test_upgrade_replaces_stale_pecs_tasks_and_preserves_user_tasks(self):
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(prefix="pecs workspace ") as tmpdir:
            workspace_root = Path(tmpdir) / "existing workspace"
            tasks_path = workspace_root / ".vscode" / "tasks.json"
            tasks_path.parent.mkdir(parents=True)
            tasks_path.write_text(
                json.dumps(
                    {
                        "version": "2.0.0",
                        "tasks": [
                            {
                                "label": "PECS: Start Daemon",
                                "type": "shell",
                                "command": "old command",
                                "windows": {"command": "cd \"${workspaceFolder}\" && .\\pecs\\run_pecs_daemon.cmd"},
                            },
                            {"label": "User: Keep Me", "type": "shell", "command": "echo user"},
                        ],
                        "inputs": [],
                    }
                ),
                encoding="utf-8",
            )

            manager = WorkspaceAssetsManager(repo_root, workspace_root)
            manager.install_assets(upgrade=True, verify=False)

            installed = json.loads(tasks_path.read_text(encoding="utf-8"))
            by_label = {task["label"]: task for task in installed["tasks"]}
            self.assertEqual(
                by_label["PECS: Start Daemon"]["windows"]["command"],
                ".\\.pecs\\run_pecs_daemon.cmd",
            )
            self.assertEqual(by_label["User: Keep Me"]["command"], "echo user")

            first_upgrade = tasks_path.read_bytes()
            manager.install_assets(upgrade=True, verify=False)
            self.assertEqual(first_upgrade, tasks_path.read_bytes())

    def test_windows_task_definitions_are_powershell_51_safe_and_space_safe(self):
        repo_root = Path(__file__).resolve().parents[1]
        template_path = repo_root / "workspace_assets" / ".vscode" / "tasks.json"
        template = json.loads(template_path.read_text(encoding="utf-8"))

        with tempfile.TemporaryDirectory(prefix="pecs workspace ") as tmpdir:
            tasks_path = Path(tmpdir) / ".vscode" / "tasks.json"
            install_workspace_integration._merge_tasks(tasks_path, repo_root)
            generated = json.loads(tasks_path.read_text(encoding="utf-8"))

        self.assertEqual(generated["version"], "2.0.0")
        self.assertIsInstance(generated["tasks"], list)
        template_by_label = {task["label"]: task for task in template["tasks"]}
        generated_by_label = {task["label"]: task for task in generated["tasks"]}

        for label, task in generated_by_label.items():
            windows = task.get("windows", {})
            self.assertNotIn("&&", json.dumps(windows))
            self.assertEqual(windows.get("options", {}).get("cwd"), "${workspaceFolder}")
            if label in template_by_label:
                self.assertTrue(task["command"].startswith("bash -lc 'cd \"${workspaceFolder}\""))

        for label in (
            "PECS: Start Daemon",
            "PECS: Auto Start Daemon On Folder Open",
            "PECS: Append Chat Event",
            "PECS: Manual Update Chat History",
            "PECS: Refresh Continuity State",
            "PECS: Validate Continuity State",
            "PECS: Observation Snapshot (Opt-In)",
            "PECS: Observation Daemon (Opt-In)",
        ):
            windows = generated_by_label[label]["windows"]
            self.assertIn("${workspaceFolder}", windows["args"])
            self.assertTrue(windows["command"].endswith(".cmd"))

        for label in (
            "PECS: Stop Daemon",
            "PECS: Show Emitted Envelope Log (Opt-In)",
            "PECS: Show Projection Snapshot Log (Opt-In)",
        ):
            windows = generated_by_label[label]["windows"]
            self.assertEqual(windows["command"], "powershell.exe")
            self.assertIn("-Command", windows["args"])

    def test_unix_task_commands_remain_identical_to_canonical_template(self):
        repo_root = Path(__file__).resolve().parents[1]
        template = json.loads(
            (repo_root / "workspace_assets" / ".vscode" / "tasks.json").read_text(
                encoding="utf-8"
            )
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            tasks_path = Path(tmpdir) / ".vscode" / "tasks.json"
            install_workspace_integration._merge_tasks(tasks_path, repo_root)
            generated = json.loads(tasks_path.read_text(encoding="utf-8"))

        template_labels = {task["label"] for task in template["tasks"]}
        for task in generated["tasks"]:
            if task["label"] in template_labels:
                self.assertTrue(task["command"].startswith("bash -lc 'cd \"${workspaceFolder}\""))

        for task in template["tasks"]:
            self.assertTrue(task["command"].startswith("bash -lc 'cd \"${workspaceFolder}\""))

    def test_install_workspace_creates_windows_daemon_launcher_for_fresh_workspace(self):
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(prefix="pecs workspace ") as tmpdir:
            workspace_root = Path(tmpdir) / "target workspace"
            workspace_root.mkdir()

            install_workspace(workspace_root, repo_root, preserve_existing=True)

            pecs_dir = workspace_root / ".pecs"
            self.assertTrue(pecs_dir.is_dir())
            for launcher_name in (
                "run_pecs_daemon.cmd",
                "run_pecs_daemon.ps1",
                "run_pecs_daemon.sh",
            ):
                self.assertTrue((pecs_dir / launcher_name).is_file())

            cmd_contents = (pecs_dir / "run_pecs_daemon.cmd").read_text(encoding="utf-8")
            self.assertIn("run_pecs_daemon.ps1", cmd_contents)
            self.assertTrue((pecs_dir / "config" / "install_root.json").is_file())

    def test_install_workspace_preserves_windows_daemon_launcher_on_initialized_workspace(self):
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(prefix="pecs workspace ") as tmpdir:
            workspace_root = Path(tmpdir) / "target workspace"
            workspace_root.mkdir()

            install_workspace(workspace_root, repo_root, preserve_existing=True)
            launcher = workspace_root / ".pecs" / "run_pecs_daemon.cmd"
            before = hashlib.sha256(launcher.read_bytes()).hexdigest()

            install_workspace(workspace_root, repo_root, preserve_existing=True)

            self.assertTrue(launcher.is_file())
            self.assertEqual(before, hashlib.sha256(launcher.read_bytes()).hexdigest())

    def test_manifest_declares_all_platform_daemon_launchers(self):
        repo_root = Path(__file__).resolve().parents[1]
        manager = WorkspaceAssetsManager(repo_root, repo_root)
        daemon_assets = {
            asset["target"]: asset
            for asset in manager.manifest.get("assets", [])
            if str(asset.get("target", "")).startswith(".pecs/run_pecs_daemon.")
        }

        self.assertEqual(
            set(daemon_assets),
            {
                ".pecs/run_pecs_daemon.cmd",
                ".pecs/run_pecs_daemon.ps1",
                ".pecs/run_pecs_daemon.sh",
            },
        )
        for target, asset in daemon_assets.items():
            self.assertTrue(asset["required"])
            self.assertTrue((repo_root / "workspace_assets" / asset["source"]).is_file())

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
