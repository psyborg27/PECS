import tempfile
import unittest
from pathlib import Path

from validation.consumer_consultation_validator import (
    ConsumerConsultationComplianceValidator,
)


class ConsumerConsultationComplianceValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.workspace_root = Path(self.tempdir.name)
        self.workspace_root.mkdir(parents=True, exist_ok=True)
        self.validator = ConsumerConsultationComplianceValidator(self.workspace_root)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_all_supported_consumers_pass_compliance(self):
        results = self.validator.validate_all()
        self.assertEqual(len(results), 4)
        for result in results:
            self.assertTrue(result.valid, f"{result.consumer} compliance failed: {result.report_errors}")
            self.assertEqual(result.compliance["query"], "PASS")
            self.assertEqual(result.compliance["response"], "PASS")
            self.assertEqual(
                result.compliance["consultation_report"],
                "PASS",
                f"{result.consumer} consultation report failed: {result.report_errors}",
            )
            self.assertEqual(result.compliance["enable_disable"], "PASS")
            self.assertIn(result.projection_schema, {"pecs_lite.runtime_projection.locality_authority.v3", "pecs_lite.runtime_projection.error.v1"})

    def test_disabled_consultation_reports_disabled(self):
        policy_path = self.workspace_root / ".pecs" / "config" / "consumer_consultation.json"
        policy_path.parent.mkdir(parents=True, exist_ok=True)
        policy_path.write_text(
            '{"schema": "pecs.consumer_consultation_config.v1", "global_enabled": false, "consumers": {"copilot": false, "continue": false, "commandcode": false, "kimi": false}}',
            encoding="utf-8",
        )

        validator = ConsumerConsultationComplianceValidator(self.workspace_root)
        results = validator.validate_all()

        for result in results:
            self.assertFalse(result.consultation.get("enabled", True))
            self.assertEqual(result.consultation.get("query_issued", True), False)
            self.assertEqual(result.compliance["enable_disable"], "PASS")
            self.assertEqual(result.compliance["query"], "PASS")


if __name__ == "__main__":
    unittest.main()
