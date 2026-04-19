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


@unittest.skipUnless(apple_rt_available(), "Apple RT backend is not available")
class Goal596AppleRtPreparedClosestHitTest(unittest.TestCase):
    def test_prepared_api_is_public_and_matches_direct_helper(self) -> None:
        rays = (
            rt.Ray3D(id=1, ox=-1.0, oy=0.0, oz=0.0, dx=1.0, dy=0.0, dz=0.0, tmax=3.0),
            rt.Ray3D(id=2, ox=-1.0, oy=5.0, oz=0.0, dx=1.0, dy=0.0, dz=0.0, tmax=3.0),
        )
        triangles = (
            rt.Triangle3D(id=10, x0=0.5, y0=-1.0, z0=-1.0, x1=0.5, y1=1.0, z1=0.0, x2=0.5, y2=-1.0, z2=1.0),
            rt.Triangle3D(id=11, x0=0.25, y0=-1.0, z0=-1.0, x1=0.25, y1=1.0, z1=0.0, x2=0.25, y2=-1.0, z2=1.0),
        )
        with rt.prepare_apple_rt_ray_triangle_closest_hit(triangles) as prepared:
            prepared_rows = tuple(prepared.run(rays))
        direct_rows = tuple(rt.ray_triangle_closest_hit_apple_rt(rays, triangles))
        self.assertEqual(prepared_rows, direct_rows)


if __name__ == "__main__":
    unittest.main()
