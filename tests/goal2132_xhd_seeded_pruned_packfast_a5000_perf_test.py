import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2132_xhd_seeded_pruned_packfast_a5000_perf_2026-05-16.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2131_public_pod_a5000_seeded_pruned_sweep_packfast"


class Goal2132XhdSeededPrunedPackfastA5000PerfTest(unittest.TestCase):
    def test_artifacts_match_grouped_cupy_and_show_best_vs_best_speedup(self) -> None:
        best: dict[str, dict[str, float]] = {}
        for path in ARTIFACT_DIR.glob("public_hd_524288_group_*.json"):
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["commit"], "8bb02b585dcb91c68378fc465b1b9c4850990f13")
            self.assertIn("RTX A5000", payload["gpu"])
            self.assertTrue(payload["claim_boundary"]["cupy_grouped_grid_fairness_baseline"])
            self.assertTrue(payload["claim_boundary"]["xhd_seeded_pruned_rtdl_path"])
            self.assertFalse(payload["claim_boundary"]["release_speedup_claim_authorized"])
            for row in payload["rows"]:
                self.assertTrue(row["matches_cupy_grouped_grid_seeded_pruned"])
                case = row["case"]
                grouped = float(row["cupy_grouped_grid_rawkernel"]["elapsed_sec"])
                rtdl = float(row["rtdl_rt_grouped_seeded_pruned_nearest_witness"]["elapsed_sec"])
                current = best.setdefault(case, {"grouped": float("inf"), "rtdl": float("inf")})
                current["grouped"] = min(current["grouped"], grouped)
                current["rtdl"] = min(current["rtdl"], rtdl)
        self.assertLess(best["stanford_dragon_xy_shifted"]["rtdl"], best["stanford_dragon_xy_shifted"]["grouped"] / 6.0)
        self.assertLess(best["stanford_dragon_vs_happy_xy"]["rtdl"], best["stanford_dragon_vs_happy_xy"]["grouped"] / 6.0)

    def test_report_records_precise_claim_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("Best grouped CuPy", report)
        self.assertIn("Best RTDL/OptiX seeded-pruned", report)
        self.assertIn("6.10x", report)
        self.assertIn("6.38x", report)
        self.assertIn("Beats all possible CUDA implementations | `not-claimed`", report)
        self.assertIn("Matches X-HD paper datasets and 3D surface setting | `not-claimed`", report)


if __name__ == "__main__":
    unittest.main()
