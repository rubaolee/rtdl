from __future__ import annotations

import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from scripts.goal571_rtxrmq_paper_workload_perf import exact_rmq_cpu
from scripts.goal571_rtxrmq_paper_workload_perf import make_rmq_queries
from scripts.goal571_rtxrmq_paper_workload_perf import make_rtxrmq_like_triangles
from scripts.goal571_rtxrmq_paper_workload_perf import make_threshold_queries
from scripts.goal571_rtxrmq_paper_workload_perf import make_threshold_rays
from scripts.goal571_rtxrmq_paper_workload_perf import make_values
from scripts.goal571_rtxrmq_paper_workload_perf import row_signature
from scripts.goal571_rtxrmq_paper_workload_perf import rtxrmq_threshold_hitcount_kernel
from scripts.goal571_rtxrmq_paper_workload_perf import threshold_count_cpu


class Goal571RtxrmqPaperWorkloadTest(unittest.TestCase):
    def test_exact_cpu_rmq_matches_paper_definition(self) -> None:
        values = (9.0, 2.0, 7.0, 8.0, 4.0, 1.0, 3.0)
        rows = exact_rmq_cpu(values, ((2, 6), (0, 1), (5, 5)))
        self.assertEqual(
            rows,
            (
                {"query_id": 0, "index": 5, "value": 1.0},
                {"query_id": 1, "index": 1, "value": 2.0},
                {"query_id": 2, "index": 5, "value": 1.0},
            ),
        )

    def test_threshold_hitcount_geometry_matches_threshold_oracle(self) -> None:
        values = make_values(64)
        queries = make_rmq_queries(24, len(values), 8)
        exact_rows = exact_rmq_cpu(values, queries)
        threshold_queries = make_threshold_queries(exact_rows, queries, threshold_slack=0.02)
        rays = make_threshold_rays(threshold_queries)
        triangles = make_rtxrmq_like_triangles(values)
        expected = threshold_count_cpu(values, threshold_queries)
        direct = rt.ray_triangle_hit_count_cpu(rays, triangles)
        self.assertEqual(row_signature(direct), row_signature(expected))

    def test_rtdl_cpu_reference_runs_threshold_hitcount_kernel(self) -> None:
        values = make_values(32)
        queries = make_rmq_queries(12, len(values), 6)
        exact_rows = exact_rmq_cpu(values, queries)
        threshold_queries = make_threshold_queries(exact_rows, queries)
        rays = make_threshold_rays(threshold_queries)
        triangles = make_rtxrmq_like_triangles(values)
        expected = threshold_count_cpu(values, threshold_queries)
        rows = rt.run_cpu_python_reference(
            rtxrmq_threshold_hitcount_kernel,
            query_rays=rays,
            element_triangles=triangles,
        )
        self.assertEqual(row_signature(rows), row_signature(expected))


if __name__ == "__main__":
    unittest.main()
