from __future__ import annotations

import json
from pathlib import Path
import sys
import time
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
import examples.visual_demo.rtdl_orbiting_star_ball_demo as orbit_demo
from examples.visual_demo.rtdl_orbiting_star_ball_demo import _frame_light
from examples.visual_demo.rtdl_orbiting_star_ball_demo import _frame_lights
from examples.visual_demo.rtdl_orbiting_star_ball_demo import _secondary_frame_light
from examples.visual_demo.rtdl_orbiting_star_ball_demo import _blend_ppm_payloads
from examples.visual_demo.rtdl_orbiting_star_ball_demo import _apply_temporal_blend
from examples.visual_demo.rtdl_orbiting_star_ball_demo import _light_visibility_to_camera
from examples.visual_demo.rtdl_orbiting_star_ball_demo import _make_shadow_rays
from examples.visual_demo.rtdl_orbiting_star_ball_demo import _overlay_star_and_ground
from examples.visual_demo.rtdl_orbiting_star_ball_demo import _orbit_phase_samples
from examples.visual_demo.rtdl_orbiting_star_ball_demo import _shade_orbit_hit
from examples.visual_demo.rtdl_orbiting_star_ball_demo import _shade_pending_hits_numpy
from examples.visual_demo.rtdl_orbiting_star_ball_demo import render_orbiting_star_ball_optix_4k
from examples.visual_demo.rtdl_orbiting_star_ball_demo import render_orbiting_star_ball_vulkan_frames
from examples.visual_demo.rtdl_orbiting_star_ball_demo import render_orbiting_star_ball_frames
from examples.visual_demo.rtdl_spinning_ball_3d_demo import _background_pixel
from examples.visual_demo.rtdl_spinning_ball_3d_demo import _run_backend_rows
from examples.visual_demo.rtdl_spinning_ball_3d_demo import make_camera_rays
from examples.visual_demo.rtdl_spinning_ball_3d_demo import make_uv_sphere_mesh


