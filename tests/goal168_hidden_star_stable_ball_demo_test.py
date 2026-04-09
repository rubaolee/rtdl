from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

from examples.visual_demo.rtdl_hidden_star_stable_ball_demo import _frame_light
from examples.visual_demo.rtdl_hidden_star_stable_ball_demo import render_hidden_star_stable_ball_frames


class Goal168HiddenStarStableBallDemoTest(unittest.TestCase):
    def test_frame_light_moves_right_to_left(self) -> None:
        start = _frame_light(0.0)["position"]
        mid = _frame_light(0.5)["position"]
        end = _frame_light(1.0)["position"]
        self.assertGreater(float(start[0]), float(mid[0]))
        self.assertGreater(float(mid[0]), float(end[0]))
        self.assertAlmostEqual(float(mid[0]), 0.0, places=6)

    def test_render_two_frames_has_zero_shadow_rays_and_distinct_outputs(self) -> None:
        output_dir = Path("build/goal168_hidden_star_stable_ball_demo_test/two_frames")
        summary = render_hidden_star_stable_ball_frames(
            backend="cpu_python_reference",
            compare_backend=None,
            width=24,
            height=24,
            latitude_bands=8,
            longitude_bands=16,
            frame_count=2,
            output_dir=output_dir,
            jobs=1,
        )
        self.assertEqual(summary["light_count"], 1)
        self.assertEqual(summary["light_layout"], "single_analytic")
        self.assertEqual(summary["total_shadow_query_seconds"], 0.0)
        self.assertEqual(len(summary["frames"]), 2)
        for frame in summary["frames"]:
            self.assertEqual(frame["shadow_rays"], 0)
            self.assertTrue(Path(frame["frame_path"]).exists())
        frame_bytes = [Path(frame["frame_path"]).read_bytes() for frame in summary["frames"]]
        self.assertNotEqual(frame_bytes[0], frame_bytes[1])
        persisted = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
        self.assertEqual(persisted["light_layout"], "single_analytic")

    def test_render_two_frames_rtdl_shadow_emits_shadow_rays(self) -> None:
        output_dir = Path("build/goal168_hidden_star_stable_ball_demo_test/two_frames_rtdl_shadow")
        summary = render_hidden_star_stable_ball_frames(
            backend="cpu_python_reference",
            compare_backend=None,
            width=24,
            height=24,
            latitude_bands=8,
            longitude_bands=16,
            frame_count=2,
            output_dir=output_dir,
            jobs=1,
            shadow_mode="rtdl_light_to_surface",
        )
        self.assertEqual(summary["light_layout"], "single_rtdl_light_to_surface_shadow")
        self.assertEqual(summary["shadow_mode"], "rtdl_light_to_surface")
        self.assertGreater(summary["total_shadow_query_seconds"], 0.0)
        self.assertEqual(len(summary["frames"]), 2)
        self.assertTrue(any(int(frame["shadow_rays"]) > 0 for frame in summary["frames"]))
        persisted = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
        self.assertEqual(persisted["shadow_mode"], "rtdl_light_to_surface")


if __name__ == "__main__":
    unittest.main()
