from __future__ import annotations

from pathlib import Path
import json
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "scripts"))


class Goal5166XhdRes4FullScalingTest(unittest.TestCase):
    def test_seeded_performance_runner_supports_res4full(self) -> None:
        import run_xhd_seeded_performance_matrix as matrix

        self.assertIn("res4full", matrix.CASE_FILES)
        self.assertEqual(
            matrix.CASE_FILES["res4full"],
            (
                "stanford_dragon_res4_full.ply",
                "stanford_happy_res4_full.ply",
            ),
        )

    def test_res4full_fixture_summaries_preserve_level_b_boundaries(self) -> None:
        expected = {
            "stanford_dragon_res4_full_summary.json": 5205,
            "stanford_happy_res4_full_summary.json": 7108,
        }
        for name, point_count in expected.items():
            path = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results" / name
            with self.subTest(path=name):
                payload = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(payload["schema"], "rtdl.paper_reproduction.xhd.ply_sample.v1")
                self.assertEqual(payload["sample_point_count"], point_count)
                self.assertEqual(payload["input_point_count"], point_count)
                self.assertEqual(payload["n_dims"], 3)
                self.assertTrue(payload["claim_boundary"]["same_source_sample"])
                self.assertFalse(payload["claim_boundary"]["exact_paper_dataset_reproduction_claimed"])
                self.assertFalse(payload["claim_boundary"]["performance_claimed"])

    def test_res4full_matrix_artifact_preserves_no_ratio_boundary_when_present(self) -> None:
        path = (
            ROOT
            / "Paper-reproduction-apps"
            / "x-hd-paper"
            / "results"
            / "xhd_seeded_res4full_post_goal5163_matrix_pod.json"
        )
        if not path.exists():
            self.skipTest("Goal5166 POD artifact not generated yet")

        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertFalse(payload["phase_policy"]["ratios_authorized"])
        self.assertFalse(payload["performance_claim_authorized"])
        cases = {case["case"]: case for case in payload["cases"]}
        self.assertEqual(set(cases), {"res4full"})
        case = cases["res4full"]
        self.assertTrue(case["matched"])
        self.assertEqual(case["point_count_a"], 5205)
        self.assertEqual(case["point_count_b"], 7108)
        self.assertEqual(case["rtdl"]["validation_mode"], "author-only")
        self.assertIsNone(case["rtdl"]["rtdl_matches_exact_reference"])
        self.assertGreater(case["rtdl"]["route_sec_median"], 0.0)
        self.assertIsNone(case["ratio_policy"]["author_avg_vs_rtdl_route_ratio"])


if __name__ == "__main__":
    unittest.main()
