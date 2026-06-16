from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

import numpy as np

from examples.current.research_benchmarks.triangle_counting import rt_graph_contract as contract_mod


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "examples/current/research_benchmarks/triangle_counting/rt_graph_contract.py"
RUNNER = ROOT / "scripts/v3_0_m27_triangle_partner_dual_measure.py"


class Goal4444V30M48TriangleNumbaDirectBinarySummaryTest(unittest.TestCase):
    def test_numpy_summary_matches_python_contract_on_named_fixtures(self) -> None:
        for fixture in (
            "single_triangle",
            "degree_oriented_two_triangles",
            "duplicates_self_and_leaf",
        ):
            with self.subTest(fixture=fixture):
                edges = contract_mod.fixture_edges(fixture)
                reference = contract_mod.build_rt_graph_triangle_contract(
                    edges,
                    include_id_ascending_adapter=False,
                )
                edges_np = np.asarray(edges, dtype=np.int64).reshape(-1, 2)
                summary = contract_mod._build_rt_graph_triangle_summary_arrays_numpy(edges_np)

                self.assertEqual(summary["compacted_vertex_count"], len(reference.compacted_vertex_ids))
                self.assertEqual(summary["directed_vertex_count"], reference.vertex_count)
                self.assertEqual(summary["directed_edges"].tolist(), [list(edge) for edge in reference.directed_edges])
                self.assertEqual(summary["row_offsets"].tolist(), list(reference.row_offsets))
                self.assertEqual(summary["column_indices"].tolist(), list(reference.column_indices))
                self.assertEqual(summary["triangle_count"], reference.triangle_count)
                self.assertEqual(
                    summary["two_hop_rays_2a1"].tolist(),
                    [list(row) for row in reference.two_hop_rays_2a1],
                )
                self.assertEqual(
                    summary["removed_low_degree_vertex_count"],
                    reference.removed_low_degree_vertex_count,
                )
                self.assertEqual(summary["removed_low_degree_edge_count"], reference.removed_low_degree_edge_count)
                self.assertEqual(
                    summary["removed_duplicate_or_self_edge_count"],
                    reference.removed_duplicate_or_self_edge_count,
                )

    def test_numba_binary_builder_no_longer_uses_python_edge_list_contract_path(self) -> None:
        source = CONTRACT.read_text(encoding="utf-8")
        builder_start = source.index("def build_rt_graph_triangle_summary_contract_numba_binary")
        builder_end = source.index("def _build_rt_graph_triangle_summary_arrays_numpy")
        builder_source = source[builder_start:builder_end]

        self.assertIn("_build_rt_graph_triangle_summary_arrays_numpy(edges_np)", builder_source)
        self.assertIn("direct_binary_summary_ms", builder_source)
        self.assertIn("direct_binary_numpy_summary_then_numba_device_upload", builder_source)
        self.assertNotIn("edges_np.tolist()", builder_source)
        self.assertNotIn("build_rt_graph_triangle_contract(", builder_source)

    def test_runner_boundary_names_m48_construction_mode(self) -> None:
        runner = RUNNER.read_text(encoding="utf-8")

        self.assertIn("rtdl.v3_0.triangle_partner_dual.m48", runner)
        self.assertIn("direct_binary_numpy_summary_then_numba_device_upload", runner)
        self.assertIn("numba_route_previous", runner)
        self.assertIn("cpu_contract_then_numba_device_upload", runner)

    def test_numba_builder_smoke_when_cuda_is_available(self) -> None:
        try:
            from numba import cuda
        except Exception:
            self.skipTest("Numba CUDA is not importable")
        if not cuda.is_available():
            self.skipTest("Numba CUDA device is not available")

        with tempfile.TemporaryDirectory() as tmp:
            edge_file = Path(tmp) / "triangle.edge"
            contract_mod.write_binary_edges(edge_file, contract_mod.fixture_edges("single_triangle"))
            summary = contract_mod.build_rt_graph_triangle_summary_contract_numba_binary(edge_file)

        self.assertEqual(summary.partner, "numba")
        self.assertEqual(summary.partner_timing_ms["construction_mode"], "direct_binary_numpy_summary_then_numba_device_upload")
        self.assertEqual(summary.triangle_count, 1)
        self.assertEqual(summary.directed_edge_count, 3)
        self.assertEqual(summary.duplicate_two_hop_relation_count, 1)
        self.assertIsInstance(summary.device_arrays, dict)


if __name__ == "__main__":
    unittest.main()
