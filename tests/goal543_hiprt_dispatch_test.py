from __future__ import annotations

import unittest

import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def hiprt_ray_triangle_hitcount_kernel():
    rays = rt.input("rays", rt.Rays3D, layout=rt.Ray3DLayout, role="probe")
    triangles = rt.input("triangles", rt.Triangles3D, layout=rt.Triangle3DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_hit_count(exact=False))
    return rt.emit(hits, fields=["ray_id", "hit_count"])


@rt.kernel(backend="rtdl", precision="float_approx")
def unsupported_hiprt_2d_ray_triangle_kernel():
    rays = rt.input("rays", rt.Rays, layout=rt.Ray2DLayout, role="probe")
    triangles = rt.input("triangles", rt.Triangles, layout=rt.Triangle2DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_hit_count(exact=False))
    return rt.emit(hits, fields=["ray_id", "hit_count"])


@rt.kernel(backend="rtdl", precision="float_approx")
def unsupported_hiprt_mismatched_ray_triangle_kernel():
    rays = rt.input("rays", rt.Rays, layout=rt.Ray2DLayout, role="probe")
    triangles = rt.input("triangles", rt.Triangles3D, layout=rt.Triangle3DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_hit_count(exact=False))
    return rt.emit(hits, fields=["ray_id", "hit_count"])


def _hiprt_available() -> bool:
    try:
        rt.hiprt_version()
    except (FileNotFoundError, OSError, RuntimeError):
        return False
    return True


def _case():
    rays = (
        rt.Ray3D(id=1, ox=0.25, oy=0.25, oz=-1.0, dx=0.0, dy=0.0, dz=1.0, tmax=3.0),
        rt.Ray3D(id=2, ox=2.0, oy=2.0, oz=-1.0, dx=0.0, dy=0.0, dz=1.0, tmax=3.0),
        rt.Ray3D(id=3, ox=0.25, oy=0.25, oz=-1.0, dx=0.0, dy=0.0, dz=1.0, tmax=0.5),
    )
    triangles = (
        rt.Triangle3D(id=10, x0=0.0, y0=0.0, z0=0.0, x1=1.0, y1=0.0, z1=0.0, x2=0.0, y2=1.0, z2=0.0),
        rt.Triangle3D(id=11, x0=0.0, y0=0.0, z0=1.0, x1=1.0, y1=0.0, z1=1.0, x2=0.0, y2=1.0, z2=1.0),
    )
    return rays, triangles


class Goal543HiprtDispatchLocalValidationTest(unittest.TestCase):
    def test_run_hiprt_rejects_mismatched_shape_before_loading_backend(self) -> None:
        with self.assertRaisesRegex(NotImplementedError, "matching Ray2D/Triangle2D or Ray3D/Triangle3D"):
            rt.run_hiprt(unsupported_hiprt_mismatched_ray_triangle_kernel, rays=(), triangles=())

    def test_prepare_hiprt_requires_build_triangles_only(self) -> None:
        rays, triangles = _case()
        with self.assertRaisesRegex(ValueError, "pass query rays later"):
            rt.prepare_hiprt(hiprt_ray_triangle_hitcount_kernel, rays=rays, triangles=triangles)


@unittest.skipUnless(_hiprt_available(), "RTDL HIPRT backend library is not available")
class Goal543HiprtDispatchBackendTest(unittest.TestCase):
    def test_run_hiprt_matches_cpu_oracle(self) -> None:
        rays, triangles = _case()
        self.assertEqual(
            rt.run_hiprt(hiprt_ray_triangle_hitcount_kernel, rays=rays, triangles=triangles),
            rt.run_cpu_python_reference(hiprt_ray_triangle_hitcount_kernel, rays=rays, triangles=triangles),
        )

    def test_prepare_hiprt_matches_cpu_oracle_across_query_batches(self) -> None:
        rays, triangles = _case()
        rays_b = (
            rt.Ray3D(id=4, ox=0.75, oy=0.05, oz=-1.0, dx=0.0, dy=0.0, dz=1.0, tmax=2.0),
            rt.Ray3D(id=5, ox=3.0, oy=3.0, oz=-1.0, dx=0.0, dy=0.0, dz=1.0, tmax=2.0),
        )
        with rt.prepare_hiprt(hiprt_ray_triangle_hitcount_kernel, triangles=triangles) as prepared:
            self.assertEqual(
                prepared.run(rays=rays),
                rt.run_cpu_python_reference(hiprt_ray_triangle_hitcount_kernel, rays=rays, triangles=triangles),
            )
            self.assertEqual(
                prepared.run(rays=rays_b),
                rt.run_cpu_python_reference(hiprt_ray_triangle_hitcount_kernel, rays=rays_b, triangles=triangles),
            )


if __name__ == "__main__":
    unittest.main()
