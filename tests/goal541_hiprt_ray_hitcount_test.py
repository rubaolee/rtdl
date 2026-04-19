from __future__ import annotations

import unittest

import rtdsl as rt


def _hiprt_available() -> bool:
    try:
        rt.hiprt_version()
    except (FileNotFoundError, OSError, RuntimeError):
        return False
    return True


@unittest.skipUnless(_hiprt_available(), "RTDL HIPRT backend library is not available")
class Goal541HiprtRayHitcountTest(unittest.TestCase):
    def test_hiprt_ray_triangle_hitcount_3d_matches_cpu_oracle(self) -> None:
        rays = (
            rt.Ray3D(id=1, ox=0.25, oy=0.25, oz=-1.0, dx=0.0, dy=0.0, dz=1.0, tmax=3.0),
            rt.Ray3D(id=2, ox=2.0, oy=2.0, oz=-1.0, dx=0.0, dy=0.0, dz=1.0, tmax=3.0),
            rt.Ray3D(id=3, ox=0.25, oy=0.25, oz=-1.0, dx=0.0, dy=0.0, dz=1.0, tmax=0.5),
        )
        triangles = (
            rt.Triangle3D(id=10, x0=0.0, y0=0.0, z0=0.0, x1=1.0, y1=0.0, z1=0.0, x2=0.0, y2=1.0, z2=0.0),
            rt.Triangle3D(id=11, x0=0.0, y0=0.0, z0=1.0, x1=1.0, y1=0.0, z1=1.0, x2=0.0, y2=1.0, z2=1.0),
        )

        self.assertEqual(
            rt.ray_triangle_hit_count_hiprt(rays, triangles),
            rt.ray_triangle_hit_count_cpu(rays, triangles),
        )

    def test_hiprt_ray_triangle_hitcount_rejects_2d_inputs(self) -> None:
        rays = (rt.Ray2D(id=1, ox=0.0, oy=0.0, dx=1.0, dy=0.0, tmax=1.0),)
        triangles = (rt.Triangle(id=1, x0=0.0, y0=0.0, x1=1.0, y1=0.0, x2=0.0, y2=1.0),)
        with self.assertRaisesRegex(TypeError, "Ray3D"):
            rt.ray_triangle_hit_count_hiprt(rays, triangles)  # type: ignore[arg-type]

    def test_prepared_hiprt_ray_triangle_hitcount_reuses_triangle_build(self) -> None:
        triangles = (
            rt.Triangle3D(id=20, x0=0.0, y0=0.0, z0=0.0, x1=1.0, y1=0.0, z1=0.0, x2=0.0, y2=1.0, z2=0.0),
            rt.Triangle3D(id=21, x0=0.0, y0=0.0, z0=1.0, x1=1.0, y1=0.0, z1=1.0, x2=0.0, y2=1.0, z2=1.0),
        )
        rays_a = (
            rt.Ray3D(id=1, ox=0.25, oy=0.25, oz=-1.0, dx=0.0, dy=0.0, dz=1.0, tmax=3.0),
            rt.Ray3D(id=2, ox=2.0, oy=2.0, oz=-1.0, dx=0.0, dy=0.0, dz=1.0, tmax=3.0),
        )
        rays_b = (
            rt.Ray3D(id=3, ox=0.25, oy=0.25, oz=-1.0, dx=0.0, dy=0.0, dz=1.0, tmax=0.5),
            rt.Ray3D(id=4, ox=0.75, oy=0.05, oz=-1.0, dx=0.0, dy=0.0, dz=1.0, tmax=2.0),
        )
        with rt.prepare_hiprt_ray_triangle_hit_count(triangles) as prepared:
            self.assertEqual(prepared.run(rays_a), rt.ray_triangle_hit_count_cpu(rays_a, triangles))
            self.assertEqual(prepared.run(rays_b), rt.ray_triangle_hit_count_cpu(rays_b, triangles))


if __name__ == "__main__":
    unittest.main()
