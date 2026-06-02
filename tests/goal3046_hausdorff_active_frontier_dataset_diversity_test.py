from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "goal3046_hausdorff_active_frontier_dataset_diversity.py"
REPORT = REPO_ROOT / "docs" / "reports" / "goal3046_hausdorff_active_frontier_dataset_diversity_2026-06-02.md"


class Goal3046HausdorffActiveFrontierDatasetDiversityTest(unittest.TestCase):
    def test_report_records_dataset_diversity_scope_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal3046",
            "dataset-diversity harness",
            "demo_offset",
            "clustered_shift",
            "ring_vs_spiral",
            "adversarial_tail_outlier",
            "per-trial exact-distance validation",
            "does not authorize release",
        ):
            self.assertIn(phrase, text)

    def test_script_defines_harder_dataset_shapes_and_claim_flags(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")

        for phrase in (
            "def _demo_offset",
            "def _clustered_shift",
            "def _ring_vs_spiral",
            "def _adversarial_tail_outlier",
            "DATASETS",
            "cupy_grouped_grid_rawkernel",
            "hausdorff_distance_2d_rt_grouped_active_frontier_nearest_witness",
            "trial % 2",
            "all_rows_match_distance",
            "min_median_speedup_vs_cupy",
            '"public_speedup_claim_authorized": False',
            '"rt_core_speedup_claim_authorized": False',
            '"true_zero_copy_claim_authorized": False',
        ):
            self.assertIn(phrase, source)


if __name__ == "__main__":
    unittest.main()
