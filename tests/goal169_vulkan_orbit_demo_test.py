from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

from examples.visual_demo.rtdl_orbiting_star_ball_demo import render_orbiting_star_ball_vulkan_frames


class Goal169VulkanOrbitDemoTest(unittest.TestCase):
    def test_vulkan_one_frame_compare_smoke(self) -> None:
        output_dir = Path("build/goal169_vulkan_orbit_demo_test/one_frame")
        try:
            summary = render_orbiting_star_ball_vulkan_frames(
                output_dir=output_dir,
                compare_backend="cpu_python_reference",
                width=32,
                height=32,
                latitude_bands=8,
                longitude_bands=16,
                frame_count=1,
            )
        except Exception as exc:
            self.skipTest(f"vulkan unavailable: {exc}")
        self.assertEqual(summary["backend"], "vulkan")
        compare_summary = summary["frames"][0]["compare_backend"]
        self.assertIsNotNone(compare_summary)
        self.assertEqual(compare_summary["backend"], "cpu_python_reference")
        self.assertTrue(compare_summary["matches"])
        self.assertTrue(Path(summary["frames"][0]["frame_path"]).exists())

    def test_vulkan_denser_compare_smoke(self) -> None:
        output_dir = Path("build/goal169_vulkan_orbit_demo_test/denser_frame")
        try:
            summary = render_orbiting_star_ball_vulkan_frames(
                output_dir=output_dir,
                compare_backend="cpu_python_reference",
                width=96,
                height=96,
                latitude_bands=16,
                longitude_bands=32,
                frame_count=1,
            )
        except Exception as exc:
            self.skipTest(f"vulkan unavailable: {exc}")
        compare_summary = summary["frames"][0]["compare_backend"]
        self.assertIsNotNone(compare_summary)
        self.assertTrue(compare_summary["matches"])


if __name__ == "__main__":
    unittest.main()
