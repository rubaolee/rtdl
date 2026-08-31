import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5289_figure5_bounded_same_pod_probe_2026-07-09.json"
)


class Goal5289XhdFigure5BoundedSamePodProbeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not ARTIFACT.exists():
            raise unittest.SkipTest(f"missing artifact: {ARTIFACT}")
        cls.payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def test_same_pod_probe_records_author_and_rtdl_but_is_value_no_go(self):
        payload = self.payload

        self.assertEqual(
            payload["schema"],
            "rtdl.paper_reproduction.xhd.goal5289.figure5_bounded_same_pod_probe.v1",
        )
        self.assertEqual(payload["goal"], "Goal5289")
        self.assertEqual(payload["dataset"], "graphics_dragon_asian_scaled_1e-3_level_b")
        self.assertEqual(payload["author_wall"]["returncode"], 0)
        self.assertEqual(payload["rtdl_wall"]["returncode"], 0)
        self.assertFalse(payload["matched_value"])
        self.assertGreater(payload["abs_diff"], 1e-5)
        self.assertAlmostEqual(payload["author_hd_result"], 0.06545527279376984)
        self.assertAlmostEqual(payload["rtdl_hd_result"], 0.06536787240753439)

    def test_author_run_is_xhd_lb256_on_candidate_not_exact_paper_input(self):
        running = self.payload["author_running"]

        self.assertTrue(running["EB"])
        self.assertTrue(running["Prune"])
        self.assertEqual(running["LB"], 256)
        self.assertEqual(running["NumPointsPerCell"], 15)
        self.assertEqual(running["Repeats"][0]["Algorithm"], "XHD")
        self.assertEqual(running["Repeats"][0]["Execution"], "GPU")
        self.assertGreater(running["AvgTime"], 0)
        self.assertGreater(running["Repeats"][0]["ReportedTime"], 0)

    def test_no_performance_ratio_or_figure5_reproduction_claim(self):
        payload = self.payload

        self.assertFalse(payload["same_denominator_ratio_allowed"])
        for value in payload["claim_boundary"].values():
            self.assertFalse(value)
        self.assertGreater(payload["rtdl_wall"]["wall_sec"], payload["author_wall"]["wall_sec"])


if __name__ == "__main__":
    unittest.main()
