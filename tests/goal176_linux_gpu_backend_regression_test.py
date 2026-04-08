from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

from examples.rtdl_orbiting_star_ball_demo import render_orbiting_star_ball_optix_4k
from examples.rtdl_orbiting_star_ball_demo import render_orbiting_star_ball_vulkan_frames


class Goal176LinuxGpuBackendRegressionTest(unittest.TestCase):
    def _assert_common_summary(self, summary: dict[str, object], *, backend: str, frame_count: int) -> None:
        self.assertEqual(summary["backend"], backend)
        self.assertEqual(summary["frame_count"], frame_count)
        self.assertEqual(summary["light_count"], 2)
        self.assertTrue(summary["show_light_source"])
        self.assertAlmostEqual(float(summary["temporal_blend_alpha"]), 0.15)
        self.assertEqual(len(summary["frames"]), frame_count)
        self.assertGreater(summary["triangle_count"], 0)

    def _assert_first_frame_compare(self, summary: dict[str, object]) -> None:
        compare_summary = summary["frames"][0]["compare_backend"]
        self.assertIsNotNone(compare_summary)
        self.assertEqual(compare_summary["backend"], "cpu_python_reference")
        self.assertTrue(compare_summary["matches"])

    def test_vulkan_two_frame_compare_and_metadata(self) -> None:
        output_dir = Path("build/goal176_linux_gpu_backend_test/vulkan_two_frame")
        try:
            summary = render_orbiting_star_ball_vulkan_frames(
                output_dir=output_dir,
                compare_backend="cpu_python_reference",
                width=96,
                height=96,
                latitude_bands=16,
                longitude_bands=32,
                frame_count=2,
                jobs=1,
                show_light_source=True,
                temporal_blend_alpha=0.15,
            )
        except Exception as exc:
            self.skipTest(f"vulkan unavailable: {exc}")
        self._assert_common_summary(summary, backend="vulkan", frame_count=2)
        self._assert_first_frame_compare(summary)
        for frame in summary["frames"]:
            self.assertTrue(Path(frame["frame_path"]).exists())
        persisted = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
        self.assertEqual(persisted["light_count"], 2)
        self.assertTrue(persisted["show_light_source"])
        self.assertAlmostEqual(float(persisted["temporal_blend_alpha"]), 0.15)

    def test_optix_two_frame_compare_and_metadata(self) -> None:
        output_dir = Path("build/goal176_linux_gpu_backend_test/optix_two_frame")
        try:
            summary = render_orbiting_star_ball_optix_4k(
                output_dir=output_dir,
                compare_backend="cpu_python_reference",
                width=96,
                height=64,
                latitude_bands=16,
                longitude_bands=32,
                frame_count=2,
                jobs=1,
                show_light_source=True,
                temporal_blend_alpha=0.15,
            )
        except Exception as exc:
            self.skipTest(f"optix unavailable: {exc}")
        self._assert_common_summary(summary, backend="optix", frame_count=2)
        self._assert_first_frame_compare(summary)
        for frame in summary["frames"]:
            self.assertTrue(Path(frame["frame_path"]).exists())
        persisted = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
        self.assertEqual(persisted["light_count"], 2)
        self.assertTrue(persisted["show_light_source"])
        self.assertAlmostEqual(float(persisted["temporal_blend_alpha"]), 0.15)


if __name__ == "__main__":
    unittest.main()
