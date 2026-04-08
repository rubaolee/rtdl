from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from examples.rtdl_orbiting_star_ball_demo import _frame_light
from examples.rtdl_orbiting_star_ball_demo import _make_shadow_rays
from examples.rtdl_orbiting_star_ball_demo import _orbit_phase_samples
from examples.rtdl_orbiting_star_ball_demo import render_orbiting_star_ball_frames
from examples.rtdl_spinning_ball_3d_demo import _run_backend_rows
from examples.rtdl_spinning_ball_3d_demo import make_camera_rays
from examples.rtdl_spinning_ball_3d_demo import make_uv_sphere_mesh


class Goal166OrbitingStarBallDemoTest(unittest.TestCase):
    def test_orbit_phase_samples_single_frame_returns_zero(self) -> None:
        phases = _orbit_phase_samples(1)
        self.assertEqual(phases, (0.0,))

    def test_orbit_phase_samples_shape_and_order(self) -> None:
        phases = _orbit_phase_samples(24)
        self.assertEqual(len(phases), 24)
        for phase in phases:
            self.assertGreaterEqual(phase, 0.0)
            self.assertLessEqual(phase, 1.0)
        for left, right in zip(phases, phases[1:]):
            self.assertLessEqual(left, right)

    def test_frame_light_completes_orbit(self) -> None:
        light_0 = _frame_light(0.0)
        light_1 = _frame_light(1.0)
        pos_0 = light_0["position"]
        pos_1 = light_1["position"]
        self.assertAlmostEqual(pos_0[0], pos_1[0], places=6)
        self.assertAlmostEqual(pos_0[2], pos_1[2], places=6)
        self.assertIn("intensity", light_0)
        self.assertGreater(float(light_0["intensity"]), 0.0)

    def test_make_shadow_rays_returns_single_positive_tmax_ray(self) -> None:
        ray = rt.Ray3D(id=7, ox=0.0, oy=0.0, oz=5.0, dx=0.0, dy=0.0, dz=-1.0, tmax=10.0)
        hit_point = (0.0, 0.0, 1.5)
        shadow = _make_shadow_rays(
            ray=ray,
            hit_point=hit_point,
            center=(0.0, 0.08, 0.0),
            light=_frame_light(0.0),
            base_id=ray.id,
        )
        self.assertEqual(len(shadow), 1)
        self.assertGreater(shadow[0].tmax, 0.0)

    def test_render_one_frame_writes_output_and_summary(self) -> None:
        output_dir = Path("build/goal166_orbiting_star_ball_demo_test/one_frame")
        summary = render_orbiting_star_ball_frames(
            backend="cpu_python_reference",
            compare_backend=None,
            width=32,
            height=32,
            latitude_bands=8,
            longitude_bands=16,
            frame_count=1,
            output_dir=output_dir,
        )

        self.assertEqual(summary["frame_count"], 1)
        self.assertEqual(summary["image_width"], 32)
        self.assertEqual(summary["image_height"], 32)
        self.assertGreater(summary["triangle_count"], 0)
        self.assertIn("numpy_fast_path", summary)
        self.assertGreater(summary["total_query_seconds"], 0.0)
        self.assertGreater(summary["total_shading_seconds"], 0.0)
        self.assertGreater(summary["wall_clock_seconds"], 0.0)
        self.assertEqual(len(summary["frames"]), 1)

        frame = summary["frames"][0]
        frame_path = Path(frame["frame_path"])
        self.assertTrue(frame_path.exists())
        self.assertGreater(frame["rt_rows"], 0)
        self.assertGreater(frame["hit_pixels"], 0)

        with frame_path.open("rb") as handle:
            self.assertEqual(handle.readline().decode("ascii").strip(), "P6")
            self.assertEqual(handle.readline().decode("ascii").strip(), "32 32")
            self.assertEqual(handle.readline().decode("ascii").strip(), "255")

        summary_path = output_dir / "summary.json"
        self.assertTrue(summary_path.exists())
        persisted = json.loads(summary_path.read_text(encoding="utf-8"))
        self.assertEqual(persisted["frame_count"], 1)
        self.assertEqual(len(persisted["frames"]), 1)

    def test_show_light_source_round_trips_in_summary(self) -> None:
        for show_light_source in (False, True):
            with self.subTest(show_light_source=show_light_source):
                output_dir = Path(f"build/goal166_orbiting_star_ball_demo_test/show_{show_light_source}")
                summary = render_orbiting_star_ball_frames(
                    backend="cpu_python_reference",
                    compare_backend=None,
                    width=24,
                    height=24,
                    latitude_bands=6,
                    longitude_bands=12,
                    frame_count=1,
                    output_dir=output_dir,
                    show_light_source=show_light_source,
                )
                self.assertEqual(summary["show_light_source"], show_light_source)
                persisted = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
                self.assertEqual(persisted["show_light_source"], show_light_source)

    def test_multi_frame_render_produces_distinct_frames(self) -> None:
        output_dir = Path("build/goal166_orbiting_star_ball_demo_test/multi")
        summary = render_orbiting_star_ball_frames(
            backend="cpu_python_reference",
            compare_backend=None,
            width=24,
            height=24,
            latitude_bands=6,
            longitude_bands=12,
            frame_count=3,
            output_dir=output_dir,
        )
        frame_bytes = [Path(frame["frame_path"]).read_bytes() for frame in summary["frames"]]
        self.assertNotEqual(frame_bytes[0], frame_bytes[1])
        self.assertNotEqual(frame_bytes[1], frame_bytes[2])

    def test_cpu_reference_smoke_path_produces_hits(self) -> None:
        triangles = make_uv_sphere_mesh(
            latitude_bands=6,
            longitude_bands=12,
            radius=1.46,
            center=(0.0, 0.08, 0.0),
        )
        rays = make_camera_rays(
            width=16,
            height=16,
            eye=(0.0, 0.16, 6.1),
            target=(0.0, 0.08, 0.0),
            up_hint=(0.0, 1.0, 0.0),
            fov_y_degrees=28.0,
        )
        rows = _run_backend_rows("cpu_python_reference", rays=rays, triangles=triangles)
        self.assertGreater(sum(int(row["hit_count"]) for row in rows), 0)


if __name__ == "__main__":
    unittest.main()
