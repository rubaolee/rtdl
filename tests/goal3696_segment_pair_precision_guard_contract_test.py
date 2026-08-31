from __future__ import annotations

import pathlib
import unittest

from rtdsl.segment_pair_contracts import (
    SEGMENT_PAIR_FLOAT32_PARAM_GUARD_EPSILON,
    SEGMENT_PAIR_PRECISION_GUARD_VERSION,
    segment_pair_intersection_float32_candidate_v0,
    segment_pair_precision_guard_candidate_v0,
    segment_pair_precision_guard_cases,
    validate_segment_pair_precision_guard_cases,
)


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal3696_segment_pair_precision_guard_candidate_contract_2026-06-07.md"
CONTRACTS = ROOT / "src/rtdsl/segment_pair_contracts.py"


class Goal3696SegmentPairPrecisionGuardContractTest(unittest.TestCase):
    def test_precision_guard_fixture_reproduces_rounding_flip(self) -> None:
        case = segment_pair_precision_guard_cases()[0]
        low_precision = segment_pair_intersection_float32_candidate_v0(case.left, case.right)
        guarded = segment_pair_precision_guard_candidate_v0(case.left, case.right)

        self.assertEqual(case.name, "endpoint_near_rounding_flip")
        self.assertEqual(SEGMENT_PAIR_FLOAT32_PARAM_GUARD_EPSILON, 1.0e-3)
        self.assertTrue(guarded.exact_decision.hit)
        self.assertFalse(low_precision.hit)
        self.assertLess(low_precision.t, 0.0)
        self.assertTrue(guarded.emit_candidate)
        self.assertTrue(guarded.refine_required)
        self.assertEqual(guarded.reason, "exact_hit_low_precision_miss_requires_refine")

    def test_precision_guard_validation_is_bounded_and_non_authorizing(self) -> None:
        summary = validate_segment_pair_precision_guard_cases()

        self.assertTrue(summary["valid"], summary)
        self.assertEqual(summary["version"], SEGMENT_PAIR_PRECISION_GUARD_VERSION)
        self.assertEqual(summary["case_count"], 1)
        self.assertEqual(summary["failures"], ())
        self.assertIn("exact_hit_low_precision_miss_requires_refine", summary["decision_reasons"])
        self.assertFalse(summary["public_api_specification"])
        self.assertFalse(summary["release_authorized"])
        self.assertFalse(summary["public_speedup_claim_authorized"])
        self.assertIn("not a native implementation", summary["claim_boundary"])

    def test_contract_source_stays_app_agnostic(self) -> None:
        source = CONTRACTS.read_text(encoding="utf-8")
        precision_guard_source = source.split("def segment_pair_intersection_float32_candidate_v0", 1)[1].split(
            "def segment_pair_contract_adversarial_cases",
            1,
        )[0]
        self.assertNotIn("RayJoin", precision_guard_source)
        self.assertNotIn("CDB", precision_guard_source)
        self.assertNotIn("GIS", precision_guard_source)
        self.assertIn("segment_pair_precision_guard_candidate_v0", source)
        self.assertIn("low-precision traversal predicate", source)

    def test_report_states_next_native_acceptance_without_claims(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("app-agnostic executable contract", report)
        self.assertIn("emit_candidate = true", report)
        self.assertIn("refine_required = true", report)
        self.assertIn("not claim the OptiX runtime has already been repaired", report)
        self.assertIn("missing count `0`", report)
        self.assertIn("does not authorize release", report)


if __name__ == "__main__":
    unittest.main()
