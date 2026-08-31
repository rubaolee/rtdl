from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3572_grouped_i64_full_reduction_fastpath_2026-06-06.md"
SUMMARY = (
    ROOT
    / "docs"
    / "reports"
    / "goal3572_grouped_i64_full_reduction_fastpath_preserve_long_a5000"
    / "summary.json"
)


class Goal3572GroupedI64FullReductionFastPathA5000Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

    def test_report_states_scope_and_boundary(self) -> None:
        self.assertIn("Goal3572 extends the v2.9 grouped-i64 small-group fast path", self.report)
        self.assertIn("device_column_grouped_i64_small_group_reduction_kernel", self.report)
        self.assertIn("no new sum speedup claim", self.report)
        self.assertIn("not a measured stats performance claim", self.report)
        for forbidden_claim in (
            "release or tag action",
            "public speedup claims",
            "whole-app acceleration claims",
            "broad RT-core speedup claims",
            "true zero-copy claims",
            "paper reproduction claims",
            "package-install claims",
        ):
            self.assertIn(forbidden_claim, self.report)

    def test_a5000_artifact_is_clean_and_claim_bounded(self) -> None:
        data = self.summary
        self.assertTrue(data["baseline_commit"].startswith("f5090057"))
        self.assertTrue(data["candidate_commit"].startswith("bfcb943c"))
        self.assertFalse(data["candidate_has_uncommitted_native_change"])
        self.assertEqual(data["copies"], 120000)
        self.assertEqual(data["warmup"], 3)
        self.assertEqual(data["repeat"], 5000)
        self.assertEqual(data["trials"], 5)
        self.assertTrue(data["summary"]["all_modes_ok"])
        boundary = data["claim_boundary"]
        self.assertTrue(boundary["internal_results_only"])
        for key, value in boundary.items():
            if key != "internal_results_only":
                self.assertFalse(value, key)

    def test_new_operations_are_materially_faster_and_sum_is_preserved(self) -> None:
        by_mode = self.summary["by_mode"]
        self.assertGreater(by_mode["count"]["candidate_speedup_vs_baseline"], 1.20)
        self.assertGreater(by_mode["min"]["candidate_speedup_vs_baseline"], 1.20)
        self.assertGreater(by_mode["max"]["candidate_speedup_vs_baseline"], 1.20)
        self.assertGreaterEqual(by_mode["avg_as_sum_count"]["candidate_speedup_vs_baseline"], 1.0)
        self.assertGreaterEqual(by_mode["sum"]["candidate_speedup_vs_baseline"], 0.98)
        self.assertGreater(self.summary["summary"]["geomean_speedup"], 1.15)
        self.assertGreater(self.summary["summary"]["median_speedup"], 1.20)


if __name__ == "__main__":
    unittest.main()
