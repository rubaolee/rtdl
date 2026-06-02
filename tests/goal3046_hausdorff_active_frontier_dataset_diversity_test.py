from __future__ import annotations

import json
import unittest
from pathlib import Path

import rtdsl as rt


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "goal3046_hausdorff_active_frontier_dataset_diversity.py"
REPORT = REPO_ROOT / "docs" / "reports" / "goal3046_hausdorff_active_frontier_dataset_diversity_2026-06-02.md"
ARTIFACT = REPO_ROOT / "docs" / "reports" / "goal3046_hausdorff_active_frontier_dataset_diversity_a4000_2026-06-02.json"


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
            "A4000 dataset-diversity run passed",
            "All 60 measured trials matched",
            "Minimum median speedup vs CuPy: 2.044x",
            "Maximum median speedup vs CuPy: 7.673x",
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

    def test_a4000_artifact_records_all_dataset_rows_and_boundaries(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["goal"], "Goal3046")
        self.assertEqual(data["trials"], 5)
        self.assertEqual(data["warmup"], 1)
        self.assertEqual(data["sizes"], [32768, 65536, 131072])
        self.assertEqual(
            data["datasets"],
            ["adversarial_tail_outlier", "clustered_shift", "demo_offset", "ring_vs_spiral"],
        )
        self.assertTrue(data["all_rows_match_distance"])
        self.assertGreater(data["min_median_speedup_vs_cupy"], 2.0)
        self.assertGreater(data["median_of_median_speedups_vs_cupy"], 4.0)
        self.assertGreater(data["max_median_speedup_vs_cupy"], 7.5)
        self.assertFalse(data["public_speedup_claim_authorized"])
        self.assertFalse(data["rt_core_speedup_claim_authorized"])
        self.assertFalse(data["true_zero_copy_claim_authorized"])

        rows = data["rows"]
        self.assertEqual(len(rows), 12)
        for row in rows:
            self.assertTrue(row["all_trials_match_distance"])
            self.assertEqual(row["cupy_grouped_grid"]["count"], 5)
            self.assertEqual(row["active_frontier"]["count"], 5)
            self.assertLess(row["active_vs_cupy_median_ratio"], 1.0)

    def test_v2_6_roadmap_indexes_dataset_diversity_without_claims(self) -> None:
        roadmap = rt.v2_6_roadmap()
        validation = rt.validate_v2_6_roadmap(repo_root=REPO_ROOT)

        self.assertEqual(roadmap["hausdorff_active_frontier_dataset_diversity_goal"], "Goal3046")
        self.assertIn("12_cases", roadmap["hausdorff_active_frontier_dataset_diversity_status"])
        self.assertIn("not_public_speedup_evidence", roadmap["hausdorff_active_frontier_dataset_diversity_status"])
        self.assertFalse(roadmap["release_authorized"])
        self.assertFalse(roadmap["public_speedup_claim_authorized"])
        self.assertEqual("accept", validation["status"])


if __name__ == "__main__":
    unittest.main()
