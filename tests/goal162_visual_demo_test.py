import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

from examples.visual_demo.rtdl_orbit_lights_ball_demo import render_orbit_lights_ball_frames


class Goal162VisualDemoTest(unittest.TestCase):
    def test_render_orbit_lights_ball_frames_writes_ppm_sequence(self) -> None:
        output_dir = Path("build/goal162_visual_demo_test")
        summary = render_orbit_lights_ball_frames(
            backend="cpu_python_reference",
            compare_backend="cpu",
            width=48,
            height=40,
            triangle_count=192,
            frame_count=3,
            vertical_samples=3,
            output_dir=output_dir,
        )

        self.assertEqual(summary["frame_count"], 3)
        self.assertEqual(summary["image_width"], 48)
        self.assertEqual(summary["image_height"], 40)
        self.assertGreater(summary["total_query_seconds"], 0.0)
        self.assertGreater(summary["total_shading_seconds"], 0.0)

        frame_paths = []
        for frame in summary["frames"]:
            self.assertTrue(frame["compare_backend"]["matches"])
            frame_path = Path(frame["frame_path"])
            self.assertTrue(frame_path.exists())
            self.assertGreater(frame["rt_rows"], 0)
            self.assertGreater(frame["sample_rows_with_hits"], 0)
            frame_paths.append(frame_path)

        header = frame_paths[0].read_text(encoding="ascii").splitlines()[:3]
        self.assertEqual(header[0], "P3")
        self.assertEqual(header[1], "48 40")
        self.assertEqual(header[2], "255")

        summary_path = output_dir / "summary.json"
        self.assertTrue(summary_path.exists())
        persisted = json.loads(summary_path.read_text(encoding="utf-8"))
        self.assertEqual(persisted["frame_count"], 3)
        self.assertEqual(len(persisted["frames"]), 3)


if __name__ == "__main__":
    unittest.main()
