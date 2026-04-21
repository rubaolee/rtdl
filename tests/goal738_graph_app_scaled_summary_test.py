import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

from examples import rtdl_graph_analytics_app
from examples import rtdl_graph_bfs
from examples import rtdl_graph_triangle_count


class Goal738GraphAppScaledSummaryTest(unittest.TestCase):
    def test_bfs_scaled_summary_matches_expected_counts(self) -> None:
        payload = rtdl_graph_bfs.run_backend("cpu_python_reference", copies=5, output_mode="summary")
        self.assertEqual(payload["graph_vertex_count"], 20)
        self.assertEqual(payload["graph_edge_count"], 25)
        self.assertEqual(payload["rows"], [])
        self.assertEqual(
            payload["summary"],
            {
                "discovered_edge_count": 10,
                "discovered_vertex_count": 10,
                "max_level": 1,
            },
        )

    def test_triangle_scaled_summary_matches_expected_counts(self) -> None:
        payload = rtdl_graph_triangle_count.run_backend("cpu_python_reference", copies=5, output_mode="summary")
        self.assertEqual(payload["graph_vertex_count"], 20)
        self.assertEqual(payload["graph_edge_count"], 30)
        self.assertEqual(payload["seed_count"], 15)
        self.assertEqual(payload["rows"], [])
        self.assertEqual(
            payload["summary"],
            {
                "triangle_count": 5,
                "touched_vertex_count": 15,
            },
        )

    def test_unified_graph_app_keeps_default_row_behavior(self) -> None:
        payload = rtdl_graph_analytics_app.run_app("cpu_python_reference")
        self.assertEqual(payload["copies"], 1)
        self.assertEqual(payload["output_mode"], "rows")
        self.assertEqual(len(payload["sections"]["bfs"]["rows"]), 2)
        self.assertEqual(len(payload["sections"]["triangle_count"]["rows"]), 1)

    def test_embree_scaled_summary_matches_cpu_reference_when_available(self) -> None:
        try:
            embree = rtdl_graph_analytics_app.run_app("embree", copies=3, output_mode="summary")
        except Exception as exc:
            self.skipTest(f"Embree unavailable: {exc}")
        cpu = rtdl_graph_analytics_app.run_app("cpu_python_reference", copies=3, output_mode="summary")
        self.assertEqual(embree["sections"]["bfs"]["summary"], cpu["sections"]["bfs"]["summary"])
        self.assertEqual(
            embree["sections"]["triangle_count"]["summary"],
            cpu["sections"]["triangle_count"]["summary"],
        )


if __name__ == "__main__":
    unittest.main()
