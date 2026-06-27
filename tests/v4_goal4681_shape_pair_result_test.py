from __future__ import annotations

import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4 as v4


class V4Goal4681ShapePairResultTest(unittest.TestCase):
    def test_goal4681_result_is_correct_but_not_speed_credit(self) -> None:
        result = v4.v4_goal4681_shape_pair_relation_result().as_dict()

        self.assertEqual(
            "goal4681_correct_same_primitive_but_no_speed_credit_do_not_promote",
            result["status"],
        )
        self.assertEqual(
            "goal4681_no_speed_credit_productization_or_reclassify",
            result["decision_label"],
        )
        self.assertTrue(result["correctness_passed"])
        self.assertTrue(result["serious_active_count_parity"])
        self.assertTrue(result["no_v4_host_row_stream_materialization"])
        self.assertFalse(result["speed_credit_passed"])
        self.assertLess(result["ratios"]["v4_hot_over_v2_14_same_primitive"], 1.20)
        self.assertLess(result["ratios"]["v4_wall_over_v2_14_same_primitive"], 1.10)
        self.assertFalse(result["release_authorized"])
        self.assertFalse(result["promote_to_measured_catalog_authorized"])

    def test_goal4681_validation_passes_no_promotion(self) -> None:
        validation = v4.validate_v4_goal4681_shape_pair_relation_result()

        self.assertEqual("passed", validation["status"])
        self.assertEqual((), validation["missing_or_invalid"])
        self.assertFalse(validation["release_authorized"])

    def test_current_frontdoor_still_has_no_candidate_surfaces(self) -> None:
        boundary = v4.claim_boundary_v4()

        self.assertEqual((), boundary["candidate_surfaces"])
        self.assertEqual([], v4.candidate_operator_catalog_v4())


if __name__ == "__main__":
    unittest.main()
