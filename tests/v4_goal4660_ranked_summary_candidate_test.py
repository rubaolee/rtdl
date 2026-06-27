from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4 as v4
from rtdsl import v4_ranked_summary


RTNN_APP = ROOT / "examples" / "current" / "research_benchmarks" / "rtnn" / "rtdl_rtnn_benchmark_app.py"
SUMMARY = ROOT / "future" / "v4" / "evidence" / "v4_goal4660_rtnn_ranked_summary_20260625" / "summary.json"


class V4Goal4660RankedSummaryCandidateTest(unittest.TestCase):
    def test_ranked_summary_is_deferred_after_goal4678_not_measured(self) -> None:
        candidates = v4.candidate_operator_catalog_v4()
        rows = {row["operator"]: row for row in candidates}

        self.assertNotIn("fixed_radius_ranked_summary_3d", rows)

        measured = {row["operator"] for row in v4.measured_operator_catalog_v4()}
        self.assertNotIn("fixed_radius_ranked_summary_3d", measured)

    def test_planner_defers_ranked_summary_without_release_claims(self) -> None:
        plan = v4.plan_operator_request_v4("fixed_radius_ranked_summary", partner="rtdl_native")

        self.assertEqual("deferred_goal4678_serious_scale_parity_not_release", plan.status)
        self.assertEqual("deferred_v4_x_or_research", plan.tier)
        self.assertIsNone(plan.api_surface)
        self.assertFalse(plan.measured_partner)
        self.assertFalse(plan.release_claim_authorized)
        self.assertFalse(plan.broad_v4_speedup_claim_authorized)

    def test_rtnn_app_calls_v4_ranked_summary_wrapper(self) -> None:
        text = RTNN_APP.read_text(encoding="utf-8")

        self.assertIn("import rtdsl.v4_ranked_summary as ranked_v4", text)
        self.assertIn("run_fixed_radius_ranked_summary_3d_prepared_runner_v4", text)
        self.assertIn("v4_fixed_radius_ranked_summary_3d_prepared_runner", text)
        self.assertNotIn("rtnn_native_kernel", text)

    def test_claim_boundary_is_deferred_only(self) -> None:
        boundary = v4_ranked_summary.fixed_radius_ranked_summary_3d_prepared_runner_claim_boundary_v4()

        self.assertEqual("deferred_goal4678_serious_scale_parity_not_release", boundary["status"])
        self.assertFalse(boundary["candidate_surface"])
        self.assertTrue(boundary["deferred_surface"])
        self.assertFalse(boundary["measured_v4_release_surface"])
        self.assertFalse(boundary["release_claim_authorized"])
        self.assertFalse(boundary["full_rtnn_paper_reproduction"])

    def test_pod_summary_marks_rtnn_candidate_as_not_moving_app_bar(self) -> None:
        summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

        self.assertEqual(["Goal4660", "Goal4661"], summary["goal_ids"])
        self.assertEqual("rtnn", summary["benchmark_app"])
        self.assertEqual(
            "v4_fixed_radius_ranked_summary_3d_prepared_runner",
            summary["v4_surface"],
        )
        self.assertEqual(
            "candidate_goal4660_needs_pod_scorecard_not_release",
            summary["v4_candidate_status"],
        )
        self.assertFalse(summary["denominator_boundary"]["old_denominator_exact_same_runner"])
        self.assertFalse(
            summary["denominator_boundary"]["old_versions_have_prepared_execution_ranked_summary_frontdoor"]
        )
        self.assertEqual("rtnn_candidate_does_not_move_app_level_bar", summary["decision"]["label"])
        self.assertFalse(summary["decision"]["may_count_as_formal_high_performance_v4_evidence"])
        self.assertFalse(summary["decision"]["may_trigger_full_all_app_rerun"])
        self.assertFalse(summary["claim_boundary"]["release_authorized"])
        self.assertFalse(summary["claim_boundary"]["public_speedup_claim_authorized"])

    def test_serious_scale_rows_show_parity_not_material_speedup(self) -> None:
        summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        rows = {row["point_count"]: row for row in summary["scales"]}

        self.assertIn(262144, rows)
        self.assertIn(1048576, rows)
        self.assertLess(rows[262144]["speedup_hot_median_v4_over_v2_14"], 1.01)
        self.assertLess(rows[262144]["speedup_hot_median_v4_over_v3_0_2"], 1.01)
        self.assertLess(rows[1048576]["speedup_hot_median_v4_over_v2_14"], 1.0)
        self.assertLess(rows[1048576]["speedup_hot_median_v4_over_v3_0_2"], 1.0)

        for row in rows.values():
            candidate = row["v4_candidate_route"]
            self.assertTrue(candidate["runtime_trunk_executes_end_to_end"])
            self.assertTrue(candidate["runtime_executed"])
            self.assertTrue(candidate["prepared_queries_resident"])
            self.assertFalse(candidate["hot_path_host_materialization"])
            self.assertTrue(candidate["validation_passed"])
            self.assertFalse(candidate["measured_v4_release_surface"])
            self.assertFalse(candidate["release_authorized"])
            self.assertFalse(candidate["public_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
