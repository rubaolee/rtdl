from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.v4_goal4639_release_scorecard_decision import V4_GOAL4639_DECISION
from rtdsl.v4_goal4639_release_scorecard_decision import validate_v4_goal4639_release_scorecard_decision


class V4Goal4639ReleaseScorecardDecisionTest(unittest.TestCase):
    def test_goal4639_passes_frozen_scorecard_without_authorizing_release(self) -> None:
        decision = validate_v4_goal4639_release_scorecard_decision()

        self.assertEqual(V4_GOAL4639_DECISION, decision["decision"])
        self.assertEqual("release_candidate_possible_pending_3ai", decision["recommendation_from_scorecard"])
        self.assertEqual(4, decision["strong_families_passed"])
        self.assertEqual(4, decision["strong_families_total"])
        self.assertEqual(8, decision["measured_surfaces_passed"])
        self.assertEqual(8, decision["measured_surfaces_total"])
        self.assertEqual((), decision["failed_surfaces"])
        self.assertFalse(decision["release_authorized"])
        self.assertFalse(decision["release_candidate_authorized"])

    def test_goal4639_records_material_but_bounded_surface_ratios(self) -> None:
        decision = validate_v4_goal4639_release_scorecard_decision()
        ratios = decision["surface_representative_ratios"]

        self.assertEqual(8, len(ratios))
        self.assertGreater(ratios["v4_aabb_index_query_2d_all_ops_count_prepared_runner"], 100.0)
        self.assertGreater(ratios["v4_point_group_nearest_witness_2d_device_arrays"], 100.0)
        self.assertGreater(ratios["v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays"], 1.20)
        self.assertGreater(ratios["v4_fixed_radius_graph_component_union_3d_device_arrays"], 1.20)
        self.assertGreater(decision["strong_representative_ratio_geomean"], 1.0)

    def test_goal4639_records_public_distribution_and_denominators(self) -> None:
        decision = validate_v4_goal4639_release_scorecard_decision()
        denominators = decision["surface_denominators"]
        distribution = decision["public_ratio_distribution"]

        self.assertEqual(set(decision["surface_representative_ratios"]), set(denominators))
        for surface, metadata in denominators.items():
            with self.subTest(surface=surface):
                self.assertTrue(metadata["baseline"])
                self.assertTrue(metadata["scale"])
                self.assertTrue(metadata["presentation_class"])
        self.assertIn("1.2-1.7x", distribution["core_operator_cluster"])
        self.assertIn("Do not headline the 5.185x geomean", distribution["headline_rule"])

    def test_goal4639_forbidden_claims_stay_false(self) -> None:
        decision = validate_v4_goal4639_release_scorecard_decision()

        for flag in (
            "broad_v4_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "all_benchmark_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
            "tier3_callback_claim_authorized",
            "raw_optix_callback_claim_authorized",
            "cupy_performance_claim_authorized",
            "c_abi_or_embedding_claim_authorized",
            "non_python_host_claim_authorized",
            "app_specific_native_kernel_authorized",
        ):
            self.assertFalse(decision[flag])


if __name__ == "__main__":
    unittest.main()
