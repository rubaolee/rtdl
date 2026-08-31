from __future__ import annotations

from pathlib import Path
import json
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class Goal5164XhdPostGoal5163ThreeSampleMatrixTest(unittest.TestCase):
    def test_three_sample_matrix_artifact_preserves_boundaries_when_present(self) -> None:
        path = (
            ROOT
            / "Paper-reproduction-apps"
            / "x-hd-paper"
            / "results"
            / "xhd_seeded_sample256_1024_2048_post_goal5163_matrix_pod.json"
        )
        if not path.exists():
            self.skipTest("Goal5164 POD artifact not generated yet")

        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertFalse(payload["phase_policy"]["ratios_authorized"])
        self.assertFalse(payload["performance_claim_authorized"])
        cases = {case["case"]: case for case in payload["cases"]}
        self.assertEqual(set(cases), {"sample256", "sample1024", "sample2048"})
        expected_sizes = {"sample256": 256, "sample1024": 1024, "sample2048": 2048}
        for name, size in expected_sizes.items():
            case = cases[name]
            self.assertTrue(case["matched"])
            self.assertEqual(case["point_count_a"], size)
            self.assertEqual(case["point_count_b"], size)
            self.assertEqual(case["rtdl"]["validation_mode"], "author-only")
            self.assertIsNone(case["rtdl"]["rtdl_matches_exact_reference"])
            self.assertGreater(case["rtdl"]["route_sec_median"], 0.0)
            self.assertIsNone(case["ratio_policy"]["author_avg_vs_rtdl_route_ratio"])


if __name__ == "__main__":
    unittest.main()
