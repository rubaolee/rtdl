from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "goal1856_segment_polygon_v2_partner_perf.py"
REPORT = ROOT / "docs" / "reports" / "goal1856_segment_polygon_v2_partner_perf_2026-05-13.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal1856_segment_polygon_v2_partner_perf_pod_512.json"
ARTIFACT_2048 = ROOT / "docs" / "reports" / "goal1856_segment_polygon_v2_partner_perf_pod_2048.json"


class Goal1856SegmentPolygonV2PartnerPerfRunnerTest(unittest.TestCase):
    def test_runner_records_same_contract_timing_boundaries(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")

        self.assertIn("segment_polygon_anyhit_rows_native_bounded_optix", text)
        self.assertIn("segment_polygon_anyhit_rows_optix_partner_columns", text)
        self.assertIn("v1_8_native_optix_rows", text)
        self.assertIn("v2_0_partner_columns_", text)
        self.assertIn("query_median_ratio_vs_v1_8_native", text)
        self.assertIn("_canonical_rows", text)
        self.assertIn("--skip-overflow-check", text)
        self.assertIn("--source-commit-label", text)
        self.assertIn("[overflow]", text)
        self.assertIn('"overflow_check"', text)
        self.assertIn('"same_contract_timing_row": True', text)
        self.assertIn('"v2_0_release_authorized": False', text)
        self.assertIn('"whole_app_speedup_claim_authorized": False', text)
        self.assertIn('"broad_rt_core_speedup_claim_authorized": False', text)
        self.assertIn('"package_install_claim_authorized": False', text)

    def test_runner_prints_progress_for_pod_use(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")

        self.assertIn("[setup]", text)
        self.assertIn("[timing]", text)
        self.assertIn("[artifact]", text)
        self.assertIn("flush=True", text)

    def test_report_and_artifact_preserve_narrow_claim_boundary(self) -> None:
        import json

        report = REPORT.read_text(encoding="utf-8")
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertIn("Status: pass-with-boundary", report)
        self.assertIn("Claude reviewed Goal1856", report)
        self.assertIn("accept-with-boundary", report)
        self.assertIn("not an all-app performance table", report)
        self.assertIn("does not authorize v2.0 release wording", report)
        self.assertIn("goal1856_segment_polygon_v2_partner_perf_pod_2048.json", report)
        self.assertEqual(artifact["status"], "pass")
        self.assertEqual(artifact["goal"], "Goal1856")
        self.assertIn("NVIDIA RTX A4500", artifact["gpu"])
        self.assertEqual(artifact["count"], 512)
        self.assertTrue(artifact["parity"]["strict_rows_match"])
        self.assertEqual(artifact["baseline"]["row_count"], 512)
        for partner in ("cupy", "torch"):
            with self.subTest(partner=partner):
                self.assertEqual(artifact["partners"][partner]["row_count"], 512)
                self.assertEqual(artifact["partners"][partner]["overflow_check"]["status"], "pass")
                self.assertLess(artifact["partners"][partner]["query_median_ratio_vs_v1_8_native"], 1.0)
        boundary = artifact["claim_boundary"]
        self.assertTrue(boundary["same_contract_timing_row"])
        self.assertFalse(boundary["v2_0_release_authorized"])
        self.assertFalse(boundary["whole_app_speedup_claim_authorized"])
        self.assertFalse(boundary["broad_rt_core_speedup_claim_authorized"])
        self.assertFalse(boundary["package_install_claim_authorized"])

    def test_scaled_artifact_keeps_same_contract_boundaries(self) -> None:
        import json

        artifact = json.loads(ARTIFACT_2048.read_text(encoding="utf-8"))
        self.assertEqual(artifact["status"], "pass")
        self.assertEqual(artifact["count"], 2048)
        self.assertTrue(artifact["parity"]["strict_rows_match"])
        self.assertEqual(artifact["baseline"]["row_count"], 2048)
        self.assertEqual(artifact["partners"]["cupy"]["overflow_check"]["status"], "pass")
        self.assertEqual(artifact["partners"]["torch"]["overflow_check"]["status"], "pass")
        self.assertLess(artifact["partners"]["cupy"]["query_median_ratio_vs_v1_8_native"], 0.5)
        self.assertLess(artifact["partners"]["torch"]["query_median_ratio_vs_v1_8_native"], 0.5)
        self.assertFalse(artifact["claim_boundary"]["v2_0_release_authorized"])


if __name__ == "__main__":
    unittest.main()
