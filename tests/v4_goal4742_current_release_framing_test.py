from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "future" / "v4" / "evidence" / "v4_goal4742_current_release_framing_after_blocker_closure_2026-06-26.json"
REPORT = ROOT / "future" / "v4" / "v4_goal4742_current_release_framing_after_blocker_closure_2026-06-26.md"


class V4Goal4742CurrentReleaseFramingTest(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        self.rows = {row["app"]: row for row in self.payload["benchmark_app_matrix"]["rows"]}

    def test_bounded_label_not_all_apps_faster(self) -> None:
        position = self.payload["current_position"]
        self.assertEqual(
            "bounded_high_performance_python_edsl_operator_pushdown_release_candidate",
            position["recommended_label"],
        )
        self.assertFalse(position["all_10_historical_benchmark_apps_faster_than_v2_14"])
        self.assertFalse(position["final_tag_authorized"])

    def test_three_historical_candidate_apps(self) -> None:
        matrix = self.payload["benchmark_app_matrix"]
        self.assertEqual(10, matrix["app_count"])
        self.assertEqual(3, matrix["candidate_rows_vs_v2_with_v3_no_regression"])
        self.assertEqual(["hausdorff_xhd", "triangle_counting", "barnes_hut"], matrix["candidate_apps"])
        for app in matrix["candidate_apps"]:
            self.assertGreater(self.rows[app]["v4_vs_v2_14_hot"], 1.20)
            self.assertGreaterEqual(self.rows[app]["v4_vs_v3_0_2_hot"], 0.98)

    def test_custom_predicate_counts_as_edsl_value_not_legacy_app_win(self) -> None:
        value = self.payload["v4_edsl_operator_pushdown_value"]
        self.assertEqual("v4_ray_triangle_custom_predicate_early_exit_3d_numba", value["surface"])
        self.assertGreater(value["v4_vs_v2_14_materialized_device_fallback_geomean"], 4.0)
        self.assertGreater(value["minimum_primary_ratio"], 2.0)
        self.assertFalse(value["counts_as_legacy_10_app_win"])
        self.assertTrue(value["counts_as_v4_edsl_value"])

    def test_blocked_wording_prevents_overclaiming(self) -> None:
        blocked = set(self.payload["blocked_wording"])
        self.assertIn("all benchmark apps are faster", blocked)
        self.assertIn("V4 universally beats V2.14", blocked)
        self.assertIn("formal high-performance across the full 10-app suite", blocked)
        self.assertIn("arbitrary Python callbacks", blocked)
        self.assertIn("true zero-copy", blocked)
        self.assertIn("does not claim that all historical benchmark apps are faster", REPORT.read_text(encoding="utf-8"))

    def test_claim_boundary_blocks_tag(self) -> None:
        boundary = self.payload["claim_boundary"]
        for key in (
            "release_authorized",
            "final_v4_tag_authorized",
            "all_benchmark_speedup_claim_authorized",
            "broad_v4_over_v2_14_claim_authorized",
            "formal_high_performance_across_full_10_app_suite_authorized",
            "arbitrary_callback_support_authorized",
            "raw_optix_callback_support_authorized",
            "true_zero_copy_wording_authorized",
            "non_python_embedding_c_abi_claim_authorized",
            "app_specific_native_kernel_authorized",
        ):
            self.assertFalse(boundary[key], key)

    def test_next_goals_are_release_hardening_not_more_churn(self) -> None:
        goals = self.payload["next_goals"]
        self.assertEqual(["Goal4743", "Goal4744", "Goal4745", "Goal4746"], [goal["id"] for goal in goals])
        self.assertEqual("public_docs_examples_status", goals[0]["target"])
        self.assertEqual("final_release_or_reject_decision", goals[-1]["target"])


if __name__ == "__main__":
    unittest.main()
