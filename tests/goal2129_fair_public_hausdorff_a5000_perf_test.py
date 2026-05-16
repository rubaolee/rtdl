from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STEADY_DIR = ROOT / "docs" / "reports" / "goal2129_public_pod_a5000_steady"
SWEEP_DIR = ROOT / "docs" / "reports" / "goal2129_public_pod_a5000_group_sweep"


class FairPublicHausdorffA5000PerfArtifactsTest(unittest.TestCase):
    def test_steady_artifacts_have_fair_baseline_and_parity(self) -> None:
        for sample_count in (8192, 32768, 65536, 131072, 262144, 524288):
            with self.subTest(sample_count=sample_count):
                payload = json.loads((STEADY_DIR / f"public_hd_{sample_count}.json").read_text(encoding="utf-8"))
                self.assertEqual(payload["commit"], "934f252dc35cb6c44ba64752c30d025496630ccd")
                self.assertIn("RTX A5000", payload["gpu"])
                boundary = payload["claim_boundary"]
                self.assertTrue(boundary["cupy_grouped_grid_fairness_baseline"])
                self.assertTrue(boundary["public_dataset_evidence"])
                self.assertFalse(boundary["release_speedup_claim_authorized"])
                self.assertFalse(boundary["xhd_paper_exact_dataset_evidence"])
                self.assertFalse(boundary["three_dimensional_surface_hausdorff_claim"])
                for row in payload["rows"]:
                    self.assertTrue(row["matches_cupy"])
                    self.assertTrue(row["matches_cupy_grouped_grid"])
                    self.assertIn("cupy_grouped_grid_rawkernel", row)
                    self.assertIn("rtdl_rt_grouped_reduced_nearest_witness", row)

    def test_best_grouped_cupy_beats_current_rtdl_on_full_public_cases(self) -> None:
        best = {}
        for path in SWEEP_DIR.glob("public_hd_524288_group_*.json"):
            payload = json.loads(path.read_text(encoding="utf-8"))
            for row in payload["rows"]:
                case = row["case"]
                grouped = float(row["cupy_grouped_grid_rawkernel"]["elapsed_sec"])
                rtdl = float(row["rtdl_rt_grouped_reduced_nearest_witness"]["elapsed_sec"])
                current = best.setdefault(case, {"grouped": float("inf"), "rtdl": float("inf")})
                current["grouped"] = min(current["grouped"], grouped)
                current["rtdl"] = min(current["rtdl"], rtdl)
                self.assertTrue(row["matches_cupy_grouped_grid"])
        self.assertLess(best["stanford_dragon_xy_shifted"]["grouped"], best["stanford_dragon_xy_shifted"]["rtdl"])
        self.assertLess(best["stanford_dragon_vs_happy_xy"]["grouped"], best["stanford_dragon_vs_happy_xy"]["rtdl"])


if __name__ == "__main__":
    unittest.main()
