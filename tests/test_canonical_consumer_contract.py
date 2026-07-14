import json
import tempfile
import unittest
from pathlib import Path

from integrations.commandcode_adapter import CommandCodeAdapter
from integrations.consumer_integration_core import CanonicalConsumerContract
from integrations.continue_adapter import ContinueAdapter
from integrations.copilot_adapter import CopilotAdapter
from integrations.kimi_adapter import KimiAdapter


class DummyTopologyRetriever:
    def build_minimal_context(self, object_id):
        return {"object_id": object_id}


class CanonicalConsumerContractTests(unittest.TestCase):
    def test_all_consumers_emit_identical_contract_shape(self):
        workspace_root = Path.cwd()
        dummy = DummyTopologyRetriever()

        payloads = [
            CopilotAdapter(dummy, workspace_root=workspace_root).build_copilot_context("test"),
            ContinueAdapter(dummy, workspace_root=workspace_root).build_continue_context("test"),
            CommandCodeAdapter(dummy, workspace_root=workspace_root).build_commandcode_context("test"),
            KimiAdapter(dummy, workspace_root=workspace_root).build_kimi_context("test"),
        ]

        validations = [CanonicalConsumerContract.validate(payload) for payload in payloads]
        for validation in validations:
            self.assertTrue(validation["valid"], json.dumps(validation, sort_keys=True))

        signatures = [
            tuple(sorted(set(payload.keys()) - {"consumer", "adapter", "canonical_query"}))
            for payload in payloads
        ]
        self.assertEqual(len(set(signatures)), 1)

    def test_workspace_override_disables_consultation(self):
        dummy = DummyTopologyRetriever()
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_root = Path(tmpdir)
            config_path = workspace_root / ".pecs" / "config" / "consumer_consultation.json"
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text(
                json.dumps(
                    {
                        "schema": "pecs.consumer_consultation_config.v1",
                        "global_enabled": False,
                        "consumers": {
                            "copilot": True,
                            "continue": True,
                            "commandcode": True,
                            "kimi": True,
                        },
                    },
                    indent=2,
                    sort_keys=True,
                ),
                encoding="utf-8",
            )

            payload = CopilotAdapter(dummy, workspace_root=workspace_root).build_copilot_context(
                "test"
            )
            self.assertFalse(payload["consultation"]["enabled"])
            self.assertFalse(payload["consultation"]["query_issued"])


if __name__ == "__main__":
    unittest.main()
