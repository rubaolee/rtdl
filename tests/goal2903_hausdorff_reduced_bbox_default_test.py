import unittest
from pathlib import Path

from scripts import goal2801_hausdorff_xhd_v25_canonical_entrypoint as entrypoint


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2903_hausdorff_reduced_bbox_default_2026-05-31.md"


class Goal2903HausdorffReducedBboxDefaultTest(unittest.TestCase):
    def test_canonical_entrypoint_defaults_to_reduced_bbox_path(self) -> None:
        self.assertEqual(entrypoint.DEFAULT_RTDL_METHOD, "rtdl_rt_grouped_reduced_nearest_witness")
        self.assertEqual(entrypoint.DEFAULT_REDUCED_TARGET_POINTS_PER_GROUP, 2048)
        self.assertFalse(entrypoint.DEFAULT_REDUCED_SEED_WITH_THRESHOLD)

    def test_run_helper_passes_reduced_bbox_defaults_to_user_function(self) -> None:
        calls = []

        class FakeResult:
            distance = 1.0
            direction = "a_to_b"
            source_index = 0
            target_index = 0
            elapsed_sec = 0.001
            method = "fake"

        original = entrypoint.hd.hausdorff_distance_2d_rt_grouped_reduced_nearest_witness
        try:
            def fake_reduced(points_a, points_b, *, seed_with_threshold, target_points_per_group):
                calls.append(
                    {
                        "seed_with_threshold": seed_with_threshold,
                        "target_points_per_group": target_points_per_group,
                    }
                )
                return FakeResult()

            entrypoint.hd.hausdorff_distance_2d_rt_grouped_reduced_nearest_witness = fake_reduced
            result = entrypoint._run_rtdl_method(
                [(0.0, 0.0)],
                [(1.0, 1.0)],
                rtdl_method="rtdl_rt_grouped_reduced_nearest_witness",
            )
        finally:
            entrypoint.hd.hausdorff_distance_2d_rt_grouped_reduced_nearest_witness = original

        self.assertEqual(result.elapsed_sec, 0.001)
        self.assertEqual(
            calls,
            [{"seed_with_threshold": False, "target_points_per_group": 2048}],
        )

    def test_report_records_design_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("reduced point-group nearest-witness path", text)
        self.assertIn("bbox upper bound", text)
        self.assertIn("native engine change: none", text)
        self.assertIn("not a public speedup claim", text)
        self.assertIn("does not claim RTDL beats X-HD", text)


if __name__ == "__main__":
    unittest.main()
