import glob
import json
import unittest
from pathlib import Path

from integrations.pecs_lite_runtime_adapter import PECSLiteRuntimeAdapter


class PECSLiteRuntimeValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workspace_root = Path.cwd()
        cls.telemetry_dir = cls.workspace_root / "telemetry" / "runtime_jsonl"

    def test_local_small_model_projection_produces_aggressive_narrowing(self):
        projection = PECSLiteRuntimeAdapter.build_projection_safe(
            workspace_root=str(self.workspace_root),
            query="validate small local projection",
            model_name="qwen",
            model_source="ollama",
            context_window=32768,
            model_size="small",
            provider="ollama",
            query_source="test_local_small",
            include_diagnostics=True,
        )

        self.assertTrue(
            projection.get("pecs_lite_telemetry", {}).get("runtime_invoked", False),
            "PECS-LITE runtime should be invoked for local small model queries",
        )
        self.assertEqual(
            projection.get("projection_profile", {}).get("profile"),
            "small_local",
            "Local small model should select the small_local projection profile",
        )
        self.assertLessEqual(
            projection.get("metrics", {}).get("locality_breadth_score", 1.0),
            0.7,
            "Local small model should enforce aggressive locality narrowing",
        )
        self.assertTrue(
            projection.get("pecs_lite_telemetry", {}).get("deterministic_narrowing_activated", False),
        )
        self.assertGreater(
            len(projection.get("runtime_targets", [])),
            0,
            "Projection should return at least one runtime target",
        )

    def test_online_large_model_projection_produces_broader_adjacency(self):
        projection = PECSLiteRuntimeAdapter.build_projection_safe(
            workspace_root=str(self.workspace_root),
            query="validate large online projection",
            model_name="gpt-4o",
            model_source="openai",
            context_window=250000,
            model_size="large",
            provider="openai",
            query_source="test_online_large",
            include_diagnostics=True,
        )

        profile = projection.get("projection_profile", {}).get("profile", "")
        self.assertIn(
            profile,
            {"frontier_online", "reasoning_frontier", "agentic_frontier", "large_local"},
            "Online large model should select a broader projection profile",
        )
        self.assertGreaterEqual(
            projection.get("metrics", {}).get("locality_breadth_score", 0.0),
            0.1,
            "Online large model should allow broader locality coverage",
        )
        self.assertTrue(
            projection.get("pecs_lite_telemetry", {}).get("projection_delivered", False),
            "Large online model projection should be delivered",
        )
        self.assertEqual(
            projection.get("pecs_lite_telemetry", {}).get("token_budget_selected"),
            10000,
            "Online large model should select the expected large token budget",
        )
        self.assertGreater(
            projection.get("pecs_lite_telemetry", {}).get("payload_size", 0),
            0,
            "Projection telemetry payload size should be populated",
        )

    def test_projection_telemetry_writes_runtime_events(self):
        projection = PECSLiteRuntimeAdapter.build_projection_safe(
            workspace_root=str(self.workspace_root),
            query="validate telemetry output",
            model_name="claude-3",
            model_source="anthropic",
            context_window=180000,
            model_size="medium",
            provider="anthropic",
            query_source="test_telemetry",
            include_diagnostics=True,
        )

        self.assertTrue(
            projection.get("pecs_lite_telemetry", {}).get("runtime_available", False),
        )
        self.assertEqual(
            projection.get("pecs_lite_telemetry", {}).get("adapter_used"),
            "PECSLiteRuntimeAdapter",
        )
        self.assertIn(
            projection.get("pecs_lite_telemetry", {}).get("selected_projection_profile", ""),
            {"medium_local", "large_local", "reasoning_frontier", "frontier_online", "agentic_frontier"},
        )

        telemetry_files = sorted(self.telemetry_dir.glob("pecs_runtime_*.jsonl"))
        self.assertGreater(
            len(telemetry_files),
            0,
            "Telemetry should produce at least one runtime JSONL file",
        )

        last_file = telemetry_files[-1]
        with last_file.open("r", encoding="utf-8") as handle:
            events = [json.loads(line) for line in handle if line.strip()]

        event_names = {entry.get("event") for entry in events}
        self.assertIn("projection_invocation_completed", event_names)
        self.assertIn("projection_hardener_completed", event_names)
        self.assertIn("projection_request_received", event_names)


if __name__ == "__main__":
    unittest.main()
