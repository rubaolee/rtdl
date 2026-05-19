from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"
README = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "README.md"
REPEAT = ROOT / "scripts" / "goal2403_rt_dbscan_repeat_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal2433_rt_dbscan_chunked_adjacency_continuation_2026-05-19.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2433_rt_dbscan_chunked_adjacency_pod"
TODO = ROOT / "docs" / "research" / "future_version_to_do_list.md"


class Goal2433RtDbscanChunkedAdjacencyContinuationTest(unittest.TestCase):
    def test_chunked_runtime_surface_is_wired(self) -> None:
        adapters = ADAPTERS.read_text(encoding="utf-8")
        init_text = INIT.read_text(encoding="utf-8")
        app = APP.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        repeat = REPEAT.read_text(encoding="utf-8")

        self.assertIn("_cupy_radius_graph_components_3d_chunked_adjacency_kernels", adapters)
        self.assertIn("PreparedOptixCupyRadiusGraphChunkedAdjacency3D", adapters)
        self.assertIn("prepare_optix_cupy_radius_graph_chunked_adjacency_3d", adapters)
        self.assertIn("radius_graph_components_3d_optix_cupy_prepared_chunked_adjacency_partner_columns", adapters)
        self.assertIn("memory_bounded_optix_written_directed_radius_graph_neighbor_index_stream_chunks", adapters)
        self.assertIn("PreparedOptixCupyRadiusGraphChunkedAdjacency3D", init_text)
        self.assertIn("optix_rt_core_chunked_adjacency_cupy_components_3d", app)
        self.assertIn("optix_rt_core_chunked_adjacency_cupy_components_3d", readme)
        self.assertIn("PREPARED_OPTIX_CHUNKED_ADJACENCY_MODE", repeat)

    def test_pod_artifacts_show_correctness_and_memory_bound(self) -> None:
        tiny = json.loads((ARTIFACT_DIR / "tiny_app.json").read_text(encoding="utf-8"))
        self.assertTrue(tiny["matches_reference"])
        self.assertEqual(tiny["metadata"]["chunk_count"], 1)
        self.assertEqual(tiny["metadata"]["total_directed_edge_count"], 33)
        self.assertTrue(tiny["metadata"]["materializes_bounded_directed_adjacency_chunks"])

        dense = json.loads((ARTIFACT_DIR / "clustered32768_chunked.json").read_text(encoding="utf-8"))
        self.assertTrue(dense["signatures_match"])
        rows = [
            row for row in dense["rows"]
            if row["mode"] == "optix_rt_core_chunked_adjacency_cupy_components_3d"
        ]
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(int(row["chunk_count"]), 8)
        self.assertEqual(int(row["directed_edge_count"]), 136345984)
        self.assertEqual(int(row["max_chunk_directed_edge_count"]), 17197789)
        self.assertLess(int(row["max_chunk_directed_edge_count"]), int(row["directed_edge_count"]))

    def test_report_keeps_performance_boundary_clear(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        todo = TODO.read_text(encoding="utf-8")

        self.assertIn("accept-with-boundary", report)
        self.assertIn("memory-bounded", report)
        self.assertIn("slower than full adjacency", report)
        self.assertIn("not a", report)
        self.assertIn("speedup claim", report)
        self.assertIn("does not add DBSCAN-native engine code", report)
        self.assertIn("Goal2433 added the bounded/chunked OptiX adjacency continuation", todo)
        self.assertIn("avoid the second RT fill", todo)


if __name__ == "__main__":
    unittest.main()
