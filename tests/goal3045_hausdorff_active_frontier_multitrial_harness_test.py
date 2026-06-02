from __future__ import annotations

import json
import unittest
from pathlib import Path

import rtdsl as rt


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "goal3045_hausdorff_active_frontier_multitrial.py"
REPORT = REPO_ROOT / "docs" / "reports" / "goal3045_hausdorff_active_frontier_multitrial_harness_2026-06-02.md"
ARTIFACT = REPO_ROOT / "docs" / "reports" / "goal3045_hausdorff_active_frontier_multitrial_a4000_2026-06-02.json"


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
            "A4000 multitrial run passed",
            "6.586x median speedup",
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

    def test_a4000_artifact_records_repeated_median_crossover(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["goal"], "Goal3045")
        self.assertEqual(data["trials"], 10)
        self.assertEqual(data["warmup"], 2)
        self.assertTrue(data["all_rows_match_distance"])
        self.assertGreater(data["best_median_speedup_vs_cupy"], 6.5)
        self.assertFalse(data["public_speedup_claim_authorized"])
        self.assertFalse(data["rt_core_speedup_claim_authorized"])
        self.assertFalse(data["true_zero_copy_claim_authorized"])

        rows = data["rows"]
        self.assertEqual([row["points_a"] for row in rows], [16384, 65536, 131072])
        for row in rows:
            self.assertTrue(row["all_trials_match_distance"])
            self.assertEqual(row["cupy_grouped_grid"]["count"], 10)
            self.assertEqual(row["active_frontier"]["count"], 10)
            self.assertLess(row["active_vs_cupy_median_ratio"], 1.0)
        self.assertGreater(rows[-1]["active_speedup_vs_cupy_median"], 6.5)

    def test_v2_6_roadmap_indexes_multitrial_without_claims(self) -> None:
        roadmap = rt.v2_6_roadmap()
        validation = rt.validate_v2_6_roadmap(repo_root=REPO_ROOT)

        self.assertEqual(roadmap["hausdorff_active_frontier_multitrial_goal"], "Goal3045")
        self.assertIn("10_trial_median", roadmap["hausdorff_active_frontier_multitrial_status"])
        self.assertIn("not_public_speedup_evidence", roadmap["hausdorff_active_frontier_multitrial_status"])
        self.assertFalse(roadmap["release_authorized"])
        self.assertFalse(roadmap["public_speedup_claim_authorized"])
        self.assertEqual("accept", validation["status"])


if __name__ == "__main__":
    unittest.main()
