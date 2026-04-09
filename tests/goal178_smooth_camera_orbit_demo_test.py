from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

from examples.visual_demo.rtdl_smooth_camera_orbit_demo import _camera_eye_for_phase
from examples.visual_demo.rtdl_smooth_camera_orbit_demo import _smooth_camera_phase_samples
from examples.visual_demo.rtdl_smooth_camera_orbit_demo import _smooth_demo_lights
from examples.visual_demo.rtdl_smooth_camera_orbit_demo import _smooth_demo_theme
from examples.visual_demo.rtdl_smooth_camera_orbit_demo import render_smooth_camera_orbit_frames
from examples.visual_demo.rtdl_smooth_camera_orbit_demo import render_smooth_camera_orbit_optix_frames
from examples.visual_demo.rtdl_smooth_camera_orbit_demo import render_smooth_camera_orbit_vulkan_frames


class Goal178SmoothCameraOrbitDemoTest(unittest.TestCase):
    def test_camera_eye_stays_on_front_arc(self) -> None:
        center = (0.0, 0.08, 0.0)
        start = _camera_eye_for_phase(0.0, center=center)
        middle = _camera_eye_for_phase(0.5, center=center)
        end = _camera_eye_for_phase(1.0, center=center)
        self.assertLess(start[0], 0.0)
        self.assertAlmostEqual(middle[0], 0.0, places=6)
        self.assertGreater(end[0], 0.0)
        self.assertGreater(start[2], 0.0)
        self.assertGreater(middle[2], 0.0)
        self.assertGreater(end[2], 0.0)

    def test_smooth_demo_lights_are_fixed_and_positive(self) -> None:
        lights = _smooth_demo_lights()
        self.assertEqual(len(lights), 1)
        for light in lights:
            self.assertGreater(float(light["intensity"]), 0.0)
            self.assertEqual(len(light["position"]), 3)
        self.assertGreater(float(lights[0]["display_alpha"]), 0.0)
        self.assertGreater(float(lights[0]["size_scale"]), 1.0)

    def test_deep_blue_redsun_theme_is_redder_and_brighter(self) -> None:
        baseline = _smooth_demo_theme("true_onelight")
        themed = _smooth_demo_theme("deep_blue_redsun")
        baseline_light = baseline["lights"][0]
        themed_light = themed["lights"][0]
        self.assertGreater(float(themed_light["intensity"]), float(baseline_light["intensity"]))
        self.assertGreater(float(themed_light["color"][0]), float(themed_light["color"][1]))
        self.assertGreater(float(themed_light["color"][0]), float(themed_light["color"][2]))
        self.assertGreater(float(themed["halo_alpha"]), float(baseline["halo_alpha"]))
        self.assertLess(float(themed["ground_shadow_alpha"]), float(baseline["ground_shadow_alpha"]))

    def test_uniform_phase_samples_do_not_repeat_opening_pose(self) -> None:
        phases = _smooth_camera_phase_samples(5, mode="uniform")
        self.assertEqual(len(phases), 5)
        self.assertEqual(len(phases), 5)
        expected_phases = (0.0, 0.2, 0.4, 0.6, 0.8)
        for actual, expected in zip(phases, expected_phases):
            self.assertAlmostEqual(actual, expected)

    def test_render_one_frame_writes_summary_and_compare(self) -> None:
        output_dir = Path("build/goal178_smooth_camera_orbit_demo_test/one_frame")
        shutil.rmtree(output_dir, ignore_errors=True)
        summary = render_smooth_camera_orbit_frames(
            backend="cpu_python_reference",
            compare_backend="cpu_python_reference",
            width=24,
            height=24,
            latitude_bands=6,
            longitude_bands=12,
            frame_count=1,
            output_dir=output_dir,
            phase_mode="uniform",
        )
        self.assertEqual(summary["frame_count"], 1)
        self.assertEqual(summary["camera_motion"], "front_arc")
        self.assertEqual(summary["light_count"], 1)
        compare_summary = summary["frames"][0]["compare_backend"]
        self.assertIsNotNone(compare_summary)
        self.assertTrue(compare_summary["matches"])
        self.assertTrue(compare_summary["exact_matches"])
        self.assertEqual(compare_summary["visible_mismatch_count"], 0)
        self.assertEqual(compare_summary["exact_mismatch_count"], 0)
        persisted = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
        self.assertEqual(persisted["phase_mode"], "uniform")
        self.assertTrue(persisted["phase_endpoint_inclusive"])

    def test_themed_render_persists_theme_name(self) -> None:
        output_dir = Path("build/goal178_smooth_camera_orbit_demo_test/redsun_theme")
        shutil.rmtree(output_dir, ignore_errors=True)
        summary = render_smooth_camera_orbit_frames(
            backend="cpu_python_reference",
            compare_backend=None,
            width=16,
            height=16,
            latitude_bands=4,
            longitude_bands=8,
            frame_count=1,
            output_dir=output_dir,
            phase_mode="uniform",
            theme="deep_blue_redsun",
        )
        self.assertEqual(summary["theme"], "deep_blue_redsun")
        persisted = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
        self.assertEqual(persisted["theme"], "deep_blue_redsun")

    def test_multi_frame_render_produces_distinct_frames(self) -> None:
        output_dir = Path("build/goal178_smooth_camera_orbit_demo_test/multi")
        shutil.rmtree(output_dir, ignore_errors=True)
        summary = render_smooth_camera_orbit_frames(
            backend="cpu_python_reference",
            compare_backend=None,
            width=20,
            height=20,
            latitude_bands=6,
            longitude_bands=12,
            frame_count=3,
            output_dir=output_dir,
            phase_mode="uniform",
        )
        frame_bytes = [Path(frame["frame_path"]).read_bytes() for frame in summary["frames"]]
        self.assertNotEqual(frame_bytes[0], frame_bytes[1])
        self.assertNotEqual(frame_bytes[1], frame_bytes[2])
        self.assertFalse(summary["phase_endpoint_inclusive"])
        self.assertLess(summary["frames"][-1]["phase"], 1.0)

    def test_jobs_gt_one_render_produces_frames(self) -> None:
        output_dir = Path("build/goal178_smooth_camera_orbit_demo_test/jobs_two")
        shutil.rmtree(output_dir, ignore_errors=True)
        summary = render_smooth_camera_orbit_frames(
            backend="cpu_python_reference",
            compare_backend=None,
            width=20,
            height=20,
            latitude_bands=6,
            longitude_bands=12,
            frame_count=2,
            output_dir=output_dir,
            jobs=2,
            phase_mode="uniform",
        )
        self.assertEqual(summary["jobs"], 2)
        for frame in summary["frames"]:
            self.assertTrue(Path(frame["frame_path"]).exists())

    def test_vulkan_wrapper_uses_expected_backend(self) -> None:
        output_dir = Path("build/goal178_smooth_camera_orbit_demo_test/vulkan_wrapper")
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

    def test_optix_wrapper_uses_expected_backend(self) -> None:
        output_dir = Path("build/goal178_smooth_camera_orbit_demo_test/optix_wrapper")
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


if __name__ == "__main__":
    unittest.main()
