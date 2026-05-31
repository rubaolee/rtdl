from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "docs" / "reports" / "goal2783_v2_5_app_migration_selection_guidance_2026-05-31.md"
CONSENSUS = REPO_ROOT / "docs" / "reports" / "goal2783_v2_5_app_migration_selection_guidance_consensus_2026-05-31.md"
CLAUDE_REVIEW = REPO_ROOT / "docs" / "reviews" / "goal2783_claude_review_app_migration_selection_guidance_2026-05-31.md"


class Goal2783V25AppMigrationSelectionGuidanceTest(unittest.TestCase):
    def test_migration_plan_consumes_partner_selection_guidance(self) -> None:
        plan = rt.v2_5_triton_benchmark_app_migration_plan()
        validation = rt.validate_v2_5_triton_benchmark_app_migration_plan()

        self.assertEqual(validation["status"], "accept")
        self.assertTrue(plan["partner_selection_guidance_integrated"])
        self.assertEqual(
            plan["partner_selection_guidance_version"],
            rt.V2_5_PARTNER_SELECTION_GUIDANCE_VERSION,
        )
        self.assertFalse(plan["auto_select_preview_partner_allowed"])
        self.assertIn("not authorization to auto-select Triton", plan["claim_boundary"])

    def test_rtnn_dense_topk_records_goal2784_negative_guidance(self) -> None:
        apps = {app["app_id"]: app for app in rt.v2_5_triton_benchmark_app_migration_plan()["apps"]}
        rtnn = apps["rtnn"]
        guidance = rtnn["partner_selection_guidance"][0]

        self.assertIn("grouped_topk_f64", rtnn["v2_5_required_operations"])
        self.assertEqual(rtnn["measured_negative_preview_guidance_count"], 1)
        self.assertFalse(rtnn["auto_select_preview_partner_allowed"])
        self.assertEqual(guidance["status"], "measured_negative_preview_guidance")
        self.assertEqual(guidance["matches"][0]["operation"], "grouped_topk_f64")
        self.assertEqual(guidance["matches"][0]["evidence_goal"], "Goal2784")
        self.assertFalse(guidance["auto_select_partner_allowed"])
        self.assertIn("Do not auto-select Triton", guidance["recommendation"])

    def test_barnes_hut_dense_vector_sum_records_goal2781_negative_guidance(self) -> None:
        apps = {app["app_id"]: app for app in rt.v2_5_triton_benchmark_app_migration_plan()["apps"]}
        barnes = apps["barnes_hut"]
        guidance = barnes["partner_selection_guidance"][0]

        self.assertIn("grouped_vector_sum_f64x2", barnes["v2_5_required_operations"])
        self.assertEqual(barnes["measured_negative_preview_guidance_count"], 1)
        self.assertFalse(barnes["auto_select_preview_partner_allowed"])
        self.assertEqual(guidance["status"], "measured_negative_preview_guidance")
        self.assertEqual(guidance["matches"][0]["operation"], "grouped_vector_sum_f64x2")
        self.assertEqual(guidance["matches"][0]["evidence_goal"], "Goal2781")
        self.assertFalse(guidance["auto_select_partner_allowed"])
        self.assertIn("Do not auto-select Triton", guidance["recommendation"])

    def test_apps_without_measured_negative_guidance_do_not_gain_false_selection_claims(self) -> None:
        apps = {app["app_id"]: app for app in rt.v2_5_triton_benchmark_app_migration_plan()["apps"]}
        for app_id in ("raydb_style", "spatial_rayjoin", "hausdorff_xhd", "rt_dbscan"):
            with self.subTest(app_id=app_id):
                app = apps[app_id]
                self.assertEqual(app["measured_negative_preview_guidance_count"], 0)
                self.assertEqual(app["partner_selection_guidance"], ())
                self.assertFalse(app["auto_select_preview_partner_allowed"])

    def test_report_and_consensus_record_selection_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")
        claude = CLAUDE_REVIEW.read_text(encoding="utf-8")

        self.assertIn("Goal2783", report)
        self.assertIn("RTNN", report)
        self.assertIn("Barnes-Hut", report)
        self.assertIn("do not auto-select Triton", report)
        self.assertIn("`accept`", consensus)
        self.assertIn(str(CLAUDE_REVIEW.relative_to(REPO_ROOT)).replace("\\", "/"), consensus)
        self.assertIn("accept", claude.lower())


if __name__ == "__main__":
    unittest.main()
