from __future__ import annotations

from pathlib import Path
import unittest

from rtdsl.v2_9_benchmark_adequacy import (
    V2_9_BENCHMARK_ADEQUACY_VERSION,
    summarize_v2_9_benchmark_adequacy,
    v2_9_benchmark_adequacy,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal3747_numba_reference_adequacy_closure_after_goal3746_2026-06-07.md"


class Goal3747NumbaReferenceAdequacyClosureTest(unittest.TestCase):
    def test_version_records_goal3746_refresh(self) -> None:
        self.assertEqual(V2_9_BENCHMARK_ADEQUACY_VERSION, "rtdl.v2_9.benchmark_adequacy_after_goal3746.v1")

    def test_only_spatial_rayjoin_still_needs_numba_reference(self) -> None:
        summary = summarize_v2_9_benchmark_adequacy()
        self.assertEqual(set(summary["numba_reference_needed_apps"]), {"spatial_rayjoin"})
        rows = {row["app"]: row for row in v2_9_benchmark_adequacy()}
        self.assertFalse(rows["rt_dbscan"]["needs_numba_reference"])
        self.assertFalse(rows["barnes_hut"]["needs_numba_reference"])
        self.assertTrue(rows["spatial_rayjoin"]["needs_numba_reference"])
        self.assertEqual(rows["rt_dbscan"]["adequacy"], "adequate")
        self.assertEqual(rows["barnes_hut"]["adequacy"], "adequate")

    def test_no_major_followup_remains_in_current_matrix(self) -> None:
        summary = summarize_v2_9_benchmark_adequacy()
        self.assertEqual(summary["adequacy_counts"].get("needs_major_followup", 0), 0)

    def test_report_explains_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal3747", text)
        self.assertIn("Only one Numba-reference pressure point remains", text)
        self.assertIn("spatial_rayjoin", text)
        self.assertIn("no-RawKernel reference", text)
        self.assertIn("does not authorize", text)


if __name__ == "__main__":
    unittest.main()
