import tempfile
import unittest
from pathlib import Path

from runtime.daemon.workspace_continuity_daemon import WorkspaceContinuityDaemon


class WorkspaceContinuityDaemonTests(unittest.TestCase):
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

            health = daemon._health_status()

            self.assertEqual(health["status"], "healthy")
            self.assertTrue(health["retrieval_ready"])
            self.assertTrue(health["topology_ready"])
            self.assertTrue(health["continuity_ready"])
            self.assertNotIn("continuity graph incomplete", health["health_issues"])


if __name__ == "__main__":
    unittest.main()
