from __future__ import annotations

import json
from pathlib import Path
import unittest

import rtdsl as rt


REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = REPO_ROOT / "docs" / "reports" / "goal2796_pod_artifacts" / "raydb_triton_frontdoor_current.json"
REPORT = REPO_ROOT / "docs" / "reports" / "goal2796_raydb_scalar_reduction_selection_guidance_2026-05-31.md"
REVIEW = REPO_ROOT / "docs" / "reviews" / "goal2796_gemini_review_raydb_scalar_reduction_selection_guidance_2026-05-31.md"
CONSENSUS = REPO_ROOT / "docs" / "reports" / "goal2796_raydb_scalar_reduction_selection_guidance_consensus_2026-05-31.md"


class Goal2796RaydbScalarReductionSelectionGuidanceTest(unittest.TestCase):
    def test_pod_artifact_records_correct_but_slow_triton_frontdoor(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["status"], "ok")
        self.assertTrue(payload["all_correct"])
        self.assertEqual(payload["device"], "NVIDIA RTX A5000")
        self.assertTrue(payload["no_public_speedup_claim"])

        for case in payload["cases"]:
            self.assertTrue(case["all_correct"])
            for row in case["modes"]:
                med = row["median_sec"]
                triton_sec = float(med["raydb_triton_public_front_door"])
                torch_sec = float(med["torch_cuda_baseline"])
                self.assertGreater(triton_sec, torch_sec)
                self.assertTrue(row["correct_vs_torch_cuda"])

    def test_guidance_blocks_auto_selection_for_scalar_reductions(self) -> None:
        for operation in ("segmented_count_i64", "segmented_sum_f64", "segmented_min_f64", "segmented_max_f64"):
            with self.subTest(operation=operation):
                plan = rt.plan_v2_5_partner_selection(
                    operation,
                    "raydb_scalar_grouped_reduction_frontdoor",
                )
                row = plan["matches"][0]

                self.assertEqual(plan["status"], "measured_negative_preview_guidance")
                self.assertEqual(row["evidence_goal"], "Goal2796")
                self.assertEqual(row["artifact_path"], str(ARTIFACT.relative_to(REPO_ROOT)).replace("\\", "/"))
                self.assertFalse(plan["auto_select_partner_allowed"])
                self.assertFalse(row["public_speedup_claim_authorized"])
                self.assertFalse(row["release_readiness_authorized"])

    def test_raydb_app_plan_integrates_scalar_guidance(self) -> None:
        apps = {app["app_id"]: app for app in rt.v2_5_triton_benchmark_app_migration_plan()["apps"]}
        raydb = apps["raydb_style"]

        self.assertEqual(raydb["measured_negative_preview_guidance_count"], 4)
        self.assertEqual(raydb["measured_mixed_preview_guidance_count"], 0)
        self.assertIn("primitive_first", raydb["v2_5_status"])
        self.assertIn("prepared fused RTDL primitive", raydb["first_port_action"])

    def test_report_review_and_consensus_are_present(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        review = REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("Goal2796", report)
        self.assertIn("RayDB", report)
        self.assertIn("correct but slower", report)
        self.assertIn("## verdict", review.lower())
        self.assertIn("accept", review.lower())
        self.assertIn("accept-with-boundary", consensus.lower())
        self.assertIn(str(REVIEW.relative_to(REPO_ROOT)).replace("\\", "/"), consensus)


if __name__ == "__main__":
    unittest.main()
