from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "docs" / "reports" / "goal2792_partner_selection_explain_plan_2026-05-31.md"
REVIEW = REPO_ROOT / "docs" / "reviews" / "goal2792_gemini_review_partner_selection_explain_plan_2026-05-31.md"
CONSENSUS = REPO_ROOT / "docs" / "reports" / "goal2792_partner_selection_explain_plan_consensus_2026-05-31.md"


class Goal2792PartnerSelectionExplainPlanTest(unittest.TestCase):
    def test_large_tiled_hausdorff_shape_is_explicit_triton_candidate_not_selection(self) -> None:
        plan = rt.explain_v2_5_partner_selection(
            "grouped_argmin_f64",
            "dense_exact_hausdorff_tiled_nearest_then_global_max",
            source_count=32768,
            target_count=32768,
            dtype="float64",
            available_device_bytes=7 * 1024 * 1024 * 1024,
        )

        self.assertEqual(plan["guidance_status"], "measured_mixed_preview_guidance")
        self.assertEqual(plan["planner_status"], "thresholded_triton_candidate_explicit_choice_required")
        self.assertTrue(plan["threshold_shape_met"])
        self.assertEqual(plan["suggested_explicit_partner_candidate"], "triton")
        self.assertEqual(plan["suggested_explicit_strategy_candidate"], "dense_point_nearest_tiled")
        self.assertFalse(plan["execution_strategy_selected"])
        self.assertFalse(plan["auto_select_partner_allowed"])
        self.assertTrue(plan["requires_explicit_caller_choice"])
        self.assertEqual(plan["memory_note"], "dense_score_matrix_exceeds_available_device_bytes")
        self.assertGreater(plan["estimated_dense_score_bytes"], plan["estimated_tiled_witness_bytes"])
        self.assertFalse(plan["public_speedup_claim_authorized"])
        self.assertFalse(plan["rt_core_speedup_claim_authorized"])
        self.assertFalse(plan["whole_app_speedup_claim_authorized"])
        self.assertFalse(plan["true_zero_copy_claim_authorized"])
        self.assertFalse(plan["release_readiness_authorized"])

    def test_mid_tiled_hausdorff_shape_remains_comparison_partner_candidate(self) -> None:
        plan = rt.explain_v2_5_partner_selection(
            "grouped_argmin_f64",
            "dense_exact_hausdorff_tiled_nearest_then_global_max",
            source_count=8192,
            target_count=8192,
            dtype="float64",
        )

        self.assertEqual(plan["guidance_status"], "measured_mixed_preview_guidance")
        self.assertEqual(plan["planner_status"], "comparison_partner_candidate_below_threshold_or_unmeasured_dtype")
        self.assertFalse(plan["threshold_shape_met"])
        self.assertEqual(plan["suggested_explicit_partner_candidate"], "torch_same_contract_branch")
        self.assertIsNone(plan["suggested_explicit_strategy_candidate"])
        self.assertFalse(plan["auto_select_partner_allowed"])

    def test_negative_guidance_explain_plan_keeps_comparison_partner(self) -> None:
        plan = rt.explain_v2_5_partner_selection(
            "grouped_topk_f64",
            "dense_exact_topk_candidate_ranking",
            row_count=1000000,
            dtype="float64",
        )

        self.assertEqual(plan["guidance_status"], "measured_negative_preview_guidance")
        self.assertEqual(plan["planner_status"], "comparison_partner_candidate_due_to_negative_preview")
        self.assertEqual(plan["suggested_explicit_partner_candidate"], "torch_same_contract_branch")
        self.assertFalse(plan["auto_select_partner_allowed"])
        self.assertIn("negative", " ".join(plan["reasons"]).lower())

    def test_unknown_guidance_stays_fail_closed(self) -> None:
        plan = rt.explain_v2_5_partner_selection(
            "segmented_count_i64",
            "unmeasured_shape",
            row_count=128,
        )

        self.assertEqual(plan["guidance_status"], "no_measured_guidance")
        self.assertEqual(plan["planner_status"], "no_measured_guidance_explicit_choice_required")
        self.assertIsNone(plan["suggested_explicit_partner_candidate"])
        self.assertFalse(plan["auto_select_partner_allowed"])

    def test_invalid_shape_values_fail_closed(self) -> None:
        with self.assertRaises(ValueError):
            rt.explain_v2_5_partner_selection(
                "grouped_argmin_f64",
                "dense_exact_hausdorff_tiled_nearest_then_global_max",
                source_count=-1,
                target_count=32768,
            )
        with self.assertRaises(ValueError):
            rt.explain_v2_5_partner_selection(
                "grouped_argmin_f64",
                "dense_exact_hausdorff_tiled_nearest_then_global_max",
                source_count=32768,
                target_count=32768,
                candidate_block_size=0,
            )

    def test_report_review_and_consensus_are_present(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        review = REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("Goal2792", report)
        self.assertIn("explain", report.lower())
        self.assertIn("explicit caller choice", report)
        self.assertIn("accept-with-boundary", review.lower())
        self.assertIn("accept-with-boundary", consensus.lower())
        self.assertIn(str(REVIEW.relative_to(REPO_ROOT)).replace("\\", "/"), consensus)


if __name__ == "__main__":
    unittest.main()
