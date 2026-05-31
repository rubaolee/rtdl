from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "docs" / "reports" / "goal2791_thresholded_partner_selection_guidance_2026-05-31.md"
REVIEW = REPO_ROOT / "docs" / "reviews" / "goal2791_gemini_review_thresholded_partner_selection_guidance_2026-05-31.md"
CONSENSUS = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2791_thresholded_partner_selection_guidance_consensus_2026-05-31.md"
)
GOAL2790_ARTIFACT = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2790_pod_artifacts"
    / "goal2790_tiled_dense_point_nearest_hausdorff_pod_69_30_85_171_2026-05-31.json"
)
GOAL2791_ARTIFACT = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2791_pod_artifacts"
    / "goal2791_hausdorff_32k_tiled_probe_pod_69_30_85_171_2026-05-31.json"
)


class Goal2791ThresholdedPartnerSelectionGuidanceTest(unittest.TestCase):
    def test_tiled_hausdorff_guidance_is_mixed_and_claim_safe(self) -> None:
        guidance = rt.v2_5_partner_selection_guidance()
        validation = rt.validate_v2_5_partner_selection_guidance(guidance, repo_root=REPO_ROOT)
        plan = rt.plan_v2_5_partner_selection(
            "grouped_argmin_f64",
            "dense_exact_hausdorff_tiled_nearest_then_global_max",
        )

        self.assertEqual(validation["status"], "accept")
        self.assertEqual(guidance["row_count"], 9)
        self.assertEqual(plan["status"], "measured_mixed_preview_guidance")
        self.assertFalse(plan["auto_select_partner_allowed"])

        row = plan["matches"][0]
        self.assertEqual(row["evidence_goal"], "Goal2790")
        self.assertEqual(row["guidance_status"], "measured_mixed_preview_guidance")
        self.assertEqual(
            row["measurement_ratio_kind"],
            "measured_partner_wall_time_over_comparison_partner_wall_time",
        )
        self.assertTrue(row["ratio_less_than_one_means_measured_partner_faster"])
        self.assertLess(row["measured_partner_over_comparison_min_ratio"], 1.0)
        self.assertGreater(row["measured_partner_over_comparison_max_ratio"], 1.0)
        self.assertEqual(row["measured_partner_faster_shape_count"], 1)
        self.assertEqual(row["measured_partner_slower_shape_count"], 3)
        self.assertIn("16K", row["measured_crossover_summary"])
        self.assertIn("thresholded preview evidence", row["recommendation"])
        self.assertFalse(row["auto_select_measured_partner_allowed"])
        self.assertFalse(row["promoted_performance_path"])
        self.assertFalse(row["public_speedup_claim_authorized"])
        self.assertFalse(row["rt_core_speedup_claim_authorized"])
        self.assertFalse(row["whole_app_speedup_claim_authorized"])
        self.assertFalse(row["true_zero_copy_claim_authorized"])
        self.assertFalse(row["release_readiness_authorized"])
        self.assertTrue((REPO_ROOT / row["artifact_path"]).exists())

    def test_hausdorff_app_migration_consumes_thresholded_guidance(self) -> None:
        apps = {app["app_id"]: app for app in rt.v2_5_triton_benchmark_app_migration_plan()["apps"]}
        hausdorff = apps["hausdorff_xhd"]
        statuses = tuple(guidance["status"] for guidance in hausdorff["partner_selection_guidance"])

        self.assertEqual(hausdorff["measured_negative_preview_guidance_count"], 2)
        self.assertEqual(hausdorff["measured_mixed_preview_guidance_count"], 1)
        self.assertIn("measured_mixed_preview_guidance", statuses)
        self.assertFalse(hausdorff["auto_select_preview_partner_allowed"])
        self.assertIn("thresholded", hausdorff["first_port_action"])
        self.assertEqual(rt.validate_v2_5_triton_benchmark_app_migration_plan()["status"], "accept")

    def test_goal2790_artifact_records_both_sides_of_crossover(self) -> None:
        import json

        artifact = json.loads(GOAL2790_ARTIFACT.read_text(encoding="utf-8"))
        ratios = [
            float(row["best_tiled_over_torch_ratio"])
            for row in artifact["rows"]
            if row.get("best_tiled_over_torch_ratio") is not None
        ]

        self.assertTrue(any(ratio < 1.0 for ratio in ratios))
        self.assertTrue(any(ratio > 1.0 for ratio in ratios))
        self.assertFalse(artifact["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertFalse(artifact["claim_boundary"]["rt_core_speedup_claim_authorized"])
        self.assertFalse(artifact["claim_boundary"]["whole_app_speedup_claim_authorized"])
        self.assertFalse(artifact["claim_boundary"]["true_zero_copy_claim_authorized"])

    def test_goal2791_large_shape_probe_records_bounded_tiled_completion(self) -> None:
        import json

        artifact = json.loads(GOAL2791_ARTIFACT.read_text(encoding="utf-8"))
        rows = [row for row in artifact["blocks"] if row["status"] == "ok"]

        self.assertEqual(artifact["shape"], 32768)
        self.assertEqual(artifact["best_block"], 4096)
        self.assertGreaterEqual(len(rows), 4)
        self.assertEqual(artifact["torch"]["status"], "not_rerun_after_prior_oom")
        self.assertTrue(artifact["claim_boundary"]["bounded_tiled_completion_evidence"])
        self.assertFalse(artifact["claim_boundary"]["same_contract_torch_speedup_claim_authorized"])
        self.assertFalse(artifact["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertFalse(artifact["claim_boundary"]["rt_core_speedup_claim_authorized"])
        self.assertFalse(artifact["claim_boundary"]["whole_app_speedup_claim_authorized"])
        self.assertFalse(artifact["claim_boundary"]["true_zero_copy_claim_authorized"])
        self.assertFalse(artifact["claim_boundary"]["v2_5_release_authorized"])
        self.assertTrue(all(row["metadata"]["v2_5_release_authorized"] is False for row in rows))
        self.assertTrue(all(row["metadata"]["rt_core_speedup_claim_authorized"] is False for row in rows))
        self.assertTrue(all(row["metadata"]["whole_app_speedup_claim_authorized"] is False for row in rows))
        self.assertTrue(all(row["metadata"]["direct_device_handoff_authorized"] is False for row in rows))
        for row in rows[1:]:
            self.assertEqual(row["distance_error_vs_block_512"], 0.0)
            self.assertTrue(row["source_id_match_vs_block_512"])
            self.assertTrue(row["target_id_match_vs_block_512"])

    def test_report_review_and_consensus_are_present(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        review = REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("Goal2791", report)
        self.assertIn("thresholded", report.lower())
        self.assertIn("Goal2790", report)
        self.assertIn("accept-with-boundary", review.lower())
        self.assertIn("accept-with-boundary", consensus.lower())
        self.assertIn(str(REVIEW.relative_to(REPO_ROOT)).replace("\\", "/"), consensus)


if __name__ == "__main__":
    unittest.main()
