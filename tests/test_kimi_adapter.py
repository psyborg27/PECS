import unittest
from pathlib import Path

from integrations.kimi_adapter import KimiAdapter


class DummyTopologyRetriever:
    def build_minimal_context(self, object_id):
        return {"object_id": object_id}


class KimiAdapterTests(unittest.TestCase):
    def test_kimi_adapter_queries_pecs_lite_with_kimi_source(self):
        adapter = KimiAdapter(
            topology_retriever=DummyTopologyRetriever(),
            workspace_root=Path.cwd(),
        )
        result = adapter.build_kimi_context(
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
            "kimi",
            "Kimi adapter must tag queries with query_source=kimi in the canonical query payload",
        )
        self.assertEqual(
            result.get("adapter"),
            "kimi",
            "Kimi adapter result must identify the adapter",
        )
        self.assertEqual(
            result.get("continuity_context", {}),
            {"object_id": "test-object"},
            "Kimi adapter should preserve the injected continuity context shape",
        )


if __name__ == "__main__":
    unittest.main()
