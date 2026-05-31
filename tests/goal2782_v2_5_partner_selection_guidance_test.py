from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "docs" / "reports" / "goal2782_v2_5_partner_selection_guidance_2026-05-31.md"
CONSENSUS = REPO_ROOT / "docs" / "reports" / "goal2782_v2_5_partner_selection_guidance_consensus_2026-05-31.md"
GEMINI_REVIEW = REPO_ROOT / "docs" / "reviews" / "goal2782_gemini_review_partner_selection_guidance_2026-05-31.md"
CLAUDE_REVIEW = REPO_ROOT / "docs" / "reviews" / "goal2782_claude_review_partner_selection_guidance_2026-05-31.md"


class Goal2782V25PartnerSelectionGuidanceTest(unittest.TestCase):
    def test_guidance_validates_and_keeps_claims_blocked(self) -> None:
        guidance = rt.v2_5_partner_selection_guidance()
        validation = rt.validate_v2_5_partner_selection_guidance(guidance, repo_root=REPO_ROOT)

        self.assertEqual(validation["status"], "accept")
        self.assertEqual(guidance["row_count"], 3)
        self.assertTrue(guidance["preview_kernel_available_does_not_imply_auto_select"])
        self.assertTrue(guidance["no_partner_forced"])
        self.assertFalse(guidance["promoted_performance_path"])
        self.assertFalse(guidance["public_speedup_claim_authorized"])
        self.assertFalse(guidance["rt_core_speedup_claim_authorized"])
        self.assertFalse(guidance["whole_app_speedup_claim_authorized"])
        self.assertFalse(guidance["true_zero_copy_claim_authorized"])
        self.assertFalse(guidance["release_readiness_authorized"])

    def test_topk_and_vector_sum_negative_guidance_is_machine_readable(self) -> None:
        topk = rt.plan_v2_5_partner_selection(
            "grouped_topk_f64",
            "dense_exact_topk_candidate_ranking",
        )
        vector = rt.plan_v2_5_partner_selection(
            "grouped_vector_sum_f64x2",
            "dense_grouped_vector_sum_2d",
        )
        hausdorff = rt.plan_v2_5_partner_selection(
            "grouped_argmin_f64",
            "dense_exact_hausdorff_argmin_argmax",
        )

        self.assertEqual(topk["status"], "measured_negative_preview_guidance")
        self.assertEqual(vector["status"], "measured_negative_preview_guidance")
        self.assertEqual(hausdorff["status"], "measured_negative_preview_guidance")
        self.assertFalse(topk["auto_select_partner_allowed"])
        self.assertFalse(vector["auto_select_partner_allowed"])
        self.assertFalse(hausdorff["auto_select_partner_allowed"])
        self.assertIn("Do not auto-select Triton", topk["recommendation"])
        self.assertIn("Do not auto-select Triton", vector["recommendation"])
        self.assertIn("Do not auto-select Triton", hausdorff["recommendation"])
        self.assertIn("Torch", topk["recommendation"])
        self.assertIn("Torch", vector["recommendation"])
        self.assertIn("Torch", hausdorff["recommendation"])

        topk_row = topk["matches"][0]
        vector_row = vector["matches"][0]
        hausdorff_row = hausdorff["matches"][0]
        self.assertEqual(topk_row["evidence_goal"], "Goal2784")
        self.assertEqual(vector_row["evidence_goal"], "Goal2786")
        self.assertEqual(hausdorff_row["evidence_goal"], "Goal2787")
        self.assertGreaterEqual(topk_row["measured_partner_slower_min_ratio"], 4.0)
        self.assertGreaterEqual(topk_row["measured_partner_slower_max_ratio"], 10.0)
        self.assertGreaterEqual(vector_row["measured_partner_slower_min_ratio"], 3.0)
        self.assertGreaterEqual(vector_row["measured_partner_slower_max_ratio"], 16.0)
        self.assertGreaterEqual(hausdorff_row["measured_partner_slower_min_ratio"], 31.0)
        self.assertGreaterEqual(hausdorff_row["measured_partner_slower_max_ratio"], 45.0)
        self.assertFalse(topk_row["rt_core_speedup_claim_authorized"])
        self.assertFalse(topk_row["whole_app_speedup_claim_authorized"])
        self.assertFalse(vector_row["rt_core_speedup_claim_authorized"])
        self.assertFalse(vector_row["whole_app_speedup_claim_authorized"])
        self.assertFalse(hausdorff_row["rt_core_speedup_claim_authorized"])
        self.assertFalse(hausdorff_row["whole_app_speedup_claim_authorized"])
        self.assertTrue((REPO_ROOT / topk_row["artifact_path"]).exists())
        self.assertTrue((REPO_ROOT / vector_row["artifact_path"]).exists())
        self.assertTrue((REPO_ROOT / hausdorff_row["artifact_path"]).exists())

    def test_unknown_shape_fails_to_advisory_explicit_choice(self) -> None:
        plan = rt.plan_v2_5_partner_selection("segmented_count_i64", "unmeasured_shape")

        self.assertEqual(plan["status"], "no_measured_guidance")
        self.assertFalse(plan["auto_select_partner_allowed"])
        self.assertIn("explicit app/user partner choice", plan["recommendation"])

    def test_symbols_are_available_but_not_star_exports(self) -> None:
        for name in (
            "v2_5_partner_selection_guidance",
            "validate_v2_5_partner_selection_guidance",
            "plan_v2_5_partner_selection",
        ):
            self.assertTrue(hasattr(rt, name))
            self.assertNotIn(name, rt.__all__)

    def test_report_records_goal2780_and_goal2781_lessons(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal2782", report)
        self.assertIn("Goal2780", report)
        self.assertIn("Goal2781", report)
        self.assertIn("Goal2786", report)
        self.assertIn("Goal2787", report)
        self.assertIn("preview kernel available", report)
        self.assertIn("not the same as selected partner", report)
        self.assertIn("no public speedup claim", report.lower())

    def test_consensus_records_external_acceptance(self) -> None:
        consensus = CONSENSUS.read_text(encoding="utf-8")
        gemini = GEMINI_REVIEW.read_text(encoding="utf-8")
        claude = CLAUDE_REVIEW.read_text(encoding="utf-8")
        self.assertIn("`accept`", consensus)
        self.assertIn(str(GEMINI_REVIEW.relative_to(REPO_ROOT)).replace("\\", "/"), consensus)
        self.assertIn(str(CLAUDE_REVIEW.relative_to(REPO_ROOT)).replace("\\", "/"), consensus)
        self.assertIn("**accept**", gemini.lower())
        self.assertIn("**verdict: `accept`**", claude.lower())
        self.assertIn("preview availability", gemini)
        self.assertIn("No New Pod Needed", gemini)


if __name__ == "__main__":
    unittest.main()
