from __future__ import annotations

from pathlib import Path
import unittest

from examples import rtdl_graph_analytics_app
from examples import rtdl_graph_bfs
from examples import rtdl_graph_triangle_count
import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]


class Goal903EmbreeGraphRayTraversalTest(unittest.TestCase):
    def test_bfs_embree_matches_cpu_and_reports_ray_tracing(self) -> None:
        case = rtdl_graph_bfs.make_case(copies=4)
        embree_rows = tuple(rt.run_embree(rtdl_graph_bfs.bfs_expand_kernel, **case))
        cpu_rows = tuple(rt.run_cpu_python_reference(rtdl_graph_bfs.bfs_expand_kernel, **case))
        self.assertEqual(embree_rows, cpu_rows)

        payload = rtdl_graph_bfs.run_backend("embree", copies=4, output_mode="summary")
        self.assertTrue(payload["ray_tracing_accelerated"])
        self.assertFalse(payload["rt_core_accelerated"])
        self.assertIn("ray traversal", str(payload["ray_tracing_note"]))

    def test_bfs_embree_matches_cpu_at_replicated_scale(self) -> None:
        case = rtdl_graph_bfs.make_case(copies=16)
        embree_rows = tuple(rt.run_embree(rtdl_graph_bfs.bfs_expand_kernel, **case))
        cpu_rows = tuple(rt.run_cpu_python_reference(rtdl_graph_bfs.bfs_expand_kernel, **case))
        self.assertEqual(embree_rows, cpu_rows)

    def test_triangle_embree_matches_cpu_and_reports_ray_tracing(self) -> None:
        case = rtdl_graph_triangle_count.make_case(copies=4)
        embree_rows = tuple(rt.run_embree(rtdl_graph_triangle_count.triangle_probe_kernel, **case))
        cpu_rows = tuple(rt.run_cpu_python_reference(rtdl_graph_triangle_count.triangle_probe_kernel, **case))
        self.assertEqual(embree_rows, cpu_rows)

        payload = rtdl_graph_triangle_count.run_backend("embree", copies=4, output_mode="summary")
        self.assertTrue(payload["ray_tracing_accelerated"])
        self.assertFalse(payload["rt_core_accelerated"])
        self.assertIn("ray traversal", str(payload["ray_tracing_note"]))

    def test_triangle_embree_matches_cpu_at_replicated_scale(self) -> None:
        case = rtdl_graph_triangle_count.make_case(copies=16)
        embree_rows = tuple(rt.run_embree(rtdl_graph_triangle_count.triangle_probe_kernel, **case))
        cpu_rows = tuple(rt.run_cpu_python_reference(rtdl_graph_triangle_count.triangle_probe_kernel, **case))
        self.assertEqual(embree_rows, cpu_rows)

    def test_unified_graph_app_reports_embree_ray_path_without_nvidia_claim(self) -> None:
        payload = rtdl_graph_analytics_app.run_app("embree", scenario="all", copies=2, output_mode="summary")
        self.assertTrue(payload["ray_tracing_accelerated"])
        self.assertFalse(payload["rt_core_accelerated"])
        self.assertIn("Embree BFS and triangle_count", payload["honesty_boundary"])
        self.assertIn("OptiX BFS and triangle_count remain host-indexed by default", payload["honesty_boundary"])
        self.assertIn("native graph-ray mode remains gated", payload["honesty_boundary"])

    def test_unified_graph_app_embree_matches_cpu_at_replicated_scale(self) -> None:
        cpu_payload = rtdl_graph_analytics_app.run_app(
            "cpu_python_reference",
            scenario="all",
            copies=16,
            output_mode="summary",
        )
        embree_payload = rtdl_graph_analytics_app.run_app(
            "embree",
            scenario="all",
            copies=16,
            output_mode="summary",
        )
        for section in ("bfs", "triangle_count", "visibility_edges"):
            self.assertEqual(
                embree_payload["sections"][section]["row_count"],
                cpu_payload["sections"][section]["row_count"],
            )
            self.assertEqual(
                embree_payload["sections"][section]["summary"],
                cpu_payload["sections"][section]["summary"],
            )

    def test_unified_graph_app_embree_large_summary_matches_analytic_counts(self) -> None:
        copies = 20000
        payload = rtdl_graph_analytics_app.run_app(
            "embree",
            scenario="all",
            copies=copies,
            output_mode="summary",
        )
        self.assertEqual(payload["sections"]["bfs"]["summary"]["discovered_edge_count"], 2 * copies)
        self.assertEqual(payload["sections"]["bfs"]["summary"]["discovered_vertex_count"], 2 * copies)
        self.assertEqual(payload["sections"]["triangle_count"]["summary"]["triangle_count"], copies)
        self.assertEqual(payload["sections"]["triangle_count"]["summary"]["touched_vertex_count"], 3 * copies)
        self.assertEqual(payload["sections"]["visibility_edges"]["summary"]["visible_edge_count"], copies)
        self.assertEqual(payload["sections"]["visibility_edges"]["summary"]["blocked_edge_count"], 3 * copies)

    def test_native_embree_graph_path_uses_intersection_not_point_query(self) -> None:
        source = (ROOT / "src/native/embree/rtdl_embree_api.cpp").read_text()
        bfs_body = source.split("RTDL_EMBREE_EXPORT int rtdl_embree_run_bfs_expand", 1)[1].split(
            "RTDL_EMBREE_EXPORT int rtdl_embree_run_triangle_probe", 1
        )[0]
        triangle_body = source.split("RTDL_EMBREE_EXPORT int rtdl_embree_run_triangle_probe", 1)[1].split(
            "RTDL_EMBREE_EXPORT int rtdl_embree_run_conjunctive_scan", 1
        )[0]
        self.assertIn("rtcSetGeometryIntersectFunction(holder.geometry, graph_edge_point_intersect)", bfs_body)
        self.assertIn("rtcIntersect1(holder.scene", bfs_body)
        self.assertNotIn("rtcPointQuery", bfs_body)
        self.assertIn("rtcSetGeometryIntersectFunction(holder.geometry, graph_edge_point_intersect)", triangle_body)
        self.assertIn("rtcIntersect1(holder.scene", triangle_body)
        self.assertNotIn("rtcPointQuery", triangle_body)


if __name__ == "__main__":
    unittest.main()
