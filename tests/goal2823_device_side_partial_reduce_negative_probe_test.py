from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
REPORT = ROOT / "docs" / "reports" / "goal2823_device_side_partial_reduce_negative_probe_2026-05-31.md"
POD_SUMMARY = ROOT / "docs" / "reports" / "goal2823_rtnn_device_side_batch_partial_reduce_pod" / "goal2823_summary.json"


class Goal2823DeviceSidePartialReduceNegativeProbeTest(unittest.TestCase):
    def test_current_code_keeps_goal2822_default_path(self) -> None:
        core = CORE.read_text(encoding="utf-8")
        workloads = WORKLOADS.read_text(encoding="utf-8")

        self.assertIn("fixed_radius_neighbors_3d_grid_ranked_summary_aggregate_f32_blocks_batch", core)
        self.assertIn("g_frn3d_grid_ranked_summary_aggregate_f32_blocks_batch", workloads)
        self.assertNotIn("fixed_radius_neighbors_3d_ranked_aggregate_partials_reduce", core)
        self.assertNotIn("g_frn3d_ranked_aggregate_partials_reduce", workloads)
        self.assertIn("download(partials.data(), d_partials.ptr, partials.size())", workloads)

    def test_report_records_negative_probe_and_revert_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("reject-as-default", report)
        self.assertIn("current branch reverts", report)
        self.assertIn("0.990x", report)
        self.assertIn("1.020x", report)
        self.assertIn("No RTDL-beats-RTNN-paper claim is authorized", report)

    def test_pod_artifacts_show_mixed_signal(self) -> None:
        summary = json.loads(POD_SUMMARY.read_text(encoding="utf-8"))

        self.assertEqual(summary["status"], "pass")
        self.assertEqual(summary["source_commit"], "eaf393c1060e31c39177d1b6a8d3193d311784bb")
        self.assertEqual(summary["source_dirty"], [])
        by_count = {row["point_count"]: row for row in summary["rows"]}

        self.assertLess(by_count[32768]["change_vs_goal2822_batch"], 1.0)
        self.assertGreater(by_count[65536]["change_vs_goal2822_batch"], 1.0)
        for row in summary["rows"]:
            self.assertTrue(row["batch_results_match_sequential"])
            self.assertFalse(row["claim_boundary"]["public_speedup_claim_authorized"])
            self.assertFalse(row["claim_boundary"]["single_request_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
