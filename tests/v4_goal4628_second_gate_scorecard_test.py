from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rtdsl.v4_second_gate_scorecard import V4_GOAL4628_FIXED_RADIUS_PREREQUISITE
from rtdsl.v4_second_gate_scorecard import V4_GOAL4628_TARGET_OPERATOR
from rtdsl.v4_second_gate_scorecard import validate_v4_goal4628_second_gate_scorecard
from rtdsl.v4_second_gate_scorecard import v4_goal4628_second_gate_scorecard


class V4Goal4628SecondGateScorecardTest(unittest.TestCase):
    def test_scorecard_targets_grouped_i64_as_second_gate(self) -> None:
        scorecard = validate_v4_goal4628_second_gate_scorecard()

        self.assertEqual(scorecard["anchor_app"], "raydb_style")
        self.assertEqual(scorecard["operator"], V4_GOAL4628_TARGET_OPERATOR)
        self.assertEqual(scorecard["generic_primitive"], "RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D")
        self.assertEqual(scorecard["group_widths"], (1, 16, 256))
        self.assertEqual(scorecard["ray_counts"], (32768, 131072))

    def test_scorecard_records_existing_serious_pod_ratios(self) -> None:
        scorecard = v4_goal4628_second_gate_scorecard()
        ratios = {(row["group_width"], row["ray_count"]): row for row in scorecard["ratios"]}

        self.assertAlmostEqual(ratios[(1, 32768)]["same_contract_ratio"], 166.5457315834383)
        self.assertAlmostEqual(ratios[(1, 131072)]["same_contract_ratio"], 411.8665310113891)
        self.assertAlmostEqual(ratios[(16, 32768)]["same_contract_ratio"], 11.270692268822637)
        self.assertAlmostEqual(ratios[(16, 131072)]["same_contract_ratio"], 21.3693298753451)
        self.assertAlmostEqual(ratios[(256, 32768)]["same_contract_ratio"], 1.6413506440190897)
        self.assertAlmostEqual(ratios[(256, 131072)]["same_contract_ratio"], 2.977954183815882)
        self.assertTrue(scorecard["parity_all_passed"])
        self.assertGreater(scorecard["min_same_contract_ratio"], 1.0)

    def test_scorecard_keeps_fixed_radius_prerequisite_visible(self) -> None:
        scorecard = v4_goal4628_second_gate_scorecard()

        self.assertEqual(scorecard["fixed_radius_wrapper_prerequisite"], V4_GOAL4628_FIXED_RADIUS_PREREQUISITE)
        self.assertIn("src/rtdsl/v4_fixed_radius.py", scorecard["fixed_radius_wrapper_prerequisite_satisfied_by"])
        self.assertIn(
            "tools/_archive/future/v4/reviews/claude_v4_section8_device_array_frontdoor_amendment_closure_2026-06-24.md",
            scorecard["fixed_radius_wrapper_prerequisite_satisfied_by"],
        )

    def test_scorecard_does_not_authorize_release_or_broad_claims(self) -> None:
        scorecard = v4_goal4628_second_gate_scorecard()

        self.assertFalse(scorecard["fresh_pod_rerun_required_before_goal4628_completion"])
        for flag in (
            "release_claim_authorized",
            "broad_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
            "tier3_callback_claim_authorized",
            "cupy_performance_claim_authorized",
            "app_specific_native_kernel_authorized",
        ):
            self.assertFalse(scorecard[flag])


if __name__ == "__main__":
    unittest.main()
