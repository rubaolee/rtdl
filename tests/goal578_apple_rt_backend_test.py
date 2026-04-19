from __future__ import annotations

import platform
import unittest

import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def ray_triangle_closest_hit_3d_kernel():
    rays = rt.input("rays", rt.Rays, layout=rt.Ray3DLayout, role="probe")
    triangles = rt.input("triangles", rt.Triangles, layout=rt.Triangle3DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_closest_hit(exact=False))
    return rt.emit(hits, fields=["ray_id", "triangle_id", "t"])


@rt.kernel(backend="rtdl", precision="float_approx")
def ray_triangle_hit_count_3d_kernel():
    rays = rt.input("rays", rt.Rays, layout=rt.Ray3DLayout, role="probe")
    triangles = rt.input("triangles", rt.Triangles, layout=rt.Triangle3DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_hit_count(exact=False))
    return rt.emit(hits, fields=["ray_id", "hit_count"])


def apple_rt_available() -> bool:
    if platform.system() != "Darwin":
        return False
    try:
        rt.apple_rt_context_probe()
        return True
    except Exception:
        return False


@unittest.skipUnless(apple_rt_available(), "Apple RT backend is not available")
class Goal578AppleRtBackendTest(unittest.TestCase):
    def _case(self) -> dict[str, tuple[object, ...]]:
        return {
            "rays": (
                rt.Ray3D(id=7, ox=-1.0, oy=0.0, oz=0.0, dx=1.0, dy=0.0, dz=0.0, tmax=3.0),
                rt.Ray3D(id=8, ox=-1.0, oy=2.0, oz=0.0, dx=1.0, dy=0.0, dz=0.0, tmax=3.0),
                rt.Ray3D(id=9, ox=-1.0, oy=0.0, oz=0.0, dx=1.0, dy=0.0, dz=0.0, tmax=0.1),
            ),
            "triangles": (
                rt.Triangle3D(id=10, x0=0.7, y0=-1.0, z0=-1.0, x1=0.7, y1=1.0, z1=0.0, x2=0.7, y2=-1.0, z2=1.0),
                rt.Triangle3D(id=11, x0=0.2, y0=-1.0, z0=-1.0, x1=0.2, y1=1.0, z1=0.0, x2=0.2, y2=-1.0, z2=1.0),
            ),
        }

    def test_version_and_context_probe(self) -> None:
        self.assertEqual(rt.apple_rt_version(), (0, 9, 3))
        self.assertTrue(rt.apple_rt_context_probe())

    def test_direct_helper_matches_cpu_reference(self) -> None:
        case = self._case()
        actual = tuple(rt.ray_triangle_closest_hit_apple_rt(case["rays"], case["triangles"]))
        expected = rt.ray_triangle_closest_hit_cpu(case["rays"], case["triangles"])
        self.assertEqual(len(actual), len(expected))
        for actual_row, expected_row in zip(actual, expected):
            self.assertEqual(actual_row["ray_id"], expected_row["ray_id"])
            self.assertEqual(actual_row["triangle_id"], expected_row["triangle_id"])
            self.assertAlmostEqual(actual_row["t"], expected_row["t"], places=5)

    def test_prepared_closest_hit_matches_cpu_reference(self) -> None:
        case = self._case()
        with rt.prepare_apple_rt_ray_triangle_closest_hit(case["triangles"]) as prepared:
            actual = tuple(prepared.run(case["rays"]))
            repeat = tuple(prepared.run(case["rays"]))
        expected = rt.ray_triangle_closest_hit_cpu(case["rays"], case["triangles"])
        self.assertEqual(len(actual), len(expected))
        self.assertEqual(len(repeat), len(expected))
        for actual_row, expected_row in zip(actual, expected):
            self.assertEqual(actual_row["ray_id"], expected_row["ray_id"])
            self.assertEqual(actual_row["triangle_id"], expected_row["triangle_id"])
            self.assertAlmostEqual(actual_row["t"], expected_row["t"], places=5)
        self.assertEqual(actual, repeat)

    def test_prepared_closest_hit_rejects_run_after_close(self) -> None:
        case = self._case()
        prepared = rt.prepare_apple_rt_ray_triangle_closest_hit(case["triangles"])
        prepared.close()
        with self.assertRaises(RuntimeError):
            prepared.run(case["rays"])

    def test_run_apple_rt_matches_cpu_reference(self) -> None:
        case = self._case()
        actual = rt.run_apple_rt(ray_triangle_closest_hit_3d_kernel, **case)
        expected = rt.run_cpu_python_reference(ray_triangle_closest_hit_3d_kernel, **case)
        self.assertEqual(len(actual), len(expected))
        for actual_row, expected_row in zip(actual, expected):
            self.assertEqual(actual_row["ray_id"], expected_row["ray_id"])
            self.assertEqual(actual_row["triangle_id"], expected_row["triangle_id"])
            self.assertAlmostEqual(actual_row["t"], expected_row["t"], places=5)

    def test_empty_triangles_return_no_rows(self) -> None:
        case = self._case()
        self.assertEqual(rt.run_apple_rt(ray_triangle_closest_hit_3d_kernel, rays=case["rays"], triangles=()), ())

    def test_ray_triangle_hit_count_native_matches_cpu_reference(self) -> None:
        case = self._case()
        actual = rt.run_apple_rt(ray_triangle_hit_count_3d_kernel, native_only=True, **case)
        expected = rt.run_cpu_python_reference(ray_triangle_hit_count_3d_kernel, **case)
        self.assertEqual(actual, expected)
        direct = tuple(rt.ray_triangle_hit_count_apple_rt(case["rays"], case["triangles"]))
        self.assertEqual(direct, expected)


if __name__ == "__main__":
    unittest.main()
