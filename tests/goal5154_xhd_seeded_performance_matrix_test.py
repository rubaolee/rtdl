from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class Goal5154XhdSeededPerformanceMatrixTest(unittest.TestCase):
    def test_seeded_performance_matrix_preserves_phase_boundaries(self) -> None:
        path = (
            ROOT
            / "Paper-reproduction-apps"
            / "x-hd-paper"
            / "results"
            / "xhd_seeded_sample256_1024_performance_matrix_pod.json"
        )
        payload = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema"], "rtdl.paper_reproduction.xhd.seeded_performance_matrix.v1")
        self.assertFalse(payload["performance_claim_authorized"])
        self.assertFalse(payload["author_performance_parity_claimed"])
        self.assertFalse(payload["phase_policy"]["ratios_authorized"])

        cases = {case["case"]: case for case in payload["cases"]}
        self.assertEqual(set(cases), {"sample256", "sample1024"})
        for case in cases.values():
            self.assertTrue(case["matched"])
            self.assertIsNone(case["ratio_policy"]["author_avg_vs_rtdl_route_ratio"])
            self.assertIsNone(case["ratio_policy"]["author_wall_vs_rtdl_total_ratio"])
            self.assertIn("Running.AvgTime", case["ratio_policy"]["reason"])
            self.assertGreater(case["author"]["running_avg_time_ms"], 0.0)
            self.assertGreater(case["author"]["process_wall_sec"], 0.0)
            self.assertGreater(case["rtdl"]["route_sec_median"], 0.0)
            self.assertGreater(case["rtdl"]["exact_reference_sec_median"], 0.0)
            self.assertEqual(len(case["rtdl"]["route_sec_runs"]), 3)
            self.assertEqual(case["rtdl"]["frontier_native_symbol"], "rtdl_optix_collect_cell_mbr_nearest_frontier_3d")


if __name__ == "__main__":
    unittest.main()
