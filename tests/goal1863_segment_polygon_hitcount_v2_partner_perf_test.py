from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "goal1863_segment_polygon_hitcount_v2_partner_perf.py"
REPORT = ROOT / "docs" / "reports" / "goal1863_segment_polygon_hitcount_v2_partner_perf_2026-05-13.md"
ARTIFACT_512 = ROOT / "docs" / "reports" / "goal1863_segment_polygon_hitcount_v2_partner_perf_pod_512.json"
ARTIFACT_2048 = ROOT / "docs" / "reports" / "goal1863_segment_polygon_hitcount_v2_partner_perf_pod_2048.json"


class Goal1863SegmentPolygonHitcountV2PartnerPerfTest(unittest.TestCase):
    def test_runner_records_same_contract_timing_boundaries(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")

        self.assertIn("segment_polygon_hitcount_reference", text)
        self.assertIn("segment_polygon_hitcount_optix_partner_device_count_columns", text)
        self.assertIn("v1_8_native_optix_hitcount_rows", text)
        self.assertIn("v2_0_partner_device_count_columns_", text)
        self.assertIn("partner_owned_device_count_columns", text)
        self.assertIn("query_median_ratio_vs_v1_8_native", text)
        self.assertIn('"same_contract_timing_row": True', text)
        self.assertIn('"partner_output_columns_true_zero_copy_authorized": True', text)
        self.assertIn('"v2_0_release_authorized": False', text)
        self.assertIn('"whole_app_speedup_claim_authorized": False', text)

    def test_runner_prints_progress_for_pod_use(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")

        self.assertIn("[setup]", text)
        self.assertIn("[timing]", text)
        self.assertIn("[artifact]", text)
        self.assertIn("flush=True", text)

    def test_report_and_artifacts_keep_narrow_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        artifact = json.loads(ARTIFACT_512.read_text(encoding="utf-8"))

        self.assertIn("Status: pass-with-boundary", report)
        self.assertIn("not an all-app performance table", report)
        self.assertIn("does not authorize v2.0 release wording", report)
        self.assertIn("goal1863_segment_polygon_hitcount_v2_partner_perf_pod_2048.json", report)
        self.assertEqual(artifact["status"], "pass")
        self.assertEqual(artifact["goal"], "Goal1863")
        self.assertIn("NVIDIA RTX A4500", artifact["gpu"])
        self.assertEqual(artifact["count"], 512)
        self.assertTrue(artifact["parity"]["strict_counts_match"])
        self.assertEqual(artifact["baseline"]["row_count"], 512)
        for partner in ("cupy", "torch"):
            with self.subTest(partner=partner):
                self.assertEqual(artifact["partners"][partner]["row_count"], 512)
                self.assertEqual(artifact["partners"][partner]["output_contract"], "partner_owned_device_count_columns")
        boundary = artifact["claim_boundary"]
        self.assertTrue(boundary["same_contract_timing_row"])
        self.assertTrue(boundary["partner_output_columns_true_zero_copy_authorized"])
        self.assertFalse(boundary["v2_0_release_authorized"])
        self.assertFalse(boundary["whole_app_speedup_claim_authorized"])

    def test_scaled_artifact_keeps_same_contract_boundaries(self) -> None:
        artifact = json.loads(ARTIFACT_2048.read_text(encoding="utf-8"))
        self.assertEqual(artifact["status"], "pass")
        self.assertEqual(artifact["count"], 2048)
        self.assertTrue(artifact["parity"]["strict_counts_match"])
        self.assertEqual(artifact["baseline"]["row_count"], 2048)
        self.assertFalse(artifact["claim_boundary"]["v2_0_release_authorized"])


if __name__ == "__main__":
    unittest.main()
