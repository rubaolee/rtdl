from __future__ import annotations

import unittest

import rtdsl as rt
from rtdsl import hiprt_runtime


@rt.kernel(backend="rtdl", precision="float_approx")
def any_hit_2d_kernel():
    rays = rt.input("rays", rt.Rays, layout=rt.Ray2DLayout, role="probe")
    triangles = rt.input("triangles", rt.Triangles, layout=rt.Triangle2DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_any_hit(exact=False))
    return rt.emit(hits, fields=["ray_id", "any_hit"])


@rt.kernel(backend="rtdl", precision="float_approx")
def any_hit_3d_kernel():
    rays = rt.input("rays", rt.Rays3D, layout=rt.Ray3DLayout, role="probe")
    triangles = rt.input("triangles", rt.Triangles3D, layout=rt.Triangle3DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_any_hit(exact=False))
    return rt.emit(hits, fields=["ray_id", "any_hit"])


def _hiprt_prepared_anyhit_available() -> bool:
    try:
        rt.hiprt_context_probe()
        return hiprt_runtime._hiprt_prepared_ray_anyhit_2d_symbols_available()
    except Exception:
        return False


class Goal674HiprtPreparedAnyHit2DPortableTest(unittest.TestCase):
    def test_empty_prepared_scene_runs_without_native_symbols(self) -> None:
        rays = (
            rt.Ray2D(id=1, ox=0.0, oy=0.0, dx=1.0, dy=0.0, tmax=10.0),
            rt.Ray2D(id=2, ox=0.0, oy=0.0, dx=0.0, dy=1.0, tmax=10.0),
        )
        with rt.prepare_hiprt_ray_triangle_any_hit_2d(()) as prepared:
            self.assertEqual(
                prepared.run(rays),
                ({"ray_id": 1, "any_hit": 0}, {"ray_id": 2, "any_hit": 0}),
            )

    def test_prepared_anyhit_rejects_3d_rays_portably(self) -> None:
        rays = (rt.Ray3D(id=1, ox=0.0, oy=0.0, oz=0.0, dx=1.0, dy=0.0, dz=0.0, tmax=1.0),)
        with rt.prepare_hiprt_ray_triangle_any_hit_2d(()) as prepared:
            with self.assertRaisesRegex(TypeError, "Ray2D"):
                prepared.run(rays)

    def test_closed_empty_prepared_scene_is_rejected(self) -> None:
        rays = (rt.Ray2D(id=1, ox=0.0, oy=0.0, dx=1.0, dy=0.0, tmax=10.0),)
        prepared = rt.prepare_hiprt_ray_triangle_any_hit_2d(())
        prepared.close()
        with self.assertRaisesRegex(RuntimeError, "closed"):
            prepared.run(rays)


@unittest.skipUnless(_hiprt_prepared_anyhit_available(), "current HIPRT prepared 2D any-hit symbols are not available")
class Goal674HiprtPreparedAnyHit2DNativeTest(unittest.TestCase):
    def test_prepared_2d_anyhit_matches_cpu_and_direct_hiprt(self) -> None:
        inputs = {
            "rays": (
                rt.Ray2D(id=1, ox=-1.0, oy=0.5, dx=1.0, dy=0.0, tmax=4.0),
                rt.Ray2D(id=2, ox=-1.0, oy=1.5, dx=1.0, dy=0.0, tmax=4.0),
                rt.Ray2D(id=3, ox=4.0, oy=4.0, dx=1.0, dy=0.0, tmax=1.0),
            ),
            "triangles": (
                rt.Triangle(id=10, x0=0.0, y0=0.0, x1=2.0, y1=0.0, x2=0.0, y2=2.0),
                rt.Triangle(id=20, x0=1.0, y0=0.25, x1=3.0, y1=0.25, x2=1.0, y2=1.25),
            ),
        }

        expected = rt.run_cpu(any_hit_2d_kernel, **inputs)
        with rt.prepare_hiprt_ray_triangle_any_hit_2d(inputs["triangles"]) as prepared:
            self.assertEqual(prepared.run(inputs["rays"]), expected)
        with rt.prepare_hiprt(any_hit_2d_kernel, triangles=inputs["triangles"]) as prepared_kernel:
            self.assertEqual(prepared_kernel.run(rays=inputs["rays"]), expected)
        self.assertEqual(rt.run_hiprt(any_hit_2d_kernel, **inputs), expected)

    def test_prepared_2d_anyhit_reuses_scene_for_multiple_ray_batches(self) -> None:
        triangles = (
            rt.Triangle(id=10, x0=0.0, y0=0.0, x1=2.0, y1=0.0, x2=0.0, y2=2.0),
        )
        rays_a = (rt.Ray2D(id=1, ox=-1.0, oy=0.5, dx=1.0, dy=0.0, tmax=4.0),)
        rays_b = (rt.Ray2D(id=2, ox=-1.0, oy=3.0, dx=1.0, dy=0.0, tmax=4.0),)

        with rt.prepare_hiprt(any_hit_2d_kernel, triangles=triangles) as prepared:
            self.assertEqual(prepared.run(rays=rays_a), rt.run_cpu(any_hit_2d_kernel, rays=rays_a, triangles=triangles))
            self.assertEqual(prepared.run(rays=rays_b), rt.run_cpu(any_hit_2d_kernel, rays=rays_b, triangles=triangles))

    def test_prepared_3d_anyhit_is_explicitly_not_claimed(self) -> None:
        triangles = (
            rt.Triangle3D(
                id=20,
                x0=5.0,
                y0=-1.0,
                z0=-1.0,
                x1=5.0,
                y1=1.0,
                z1=-1.0,
                x2=5.0,
                y2=0.0,
                z2=1.0,
            ),
        )
        with self.assertRaisesRegex(Exception, "Ray2D/Triangle2D any-hit"):
            rt.prepare_hiprt(any_hit_3d_kernel, triangles=triangles)


if __name__ == "__main__":
    unittest.main()
