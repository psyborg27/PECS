import json
import tempfile
import unittest
from pathlib import Path

from runtime.daemon.workspace_continuity_daemon import WorkspaceContinuityDaemon
from run_pecs_pro import PECSProRuntime


class WorkspaceContinuityDaemonTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.workspace_root = Path(self.tempdir.name)
        self.workspace_root.mkdir(parents=True, exist_ok=True)
        self.runtime = PECSProRuntime(workspace_root=self.workspace_root)
        components = self.runtime.initialize()
        self.daemon = WorkspaceContinuityDaemon(
            workspace_root=self.workspace_root,
            runtime_session=components["runtime_session"],
            compact_builder=components["compact_builder"],
        )
        self.daemon._chat_history_path = self.workspace_root / ".pecs" / "ai_chat_history.json"
        self.daemon._chat_history_path.parent.mkdir(parents=True, exist_ok=True)
        self.daemon._chat_history_path.write_text("[]", encoding="utf-8")

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def _read_json_artifact(self, name: str) -> dict:
        path = self.workspace_root / ".pecs" / name
        return json.loads(path.read_text(encoding="utf-8"))

    def _create_main_app(self, content: str = "print('hello')\n") -> None:
        self.workspace_root.mkdir(parents=True, exist_ok=True)
        (self.workspace_root / "main_app.py").write_text(content, encoding="utf-8")

    def test_health_status_single_file_workspace_is_healthy(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_root = Path(tmpdir)
            daemon = WorkspaceContinuityDaemon(
                workspace_root=workspace_root,
                runtime_session=object(),
                compact_builder=object(),
            )
            daemon.runtime_locality_payload = {"PECS_ID:main": {"path": "main.py"}}
            daemon.runtime_reachable_files = {workspace_root / "main.py"}
            daemon.runtime_topology_edges = []
            artifact_dir = workspace_root / ".pecs"
            artifact_dir.mkdir(parents=True, exist_ok=True)
            (artifact_dir / "workspace_graph_validation.json").write_text(
                json.dumps({"valid": True}), encoding="utf-8"
            )
            (artifact_dir / "workspace_registry_validation.json").write_text(
                json.dumps({"valid": True}), encoding="utf-8"
            )

            health = daemon._health_status()

            self.assertEqual(health["status"], "healthy")
            self.assertTrue(health["retrieval_ready"])
            self.assertTrue(health["topology_ready"])
            self.assertTrue(health["continuity_ready"])
            self.assertEqual(health["health_issues"], [])

    def test_fresh_workspace_emits_validation_artifacts(self):
        self._create_main_app()

        self.daemon._rebuild_runtime_topology()

        graph_validation_path = self.workspace_root / ".pecs" / "workspace_graph_validation.json"
        registry_validation_path = self.workspace_root / ".pecs" / "workspace_registry_validation.json"

        self.assertTrue(graph_validation_path.exists())
        self.assertTrue(registry_validation_path.exists())

        graph_validation = self._read_json_artifact("workspace_graph_validation.json")
        registry_validation = self._read_json_artifact("workspace_registry_validation.json")

        self.assertIn("valid", graph_validation)
        self.assertIn("valid", registry_validation)

    def test_empty_workspace_emits_validation_artifacts(self):
        self.daemon._rebuild_runtime_topology()

        self.assertTrue((self.workspace_root / ".pecs" / "workspace_graph_validation.json").exists())
        self.assertTrue((self.workspace_root / ".pecs" / "workspace_registry_validation.json").exists())

        health = self.daemon._health_status()
        self.assertEqual(health["status"], "healthy")

    def test_large_workspace_emits_validation_artifacts(self):
        self.workspace_root.mkdir(parents=True, exist_ok=True)
        modules = []
        for index in range(100):
            module_name = f"module_{index}.py"
            modules.append(module_name)
            content = "\n".join(
                [f"from module_{index - 1} import foo" if index > 0 else "def foo():\n    return 'root'", "\n"]
            )
            (self.workspace_root / module_name).write_text(content, encoding="utf-8")
        (self.workspace_root / "main_app.py").write_text(
            "from module_0 import foo\nprint(foo())\n", encoding="utf-8"
        )

        self.daemon._rebuild_runtime_topology()

        self.assertTrue((self.workspace_root / ".pecs" / "workspace_graph_validation.json").exists())
        self.assertTrue((self.workspace_root / ".pecs" / "workspace_registry_validation.json").exists())

    def test_incremental_update_updates_validation_artifacts(self):
        self._create_main_app("print('first')\n")
        self.daemon._rebuild_runtime_topology()

        graph_mtime_before = (self.workspace_root / ".pecs" / "workspace_graph_validation.json").stat().st_mtime_ns
        registry_mtime_before = (self.workspace_root / ".pecs" / "workspace_registry_validation.json").stat().st_mtime_ns

        (self.workspace_root / "main_app.py").write_text("print('second')\n", encoding="utf-8")
        self.daemon._rebuild_runtime_topology()

        graph_mtime_after = (self.workspace_root / ".pecs" / "workspace_graph_validation.json").stat().st_mtime_ns
        registry_mtime_after = (self.workspace_root / ".pecs" / "workspace_registry_validation.json").stat().st_mtime_ns

        self.assertGreaterEqual(graph_mtime_after, graph_mtime_before)
        self.assertGreaterEqual(registry_mtime_after, registry_mtime_before)

    def test_daemon_restart_preserves_validation_artifacts(self):
        self._create_main_app()
        self.daemon._rebuild_runtime_topology()

        graph_validation_path = self.workspace_root / ".pecs" / "workspace_graph_validation.json"
        registry_validation_path = self.workspace_root / ".pecs" / "workspace_registry_validation.json"
        self.assertTrue(graph_validation_path.exists())
        self.assertTrue(registry_validation_path.exists())

        restarted_runtime = PECSProRuntime(workspace_root=self.workspace_root)
        restarted_components = restarted_runtime.initialize()
        restarted_daemon = WorkspaceContinuityDaemon(
            workspace_root=self.workspace_root,
            runtime_session=restarted_components["runtime_session"],
            compact_builder=restarted_components["compact_builder"],
        )
        restarted_daemon._chat_history_path = self.workspace_root / ".pecs" / "ai_chat_history.json"
        restarted_daemon._chat_history_path.parent.mkdir(parents=True, exist_ok=True)
        restarted_daemon._chat_history_path.write_text("[]", encoding="utf-8")
        restarted_daemon._rebuild_runtime_topology()

        self.assertTrue(graph_validation_path.exists())
        self.assertTrue(registry_validation_path.exists())


if __name__ == "__main__":
    unittest.main()
