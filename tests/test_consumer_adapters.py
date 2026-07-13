import unittest
from pathlib import Path

from integrations.commandcode_adapter import CommandCodeAdapter
from integrations.continue_adapter import ContinueAdapter
from integrations.copilot_adapter import CopilotAdapter
from integrations.kimi_adapter import KimiAdapter


class DummyTopologyRetriever:
    def build_minimal_context(self, object_id):
        return {"object_id": object_id}


class ConsumerAdapterIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workspace_root = Path.cwd()
        self.topology_retriever = DummyTopologyRetriever()

    def test_copilot_adapter_uses_pecs_lite_query_source(self):
        adapter = CopilotAdapter(
            topology_retriever=self.topology_retriever,
            workspace_root=self.workspace_root,
        )
        result = adapter.build_copilot_context(
            object_id="copilot-object",
            model_name="gpt-4o",
            model_source="openai",
            context_window=250000,
            model_size="large",
            provider="openai",
            profile_class="frontier",
            local_vs_frontier="frontier",
            reasoning_capability_class="very_high",
        )

        self.assertEqual(
            result.get("projection", {}).get("canonical_query", {}).get("consumer"),
            "copilot",
        )
        self.assertEqual(result.get("adapter"), "copilot")

    def test_continue_adapter_uses_pecs_lite_query_source(self):
        adapter = ContinueAdapter(
            topology_retriever=self.topology_retriever,
            workspace_root=self.workspace_root,
        )
        result = adapter.build_continue_context(
            object_id="continue-object",
            model_name="gpt-4o",
            model_source="openai",
            context_window=250000,
            model_size="large",
            provider="openai",
            profile_class="frontier",
            local_vs_frontier="frontier",
            reasoning_capability_class="very_high",
        )

        self.assertEqual(
            result.get("projection", {}).get("canonical_query", {}).get("consumer"),
            "continue",
        )
        self.assertEqual(result.get("adapter"), "continue")

    def test_kimi_adapter_uses_pecs_lite_query_source(self):
        adapter = KimiAdapter(
            topology_retriever=self.topology_retriever,
            workspace_root=self.workspace_root,
        )
        result = adapter.build_kimi_context(
            object_id="kimi-object",
            model_name="gpt-4o",
            model_source="openai",
            context_window=250000,
            model_size="large",
            provider="openai",
            profile_class="frontier",
            local_vs_frontier="frontier",
            reasoning_capability_class="very_high",
        )

        self.assertEqual(
            result.get("projection", {}).get("canonical_query", {}).get("consumer"),
            "kimi",
        )
        self.assertEqual(result.get("adapter"), "kimi")

    def test_commandcode_adapter_uses_pecs_lite_query_source(self):
        adapter = CommandCodeAdapter(
            topology_retriever=self.topology_retriever,
            workspace_root=self.workspace_root,
        )
        result = adapter.build_commandcode_context(
            object_id="commandcode-object",
            model_name="gpt-4o",
            model_source="openai",
            context_window=250000,
            model_size="large",
            provider="openai",
            profile_class="frontier",
            local_vs_frontier="frontier",
            reasoning_capability_class="very_high",
        )

        self.assertEqual(
            result.get("projection", {}).get("canonical_query", {}).get("consumer"),
            "commandcode",
        )
        self.assertEqual(result.get("adapter"), "commandcode")


if __name__ == "__main__":
    unittest.main()
