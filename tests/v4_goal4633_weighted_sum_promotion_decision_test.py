from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rtdsl.v4_weighted_sum_promotion_decision import validate_v4_goal4633_weighted_sum_promotion_decision
from rtdsl.v4_weighted_sum_promotion_decision import v4_goal4633_weighted_sum_promotion_decision


EVIDENCE_JSON = ROOT / "future" / "v4" / "evidence" / "v4_goal4633_weighted_sum_promotion_gate_2026-06-25.json"
EVIDENCE_MD = ROOT / "future" / "v4" / "evidence" / "v4_goal4633_weighted_sum_promotion_gate_2026-06-25.md"


class V4Goal4633WeightedSumPromotionDecisionTest(unittest.TestCase):
    def test_decision_records_measured_catalog_promotion_with_review_debt(self) -> None:
        decision = validate_v4_goal4633_weighted_sum_promotion_decision()

        self.assertEqual(decision["decision"], "promote_weighted_sum_measured_torch_v4_tier2")
        self.assertTrue(decision["promotion_thresholds_passed"])
        self.assertTrue(decision["measured_catalog_promotion_authorized"])
        self.assertTrue(decision["weighted_sum_can_count_as_measured_release_surface"])
        self.assertTrue(decision["completion_review_debt_recorded"])
        self.assertEqual(decision["surface_status_after_goal4633"], "tier2_measured_pod_validated_not_release")

    def test_evidence_json_matches_recorded_ratios_and_boundary(self) -> None:
        payload = json.loads(EVIDENCE_JSON.read_text(encoding="utf-8"))
        decision = v4_goal4633_weighted_sum_promotion_decision()

        self.assertEqual(payload["comparison_boundary"]["comparison_class"], "same_operator_comparable_route")
        self.assertFalse(payload["comparison_boundary"]["pure_kernel_speedup"])
        self.assertTrue(payload["promotion_gate"]["promotion_thresholds_passed"])
        self.assertAlmostEqual(
            payload["promotion_gate"]["min_ratio"],
            decision["min_comparable_route_ratio"],
        )
        self.assertAlmostEqual(
            payload["promotion_gate"]["geomean_ratio"],
            decision["geomean_comparable_route_ratio"],
        )
        by_ray = {
            row["ray_count"]: row["comparison"]["host_materialization_over_device_resident_median_ratio"]
            for row in payload["results"]
        }
        for row in decision["ratios"]:
            self.assertAlmostEqual(by_ray[row["ray_count"]], row["comparable_route_ratio"])

    def test_evidence_markdown_preserves_non_authorization(self) -> None:
        text = EVIDENCE_MD.read_text(encoding="utf-8")

        self.assertIn("same weighted-sum operator", text)
        self.assertIn("not a pure kernel-vs-kernel speedup", text)
        self.assertIn("V4 release is not authorized", text)
        self.assertIn("CuPy performance claims are not authorized", text)

    def test_caveats_include_barely_above_gate_row(self) -> None:
        decision = v4_goal4633_weighted_sum_promotion_decision()

        self.assertAlmostEqual(decision["min_comparable_route_ratio"], 1.2011325646448796)
        self.assertIn(
            "minimum_shape_ratio_is_barely_above_gate_at_524288_rows",
            decision["promotion_caveats"],
        )


if __name__ == "__main__":
    unittest.main()
