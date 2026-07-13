from __future__ import annotations

from pathlib import Path
import json
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "scripts"))


class Goal5165XhdSample4096ScalingTest(unittest.TestCase):
    def test_seeded_performance_runner_supports_sample4096(self) -> None:
        import run_xhd_seeded_performance_matrix as matrix

        self.assertIn("sample4096", matrix.CASE_FILES)
        self.assertEqual(
            matrix.CASE_FILES["sample4096"],
            (
                "stanford_dragon_res4_sample4096.ply",
                "stanford_happy_res4_sample4096.ply",
            ),
        )

    def test_sample4096_fixture_summaries_preserve_level_b_boundaries(self) -> None:
        summaries = [
            ROOT
            / "Paper-reproduction-apps"
            / "x-hd-paper"
            / "results"
            / "stanford_dragon_res4_sample4096_summary.json",
            ROOT
            / "Paper-reproduction-apps"
            / "x-hd-paper"
            / "results"
            / "stanford_happy_res4_sample4096_summary.json",
        ]
        for path in summaries:
            with self.subTest(path=path.name):
                payload = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(payload["schema"], "rtdl.paper_reproduction.xhd.ply_sample.v1")
                self.assertEqual(payload["sample_point_count"], 4096)
                self.assertEqual(payload["n_dims"], 3)
                self.assertTrue(payload["claim_boundary"]["same_source_sample"])
                self.assertFalse(payload["claim_boundary"]["exact_paper_dataset_reproduction_claimed"])
                self.assertFalse(payload["claim_boundary"]["performance_claimed"])

    def test_sample4096_matrix_artifact_preserves_no_ratio_boundary_when_present(self) -> None:
        path = (
            ROOT
            / "Paper-reproduction-apps"
            / "x-hd-paper"
            / "results"
            / "xhd_seeded_sample4096_post_goal5163_matrix_pod.json"
        )
        if not path.exists():
            self.skipTest("Goal5165 POD artifact not generated yet")

        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertFalse(payload["phase_policy"]["ratios_authorized"])
        self.assertFalse(payload["performance_claim_authorized"])
        cases = {case["case"]: case for case in payload["cases"]}
        self.assertEqual(set(cases), {"sample4096"})
        case = cases["sample4096"]
        self.assertTrue(case["matched"])
        self.assertEqual(case["point_count_a"], 4096)
        self.assertEqual(case["point_count_b"], 4096)
        self.assertEqual(case["rtdl"]["validation_mode"], "author-only")
        self.assertIsNone(case["rtdl"]["rtdl_matches_exact_reference"])
        self.assertGreater(case["rtdl"]["route_sec_median"], 0.0)
        self.assertIsNone(case["ratio_policy"]["author_avg_vs_rtdl_route_ratio"])


if __name__ == "__main__":
    unittest.main()
