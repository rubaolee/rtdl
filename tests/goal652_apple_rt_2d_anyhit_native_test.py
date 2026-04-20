from __future__ import annotations

import platform
import unittest

import rtdsl as rt
from rtdsl.apple_rt_runtime import _load_library


@rt.kernel(backend="rtdl", precision="float_approx")
def ray_triangle_any_hit_2d_kernel():
    rays = rt.input("rays", rt.Rays, layout=rt.Ray2DLayout, role="probe")
    triangles = rt.input("triangles", rt.Triangles, layout=rt.Triangle2DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_any_hit(exact=False))
    return rt.emit(hits, fields=["ray_id", "any_hit"])


def _apple_rt_anyhit_2d_available() -> bool:
    if platform.system() != "Darwin":
        return False
    try:
        rt.apple_rt_context_probe()
        return hasattr(_load_library(), "rtdl_apple_rt_run_ray_anyhit_2d")
    except Exception:
        return False


@unittest.skipUnless(
    _apple_rt_anyhit_2d_available(),
    "Apple RT 2D native any-hit symbol is not available in the loaded library",
)
class Goal652AppleRt2DAnyHitNativeTest(unittest.TestCase):
    def test_native_2d_anyhit_symbol_matches_cpu_dispatch(self) -> None:
        self.assertTrue(hasattr(_load_library(), "rtdl_apple_rt_run_ray_anyhit_2d"))
        case = {
            "rays": (
                rt.Ray2D(id=1, ox=-1.0, oy=0.5, dx=1.0, dy=0.0, tmax=4.0),
                rt.Ray2D(id=2, ox=-1.0, oy=1.5, dx=1.0, dy=0.0, tmax=4.0),
                rt.Ray2D(id=3, ox=4.0, oy=4.0, dx=1.0, dy=0.0, tmax=2.0),
            ),
            "triangles": (
                rt.Triangle(id=10, x0=0.0, y0=0.0, x1=2.0, y1=0.0, x2=0.0, y2=2.0),
                rt.Triangle(id=20, x0=1.0, y0=0.0, x1=3.0, y1=0.0, x2=1.0, y2=2.0),
            ),
        }
        self.assertEqual(
            rt.run_apple_rt(ray_triangle_any_hit_2d_kernel, native_only=True, **case),
            rt.run_cpu(ray_triangle_any_hit_2d_kernel, **case),
        )

    def test_native_2d_anyhit_handles_empty_build_side(self) -> None:
        case = {
            "rays": (
                rt.Ray2D(id=1, ox=-1.0, oy=0.5, dx=1.0, dy=0.0, tmax=4.0),
                rt.Ray2D(id=2, ox=4.0, oy=4.0, dx=1.0, dy=0.0, tmax=2.0),
            ),
            "triangles": (),
        }
        self.assertEqual(
            rt.run_apple_rt(ray_triangle_any_hit_2d_kernel, native_only=True, **case),
            rt.run_cpu(ray_triangle_any_hit_2d_kernel, **case),
        )


if __name__ == "__main__":
    unittest.main()
