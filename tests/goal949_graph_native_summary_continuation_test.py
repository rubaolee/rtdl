from __future__ import annotations

import unittest

from examples import rtdl_graph_analytics_app
from examples import rtdl_graph_bfs
from examples import rtdl_graph_triangle_count
import rtdsl as rt


class Goal949GraphNativeSummaryContinuationTest(unittest.TestCase):
    def test_native_bfs_summary_matches_python_reference_shape(self) -> None:
        rows = (
            {"src_vertex": 0, "dst_vertex": 2, "level": 1},
            {"src_vertex": 1, "dst_vertex": 2, "level": 1},
            {"src_vertex": 2, "dst_vertex": 3, "level": 2},
        )
        self.assertEqual(
            rt.summarize_bfs_rows(rows),
            {
                "discovered_edge_count": 3,
                "discovered_vertex_count": 2,
                "max_level": 2,
            },
        )

    def test_native_triangle_summary_matches_python_reference_shape(self) -> None:
        rows = (
            {"u": 0, "v": 1, "w": 2},
            {"u": 2, "v": 3, "w": 4},
        )
        self.assertEqual(
            rt.summarize_triangle_rows(rows),
            {"triangle_count": 2, "touched_vertex_count": 5},
        )

    def test_graph_bfs_summary_mode_uses_native_continuation(self) -> None:
        rows_payload = rtdl_graph_bfs.run_backend("cpu_python_reference", copies=3, output_mode="rows")
        summary_payload = rtdl_graph_bfs.run_backend("cpu_python_reference", copies=3, output_mode="summary")
        self.assertEqual(summary_payload["summary"], rt.summarize_bfs_rows(rows_payload["rows"]))
        self.assertEqual(summary_payload["rows"], [])
        self.assertTrue(summary_payload["native_continuation_active"])
        self.assertEqual(summary_payload["native_continuation_backend"], "oracle_cpp")

    def test_graph_triangle_summary_mode_uses_native_continuation(self) -> None:
        rows_payload = rtdl_graph_triangle_count.run_backend("cpu_python_reference", copies=3, output_mode="rows")
        summary_payload = rtdl_graph_triangle_count.run_backend("cpu_python_reference", copies=3, output_mode="summary")
        self.assertEqual(summary_payload["summary"], rt.summarize_triangle_rows(rows_payload["rows"]))
        self.assertEqual(summary_payload["rows"], [])
        self.assertTrue(summary_payload["native_continuation_active"])
        self.assertEqual(summary_payload["native_continuation_backend"], "oracle_cpp")

    def test_unified_graph_summary_reports_native_continuation_boundary(self) -> None:
        payload = rtdl_graph_analytics_app.run_app(
            "cpu_python_reference",
            scenario="all",
            copies=2,
            output_mode="summary",
        )
        self.assertTrue(payload["sections"]["bfs"]["native_continuation_active"])
        self.assertTrue(payload["sections"]["triangle_count"]["native_continuation_active"])
        self.assertIn(
            "native C++ summary continuation for BFS and triangle_count summary mode",
            payload["data_flow"],
        )
        self.assertIn("summary mode uses native C++ continuation", payload["honesty_boundary"])


if __name__ == "__main__":
    unittest.main()
