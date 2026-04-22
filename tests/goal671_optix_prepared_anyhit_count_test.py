from __future__ import annotations

import unittest

import rtdsl as rt
from rtdsl.optix_runtime import _find_optional_backend_symbol
from rtdsl.optix_runtime import _load_optix_library


def optix_prepared_anyhit_available() -> bool:
    try:
        lib = _load_optix_library()
    except Exception:
        return False
    return (
        _find_optional_backend_symbol(lib, "rtdl_optix_prepare_ray_anyhit_2d") is not None
        and _find_optional_backend_symbol(lib, "rtdl_optix_count_prepared_ray_anyhit_2d") is not None
        and _find_optional_backend_symbol(lib, "rtdl_optix_destroy_prepared_ray_anyhit_2d") is not None
    )


def optix_prepared_packed_anyhit_available() -> bool:
    try:
        lib = _load_optix_library()
    except Exception:
        return False
    return (
        optix_prepared_anyhit_available()
        and _find_optional_backend_symbol(lib, "rtdl_optix_prepare_rays_2d") is not None
        and _find_optional_backend_symbol(lib, "rtdl_optix_count_prepared_ray_anyhit_2d_packed") is not None
        and _find_optional_backend_symbol(lib, "rtdl_optix_destroy_prepared_rays_2d") is not None
    )


def optix_prepared_pose_flags_available() -> bool:
    try:
        lib = _load_optix_library()
    except Exception:
        return False
    return (
        optix_prepared_packed_anyhit_available()
        and _find_optional_backend_symbol(lib, "rtdl_optix_pose_flags_prepared_ray_anyhit_2d_packed") is not None
    )


class Goal671OptixPreparedAnyHitCountPortableTest(unittest.TestCase):
    def test_empty_prepared_scene_counts_zero_without_native_library(self) -> None:
        prepared = rt.prepare_optix_ray_triangle_any_hit_2d(())
        try:
            rays = (
                rt.Ray2D(id=1, ox=0.0, oy=0.0, dx=1.0, dy=0.0, tmax=10.0),
                rt.Ray2D(id=2, ox=0.0, oy=0.0, dx=0.0, dy=1.0, tmax=10.0),
            )
            self.assertEqual(prepared.count(rays), 0)
        finally:
            prepared.close()

    def test_context_manager_is_supported_for_empty_scene(self) -> None:
        with rt.prepare_optix_ray_triangle_any_hit_2d(()) as prepared:
            self.assertEqual(prepared.count(()), 0)

    def test_prepared_count_rejects_3d_rays(self) -> None:
        prepared = rt.prepare_optix_ray_triangle_any_hit_2d(())
        try:
            rays = (rt.Ray3D(id=1, ox=0.0, oy=0.0, oz=0.0, dx=1.0, dy=0.0, dz=0.0, tmax=1.0),)
            with self.assertRaisesRegex(ValueError, "2D ray|2-D rays"):
                prepared.count(rays)
        finally:
            prepared.close()

    def test_empty_prepared_ray_buffer_counts_zero_without_native_library(self) -> None:
        with rt.prepare_optix_rays_2d(()) as rays:
            with rt.prepare_optix_ray_triangle_any_hit_2d(()) as prepared:
                self.assertEqual(prepared.count_packed(rays), 0)

    def test_closed_prepared_ray_buffer_is_rejected(self) -> None:
        rays = rt.prepare_optix_rays_2d(())
        rays.close()
        with rt.prepare_optix_ray_triangle_any_hit_2d(()) as prepared:
            with self.assertRaisesRegex(RuntimeError, "ray buffer is closed"):
                prepared.count_packed(rays)

    def test_empty_prepared_pose_flags_do_not_need_native_library(self) -> None:
        with rt.prepare_optix_rays_2d(()) as rays:
            with rt.prepare_optix_ray_triangle_any_hit_2d(()) as prepared:
                self.assertEqual(prepared.pose_flags_packed(rays, (), pose_count=3), (False, False, False))

    def test_prepared_pose_flags_rejects_bad_pose_index_length(self) -> None:
        with rt.prepare_optix_rays_2d(()) as rays:
            with rt.prepare_optix_ray_triangle_any_hit_2d(()) as prepared:
                with self.assertRaisesRegex(ValueError, "pose_indices length"):
                    prepared.pose_flags_packed(rays, (0,), pose_count=1)


