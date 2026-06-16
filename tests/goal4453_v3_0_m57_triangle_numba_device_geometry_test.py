from __future__ import annotations

import importlib
from pathlib import Path
import tempfile
import unittest

import numpy as np

from examples.current.research_benchmarks.triangle_counting import rt_graph_contract as contract_mod
from examples.current.research_benchmarks.triangle_counting import rtdl_triangle_counting_benchmark_app as app

routes = importlib.import_module("rtdsl.current_benchmark_route_decisions")


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples/current/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py"
REPORT = ROOT / "docs" / "reports" / "goal4453_v3_0_m57_triangle_numba_device_geometry_2026-06-16.md"
EVIDENCE = ROOT / "docs" / "reports" / "goal4453_v3_0_m57_triangle_numba_device_geometry_200000_2026-06-16.json"


def _has_numba_cuda() -> bool:
    try:
        from numba import cuda
    except Exception:
        return False
    try:
        return bool(cuda.is_available())
    except Exception:
        return False


class Goal4453V30M57TriangleNumbaDeviceGeometryTest(unittest.TestCase):
    def test_numba_geometry_uses_summary_device_columns(self) -> None:
        source = APP.read_text(encoding="utf-8")
        one_start = source.index("def _build_rt_graph_1a2_numba_device_geometry")
        one_end = source.index("def _build_rt_graph_1a2_geometry")
        two_start = source.index("def _build_rt_graph_2a1_numba_device_geometry")
        two_end = source.index("def _build_rt_graph_2a1_geometry")
        one_source = source[one_start:one_end]
        two_source = source[two_start:two_end]

        self.assertIn('_require_summary_device_arrays(contract, partner="numba")', one_source)
        self.assertIn('_require_summary_device_arrays(contract, partner="numba")', two_source)
        self.assertIn("_get_rt_graph_1a2_fill_triangles_numba_kernel", one_source)
        self.assertIn("_get_rt_graph_2a1_fill_triangles_numba_kernel", two_source)
        self.assertIn('ray_weights = device_arrays["two_hop_weights"]', two_source)
        self.assertNotIn("np.repeat(np.arange(contract.vertex_count", one_source)
        self.assertNotIn("np.asarray(contract.directed_edges", two_source)
        self.assertNotIn("cuda.to_device(ray_weights_host)", two_source)

    @unittest.skipUnless(_has_numba_cuda(), "Numba CUDA device is not available")
    def test_live_numba_device_geometry_matches_summary_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            edge_file = Path(tmp) / "triangle.edge"
            contract_mod.write_binary_edges(edge_file, contract_mod.fixture_edges("single_triangle"))
            summary = contract_mod.build_rt_graph_triangle_summary_contract_numba_binary(edge_file)

        triangles_2a1, rays_2a1, weights_2a1 = app._build_rt_graph_2a1_numba_device_geometry(summary)
        triangles_1a2, rays_1a2 = app._build_rt_graph_1a2_numba_device_geometry(summary)

        directed_edges = np.asarray(summary.directed_edges, dtype=np.int64).reshape(-1, 2)
        two_hop = np.asarray(summary.two_hop_rays_2a1, dtype=np.int64).reshape(-1, 3)
        row_offsets = np.asarray(summary.row_offsets, dtype=np.int64)
        column_indices = np.asarray(summary.column_indices, dtype=np.int64)
        out_degrees = row_offsets[1:] - row_offsets[:-1]
        one_a_two_primitive_count = int(out_degrees[column_indices].sum(dtype=np.int64))

        np.testing.assert_array_equal(
            triangles_2a1["ids"].copy_to_host(),
            np.arange(directed_edges.shape[0], dtype=np.uint32),
        )
        np.testing.assert_array_equal(
            rays_2a1["ids"].copy_to_host(),
            np.arange(two_hop.shape[0], dtype=np.uint32),
        )
        np.testing.assert_array_equal(
            weights_2a1.copy_to_host(),
            two_hop[:, 2].astype(np.uint64, copy=False),
        )
        np.testing.assert_array_equal(
            triangles_1a2["ids"].copy_to_host(),
            np.arange(one_a_two_primitive_count, dtype=np.uint32),
        )
        np.testing.assert_array_equal(
            rays_1a2["ids"].copy_to_host(),
            np.arange(directed_edges.shape[0], dtype=np.uint32),
        )

    def test_report_and_evidence_record_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        evidence = EVIDENCE.read_text(encoding="utf-8")

        for phrase in (
            "Goal4453",
            "partner-resident device columns",
            "does not authorize a triangle-counting RT-core speedup claim",
            "remaining debt is graph-summary construction",
        ):
            self.assertIn(phrase, report)
        self.assertIn('"goal": 4453', evidence)
        self.assertIn('"numba_device_geometry"', evidence)

    def test_route_guidance_records_device_geometry_but_not_speedup_claim(self) -> None:
        route = routes.explain_current_benchmark_route("triangle_counting")

        self.assertEqual("rtdl.v3_0.current_benchmark_route_decisions.goal4476.v1", route["version"])
        self.assertIn("Goal4453", route["evidence_refs"])
        self.assertIn("partner-resident Numba device columns", route["current_reader_decision"])
        self.assertIn("prepared ray-batch weighted-sum API", route["next_runtime_action"])
        self.assertFalse(route["public_speedup_claim_authorized"])
        self.assertFalse(route["broad_rt_core_claim_authorized"])


if __name__ == "__main__":
    unittest.main()



