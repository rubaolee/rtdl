from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3840_current_benchmark_adequacy_after_goal3838_2026-06-08.md"


class Goal3840CurrentBenchmarkAdequacyAfterGoal3838Test(unittest.TestCase):
    def test_current_adequacy_version_and_summary_remain_fail_closed(self) -> None:
        self.assertEqual(
            rt.CURRENT_BENCHMARK_ADEQUACY_VERSION,
            "rtdl.v2_10.benchmark_adequacy_after_goal3838.v1",
        )
        validation = rt.validate_current_benchmark_adequacy()
        self.assertEqual(validation["status"], "accept")
        self.assertEqual(validation["errors"], ())
        summary = rt.summarize_current_benchmark_adequacy()
        self.assertEqual(summary["app_count"], 10)
        self.assertEqual(summary["numba_reference_needed_apps"], ())
        self.assertFalse(summary["release_authorized"])
        self.assertFalse(summary["public_speedup_claim_authorized"])

    def test_spatial_rayjoin_row_carries_goal3834_3838_numba_coverage(self) -> None:
        rows = {row["app"]: row for row in rt.current_benchmark_adequacy()}
        spatial = rows["spatial_rayjoin"]
        self.assertIn("Goal3834", spatial["evidence_refs"])
        self.assertIn("Goal3838", spatial["evidence_refs"])
        self.assertIn("PIP, LSI, and overlay", spatial["current_partner_role"])
        self.assertIn("RTDL/OptiX remains about 260x faster", spatial["current_performance_reading"])
        self.assertIn("count parity with CuPy and RTDL/OptiX", spatial["numba_reference_reason"])
        self.assertFalse(spatial["paper_reproduction_claim_authorized"])
        self.assertFalse(spatial["automatic_partner_selection_authorized"])

    def test_report_documents_metadata_cleanup_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal3840 Current Benchmark Adequacy", text)
        self.assertIn("rtdl.v2_10.benchmark_adequacy_after_goal3838.v1", text)
        self.assertIn("Goal3834 no-RawKernel Numba PIP", text)
        self.assertIn("Goal3838 no-RawKernel Numba LSI", text)
        self.assertIn("does not authorize", text)


if __name__ == "__main__":
    unittest.main()
