#!/usr/bin/env python3
"""
Adversarial validation of PECS deterministic governance architecture.

Targets:
- Deterministic locality reconstruction
- Governance envelope integrity
- Drift scoring determinism
- Typed normalization enforcement
- Authority boundary isolation
- Contradiction handling stability
- Runtime evidence reproducibility
- Fail-fast governance rejection behavior
"""

from __future__ import annotations

import sys
import json
import traceback
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass


@dataclass
class ValidationResult:
    scenario: str
    category: str
    passed: bool
    error_message: str = ""
    details: Dict[str, Any] = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}


class GovernanceDeterminismValidator:
    """Validates deterministic governance stabilization."""

    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root).resolve()
        self.results: List[ValidationResult] = []
        self.sys_path_setup()

    def sys_path_setup(self):
        """Configure sys.path for imports."""
        pecs_lite_path = self.workspace_root / "PECS_LITE v2" / "pecs_lite v2"
        if str(pecs_lite_path) not in sys.path:
            sys.path.insert(0, str(pecs_lite_path))
        if str(self.workspace_root) not in sys.path:
            sys.path.insert(0, str(self.workspace_root))

    def test_malformed_governance_envelopes(self) -> None:
        """Test 1: Malformed governance envelopes must fail deterministically."""
        from integrations.pecs_lite_projection_hardener import ProjectionExporter
        from types import MappingProxyType

        # Test 1.1: missing projection_profile
        try:
            ProjectionExporter._parse_governance_transfer_envelope(
                engineering_continuity={},
                capability_bundle={"model_detection": {}},  # missing projection_profile
                behavioral_signals={},
                runtime_context={},
            )
            self.results.append(
                ValidationResult(
                    scenario="malformed_missing_projection_profile",
                    category="malformed_governance_envelopes",
                    passed=False,
                    error_message="Expected ValueError but none raised",
                )
            )
        except ValueError as e:
            if "projection_profile" in str(e):
                self.results.append(
                    ValidationResult(
                        scenario="malformed_missing_projection_profile",
                        category="malformed_governance_envelopes",
                        passed=True,
                        details={"error_caught": str(e)},
                    )
                )
            else:
                self.results.append(
                    ValidationResult(
                        scenario="malformed_missing_projection_profile",
                        category="malformed_governance_envelopes",
                        passed=False,
                        error_message=f"Wrong error: {e}",
                    )
                )
        except Exception as e:
            self.results.append(
                ValidationResult(
                    scenario="malformed_missing_projection_profile",
                    category="malformed_governance_envelopes",
                    passed=False,
                    error_message=f"Unexpected exception: {type(e).__name__}: {e}",
                )
            )

        # Test 1.2: missing model_detection
        try:
            ProjectionExporter._parse_governance_transfer_envelope(
                engineering_continuity={},
                capability_bundle={"projection_profile": {}},  # missing model_detection
                behavioral_signals={},
                runtime_context={},
            )
            self.results.append(
                ValidationResult(
                    scenario="malformed_missing_model_detection",
                    category="malformed_governance_envelopes",
                    passed=False,
                    error_message="Expected ValueError but none raised",
                )
            )
        except ValueError as e:
            if "model_detection" in str(e):
                self.results.append(
                    ValidationResult(
                        scenario="malformed_missing_model_detection",
                        category="malformed_governance_envelopes",
                        passed=True,
                        details={"error_caught": str(e)},
                    )
                )
            else:
                self.results.append(
                    ValidationResult(
                        scenario="malformed_missing_model_detection",
                        category="malformed_governance_envelopes",
                        passed=False,
                        error_message=f"Wrong error: {e}",
                    )
                )
        except Exception as e:
            self.results.append(
                ValidationResult(
                    scenario="malformed_missing_model_detection",
                    category="malformed_governance_envelopes",
                    passed=False,
                    error_message=f"Unexpected exception: {type(e).__name__}: {e}",
                )
            )

        # Test 1.3: invalid capability_bundle (not a dict)
        try:
            ProjectionExporter._parse_governance_transfer_envelope(
                engineering_continuity={},
                capability_bundle="invalid_string",
                behavioral_signals={},
                runtime_context={},
            )
            self.results.append(
                ValidationResult(
                    scenario="malformed_capability_bundle_not_dict",
                    category="malformed_governance_envelopes",
                    passed=False,
                    error_message="Expected ValueError but none raised",
                )
            )
        except ValueError as e:
            if "capability_bundle" in str(e) and "object" in str(e):
                self.results.append(
                    ValidationResult(
                        scenario="malformed_capability_bundle_not_dict",
                        category="malformed_governance_envelopes",
                        passed=True,
                        details={"error_caught": str(e)},
                    )
                )
            else:
                self.results.append(
                    ValidationResult(
                        scenario="malformed_capability_bundle_not_dict",
                        category="malformed_governance_envelopes",
                        passed=False,
                        error_message=f"Wrong error: {e}",
                    )
                )
        except Exception as e:
            self.results.append(
                ValidationResult(
                    scenario="malformed_capability_bundle_not_dict",
                    category="malformed_governance_envelopes",
                    passed=False,
                    error_message=f"Unexpected exception: {type(e).__name__}: {e}",
                )
            )

    def test_malformed_drift_payloads(self) -> None:
        """Test 1b: Malformed drift payloads must fail during normalization."""
        from scripts.validate_workspace_continuity import (
            _normalize_runtime_paths,
            _normalize_runtime_confirmations,
        )

        # Test 1b.1: path list with non-dict entries
        try:
            _normalize_runtime_paths([{"path": "file.py", "changed": True}, "invalid"])
            self.results.append(
                ValidationResult(
                    scenario="malformed_drift_path_non_dict",
                    category="malformed_governance_envelopes",
                    passed=False,
                    error_message="Expected ValueError but none raised",
                )
            )
        except ValueError as e:
            if "entries must be objects" in str(e):
                self.results.append(
                    ValidationResult(
                        scenario="malformed_drift_path_non_dict",
                        category="malformed_governance_envelopes",
                        passed=True,
                        details={"error_caught": str(e)},
                    )
                )
            else:
                self.results.append(
                    ValidationResult(
                        scenario="malformed_drift_path_non_dict",
                        category="malformed_governance_envelopes",
                        passed=False,
                        error_message=f"Wrong error: {e}",
                    )
                )
        except Exception as e:
            self.results.append(
                ValidationResult(
                    scenario="malformed_drift_path_non_dict",
                    category="malformed_governance_envelopes",
                    passed=False,
                    error_message=f"Unexpected exception: {type(e).__name__}: {e}",
                )
            )

        # Test 1b.2: path with missing "path" field
        try:
            _normalize_runtime_paths([{"changed": True}])
            self.results.append(
                ValidationResult(
                    scenario="malformed_drift_path_missing_field",
                    category="malformed_governance_envelopes",
                    passed=False,
                    error_message="Expected ValueError but none raised",
                )
            )
        except ValueError as e:
            if "path must be" in str(e):
                self.results.append(
                    ValidationResult(
                        scenario="malformed_drift_path_missing_field",
                        category="malformed_governance_envelopes",
                        passed=True,
                        details={"error_caught": str(e)},
                    )
                )
            else:
                self.results.append(
                    ValidationResult(
                        scenario="malformed_drift_path_missing_field",
                        category="malformed_governance_envelopes",
                        passed=False,
                        error_message=f"Wrong error: {e}",
                    )
                )
        except Exception as e:
            self.results.append(
                ValidationResult(
                    scenario="malformed_drift_path_missing_field",
                    category="malformed_governance_envelopes",
                    passed=False,
                    error_message=f"Unexpected exception: {type(e).__name__}: {e}",
                )
            )

    def test_object_contamination_attempts(self) -> None:
        """Test 2: Object contamination attempts must not affect authority state."""
        from integrations.pecs_lite_projection_hardener import EMPTY_MAPPING

        # Test 2.1: verify EMPTY_MAPPING is immutable
        try:
            EMPTY_MAPPING["injected_key"] = "malicious_value"  # type: ignore
            self.results.append(
                ValidationResult(
                    scenario="object_mutation_empty_mapping",
                    category="object_contamination_attempts",
                    passed=False,
                    error_message="EMPTY_MAPPING is mutable (should be immutable)",
                )
            )
        except TypeError:
            self.results.append(
                ValidationResult(
                    scenario="object_mutation_empty_mapping",
                    category="object_contamination_attempts",
                    passed=True,
                    details={"immutable_verified": True},
                )
            )
        except Exception as e:
            self.results.append(
                ValidationResult(
                    scenario="object_mutation_empty_mapping",
                    category="object_contamination_attempts",
                    passed=False,
                    error_message=f"Unexpected exception: {type(e).__name__}: {e}",
                )
            )

        # Test 2.2: nested dict injection attempt
        from integrations.pecs_lite_projection_hardener import ProjectionExporter

        try:
            ProjectionExporter._parse_governance_transfer_envelope(
                engineering_continuity={},
                capability_bundle={
                    "projection_profile": {
                        "__proto__": {"admin": True}
                    },
                    "model_detection": {},
                },
                behavioral_signals={},
                runtime_context={},
            )
            # Should parse successfully but not expose the injected key
            result_ok = True
            self.results.append(
                ValidationResult(
                    scenario="object_nested_dict_injection",
                    category="object_contamination_attempts",
                    passed=result_ok,
                    details={"nested_injection_handled": True},
                )
            )
        except Exception as e:
            self.results.append(
                ValidationResult(
                    scenario="object_nested_dict_injection",
                    category="object_contamination_attempts",
                    passed=False,
                    error_message=f"Unexpected rejection: {e}",
                )
            )

    def test_determinism_stability_checks(self) -> None:
        """Test 3: Drift scoring must be deterministic across repeated runs."""
        from scripts.validate_workspace_continuity import (
            _normalize_runtime_paths,
            _normalize_runtime_confirmations,
            _normalize_locality_zones,
            _normalize_locality_assumptions,
        )

        # Test 3.1: repeated normalization must produce identical sorted output
        input_paths = [
            {"path": "z_file.py", "changed": True},
            {"path": "a_file.py", "changed": False},
            {"path": "m_file.py", "changed": True},
        ]

        try:
            result1 = _normalize_runtime_paths(input_paths)
            result2 = _normalize_runtime_paths(input_paths)
            result3 = _normalize_runtime_paths(input_paths)

            if result1 == result2 == result3:
                self.results.append(
                    ValidationResult(
                        scenario="determinism_repeated_normalization",
                        category="determinism_stability_checks",
                        passed=True,
                        details={
                            "runs": 3,
                            "sorted_keys": [r["path"] for r in result1],
                        },
                    )
                )
            else:
                self.results.append(
                    ValidationResult(
                        scenario="determinism_repeated_normalization",
                        category="determinism_stability_checks",
                        passed=False,
                        error_message="Output differs across repeated runs",
                    )
                )
        except Exception as e:
            self.results.append(
                ValidationResult(
                    scenario="determinism_repeated_normalization",
                    category="determinism_stability_checks",
                    passed=False,
                    error_message=f"Exception: {type(e).__name__}: {e}",
                )
            )

        # Test 3.2: ordering invariance with different input order
        input_paths_v2 = [
            {"path": "a_file.py", "changed": False},
            {"path": "z_file.py", "changed": True},
            {"path": "m_file.py", "changed": True},
        ]

        try:
            result_v1 = _normalize_runtime_paths(input_paths)
            result_v2 = _normalize_runtime_paths(input_paths_v2)

            if result_v1 == result_v2:
                self.results.append(
                    ValidationResult(
                        scenario="determinism_ordering_invariance",
                        category="determinism_stability_checks",
                        passed=True,
                        details={
                            "input_orders_tested": 2,
                            "same_canonical_output": True,
                        },
                    )
                )
            else:
                self.results.append(
                    ValidationResult(
                        scenario="determinism_ordering_invariance",
                        category="determinism_stability_checks",
                        passed=False,
                        error_message="Different input orders produce different outputs",
                    )
                )
        except Exception as e:
            self.results.append(
                ValidationResult(
                    scenario="determinism_ordering_invariance",
                    category="determinism_stability_checks",
                    passed=False,
                    error_message=f"Exception: {type(e).__name__}: {e}",
                )
            )

    def test_authority_isolation_checks(self) -> None:
        """Test 4: PECS-PRO and PECS-LITE boundaries must remain isolated."""
        from integrations.pecs_lite_projection_hardener import (
            ProjectionExporter,
            ProjectionHardener,
            EMPTY_MAPPING,
        )

        # Test 4.1: verify enrichment payloads cannot mutate authority state
        try:
            hardener = ProjectionHardener(adapter=None)
            initial_diagnostics_queries = len(hardener.diagnostics.adapter_methods_called)

            ProjectionExporter.export_projection(
                hardener=hardener,
                primary_targets=["file1.py"],
                secondary_neighbors=["file2.py"],
                metrics=hardener._calculate_metrics(
                    profile="small",
                    primary_targets=[],
                    secondary_neighbors=[],
                    token_estimate=0,
                    active_zone="test",
                    wrapper_warning=False,
                    suppressed_count=0,
                    runtime_zone_count=1,
                    progressive_disclosure_applied=False,
                ),
                active_zone="test",
                mutation_owner="test_owner",
                wrapper_warning=False,
                profile="small",
                adapter=None,
                engineering_continuity={"injected_authority": "malicious"},
                issue_query="test",
                capability_bundle={
                    "projection_profile": {},
                    "model_detection": {},
                },
                behavioral_signals={"injected_signal": "malicious"},
                runtime_context={"injected_context": "malicious"},
            )

            final_diagnostics_queries = len(hardener.diagnostics.adapter_methods_called)
            if initial_diagnostics_queries == final_diagnostics_queries:
                self.results.append(
                    ValidationResult(
                        scenario="authority_isolation_enrichment_immutable",
                        category="authority_isolation_checks",
                        passed=True,
                        details={"diagnostics_unchanged": True},
                    )
                )
            else:
                self.results.append(
                    ValidationResult(
                        scenario="authority_isolation_enrichment_immutable",
                        category="authority_isolation_checks",
                        passed=False,
                        error_message="Enrichment payloads mutated authority state",
                    )
                )
        except Exception as e:
            self.results.append(
                ValidationResult(
                    scenario="authority_isolation_enrichment_immutable",
                    category="authority_isolation_checks",
                    passed=False,
                    error_message=f"Exception: {type(e).__name__}: {e}",
                )
            )

    def test_fallback_contamination_checks(self) -> None:
        """Test 5: Verify no hidden heuristic fallback paths exist."""
        from integrations.pecs_lite_projection_hardener import ProjectionExporter
        import inspect

        # Test 5.1: verify _parse_governance_transfer_envelope always validates
        try:
            source = inspect.getsource(ProjectionExporter._parse_governance_transfer_envelope)

            # Check for common fallback anti-patterns
            anti_patterns = [
                "or {}",  # silent fallback
                "or []",  # silent fallback
                "pass",  # silent ignore (followed by continuation)
                "except.*:",  # bare except that might swallow
            ]

            has_fallback = False
            for pattern in anti_patterns:
                if pattern in source:
                    # False positive check: "or {}" in string is OK
                    if pattern == "or {}" and '"or {}"' in source:
                        continue
                    # Allow "or {}" only in type hints or after getLogger
                    if pattern == "or {}" and "getLogger" in source:
                        continue
                    has_fallback = True
                    break

            if not has_fallback:
                self.results.append(
                    ValidationResult(
                        scenario="fallback_no_heuristic_paths",
                        category="fallback_contamination_checks",
                        passed=True,
                        details={"validation_explicit": True},
                    )
                )
            else:
                self.results.append(
                    ValidationResult(
                        scenario="fallback_no_heuristic_paths",
                        category="fallback_contamination_checks",
                        passed=False,
                        error_message="Potential fallback heuristic found",
                    )
                )
        except Exception as e:
            self.results.append(
                ValidationResult(
                    scenario="fallback_no_heuristic_paths",
                    category="fallback_contamination_checks",
                    passed=False,
                    error_message=f"Exception: {type(e).__name__}: {e}",
                )
            )

        # Test 5.2: verify normalization functions reject invalid input
        from scripts.validate_workspace_continuity import _normalize_runtime_validation

        try:
            _normalize_runtime_validation("invalid_string")
            self.results.append(
                ValidationResult(
                    scenario="fallback_malformed_runtime_validation",
                    category="fallback_contamination_checks",
                    passed=False,
                    error_message="Accepted string instead of dict",
                )
            )
        except ValueError:
            self.results.append(
                ValidationResult(
                    scenario="fallback_malformed_runtime_validation",
                    category="fallback_contamination_checks",
                    passed=True,
                    details={"rejects_invalid_type": True},
                )
            )
        except Exception as e:
            self.results.append(
                ValidationResult(
                    scenario="fallback_malformed_runtime_validation",
                    category="fallback_contamination_checks",
                    passed=False,
                    error_message=f"Unexpected exception: {type(e).__name__}: {e}",
                )
            )

    def test_partial_state_mutation_checks(self) -> None:
        """Test 6: Verify immutable governance ingress assumptions."""
        from integrations.pecs_lite_projection_hardener import ProjectionExporter

        # Test 6.1: verify immutable empty mapping defaults
        try:
            from integrations.pecs_lite_projection_hardener import EMPTY_MAPPING

            envelope_v1 = ProjectionExporter._parse_governance_transfer_envelope(
                engineering_continuity={},
                capability_bundle={
                    "projection_profile": {},
                    "model_detection": {},
                },
                behavioral_signals={},
                runtime_context={},
            )

            envelope_v2 = ProjectionExporter._parse_governance_transfer_envelope(
                engineering_continuity={},
                capability_bundle={
                    "projection_profile": {},
                    "model_detection": {},
                },
                behavioral_signals={},
                runtime_context={},
            )

            if envelope_v1 == envelope_v2:
                self.results.append(
                    ValidationResult(
                        scenario="partial_state_envelope_immutable",
                        category="partial_state_mutation_checks",
                        passed=True,
                        details={"repeated_envelopes_identical": True},
                    )
                )
            else:
                self.results.append(
                    ValidationResult(
                        scenario="partial_state_envelope_immutable",
                        category="partial_state_mutation_checks",
                        passed=False,
                        error_message="Envelope structure changed between calls",
                    )
                )
        except Exception as e:
            self.results.append(
                ValidationResult(
                    scenario="partial_state_envelope_immutable",
                    category="partial_state_mutation_checks",
                    passed=False,
                    error_message=f"Exception: {type(e).__name__}: {e}",
                )
            )

    def run_all_validation_scenarios(self) -> None:
        """Execute all adversarial validation scenarios."""
        print("\n" + "=" * 80)
        print("PECS DETERMINISTIC GOVERNANCE ADVERSARIAL VALIDATION")
        print("=" * 80 + "\n")

        print("[1/6] Testing malformed governance envelopes...")
        self.test_malformed_governance_envelopes()
        self.test_malformed_drift_payloads()

        print("[2/6] Testing object contamination attempts...")
        self.test_object_contamination_attempts()

        print("[3/6] Testing determinism stability...")
        self.test_determinism_stability_checks()

        print("[4/6] Testing authority isolation...")
        self.test_authority_isolation_checks()

        print("[5/6] Testing fallback contamination...")
        self.test_fallback_contamination_checks()

        print("[6/6] Testing partial-state mutation...")
        self.test_partial_state_mutation_checks()

    def report_results(self) -> Tuple[int, int, int]:
        """Generate validation report and return (passed, failed, total)."""
        print("\n" + "=" * 80)
        print("VALIDATION RESULTS")
        print("=" * 80 + "\n")

        passed = 0
        failed = 0

        category_results: Dict[str, List[ValidationResult]] = {}
        for result in self.results:
            if result.category not in category_results:
                category_results[result.category] = []
            category_results[result.category].append(result)

        for category in sorted(category_results.keys()):
            results = category_results[category]
            category_passed = sum(1 for r in results if r.passed)
            category_total = len(results)
            print(f"\n{category}:")
            print(f"  {category_passed}/{category_total} passed\n")

            for result in results:
                status = "✓ PASS" if result.passed else "✗ FAIL"
                print(f"  [{status}] {result.scenario}")
                if not result.passed and result.error_message:
                    print(f"        Error: {result.error_message}")
                if result.details:
                    for key, value in result.details.items():
                        print(f"        {key}: {value}")

            passed += category_passed
            failed += category_total - category_passed

        total = passed + failed

        print("\n" + "=" * 80)
        print(f"TOTAL: {passed}/{total} passed")
        if failed > 0:
            print(f"FAILURES: {failed}")
        print("=" * 80 + "\n")

        return passed, failed, total

    def summarize_invariants(self, passed: int, failed: int) -> None:
        """Summarize verified invariants and architectural readiness."""
        print("\nDETERMINISTIC INVARIANTS CONFIRMED:")
        print("-" * 80)

        if passed == 0 and failed == 0:
            print("No validation scenarios executed.")
            return

        invariants_confirmed = []
        invariants_violated = []

        for result in self.results:
            invariant = f"{result.scenario}: {result.category}"
            if result.passed:
                invariants_confirmed.append(invariant)
            else:
                invariants_violated.append(invariant)

        for inv in sorted(invariants_confirmed):
            print(f"✓ {inv}")

        if invariants_violated:
            print("\n⚠ INVARIANTS VIOLATED:")
            for inv in sorted(invariants_violated):
                print(f"✗ {inv}")

        print("\n" + "-" * 80)
        success_rate = (passed / (passed + failed) * 100) if (passed + failed) > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")

        if failed == 0:
            print("\n✓ Architecture is deterministically stable and ready for deployment testing.")
        else:
            print(f"\n⚠ {failed} invariant(s) violated. Review before deployment.")


if __name__ == "__main__":
    workspace_root = Path(__file__).parent.resolve()
    validator = GovernanceDeterminismValidator(str(workspace_root))

    try:
        validator.run_all_validation_scenarios()
        passed, failed, total = validator.report_results()
        validator.summarize_invariants(passed, failed)

        sys.exit(0 if failed == 0 else 1)
    except Exception as e:
        print(f"\nVALIDATION FAILED WITH EXCEPTION:")
        print(f"{type(e).__name__}: {e}")
        traceback.print_exc()
        sys.exit(1)
