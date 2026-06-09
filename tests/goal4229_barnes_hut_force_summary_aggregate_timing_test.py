from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "v2_0" / "apps" / "simulation" / "rtdl_barnes_hut_force_app.py"
ARTIFACT = ROOT / "docs" / "reports" / "goal4229_barnes_hut_numba_long_repeat_rtx4000ada" / "summary.json"
PAYLOAD = (
    ROOT
    / "docs"
    / "reports"
    / "goal4229_barnes_hut_numba_long_repeat_rtx4000ada"
    / "barnes_hut_numba_8192_repeat200.stdout.json"
)
REPORT = ROOT / "docs" / "reports" / "goal4229_barnes_hut_force_summary_aggregate_timing_2026-06-09.md"


class Goal4229BarnesHutForceSummaryAggregateTimingTest(unittest.TestCase):
    def test_app_exposes_real_aggregate_timing_fields(self) -> None:
        source = APP.read_text(encoding="utf-8")

        self.assertIn("force_kernel_runs_sec", source)
        self.assertIn("force_kernel_total_sec", source)
        self.assertIn("median_force_kernel_sec", source)

    def test_pod_artifact_uses_real_aggregate_not_proxy(self) -> None:
        summary = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        payload = json.loads(PAYLOAD.read_text(encoding="utf-8"))
        protocol = payload["partner_metadata"]["prepared_force_repeat_protocol"]

        self.assertEqual(summary["schema"], "rtdl.goal4229.barnes_hut_numba_long_repeat.v2")
        self.assertEqual(summary["commit"], "21d5af1d")
        self.assertEqual(summary["tracked_worktree_status_excluding_artifact_dir"], [])
        self.assertEqual(summary["repeat"], 200)
        self.assertEqual(summary["measured_iterations"], 200)
        self.assertEqual(summary["force_kernel_runs_sec_count"], 200)
        self.assertEqual(len(protocol["force_kernel_runs_sec"]), 200)
        self.assertAlmostEqual(summary["force_kernel_total_sec"], sum(protocol["force_kernel_runs_sec"]))
        self.assertTrue(summary["hot_path_duration_target_met"])
        self.assertGreater(summary["force_kernel_total_sec"], 1.0)
        self.assertFalse(summary["materializes_python_force_rows"])

    def test_report_keeps_claims_closed(self) -> None:
        summary = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        report = REPORT.read_text(encoding="utf-8")

        for key in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "broad_rt_core_claim_authorized",
            "paper_reproduction_claim_authorized",
            "true_zero_copy_claim_authorized",
            "automatic_partner_selection_authorized",
            "amd_performance_claim_authorized",
        ):
            self.assertFalse(summary[key], key)
        self.assertIn("not a public speedup claim", report)


if __name__ == "__main__":
    unittest.main()