class Goal166OrbitingStarBallDemoTest(unittest.TestCase):
    def test_blend_ppm_payloads_zero_alpha_keeps_current(self) -> None:
        previous = bytes([10, 20, 30, 40, 50, 60])
        current = bytes([60, 50, 40, 30, 20, 10])
        self.assertEqual(_blend_ppm_payloads(previous, current, 0.0), current)

    def test_blend_ppm_payloads_half_alpha_blends_evenly(self) -> None:
        previous = bytes([0, 0, 0, 200, 200, 200])
        current = bytes([100, 100, 100, 0, 0, 0])
        self.assertEqual(
            _blend_ppm_payloads(previous, current, 0.5),
            bytes([50, 50, 50, 100, 100, 100]),
        )

    def test_apply_temporal_blend_leaves_first_frame_and_changes_second(self) -> None:
        output_dir = Path("build/goal166_orbiting_star_ball_demo_test/temporal_blend_files")
        output_dir.mkdir(parents=True, exist_ok=True)
        frame0 = output_dir / "frame_000.ppm"
        frame1 = output_dir / "frame_001.ppm"
        frame0.write_bytes(b"P6\n1 1\n255\n" + bytes([0, 0, 0]))
        frame1.write_bytes(b"P6\n1 1\n255\n" + bytes([200, 100, 0]))
        _apply_temporal_blend([frame0, frame1], 0.25)
        self.assertEqual(frame0.read_bytes(), b"P6\n1 1\n255\n" + bytes([0, 0, 0]))
        self.assertEqual(frame1.read_bytes(), b"P6\n1 1\n255\n" + bytes([150, 75, 0]))

    def test_apply_temporal_blend_uses_previous_raw_frame_not_recursive_output(self) -> None:
        output_dir = Path("build/goal166_orbiting_star_ball_demo_test/temporal_blend_pairwise")
        output_dir.mkdir(parents=True, exist_ok=True)
        frame0 = output_dir / "frame_000.ppm"
        frame1 = output_dir / "frame_001.ppm"
        frame2 = output_dir / "frame_002.ppm"
        frame0.write_bytes(b"P6\n1 1\n255\n" + bytes([0, 0, 0]))
        frame1.write_bytes(b"P6\n1 1\n255\n" + bytes([200, 0, 0]))
        frame2.write_bytes(b"P6\n1 1\n255\n" + bytes([100, 0, 0]))
        _apply_temporal_blend([frame0, frame1, frame2], 0.5)
        self.assertEqual(frame1.read_bytes(), b"P6\n1 1\n255\n" + bytes([100, 0, 0]))
        self.assertEqual(frame2.read_bytes(), b"P6\n1 1\n255\n" + bytes([150, 0, 0]))

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

    def test_orbit_phase_samples_uniform_mode_is_linear(self) -> None:
        self.assertEqual(_orbit_phase_samples(5, mode="uniform"), (0.0, 0.25, 0.5, 0.75, 1.0))

    def test_frame_light_moves_right_to_left_horizontally(self) -> None:
        light_0 = _frame_light(0.0)
        light_mid = _frame_light(0.5)
        light_1 = _frame_light(1.0)
        pos_0 = light_0["position"]
        pos_mid = light_mid["position"]
        pos_1 = light_1["position"]
        self.assertGreater(pos_0[0], pos_1[0])
        self.assertGreater(pos_0[0], 44.0)
        self.assertLess(pos_1[0], -44.0)
        self.assertAlmostEqual(pos_mid[0], 0.0, places=6)
        self.assertAlmostEqual(pos_0[1], 0.08, places=6)
        self.assertAlmostEqual(pos_1[1], 0.08, places=6)
        self.assertAlmostEqual(pos_0[2], 11.8, places=6)
        self.assertAlmostEqual(pos_0[2], pos_1[2], places=6)
        self.assertIn("intensity", light_0)
        self.assertGreater(float(light_0["intensity"]), 0.0)
        self.assertGreater(float(light_0["intensity"]), 2.5)
        self.assertGreater(float(light_0["size_scale"]), 1.0)

    def test_support_star_is_on_early_and_off_late(self) -> None:
        early = _secondary_frame_light(0.0)
        mid = _secondary_frame_light(0.35)
        late = _secondary_frame_light(0.75)
        self.assertGreater(float(early["intensity"]), 0.0)
        self.assertGreater(float(mid["intensity"]), 0.0)
        self.assertEqual(float(late["intensity"]), 0.0)
        self.assertEqual(float(late["display_alpha"]), 0.0)

    def test_support_star_runs_through_left_bottom_region(self) -> None:
        start = _secondary_frame_light(0.0)["position"]
        mid = _secondary_frame_light(0.29)["position"]
        fade = _secondary_frame_light(0.58)["position"]
        self.assertLess(float(start[0]), float(mid[0]))
        self.assertLess(float(mid[0]), float(fade[0]))
        self.assertLess(float(start[1]), -0.5)
        self.assertAlmostEqual(float(start[1]), float(mid[1]), places=6)
        self.assertAlmostEqual(float(start[2]), float(mid[2]), places=6)

    def test_frame_lights_returns_main_star_plus_support_star(self) -> None:
        lights = _frame_lights(0.5)
        self.assertEqual(len(lights), 2)
        primary, support = lights
        self.assertGreater(float(primary["intensity"]), 0.0)
        self.assertGreaterEqual(float(support["intensity"]), 0.0)
        self.assertGreater(float(primary["color"][1]), 0.5)
        self.assertLessEqual(float(support["intensity"]), float(primary["intensity"]))

    def test_frame_lights_keep_support_star_low_and_primary_high(self) -> None:
        for phase in (0.0, 0.25, 0.5, 0.75, 1.0):
            primary, support = _frame_lights(phase)
            primary_position = primary["position"]
            self.assertAlmostEqual(float(primary_position[1]), 0.08, places=6)
            self.assertAlmostEqual(float(primary_position[2]), 11.8, places=6)
            support_position = support["position"]
            self.assertLess(float(support_position[1]), primary_position[1])
            self.assertLess(float(support_position[2]), primary_position[2])

    def test_overlay_star_skips_zero_alpha_support_light(self) -> None:
        width = 32
        height = 32
        image = [[_background_pixel(px, py, width, height) for px in range(width)] for py in range(height)]
        snapshot = [row[:] for row in image]
        _overlay_star_and_ground(
            image,
            light=_secondary_frame_light(0.75),
            eye=(0.0, 0.16, 6.1),
            target=(0.0, 0.08, 0.0),
            up_hint=(0.0, 1.0, 0.0),
            width=width,
            height=height,
            fov_y_degrees=28.0,
            center=(0.0, 0.08, 0.0),
            radius=1.46,
            show_light_source=True,
        )
        self.assertEqual(image, snapshot)

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

    def test_light_visibility_to_camera_is_soft_near_silhouette(self) -> None:
        eye = (0.0, 0.16, 6.1)
        center = (0.0, 0.08, 0.0)
        radius = 1.46
        hidden = _light_visibility_to_camera(
            light_position=(0.0, 0.08, -8.0),
            eye=eye,
            center=center,
            radius=radius,
        )
        grazing = _light_visibility_to_camera(
            light_position=(3.2, 0.25, -8.0),
            eye=eye,
            center=center,
            radius=radius,
        )
        visible = _light_visibility_to_camera(
            light_position=(5.0, 6.0, 6.0),
            eye=eye,
            center=center,
            radius=radius,
        )
        self.assertLess(hidden, 0.15)
        self.assertGreater(grazing, hidden)
        self.assertLess(grazing, 0.95)
        self.assertGreater(visible, 0.95)

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
            phase_mode="uniform",
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
        self.assertIsNone(frame["compare_backend"])
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
                    phase_mode="uniform",
                )
        self.assertEqual(summary["show_light_source"], show_light_source)
        persisted = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
        self.assertEqual(persisted["show_light_source"], show_light_source)

    def test_temporal_blend_round_trips_in_summary(self) -> None:
        output_dir = Path("build/goal166_orbiting_star_ball_demo_test/temporal_blend_summary")
        summary = render_orbiting_star_ball_frames(
            backend="cpu_python_reference",
            compare_backend=None,
            width=20,
            height=20,
            latitude_bands=6,
            longitude_bands=12,
            frame_count=2,
            output_dir=output_dir,
            temporal_blend_alpha=0.2,
            phase_mode="uniform",
        )
        self.assertAlmostEqual(summary["temporal_blend_alpha"], 0.2)
        self.assertEqual(summary["phase_mode"], "uniform")
        persisted = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
        self.assertAlmostEqual(persisted["temporal_blend_alpha"], 0.2)

    def test_summary_records_two_light_setup(self) -> None:
        output_dir = Path("build/goal166_orbiting_star_ball_demo_test/light_count")
        summary = render_orbiting_star_ball_frames(
            backend="cpu_python_reference",
            compare_backend=None,
            width=20,
            height=20,
            latitude_bands=6,
            longitude_bands=12,
            frame_count=1,
            output_dir=output_dir,
            phase_mode="uniform",
        )
        self.assertEqual(summary["light_count"], 2)
        persisted = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
        self.assertEqual(persisted["light_count"], 2)

    def test_fill_light_contributes_shadow_ray_work(self) -> None:
        output_dir = Path("build/goal166_orbiting_star_ball_demo_test/fill_shadow_rays")
        summary = render_orbiting_star_ball_frames(
            backend="cpu_python_reference",
            compare_backend=None,
            width=20,
            height=20,
            latitude_bands=6,
            longitude_bands=12,
            frame_count=1,
            output_dir=output_dir,
            phase_mode="uniform",
        )
        frame = summary["frames"][0]
        self.assertGreaterEqual(frame["shadow_rays"], frame["hit_pixels"] * 2)

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
            phase_mode="uniform",
        )
        frame_bytes = [Path(frame["frame_path"]).read_bytes() for frame in summary["frames"]]
        self.assertNotEqual(frame_bytes[0], frame_bytes[1])
        self.assertNotEqual(frame_bytes[1], frame_bytes[2])

    def test_compare_backend_summary_matches_reference(self) -> None:
        output_dir = Path("build/goal166_orbiting_star_ball_demo_test/compare_backend")
        summary = render_orbiting_star_ball_frames(
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
        compare_summary = summary["frames"][0]["compare_backend"]
        self.assertIsNotNone(compare_summary)
        self.assertEqual(compare_summary["backend"], "cpu_python_reference")
        self.assertTrue(compare_summary["matches"])

    def test_jobs_gt_one_render_produces_frames(self) -> None:
        output_dir = Path("build/goal166_orbiting_star_ball_demo_test/jobs_two")
        try:
            summary = render_orbiting_star_ball_frames(
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
        except PermissionError as exc:
            raise unittest.SkipTest(f"ProcessPoolExecutor unavailable in this environment: {exc}") from exc
        self.assertEqual(summary["jobs"], 2)
        for frame in summary["frames"]:
            self.assertTrue(Path(frame["frame_path"]).exists())

    def test_rerun_reuses_existing_raw_frame_checkpoint(self) -> None:
        output_dir = Path("build/goal166_orbiting_star_ball_demo_test/checkpoint_reuse")
        first = render_orbiting_star_ball_frames(
            backend="cpu_python_reference",
            compare_backend=None,
            width=20,
            height=20,
            latitude_bands=6,
            longitude_bands=12,
            frame_count=1,
            output_dir=output_dir,
            phase_mode="uniform",
        )
        raw_path = output_dir / "frame_000_raw.ppm"
        meta_path = output_dir / "frame_000.json"
        self.assertTrue(raw_path.exists())
        self.assertTrue(meta_path.exists())
        raw_mtime_before = raw_path.stat().st_mtime_ns
        time.sleep(0.01)
        second = render_orbiting_star_ball_frames(
            backend="cpu_python_reference",
            compare_backend=None,
            width=20,
            height=20,
            latitude_bands=6,
            longitude_bands=12,
            frame_count=1,
            output_dir=output_dir,
            phase_mode="uniform",
        )
        self.assertEqual(first["frames"][0]["frame_path"], second["frames"][0]["frame_path"])
        self.assertEqual(raw_mtime_before, raw_path.stat().st_mtime_ns)

    def test_numpy_and_scalar_shading_match_for_same_hit(self) -> None:
        if orbit_demo.np is None:
            self.skipTest("numpy unavailable")
        lights = (_frame_light(0.15),)
        center = (0.0, 0.08, 0.0)
        ray = rt.Ray3D(id=11, ox=0.0, oy=0.16, oz=6.1, dx=0.0, dy=-0.01, dz=-1.0, tmax=10.0)
        hit_point = (0.12, 0.55, 1.32)
        scalar = _shade_orbit_hit(
            ray,
            hit_point,
            center=center,
            lights=lights,
            shadow_lookup={},
            light_count=1,
        )
        image = orbit_demo.np.zeros((1, 1, 3), dtype=orbit_demo.np.uint8)
        _shade_pending_hits_numpy(
            image,
            pending_hits=[(0, 0, ray, hit_point)],
            center=center,
            lights=lights,
            shadow_lookup={},
            light_count=1,
        )
        self.assertEqual(tuple(int(v) for v in image[0, 0]), scalar)

    def test_vulkan_render_wrapper_uses_expected_backend(self) -> None:
        output_dir = Path("build/goal169_vulkan_orbit_wrapper")
        try:
            summary = render_orbiting_star_ball_vulkan_frames(
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

    def test_vulkan_backend_rows_match_reference_when_available(self) -> None:
        triangles = make_uv_sphere_mesh(
            latitude_bands=6,
            longitude_bands=12,
            radius=1.46,
            center=(0.0, 0.08, 0.0),
        )
        rays = make_camera_rays(
            width=12,
            height=12,
            eye=(0.0, 0.16, 6.1),
            target=(0.0, 0.08, 0.0),
            up_hint=(0.0, 1.0, 0.0),
            fov_y_degrees=28.0,
        )
        reference = _run_backend_rows("cpu_python_reference", rays=rays, triangles=triangles)
        try:
            rows = _run_backend_rows("vulkan", rays=rays, triangles=triangles)
        except Exception as exc:
            self.skipTest(f"vulkan unavailable: {exc}")
        self.assertEqual(rows, reference)

    def test_optix_4k_wrapper_exposes_expected_defaults(self) -> None:
        output_dir = Path("build/goal169_optix_4k_wrapper")
        try:
            summary = render_orbiting_star_ball_optix_4k(
                output_dir=output_dir,
                compare_backend=None,
                width=32,
                height=18,
                latitude_bands=8,
                longitude_bands=16,
                frame_count=1,
            )
        except Exception as exc:
            self.skipTest(f"optix unavailable: {exc}")
        self.assertEqual(summary["backend"], "optix")
        self.assertEqual(summary["image_width"], 32)
        self.assertEqual(summary["image_height"], 18)

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
