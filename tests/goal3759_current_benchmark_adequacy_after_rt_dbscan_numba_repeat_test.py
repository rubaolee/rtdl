from __future__ import annotations

from pathlib import Path
import unittest

from rtdsl.v2_8_benchmark_runtime_gap import V2_8_PROMOTED_BENCHMARK_APPS
from rtdsl.v2_9_benchmark_adequacy import (
    V2_9_BENCHMARK_ADEQUACY_VERSION,
    summarize_v2_9_benchmark_adequacy,
    validate_v2_9_benchmark_adequacy,
    v2_9_benchmark_adequacy,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3759_current_benchmark_adequacy_after_rt_dbscan_numba_repeat_2026-06-07.md"


class Goal3759CurrentBenchmarkAdequacyAfterRtDbscanNumbaRepeatTest(unittest.TestCase):
    def test_current_matrix_version_and_counts_match_goal3758_refresh(self) -> None:
        self.assertEqual(V2_9_BENCHMARK_ADEQUACY_VERSION, "rtdl.v2_10.benchmark_adequacy_after_goal3785.v1")
        validation = validate_v2_9_benchmark_adequacy()
        self.assertEqual(validation["status"], "accept")
        self.assertEqual(validation["errors"], ())
        summary = summarize_v2_9_benchmark_adequacy()
        self.assertEqual(summary["app_count"], 10)
        self.assertEqual(summary["row_count"], 10)
        self.assertEqual(summary["adequacy_counts"]["strong"], 3)
        self.assertEqual(summary["adequacy_counts"]["needs_major_followup"], 0)

    def test_rt_dbscan_is_now_strong_with_goal3758_evidence(self) -> None:
        rows = {row["app"]: row for row in v2_9_benchmark_adequacy()}
        rt_dbscan = rows["rt_dbscan"]
        self.assertEqual(rt_dbscan["adequacy"], "strong")
        self.assertIn("Goal3758", rt_dbscan["evidence_refs"])
        self.assertIn("1.748x", rt_dbscan["current_performance_reading"])
        self.assertIn("no-RawKernel", rt_dbscan["current_partner_role"])
        self.assertFalse(rt_dbscan["public_speedup_claim_authorized"])
        self.assertFalse(rt_dbscan["broad_rt_core_claim_authorized"])

    def test_report_covers_all_promoted_apps_without_old_rt_dbscan_wording(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn(V2_9_BENCHMARK_ADEQUACY_VERSION, text)
        for app in V2_8_PROMOTED_BENCHMARK_APPS:
            self.assertIn(f"`{app}`", text)
        self.assertIn("RT-DBSCAN Update", text)
        self.assertIn("1.748x", text)
        self.assertIn("does not authorize", text)
        self.assertNotIn("0.997206x", text)


if __name__ == "__main__":
    unittest.main()
