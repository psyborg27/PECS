import unittest
from pathlib import Path

from integrations.commandcode_adapter import CommandCodeAdapter


class DummyTopologyRetriever:
    def build_minimal_context(self, object_id):
        return {"object_id": object_id}


class CommandCodeAdapterTests(unittest.TestCase):
    def test_commandcode_adapter_queries_pecs_lite_with_commandcode_source(self):
        adapter = CommandCodeAdapter(
            topology_retriever=DummyTopologyRetriever(),
            workspace_root=Path.cwd(),
        )
        result = adapter.build_commandcode_context(
            object_id="test-object",
            model_name="gpt-4o",
            model_source="openai",
            context_window=250000,
            model_size="large",
            provider="openai",
            profile_class="frontier",
            local_vs_frontier="frontier",
            reasoning_capability_class="very_high",
        )

        projection = result.get("projection", {})
        self.assertEqual(
            projection.get("canonical_query", {}).get("consumer"),
            "commandcode",
            "CommandCode adapter must tag queries with query_source=commandcode in the canonical query payload",
        )
        self.assertEqual(
            result.get("adapter"),
            "commandcode",
            "CommandCode adapter result must identify the adapter",
        )
        self.assertEqual(
            result.get("continuity_context", {}),
            {"object_id": "test-object"},
            "CommandCode adapter should preserve the injected continuity context shape",
        )


if __name__ == "__main__":
    unittest.main()
