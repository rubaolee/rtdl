from __future__ import annotations

import pathlib
import json
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal1869_road_hazard_v2_partner_perf.py"
REPORT = ROOT / "docs" / "reports" / "goal1869_road_hazard_v2_partner_perf_plan_2026-05-13.md"
ARTIFACT_512 = ROOT / "docs" / "reports" / "goal1869_road_hazard_v2_partner_perf_pod_512.json"
ARTIFACT_2048 = ROOT / "docs" / "reports" / "goal1869_road_hazard_v2_partner_perf_pod_2048.json"
CLAUDE_REVIEW = ROOT / "docs" / "reviews" / "goal1871_claude_review_goal1868_1869_road_hazard_pod_evidence_2026-05-13.md"


class Goal1869RoadHazardV2PartnerPerfPlanTest(unittest.TestCase):
    def test_runner_records_dual_v1_8_baselines_and_v2_partner_path(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("road_hazard_hitcount", text)
        self.assertIn("prepare_optix_segment_polygon_hitcount_2d", text)
        self.assertIn("road_hazard_priority_flags_optix_partner_device_columns", text)
        self.assertIn("v1_8_one_shot_native_optix_road_hazard_rows", text)
        self.assertIn("v1_8_prepared_native_optix_road_hazard_rows", text)
        self.assertIn("v2_0_partner_road_hazard_priority_flags_", text)
        self.assertIn("query_median_ratio_vs_v1_8_one_shot_native", text)
        self.assertIn("query_median_ratio_vs_v1_8_prepared_native", text)

    def test_runner_prints_progress_and_keeps_claim_boundaries(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("[setup]", text)
        self.assertIn("[timing]", text)
        self.assertIn("[artifact]", text)
        self.assertIn("flush=True", text)
        self.assertIn('"same_contract_timing_row": True', text)
        self.assertIn('"v2_0_release_authorized": False', text)
        self.assertIn('"whole_app_speedup_claim_authorized": False', text)
        self.assertIn('"broad_rt_core_speedup_claim_authorized": False', text)

    def test_report_keeps_pod_timing_pending(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: pass-with-boundary", report)
        self.assertIn("road_hazard_priority_flags_optix_partner_device_columns", report)
        self.assertIn("goal1869_road_hazard_v2_partner_perf_pod_512.json", report)
        self.assertIn("goal1869_road_hazard_v2_partner_perf_pod_2048.json", report)
        self.assertIn("NVIDIA GeForce RTX 3090", report)
        self.assertIn("Observed Timing", report)
        self.assertIn("does not authorize v2.0 release wording", report)
        self.assertIn("goal1871_claude_review_goal1868_1869", report)
        self.assertIn("accept-with-boundary", report)

    def test_pod_artifacts_record_same_contract_timing_boundaries(self) -> None:
        for path, count in ((ARTIFACT_512, 512), (ARTIFACT_2048, 2048)):
            with self.subTest(path=path.name):
                artifact = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(artifact["status"], "pass")
                self.assertEqual(artifact["goal"], "Goal1869")
                self.assertEqual(artifact["count"], count)
                self.assertIn("NVIDIA GeForce RTX 3090", artifact["gpu"])
                self.assertTrue(artifact["parity"]["strict_priority_flags_match"])
                self.assertEqual(artifact["baseline"]["row_count"], count)
                self.assertEqual(artifact["prepared_baseline"]["row_count"], count)
                for partner in ("cupy", "torch"):
                    result = artifact["partners"][partner]
                    self.assertEqual(result["row_count"], count)
                    self.assertEqual(result["output_contract"], "partner_owned_road_hazard_priority_columns")
                    self.assertIn("query_median_ratio_vs_v1_8_one_shot_native", result)
                    self.assertIn("query_median_ratio_vs_v1_8_prepared_native", result)
                boundary = artifact["claim_boundary"]
                self.assertTrue(boundary["same_contract_timing_row"])
                self.assertTrue(boundary["partner_output_columns_true_zero_copy_authorized"])
                self.assertFalse(boundary["v2_0_release_authorized"])
                self.assertFalse(boundary["whole_app_speedup_claim_authorized"])

    def test_claude_review_accepts_with_boundary(self) -> None:
        review = CLAUDE_REVIEW.read_text(encoding="utf-8")

        self.assertIn("Claude", review)
        self.assertIn("Verdict:** `accept-with-boundary`", review)
        self.assertIn("Torch uint32 comparison fix", review)
        self.assertIn("dual-baseline", review)
        self.assertIn("v2.0 release wording", review)
        self.assertIn("Remaining gaps", review)


if __name__ == "__main__":
    unittest.main()
