from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rtdsl.v4_coverage_audit import V4_COVERAGE_STRONG_MEASURED
from rtdsl.v4_coverage_audit import v4_goal4627_coverage_rows
from rtdsl.v4_weighted_sum_candidate_decision import V4_GOAL4629_DECISION
from rtdsl.v4_weighted_sum_candidate_decision import V4_GOAL4629_SURFACE
from rtdsl.v4_weighted_sum_candidate_decision import V4_GOAL4629_SURFACE_STATUS
from rtdsl.v4_weighted_sum_candidate_decision import validate_v4_goal4629_weighted_sum_candidate_decision
from rtdsl.v4_weighted_sum_candidate_decision import v4_goal4629_weighted_sum_candidate_decision


class V4Goal4629WeightedSumCandidateDecisionTest(unittest.TestCase):
    def test_decision_keeps_weighted_sum_candidate_not_measured(self) -> None:
        decision = validate_v4_goal4629_weighted_sum_candidate_decision()

        self.assertEqual(decision["decision"], V4_GOAL4629_DECISION)
        self.assertEqual(decision["surface"], V4_GOAL4629_SURFACE)
        self.assertEqual(decision["surface_status_after_goal4629"], V4_GOAL4629_SURFACE_STATUS)
        self.assertTrue(decision["candidate_gate_passed"])
        self.assertFalse(decision["measured_catalog_promotion_authorized"])
        self.assertFalse(decision["weighted_sum_can_count_as_measured_release_surface"])

    def test_decision_records_candidate_ratios_without_promoting(self) -> None:
        decision = v4_goal4629_weighted_sum_candidate_decision()
        ratios = {row["ray_count"]: row for row in decision["ratios"]}

        self.assertAlmostEqual(ratios[32768]["same_contract_ratio"], 2.047)
        self.assertAlmostEqual(ratios[131072]["same_contract_ratio"], 1.557)
        self.assertTrue(ratios[32768]["parity_passed"])
        self.assertTrue(ratios[131072]["parity_passed"])
        self.assertEqual(decision["repeat_count"], 5)
        self.assertEqual(decision["warmup_count"], 2)
        self.assertEqual(decision["partner_scope"], ("torch_cuda",))
        self.assertGreater(decision["min_same_contract_ratio"], 1.0)

    def test_decision_preserves_device_output_metadata_and_promotion_blockers(self) -> None:
        decision = v4_goal4629_weighted_sum_candidate_decision()

        self.assertTrue(decision["device_output_used"])
        self.assertFalse(decision["host_scalar_read_before_consumer"])
        self.assertFalse(decision["host_row_materialization_before_consumer"])
        self.assertTrue(decision["cuda_stream_ptr_nonzero"])
        self.assertIn(
            "goal4620_external_review_authorized_candidate_completion_but_not_measured_catalog_promotion",
            decision["promotion_blockers"],
        )
        self.assertIn("expand_same_contract_shape_matrix_beyond_two_sizes", decision["future_promotion_requirements"])
        self.assertIn(
            "increase_repeat_count_to_release_gate_level_beyond_5_candidate_repeats",
            decision["future_promotion_requirements"],
        )
        self.assertIn("measure_cupy_and_non_torch_partner_performance", decision["future_promotion_requirements"])
        self.assertIn(
            "prove_triangle_counting_primary_route_release_coverage",
            decision["future_promotion_requirements"],
        )

    def test_historical_candidate_decision_is_superseded_by_goal4633_coverage_refresh(self) -> None:
        decision = v4_goal4629_weighted_sum_candidate_decision()
        rows_by_app = {row.app: row for row in v4_goal4627_coverage_rows()}

        self.assertEqual(decision["triangle_counting_release_coverage_after_goal4629"], "candidate_not_measured_release_coverage")
        self.assertEqual(rows_by_app["triangle_counting"].coverage_status, V4_COVERAGE_STRONG_MEASURED)
        self.assertIn(V4_GOAL4629_SURFACE, rows_by_app["triangle_counting"].mapped_v4_operators)
        self.assertIn("goal4633", rows_by_app["triangle_counting"].evidence_refs[-1])

    def test_decision_does_not_authorize_release_or_broad_claims(self) -> None:
        decision = v4_goal4629_weighted_sum_candidate_decision()

        for flag in (
            "release_claim_authorized",
            "broad_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "measured_catalog_claim_authorized",
            "true_zero_copy_claim_authorized",
            "tier3_callback_claim_authorized",
            "cupy_performance_claim_authorized",
            "c_abi_or_embedding_claim_authorized",
            "app_specific_native_kernel_authorized",
        ):
            self.assertFalse(decision[flag])


if __name__ == "__main__":
    unittest.main()
