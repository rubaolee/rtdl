from __future__ import annotations

import unittest

import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def ray_hitcount_3d_kernel():
    rays = rt.input("rays", rt.Rays3D, role="probe")
    triangles = rt.input("triangles", rt.Triangles3D, role="build")
    hits = rt.refine(rt.traverse(rays, triangles, accel="bvh"), predicate=rt.ray_triangle_hit_count())
    return rt.emit(hits, fields=["ray_id", "hit_count"])


@unittest.skipUnless(rt.adaptive_available(), "adaptive native backend library is not built")
class Goal586AdaptiveNativeRayHitcountTest(unittest.TestCase):
    def test_native_3d_ray_hitcount_matches_python_reference(self) -> None:
        rays = (
            rt.Ray3D(1, -1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 4.0),
            rt.Ray3D(2, -1.0, 2.0, 0.0, 1.0, 0.0, 0.0, 4.0),
            rt.Ray3D(3, 0.5, 0.0, -2.0, 0.0, 0.0, 1.0, 5.0),
        )
        triangles = (
            rt.Triangle3D(10, 0.5, -1.0, -1.0, 0.5, 1.0, 0.0, 0.5, -1.0, 1.0),
            rt.Triangle3D(11, 1.5, -1.0, -1.0, 1.5, 1.0, 0.0, 1.5, -1.0, 1.0),
            rt.Triangle3D(12, 0.0, 5.0, 0.0, 1.0, 5.0, 0.0, 0.0, 5.0, 1.0),
        )
        inputs = {"rays": rays, "triangles": triangles}

        self.assertEqual(rt.adaptive_version(), (0, 1, 0))
        self.assertEqual(rt.adaptive_predicate_mode(ray_hitcount_3d_kernel)["mode"], "native_adaptive_cpu_soa_3d")
        self.assertEqual(
            rt.run_adaptive(ray_hitcount_3d_kernel, **inputs),
            rt.run_cpu_python_reference(ray_hitcount_3d_kernel, **inputs),
        )


if __name__ == "__main__":
    unittest.main()
