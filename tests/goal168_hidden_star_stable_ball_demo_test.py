from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from examples.visual_demo.rtdl_hidden_star_stable_ball_demo import _frame_light
from examples.visual_demo.rtdl_hidden_star_stable_ball_demo import _make_light_to_surface_shadow_ray
from examples.visual_demo.rtdl_hidden_star_stable_ball_demo import render_hidden_star_stable_ball_optix_frames
from examples.visual_demo.rtdl_hidden_star_stable_ball_demo import render_hidden_star_stable_ball_frames
from examples.visual_demo.rtdl_hidden_star_stable_ball_demo import render_hidden_star_stable_ball_vulkan_frames
from examples.visual_demo.rtdl_spinning_ball_3d_demo import _run_backend_rows


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

    def test_light_to_surface_shadow_ray_detects_real_occluder(self) -> None:
        light = _frame_light(0.0)
        hit_point = (0.0, 0.08, 1.46)
        shadow_ray = _make_light_to_surface_shadow_ray(ray_id=7, hit_point=hit_point, light=light)
        occluder = (
            rt.Triangle3D(
                id=1,
                x0=33.6,
                y0=-0.12,
                z0=6.60,
                x1=34.0,
                y1=-0.12,
                z1=6.60,
                x2=33.8,
                y2=0.28,
                z2=6.60,
            ),
        )
        rows = _run_backend_rows("cpu_python_reference", rays=(shadow_ray,), triangles=occluder)
        lookup = {int(row["ray_id"]): int(row["hit_count"]) for row in rows}
        self.assertGreater(lookup.get(7, 0), 0)

    def test_shadow_ray_tmax_stops_before_surface(self) -> None:
        light = _frame_light(0.0)
        hit_point = (0.0, 0.08, 1.46)
        shadow_ray = _make_light_to_surface_shadow_ray(ray_id=9, hit_point=hit_point, light=light)
        surface_triangle = (
            rt.Triangle3D(
                id=99,
                x0=hit_point[0] - 0.1,
                y0=hit_point[1] - 0.1,
                z0=hit_point[2],
                x1=hit_point[0] + 0.1,
                y1=hit_point[1] - 0.1,
                z1=hit_point[2],
                x2=hit_point[0],
                y2=hit_point[1] + 0.1,
                z2=hit_point[2],
            ),
        )
        rows = _run_backend_rows(
            "cpu_python_reference",
            rays=(shadow_ray,),
            triangles=surface_triangle,
        )
        lookup = {int(row["ray_id"]): int(row["hit_count"]) for row in rows}
        self.assertEqual(
            lookup.get(9, 0),
            0,
            "tmax should stop before the surface triangle",
        )

    def test_compare_backend_self_parity(self) -> None:
        output_dir = Path("build/goal168_hidden_star_stable_ball_demo_test/compare_self")
        summary = render_hidden_star_stable_ball_frames(
            backend="cpu_python_reference",
            compare_backend="cpu_python_reference",
            width=20,
            height=20,
            latitude_bands=6,
            longitude_bands=12,
            frame_count=1,
            output_dir=output_dir,
            jobs=1,
        )
        compare = summary["frames"][0].get("compare_backend")
        self.assertIsNotNone(compare)
        assert compare is not None
        self.assertEqual(compare["backend"], "cpu_python_reference")
        self.assertTrue(compare["matches"])

    def test_jobs_2_matches_jobs_1(self) -> None:
        output_dir_jobs_1 = Path("build/goal168_hidden_star_stable_ball_demo_test/jobs_1")
        output_dir_jobs_2 = Path("build/goal168_hidden_star_stable_ball_demo_test/jobs_2")
        kwargs = {
            "backend": "cpu_python_reference",
            "compare_backend": None,
            "width": 20,
            "height": 20,
            "latitude_bands": 6,
            "longitude_bands": 12,
            "frame_count": 2,
            "shadow_mode": "rtdl_light_to_surface",
        }
        summary_1 = render_hidden_star_stable_ball_frames(
            output_dir=output_dir_jobs_1,
            jobs=1,
            **kwargs,
        )
        try:
            summary_2 = render_hidden_star_stable_ball_frames(
                output_dir=output_dir_jobs_2,
                jobs=2,
                **kwargs,
            )
        except PermissionError as exc:
            raise unittest.SkipTest(f"ProcessPoolExecutor unavailable in this environment: {exc}") from exc
        for index in range(2):
            bytes_1 = Path(summary_1["frames"][index]["frame_path"]).read_bytes()
            bytes_2 = Path(summary_2["frames"][index]["frame_path"]).read_bytes()
            self.assertEqual(
                bytes_1,
                bytes_2,
                f"frame {index}: jobs=2 output differs from jobs=1",
            )

    def test_vulkan_wrapper_uses_expected_backend(self) -> None:
        output_dir = Path("build/goal168_hidden_star_stable_ball_demo_test/vulkan_wrapper")
        try:
            summary = render_hidden_star_stable_ball_vulkan_frames(
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
        self.assertEqual(summary["shadow_mode"], "rtdl_light_to_surface")

    def test_optix_wrapper_uses_expected_backend(self) -> None:
        output_dir = Path("build/goal168_hidden_star_stable_ball_demo_test/optix_wrapper")
        try:
            summary = render_hidden_star_stable_ball_optix_frames(
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
        self.assertEqual(summary["shadow_mode"], "rtdl_light_to_surface")


if __name__ == "__main__":
    unittest.main()
