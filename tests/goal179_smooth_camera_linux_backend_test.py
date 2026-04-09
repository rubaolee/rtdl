from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

from examples.visual_demo.rtdl_smooth_camera_orbit_demo import render_smooth_camera_orbit_optix_frames
from examples.visual_demo.rtdl_smooth_camera_orbit_demo import render_smooth_camera_orbit_vulkan_frames


class Goal179SmoothCameraLinuxBackendTest(unittest.TestCase):
    def test_optix_wrapper_reports_optix_backend(self) -> None:
        output_dir = Path("build/goal179_smooth_camera_linux_backend_test/optix_backend_name")
        try:
            summary = render_smooth_camera_orbit_optix_frames(
                output_dir=output_dir,
                compare_backend=None,
                width=16,
                height=16,
                latitude_bands=4,
                longitude_bands=8,
                frame_count=1,
            )
        except Exception as exc:
            self.skipTest(f"optix unavailable: {exc}")
        self.assertEqual(summary["backend"], "optix")

    def test_vulkan_wrapper_reports_vulkan_backend(self) -> None:
        output_dir = Path("build/goal179_smooth_camera_linux_backend_test/vulkan_backend_name")
        try:
            summary = render_smooth_camera_orbit_vulkan_frames(
                output_dir=output_dir,
                compare_backend=None,
                width=16,
                height=16,
                latitude_bands=4,
                longitude_bands=8,
                frame_count=1,
            )
        except Exception as exc:
            self.skipTest(f"vulkan unavailable: {exc}")
        self.assertEqual(summary["backend"], "vulkan")

    def test_optix_smoke_compare_matches_reference(self) -> None:
        output_dir = Path("build/goal179_smooth_camera_linux_backend_test/optix_smoke")
        try:
            summary = render_smooth_camera_orbit_optix_frames(
                output_dir=output_dir,
                compare_backend="cpu_python_reference",
                width=16,
                height=16,
                latitude_bands=4,
                longitude_bands=8,
                frame_count=1,
            )
        except Exception as exc:
            self.skipTest(f"optix unavailable: {exc}")
        self.assertEqual(summary["image_width"], 16)
        self.assertEqual(summary["image_height"], 16)
        self.assertEqual(summary["frame_count"], 1)
        self.assertEqual(len(summary["frames"]), 1)
        compare_summary = summary["frames"][0]["compare_backend"]
        self.assertIsNotNone(compare_summary)
        self.assertEqual(compare_summary["backend"], "cpu_python_reference")
        self.assertTrue(compare_summary["matches"])

    def test_vulkan_smoke_compare_matches_reference(self) -> None:
        output_dir = Path("build/goal179_smooth_camera_linux_backend_test/vulkan_smoke")
        try:
            summary = render_smooth_camera_orbit_vulkan_frames(
                output_dir=output_dir,
                compare_backend="cpu_python_reference",
                width=16,
                height=16,
                latitude_bands=4,
                longitude_bands=8,
                frame_count=1,
            )
        except Exception as exc:
            self.skipTest(f"vulkan unavailable: {exc}")
        self.assertEqual(summary["image_width"], 16)
        self.assertEqual(summary["image_height"], 16)
        self.assertEqual(summary["frame_count"], 1)
        self.assertEqual(len(summary["frames"]), 1)
        compare_summary = summary["frames"][0]["compare_backend"]
        self.assertIsNotNone(compare_summary)
        self.assertEqual(compare_summary["backend"], "cpu_python_reference")
        self.assertTrue(compare_summary["matches"])


if __name__ == "__main__":
    unittest.main()