@unittest.skipUnless(optix_prepared_anyhit_available(), "current OptiX prepared any-hit symbols are not available")
class Goal671OptixPreparedAnyHitCountNativeTest(unittest.TestCase):
    def test_prepared_anyhit_count_matches_cpu_anyhit_rows(self) -> None:
        triangles = (
            rt.Triangle(id=10, x0=2.0, y0=-1.0, x1=3.0, y1=1.0, x2=4.0, y2=-1.0),
            rt.Triangle(id=11, x0=0.0, y0=3.0, x1=1.0, y1=4.0, x2=-1.0, y2=4.0),
        )
        rays = (
            rt.Ray2D(id=1, ox=0.0, oy=0.0, dx=1.0, dy=0.0, tmax=10.0),
            rt.Ray2D(id=2, ox=0.0, oy=0.0, dx=0.0, dy=1.0, tmax=2.0),
            rt.Ray2D(id=3, ox=0.0, oy=0.0, dx=0.0, dy=1.0, tmax=10.0),
        )
        expected = sum(1 for row in rt.ray_triangle_any_hit_cpu(rays, triangles) if row["any_hit"])
        with rt.prepare_optix_ray_triangle_any_hit_2d(triangles) as prepared:
            self.assertEqual(prepared.count(rays), expected)

    def test_prepared_anyhit_count_matches_cpu_for_short_rays(self) -> None:
        triangles = (
            rt.Triangle(id=10, x0=-0.1, y0=0.1, x1=0.1, y1=0.1, x2=0.0, y2=0.2),
        )
        rays = (
            rt.Ray2D(id=1, ox=0.0, oy=0.0, dx=0.0, dy=0.25, tmax=1.0),
            rt.Ray2D(id=2, ox=1.0, oy=0.0, dx=0.0, dy=0.25, tmax=1.0),
        )
        expected = sum(1 for row in rt.ray_triangle_any_hit_cpu(rays, triangles) if row["any_hit"])
        self.assertEqual(expected, 1)
        with rt.prepare_optix_ray_triangle_any_hit_2d(triangles) as prepared:
            self.assertEqual(prepared.count(rays), expected)


@unittest.skipUnless(optix_prepared_packed_anyhit_available(), "current OptiX packed prepared any-hit symbols are not available")
class Goal672OptixPreparedAnyHitPackedCountNativeTest(unittest.TestCase):
    def test_packed_prepared_anyhit_count_matches_unpacked_count(self) -> None:
        triangles = (
            rt.Triangle(id=10, x0=2.0, y0=-1.0, x1=3.0, y1=1.0, x2=4.0, y2=-1.0),
            rt.Triangle(id=11, x0=0.0, y0=3.0, x1=1.0, y1=4.0, x2=-1.0, y2=4.0),
        )
        rays = (
            rt.Ray2D(id=1, ox=0.0, oy=0.0, dx=1.0, dy=0.0, tmax=10.0),
            rt.Ray2D(id=2, ox=0.0, oy=0.0, dx=0.0, dy=1.0, tmax=2.0),
            rt.Ray2D(id=3, ox=0.0, oy=0.0, dx=0.0, dy=1.0, tmax=10.0),
        )
        with rt.prepare_optix_ray_triangle_any_hit_2d(triangles) as prepared:
            with rt.prepare_optix_rays_2d(rays) as packed_rays:
                self.assertEqual(prepared.count_packed(packed_rays), prepared.count(rays))
                self.assertEqual(prepared.count(packed_rays), prepared.count(rays))


@unittest.skipUnless(optix_prepared_pose_flags_available(), "current OptiX packed pose-flag any-hit symbols are not available")
class Goal753OptixPreparedAnyHitPoseFlagsNativeTest(unittest.TestCase):
    def test_packed_prepared_pose_flags_match_cpu_anyhit_rows(self) -> None:
        triangles = (
            rt.Triangle(id=10, x0=-0.1, y0=0.1, x1=0.1, y1=0.1, x2=0.0, y2=0.2),
        )
        rays = (
            rt.Ray2D(id=1000, ox=0.0, oy=0.0, dx=0.0, dy=0.25, tmax=1.0),
            rt.Ray2D(id=1001, ox=1.0, oy=0.0, dx=0.0, dy=0.25, tmax=1.0),
            rt.Ray2D(id=2000, ox=2.0, oy=0.0, dx=0.0, dy=0.25, tmax=1.0),
        )
        pose_indices = (0, 0, 1)
        expected_rows = tuple(rt.ray_triangle_any_hit_cpu(rays, triangles))
        expected = (
            any(bool(row["any_hit"]) for row in expected_rows[:2]),
            bool(expected_rows[2]["any_hit"]),
        )
        self.assertEqual(expected, (True, False))
        with rt.prepare_optix_ray_triangle_any_hit_2d(triangles) as prepared:
            with rt.prepare_optix_rays_2d(rays) as packed_rays:
                self.assertEqual(prepared.pose_flags_packed(packed_rays, pose_indices, pose_count=2), expected)


if __name__ == "__main__":
    unittest.main()
