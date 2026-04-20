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


def _available(probe) -> bool:
    try:
        probe()
        return True
    except Exception:
        return False


class Goal639HiprtNativeAnyHitTest(unittest.TestCase):
    @unittest.skipUnless(_available(rt.hiprt_context_probe), "HIPRT backend is not available")
    def test_hiprt_exports_native_any_hit_symbols(self) -> None:
        self.assertIsNotNone(hiprt_runtime._hiprt_ray_anyhit_symbol(2))
        self.assertIsNotNone(hiprt_runtime._hiprt_ray_anyhit_symbol(3))

    @unittest.skipUnless(_available(rt.hiprt_context_probe), "HIPRT backend is not available")
    def test_hiprt_native_any_hit_2d_matches_cpu(self) -> None:
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
        self.assertEqual(rt.run_hiprt(any_hit_2d_kernel, **inputs), expected)
        self.assertEqual(
            hiprt_runtime.ray_triangle_any_hit_2d_hiprt(inputs["rays"], inputs["triangles"]),
            expected,
        )

    @unittest.skipUnless(_available(rt.hiprt_context_probe), "HIPRT backend is not available")
    def test_hiprt_native_any_hit_3d_matches_cpu(self) -> None:
        inputs = {
            "rays": (
                rt.Ray3D(id=1, ox=0.0, oy=0.0, oz=0.0, dx=10.0, dy=0.0, dz=0.0, tmax=1.0),
                rt.Ray3D(id=2, ox=0.0, oy=2.0, oz=0.0, dx=10.0, dy=0.0, dz=0.0, tmax=1.0),
            ),
            "triangles": (
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
            ),
        }

        expected = rt.run_cpu(any_hit_3d_kernel, **inputs)
        self.assertEqual(rt.run_hiprt(any_hit_3d_kernel, **inputs), expected)
        self.assertEqual(
            hiprt_runtime.ray_triangle_any_hit_3d_hiprt(inputs["rays"], inputs["triangles"]),
            expected,
        )


if __name__ == "__main__":
    unittest.main()
