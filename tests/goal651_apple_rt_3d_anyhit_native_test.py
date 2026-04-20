from __future__ import annotations

import platform
import unittest

import rtdsl as rt
from rtdsl.apple_rt_runtime import _load_library


@rt.kernel(backend="rtdl", precision="float_approx")
def ray_triangle_any_hit_3d_kernel():
    rays = rt.input("rays", rt.Rays3D, layout=rt.Ray3DLayout, role="probe")
    triangles = rt.input("triangles", rt.Triangles3D, layout=rt.Triangle3DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_any_hit(exact=False))
    return rt.emit(hits, fields=["ray_id", "any_hit"])


def _apple_rt_anyhit_3d_available() -> bool:
    if platform.system() != "Darwin":
        return False
    try:
        rt.apple_rt_context_probe()
        return hasattr(_load_library(), "rtdl_apple_rt_run_ray_anyhit_3d")
    except Exception:
        return False


@unittest.skipUnless(
    _apple_rt_anyhit_3d_available(),
    "Apple RT 3D native any-hit symbol is not available in the loaded library",
)
class Goal651AppleRt3DAnyHitNativeTest(unittest.TestCase):
    def test_native_3d_anyhit_symbol_matches_cpu_dispatch(self) -> None:
        self.assertTrue(hasattr(_load_library(), "rtdl_apple_rt_run_ray_anyhit_3d"))
        case = {
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
        self.assertEqual(
            rt.run_apple_rt(ray_triangle_any_hit_3d_kernel, native_only=True, **case),
            rt.run_cpu(ray_triangle_any_hit_3d_kernel, **case),
        )


if __name__ == "__main__":
    unittest.main()
