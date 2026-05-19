from __future__ import annotations

import pathlib
import unittest

from rtdsl.partner_adapters import _radius_graph_degree_budget_chunk_ranges


ROOT = pathlib.Path(__file__).resolve().parents[1]
ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"
README = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "README.md"
REPORT = ROOT / "docs" / "reports" / "goal2441_rt_dbscan_adaptive_chunk_budget_2026-05-19.md"


class Goal2441RtDbscanAdaptiveChunkBudgetTest(unittest.TestCase):
    def test_chunk_range_helper_obeys_point_and_edge_limits(self) -> None:
        counts = [4, 3, 6, 2, 5, 1]
        ranges = _radius_graph_degree_budget_chunk_ranges(
            counts,
            max_chunk_points=3,
            max_directed_edges_per_chunk=8,
        )

        self.assertEqual(ranges, [(0, 2), (2, 4), (4, 6)])
        for start, end in ranges:
            self.assertLessEqual(end - start, 3)
            self.assertLessEqual(sum(counts[start:end]), 8)

    def test_chunk_range_helper_preserves_fixed_point_chunks_without_edge_budget(self) -> None:
        ranges = _radius_graph_degree_budget_chunk_ranges(
            [2, 2, 2, 2, 2],
            max_chunk_points=2,
            max_directed_edges_per_chunk=None,
        )

        self.assertEqual(ranges, [(0, 2), (2, 4), (4, 5)])

    def test_chunk_range_helper_rejects_impossible_single_query_budget(self) -> None:
        with self.assertRaisesRegex(ValueError, "single query exceeds"):
            _radius_graph_degree_budget_chunk_ranges(
                [2, 9, 2],
                max_chunk_points=3,
                max_directed_edges_per_chunk=8,
            )

    def test_runtime_and_app_expose_adaptive_budget_metadata(self) -> None:
        adapters = ADAPTERS.read_text(encoding="utf-8")
        app = APP.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("count_chunk_ranges", adapters)
        self.assertIn("chunk_planning_policy", adapters)
        self.assertIn("adaptive_degree_budget_and_max_point_count", adapters)
        self.assertIn("max_directed_edges_per_chunk", adapters)
        self.assertIn("chunk_adjacency_edge_budget", app)
        self.assertIn("--chunk-adjacency-edge-budget", app)
        self.assertIn("--chunk-adjacency-edge-budget", readme)
        self.assertIn("memory-control knob", readme)
        self.assertIn("accept-with-boundary", report)
        self.assertIn("not a speedup claim", report)


if __name__ == "__main__":
    unittest.main()
