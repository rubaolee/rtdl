from __future__ import annotations

import platform
import unittest

import rtdsl as rt


def apple_rt_available() -> bool:
    if platform.system() != "Darwin":
        return False
    try:
        rt.apple_rt_context_probe()
        return True
    except Exception:
        return False


@rt.kernel(backend="rtdl", precision="float_approx")
def ray_triangle_hit_count_2d_kernel():
    rays = rt.input("rays", rt.Rays, layout=rt.Ray2DLayout, role="probe")
    triangles = rt.input("triangles", rt.Triangles, layout=rt.Triangle2DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_hit_count(exact=False))
    return rt.emit(hits, fields=["ray_id", "hit_count"])


@unittest.skipUnless(apple_rt_available(), "Apple RT backend is not available")
class Goal604AppleRtRayHitCount2DNativeTest(unittest.TestCase):
    def _case(self) -> dict[str, tuple[object, ...]]:
        return {
            "rays": (
                rt.Ray2D(id=1, ox=-1.0, oy=0.5, dx=1.0, dy=0.0, tmax=4.0),
                rt.Ray2D(id=2, ox=0.25, oy=0.25, dx=0.2, dy=0.1, tmax=1.0),
                rt.Ray2D(id=3, ox=4.0, oy=4.0, dx=1.0, dy=0.0, tmax=1.0),
                rt.Ray2D(id=4, ox=2.5, oy=0.5, dx=1.0, dy=0.0, tmax=0.2),
            ),
            "triangles": (
                rt.Triangle(id=10, x0=0.0, y0=0.0, x1=2.0, y1=0.0, x2=0.0, y2=2.0),
                rt.Triangle(id=20, x0=2.0, y0=0.0, x1=3.0, y1=0.0, x2=2.0, y2=1.0),
                rt.Triangle(id=30, x0=10.0, y0=10.0, x1=11.0, y1=10.0, x2=10.0, y2=11.0),
            ),
        }

    def test_run_apple_rt_2d_hitcount_native_only_matches_cpu(self) -> None:
        case = self._case()
        actual = rt.run_apple_rt(ray_triangle_hit_count_2d_kernel, native_only=True, **case)
        expected = rt.run_cpu_python_reference(ray_triangle_hit_count_2d_kernel, **case)
        self.assertEqual(actual, expected)

    def test_direct_2d_hitcount_helper_matches_cpu(self) -> None:
        case = self._case()
        actual = tuple(rt.ray_triangle_hit_count_apple_rt(case["rays"], case["triangles"]))
        expected = rt.ray_triangle_hit_count_cpu(case["rays"], case["triangles"])
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
