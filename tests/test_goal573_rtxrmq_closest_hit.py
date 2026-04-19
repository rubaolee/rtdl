from __future__ import annotations

import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from scripts.goal573_rtxrmq_closest_hit_perf import closest_rows_to_rmq
from scripts.goal573_rtxrmq_closest_hit_perf import exact_rmq_cpu
from scripts.goal573_rtxrmq_closest_hit_perf import make_query_rays
from scripts.goal573_rtxrmq_closest_hit_perf import make_queries
from scripts.goal573_rtxrmq_closest_hit_perf import make_rmq_triangles
from scripts.goal573_rtxrmq_closest_hit_perf import make_values
from scripts.goal573_rtxrmq_closest_hit_perf import rtxrmq_closest_hit_kernel


class Goal573RtxrmqClosestHitTest(unittest.TestCase):
    def test_cpu_closest_hit_primitive_returns_nearest_triangle(self) -> None:
        rays = (rt.Ray3D(id=7, ox=-1.0, oy=0.0, oz=0.0, dx=1.0, dy=0.0, dz=0.0, tmax=3.0),)
        triangles = (
            rt.Triangle3D(id=10, x0=0.7, y0=-1.0, z0=-1.0, x1=0.7, y1=1.0, z1=0.0, x2=0.7, y2=-1.0, z2=1.0),
            rt.Triangle3D(id=11, x0=0.2, y0=-1.0, z0=-1.0, x1=0.2, y1=1.0, z1=0.0, x2=0.2, y2=-1.0, z2=1.0),
        )
        self.assertEqual(rt.ray_triangle_closest_hit_cpu(rays, triangles)[0]["triangle_id"], 11)

    def test_exact_rmq_geometry_matches_cpu_rmq(self) -> None:
        values = (0.9, 0.2, 0.7, 0.8, 0.4, 0.1, 0.3)
        queries = ((2, 6), (0, 1), (5, 5))
        expected = exact_rmq_cpu(values, queries)
        rows = rt.run_cpu_python_reference(
            rtxrmq_closest_hit_kernel,
            query_rays=make_query_rays(queries),
            element_triangles=make_rmq_triangles(values),
        )
        self.assertEqual(
            closest_rows_to_rmq(rows, values),
            expected,
        )

    def test_exact_rmq_geometry_matches_native_cpu_runtime(self) -> None:
        values = (0.9, 0.2, 0.7, 0.8, 0.4, 0.1, 0.3)
        queries = ((2, 6), (0, 1), (5, 5))
        rows = rt.run_cpu(
            rtxrmq_closest_hit_kernel,
            query_rays=make_query_rays(queries),
            element_triangles=make_rmq_triangles(values),
        )
        self.assertEqual(closest_rows_to_rmq(rows, values), exact_rmq_cpu(values, queries))

    def test_exact_rmq_generated_case_matches_cpu_rmq(self) -> None:
        values = make_values(64)
        queries = make_queries(24, len(values), 10)
        rows = rt.run_cpu_python_reference(
            rtxrmq_closest_hit_kernel,
            query_rays=make_query_rays(queries),
            element_triangles=make_rmq_triangles(values),
        )
        self.assertEqual(closest_rows_to_rmq(rows, values), exact_rmq_cpu(values, queries))


if __name__ == "__main__":
    unittest.main()
