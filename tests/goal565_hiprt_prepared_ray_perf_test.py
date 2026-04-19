from __future__ import annotations

import unittest

from scripts.goal565_hiprt_prepared_ray_perf import make_case, run_prepared_perf


class Goal565HiprtPreparedRayPerfHarnessTest(unittest.TestCase):
    def test_make_case_is_deterministic_and_nonempty(self) -> None:
        rays_a, triangles_a = make_case(8, 16)
        rays_b, triangles_b = make_case(8, 16)
        self.assertEqual(rays_a, rays_b)
        self.assertEqual(triangles_a, triangles_b)
        self.assertEqual(len(rays_a), 8)
        self.assertEqual(len(triangles_a), 16)

    def test_cpu_reference_path_runs_without_gpu(self) -> None:
        payload = run_prepared_perf(ray_count=4, triangle_count=8, repeats=1)
        self.assertEqual(payload["goal"], 565)
        self.assertEqual(payload["ray_count"], 4)
        self.assertEqual(payload["triangle_count"], 8)
        self.assertIn("cpu_python_reference", payload["results"])
        self.assertGreater(payload["results"]["cpu_python_reference"]["row_count"], 0)


if __name__ == "__main__":
    unittest.main()
