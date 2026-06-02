from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "goal3045_hausdorff_active_frontier_multitrial.py"
REPORT = REPO_ROOT / "docs" / "reports" / "goal3045_hausdorff_active_frontier_multitrial_harness_2026-06-02.md"


class Goal3045HausdorffActiveFrontierMultitrialHarnessTest(unittest.TestCase):
    def test_report_records_multitrial_purpose_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal3045",
            "warmup",
            "medians",
            "dispersion",
            "alternating measurement order",
            "per-trial exact-distance validation",
            "does not authorize release",
        ):
            self.assertIn(phrase, text)

    def test_script_collects_repeated_same_process_stats(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")

        for phrase in (
            "def _timing_stats",
            "median_sec",
            "iqr_sec",
            "if trial % 2 == 0",
            "cupy_grouped_grid_rawkernel",
            "hausdorff_distance_2d_rt_grouped_active_frontier_nearest_witness",
            "all_trials_match_distance",
            "best_median_speedup_vs_cupy",
            '"public_speedup_claim_authorized": False',
            '"rt_core_speedup_claim_authorized": False',
            '"true_zero_copy_claim_authorized": False',
        ):
            self.assertIn(phrase, source)


if __name__ == "__main__":
    unittest.main()
