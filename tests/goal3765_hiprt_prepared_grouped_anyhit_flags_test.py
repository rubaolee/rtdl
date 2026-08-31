from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt
from examples.current.apps.robotics import rtdl_robot_collision_screening_app as robot_app
from rtdsl import hiprt_runtime


def _hiprt_grouped_flags_available() -> bool:
    try:
        rt.hiprt_context_probe()
        lib = hiprt_runtime._hiprt_lib()
    except Exception:
        return False
    return (
        getattr(lib, "rtdl_hiprt_prepare_ray_anyhit_2d", None) is not None
        and getattr(lib, "rtdl_hiprt_group_flags_prepared_ray_anyhit_2d_packed", None) is not None
        and getattr(lib, "rtdl_hiprt_destroy_prepared_ray_anyhit_2d", None) is not None
    )


class Goal3765HiprtPreparedGroupedAnyhitFlagsPortableTest(unittest.TestCase):
    def test_report_records_boundary_and_artifact(self) -> None:
        root = Path(__file__).resolve().parents[1]
        report = root / "docs/reports/goal3765_hiprt_prepared_grouped_anyhit_flags_2026-06-07.md"
        text = report.read_text(encoding="utf-8")
        self.assertIn("rtdl_hiprt_group_flags_prepared_ray_anyhit_2d_packed", text)
        self.assertIn("goal3765_robot_collision_hiprt_prepared_group_flags_a5000.json", text)
        self.assertIn("not AMD hardware evidence", text)
        self.assertIn("does not authorize", text)

    def test_empty_scene_group_flags_work_without_native_grouped_symbol(self) -> None:
        rays = (
            rt.Ray2D(id=10, ox=0.0, oy=0.0, dx=1.0, dy=0.0, tmax=1.0),
            rt.Ray2D(id=11, ox=0.0, oy=1.0, dx=1.0, dy=0.0, tmax=1.0),
        )
        with rt.prepare_hiprt_ray_triangle_any_hit_2d(()) as prepared_scene:
            with rt.prepare_hiprt_rays_2d(rays) as prepared_rays:
                self.assertEqual(
                    prepared_scene.group_flags_packed(prepared_rays, (0, 1), group_count=2),
                    (False, False),
                )

    def test_robot_app_rejects_unsupported_prepared_summary_backend(self) -> None:
        with self.assertRaisesRegex(ValueError, "prepared_pose_flags"):
            robot_app.run_app("cpu", optix_summary_mode="prepared_pose_flags")

    def test_hiprt_prepared_count_is_not_implied_by_group_flags(self) -> None:
        with self.assertRaisesRegex(ValueError, "count is not available"):
            rt.run_generic_prepared_ray_triangle_any_hit_count(
                triangles=(),
                rays=(),
                backend="hiprt",
                prepare_scene=rt.prepare_hiprt_ray_triangle_any_hit_2d,
                prepare_rays=rt.prepare_hiprt_rays_2d,
            )

    def test_native_hiprt_grouped_symbol_is_app_agnostic(self) -> None:
        root = Path(__file__).resolve().parents[1]
        native_text = "\n".join(
            (root / path).read_text(encoding="utf-8")
            for path in (
                "src/native/hiprt/rtdl_hiprt_api.cpp",
                "src/native/hiprt/rtdl_hiprt_core.cpp",
                "src/native/hiprt/rtdl_hiprt_kernels.cpp",
            )
        )
        self.assertIn("rtdl_hiprt_group_flags_prepared_ray_anyhit_2d_packed", native_text)
        self.assertIn("RtdlGroupedRayAnyhit2DKernel", native_text)
        self.assertNotIn("robot", native_text.lower())
        self.assertNotIn("pose_flags", native_text)


@unittest.skipUnless(_hiprt_grouped_flags_available(), "HIPRT grouped any-hit flags are not available")
class Goal3765HiprtPreparedGroupedAnyhitFlagsNativeTest(unittest.TestCase):
    def test_group_flags_match_cpu_oracle(self) -> None:
        triangles = (
            rt.Triangle(id=10, x0=0.0, y0=0.0, x1=2.0, y1=0.0, x2=0.0, y2=2.0),
            rt.Triangle(id=20, x0=4.0, y0=4.0, x1=5.0, y1=4.0, x2=4.0, y2=5.0),
        )
        rays = (
            rt.Ray2D(id=1, ox=-1.0, oy=0.5, dx=1.0, dy=0.0, tmax=4.0),
            rt.Ray2D(id=2, ox=-1.0, oy=3.0, dx=1.0, dy=0.0, tmax=4.0),
            rt.Ray2D(id=3, ox=3.5, oy=4.25, dx=1.0, dy=0.0, tmax=2.0),
            rt.Ray2D(id=4, ox=6.0, oy=6.0, dx=1.0, dy=0.0, tmax=1.0),
        )
        group_indices = (0, 0, 1, 1)
        cpu_rows = rt.ray_triangle_any_hit_cpu(rays, triangles)
        expected = [False, False]
        for row, group in zip(cpu_rows, group_indices):
            expected[group] = expected[group] or bool(row["any_hit"])

        with rt.prepare_hiprt_ray_triangle_any_hit_2d(triangles) as prepared_scene:
            with rt.prepare_hiprt_rays_2d(rays) as prepared_rays:
                self.assertEqual(
                    prepared_scene.group_flags_packed(prepared_rays, group_indices, group_count=2),
                    tuple(expected),
                )

    def test_robot_app_hiprt_prepared_pose_flags_match_oracle(self) -> None:
        payload = robot_app.run_app(
            "hiprt",
            optix_summary_mode="prepared_pose_flags",
            output_mode="pose_flags",
            pose_count=32,
            obstacle_count=32,
            skip_validation=False,
        )
        self.assertTrue(payload["native_continuation_active"])
        self.assertEqual(payload["native_continuation_backend"], "hiprt_prepared_pose_flags")
        self.assertTrue(payload["matches_oracle"])
        self.assertEqual(
            payload["prepared_summary"]["colliding_pose_count"],
            len(payload["prepared_summary"]["colliding_pose_ids"]),
        )


if __name__ == "__main__":
    unittest.main()
