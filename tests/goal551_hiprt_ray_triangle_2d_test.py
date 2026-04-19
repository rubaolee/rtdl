from __future__ import annotations

import unittest

import rtdsl as rt
from rtdsl.hiprt_runtime import hiprt_context_probe
from rtdsl.hiprt_runtime import ray_triangle_hit_count_2d_hiprt


@rt.kernel(backend="rtdl", precision="float_approx")
def ray_triangle_2d_kernel():
    rays = rt.input("rays", rt.Rays, layout=rt.Ray2DLayout, role="probe")
    triangles = rt.input("triangles", rt.Triangles, layout=rt.Triangle2DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_hit_count(exact=False))
    return rt.emit(hits, fields=["ray_id", "hit_count"])


def hiprt_available() -> bool:
    try:
        hiprt_context_probe()
        return True
    except Exception:
        return False


@unittest.skipUnless(hiprt_available(), "HIPRT runtime is not available")
class Goal551HiprtRayTriangle2DTest(unittest.TestCase):
    def _case(self) -> dict[str, tuple[object, ...]]:
        return {
            "rays": (
                rt.Ray2D(id=1, ox=0.0, oy=0.0, dx=1.0, dy=0.0, tmax=5.0),
                rt.Ray2D(id=2, ox=0.5, oy=0.5, dx=1.0, dy=0.0, tmax=1.0),
                rt.Ray2D(id=3, ox=4.0, oy=4.0, dx=1.0, dy=0.0, tmax=1.0),
            ),
            "triangles": (
                rt.Triangle(id=10, x0=2.0, y0=-1.0, x1=3.0, y1=1.0, x2=4.0, y2=-1.0),
                rt.Triangle(id=20, x0=0.0, y0=0.0, x1=1.0, y1=0.0, x2=0.0, y2=1.0),
                rt.Triangle(id=30, x0=10.0, y0=10.0, x1=11.0, y1=10.0, x2=10.0, y2=11.0),
            ),
        }

    def test_direct_helper_matches_cpu_reference(self) -> None:
        case = self._case()
        self.assertEqual(
            ray_triangle_hit_count_2d_hiprt(case["rays"], case["triangles"]),
            rt.run_cpu_python_reference(ray_triangle_2d_kernel, **case),
        )

    def test_run_hiprt_matches_cpu_reference(self) -> None:
        case = self._case()
        self.assertEqual(
            rt.run_hiprt(ray_triangle_2d_kernel, **case),
            rt.run_cpu_python_reference(ray_triangle_2d_kernel, **case),
        )

    def test_empty_triangles_emit_zero_counts(self) -> None:
        rays = self._case()["rays"]
        self.assertEqual(
            rt.run_hiprt(ray_triangle_2d_kernel, rays=rays, triangles=()),
            tuple({"ray_id": ray.id, "hit_count": 0} for ray in rays),
        )


if __name__ == "__main__":
    unittest.main()
