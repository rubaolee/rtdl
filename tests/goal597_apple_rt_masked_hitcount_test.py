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


def _triangle(triangle_id: int, x: float) -> rt.Triangle3D:
    return rt.Triangle3D(
        id=triangle_id,
        x0=x,
        y0=-1.0,
        z0=-1.0,
        x1=x,
        y1=1.0,
        z1=0.0,
        x2=x,
        y2=-1.0,
        z2=1.0,
    )


@unittest.skipUnless(apple_rt_available(), "Apple RT backend is not available")
class Goal597AppleRtMaskedHitcountTest(unittest.TestCase):
    def test_counts_stacked_same_distance_triangles(self) -> None:
        rays = (rt.Ray3D(id=1, ox=0.0, oy=0.0, oz=0.0, dx=1.0, dy=0.0, dz=0.0, tmax=2.0),)
        triangles = (_triangle(10, 0.5), _triangle(11, 0.5), _triangle(12, 1.0))
        actual = tuple(rt.ray_triangle_hit_count_apple_rt(rays, triangles))
        expected = rt.ray_triangle_hit_count_cpu(rays, triangles)
        self.assertEqual(actual, expected)
        self.assertEqual(actual[0]["hit_count"], 3)

    def test_counts_more_than_one_mask_chunk(self) -> None:
        rays = (
            rt.Ray3D(id=1, ox=0.0, oy=0.0, oz=0.0, dx=1.0, dy=0.0, dz=0.0, tmax=10.0),
            rt.Ray3D(id=2, ox=0.0, oy=4.0, oz=0.0, dx=1.0, dy=0.0, dz=0.0, tmax=10.0),
            rt.Ray3D(id=3, ox=0.0, oy=0.0, oz=0.0, dx=0.0, dy=0.0, dz=0.0, tmax=10.0),
        )
        triangles = tuple(_triangle(100 + index, 0.1 + index * 0.02) for index in range(40))
        actual = tuple(rt.ray_triangle_hit_count_apple_rt(rays, triangles))
        expected = rt.ray_triangle_hit_count_cpu(rays, triangles)
        self.assertEqual(actual, expected)
        self.assertEqual(actual[0]["hit_count"], 40)
        self.assertEqual(actual[1]["hit_count"], 0)
        self.assertEqual(actual[2]["hit_count"], 0)


if __name__ == "__main__":
    unittest.main()

