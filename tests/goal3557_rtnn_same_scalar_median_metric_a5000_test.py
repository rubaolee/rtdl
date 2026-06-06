from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs" / "reports" / "goal3557_rtnn_same_scalar_median_metric_a5000" / "summary.json"
REPORT = ROOT / "docs" / "reports" / "goal3557_rtnn_same_scalar_median_metric_a5000_2026-06-06.md"
V23_ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal3557_rtnn_same_scalar_median_metric_a5000"
    / "artifacts"
    / "v23"
    / "rtnn_optix_65536.json"
)
V28_ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal3557_rtnn_same_scalar_median_metric_a5000"
    / "artifacts"
    / "v28"
    / "rtnn_optix_65536.json"
)
OVERLAY = ROOT / "docs" / "patches" / "goal3547_v23_measurement_overlay_repeat_hooks_2026-06-06.patch"


class Goal3557RTNNSameScalarMedianMetricA5000Test(unittest.TestCase):
    def test_targeted_packet_uses_corrected_same_scalar_metric(self) -> None:
        payload = json.loads(PACKET.read_text(encoding="utf-8"))
        summary = payload["summary"]
        row = payload["comparisons"][0]
        v23 = json.loads(V23_ARTIFACT.read_text(encoding="utf-8"))
        v28 = json.loads(V28_ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(summary["row_count"], 1)
        self.assertEqual(summary["observed_target_miss_count"], 0)
        self.assertEqual(row["case_id"], "rtnn_optix_prepared_3d_ranked_summary")
        self.assertEqual(row["v23_primary_metric_sec"], v23["elapsed_median_sec"])
        self.assertEqual(row["v28_primary_metric_sec"], v28["elapsed_median_sec"])
        self.assertAlmostEqual(row["v28_speedup_vs_v23"], 0.9795780056463211)
        self.assertGreater(row["v28_speedup_vs_v23"], 0.97)
        self.assertLess(row["v28_speedup_vs_v23"], 1.0)
        self.assertTrue(row["v23_target_met_by_observed_sum"])
        self.assertTrue(row["v28_target_met_by_observed_sum"])

    def test_claim_boundary_remains_internal_only(self) -> None:
        row = json.loads(PACKET.read_text(encoding="utf-8"))["comparisons"][0]
        boundary = row["claim_boundary"]
        self.assertTrue(boundary["internal_results_only"])
        for key in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "broad_rt_core_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
            "package_install_claim_authorized",
            "paper_reproduction_claim_authorized",
        ):
            self.assertFalse(boundary[key], key)

    def test_overlay_patch_selects_median_for_v23_rtnn_rows(self) -> None:
        text = OVERLAY.read_text(encoding="utf-8")
        self.assertGreaterEqual(text.count('primary_metric_path=("elapsed_median_sec",)'), 2)

    def test_report_rejects_mismatched_scalar_run_and_names_full_packet_next(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("rejected as final evidence", text)
        self.assertIn("0.979578x", text)
        self.assertIn("internal benchmark evidence only", text)
        self.assertIn("Refresh the full 11-row", text)


if __name__ == "__main__":
    unittest.main()
