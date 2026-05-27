from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP = (
    ROOT
    / "examples"
    / "v2_0"
    / "research_benchmarks"
    / "triangle_counting"
    / "rtdl_triangle_counting_benchmark_app.py"
)

sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples.v2_0.research_benchmarks.triangle_counting.rt_graph_contract import (  # noqa: E402
    build_rt_graph_triangle_contract,
)
from examples.v2_0.research_benchmarks.triangle_counting.rt_graph_contract import (  # noqa: E402
    build_rt_graph_triangle_summary_contract_cupy_binary,
)
from examples.v2_0.research_benchmarks.triangle_counting.rt_graph_contract import (  # noqa: E402
    fixture_edges,
)
from examples.v2_0.research_benchmarks.triangle_counting.rt_graph_contract import (  # noqa: E402
    read_binary_edges,
)
from examples.v2_0.research_benchmarks.triangle_counting.rt_graph_contract import (  # noqa: E402
    write_binary_edges,
)
from examples.v2_0.research_benchmarks.triangle_counting import (  # noqa: E402
    rtdl_triangle_counting_benchmark_app as triangle_app,
)
import rtdsl as rt  # noqa: E402


def _run_app(*args: str) -> dict:
    completed = subprocess.run(
        [sys.executable, str(APP), *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


class Goal2589RTGraphTriangleContractTest(unittest.TestCase):
    def test_single_triangle_matches_rt_graph_directed_csr_contract(self) -> None:
        contract = build_rt_graph_triangle_contract(fixture_edges("single_triangle"))

        self.assertEqual(contract.compacted_vertex_ids, (10, 20, 30))
        self.assertEqual(contract.degree_before_orientation, (2, 2, 2))
        self.assertEqual(contract.directed_edges, ((0, 1), (0, 2), (1, 2)))
        self.assertEqual(contract.row_offsets, (0, 2, 3, 3))
        self.assertEqual(contract.column_indices, (1, 2, 2))
        self.assertEqual(contract.triangle_witnesses, ((0, 1, 2),))
        self.assertEqual(contract.triangle_count, 1)
        self.assertEqual(contract.two_hop_rays_2a1, ((0, 2, 1),))
        self.assertEqual(contract.id_ascending_vertex_order, (0, 1, 2))
        self.assertEqual(contract.id_ascending_edges, ((0, 1), (0, 2), (1, 2)))
        self.assertEqual(contract.id_ascending_triangle_witnesses, ((0, 1, 2),))

    def test_degree_orientation_is_not_equivalent_to_id_ascending_contract(self) -> None:
        contract = build_rt_graph_triangle_contract(fixture_edges("degree_oriented_two_triangles"))

        self.assertEqual(contract.degree_before_orientation, (3, 2, 3, 2))
        self.assertIn((1, 0), contract.directed_edges)
        self.assertEqual(contract.directed_edges, ((0, 2), (1, 0), (1, 2), (3, 0), (3, 2)))
        self.assertEqual(contract.triangle_witnesses, ((1, 0, 2), (3, 0, 2)))
        self.assertEqual(contract.triangle_count, 2)
        self.assertEqual(contract.duplicate_two_hop_relation_count, 2)
        self.assertEqual(contract.id_ascending_vertex_order, (1, 3, 0, 2))
        self.assertEqual(contract.id_ascending_edges, ((0, 2), (0, 3), (1, 2), (1, 3), (2, 3)))
        self.assertEqual(contract.id_ascending_triangle_witnesses, ((0, 2, 3), (1, 2, 3)))

    def test_low_degree_duplicate_and_self_cleanup_is_explicit(self) -> None:
        contract = build_rt_graph_triangle_contract(fixture_edges("duplicates_self_and_leaf"))

        self.assertEqual(contract.triangle_count, 1)
        self.assertEqual(contract.removed_low_degree_vertex_count, 2)
        self.assertEqual(contract.removed_low_degree_edge_count, 1)
        self.assertEqual(contract.removed_duplicate_or_self_edge_count, 2)
        self.assertEqual(contract.directed_edges, ((0, 1), (0, 2), (1, 2)))

    def test_id_ascending_adapter_can_be_skipped_for_rt_summary_lowering(self) -> None:
        contract = build_rt_graph_triangle_contract(
            fixture_edges("degree_oriented_two_triangles"),
            include_id_ascending_adapter=False,
        )

        self.assertFalse(contract.id_ascending_adapter_materialized)
        self.assertEqual(contract.triangle_count, 2)
        self.assertEqual(contract.directed_edges, ((0, 2), (1, 0), (1, 2), (3, 0), (3, 2)))
        self.assertEqual(contract.two_hop_rays_2a1, ((1, 2, 1), (3, 2, 1)))
        self.assertEqual(contract.id_ascending_edges, ())
        self.assertEqual(contract.id_ascending_triangle_witnesses, ())

    def test_binary_edge_round_trip_uses_authors_file_shape(self) -> None:
        edges = fixture_edges("degree_oriented_two_triangles")
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "graph.edge"
            write_binary_edges(path, edges)
            self.assertEqual(read_binary_edges(path), edges)

            payload = _run_app("--mode", "rt_graph_contract", "--edge-file", str(path), "--edge-format", "binary")

        self.assertEqual(payload["input_source"]["format"], "binary")
        self.assertEqual(payload["rt_graph_contract"]["triangle_count"], 2)
        self.assertFalse(payload["authors_code_reproduction"])
        self.assertFalse(payload["same_contract_rtdl_backend_rows"])
        self.assertIn("id-ascending relabeling adapter", payload["rtdl_feature_gap"])

    def test_app_exposes_fixture_oracle_without_authorizing_perf_claims(self) -> None:
        payload = _run_app(
            "--mode",
            "rt_graph_contract",
            "--fixture",
            "degree_oriented_two_triangles",
        )

        self.assertEqual(payload["contract"], "rt_graph_style_degree_oriented_triangle_count")
        self.assertEqual(payload["status"], "python_preprocessing_oracle_only")
        self.assertEqual(payload["rt_graph_contract"]["triangle_count"], 2)
        self.assertTrue(payload["claim_boundary"]["rt_graph_preprocessing_oracle"])
        self.assertTrue(payload["claim_boundary"]["rt_graph_id_ascending_adapter"])
        self.assertTrue(payload["claim_boundary"]["rt_graph_2a1_generic_rt_mapping"])
        self.assertTrue(payload["claim_boundary"]["rt_graph_1a2_generic_rt_mapping"])
        self.assertTrue(payload["claim_boundary"]["generic_ray_triangle_rt_core_subpath_authorized"])
        self.assertFalse(payload["claim_boundary"]["paper_reproduction"])
        self.assertFalse(payload["claim_boundary"]["triangle_count_rt_core_claim_authorized"])

    def test_rtdl_id_ascending_adapter_matches_rt_graph_oracle_count(self) -> None:
        payload = _run_app(
            "--mode",
            "rt_graph_rtdl_adapter",
            "--fixture",
            "degree_oriented_two_triangles",
            "--backend",
            "cpu_python_reference",
        )

        self.assertEqual(payload["contract"], "rt_graph_contract_via_id_ascending_adapter")
        self.assertEqual(payload["oracle_triangle_count"], 2)
        self.assertEqual(payload["rtdl_triangle_count"], 2)
        self.assertTrue(payload["triangle_count_matches_oracle"])
        self.assertEqual(
            payload["rtdl_rows"],
            [{"u": 0, "v": 2, "w": 3}, {"u": 1, "v": 2, "w": 3}],
        )
        self.assertFalse(payload["same_contract_native_timing"])

    def test_rt_graph_2a1_generic_rt_mapping_matches_oracle_count(self) -> None:
        payload = _run_app(
            "--mode",
            "rt_graph_2a1_generic_rt",
            "--fixture",
            "degree_oriented_two_triangles",
            "--backend",
            "cpu",
        )

        self.assertEqual(payload["contract"], "rt_graph_2a1_mapped_to_generic_ray_triangle_any_hit")
        self.assertEqual(payload["primitive_layout"]["paper_method"], "RT-2A1")
        self.assertEqual(payload["primitive_count"], 5)
        self.assertEqual(payload["ray_count"], 2)
        self.assertEqual(payload["ray_weights"], [1, 1])
        self.assertEqual(payload["oracle_triangle_count"], 2)
        self.assertEqual(payload["generic_rt_weighted_triangle_count"], 2)
        self.assertTrue(payload["triangle_count_matches_oracle"])
        self.assertEqual(
            payload["hit_rows"],
            [{"any_hit": 1, "ray_id": 0}, {"any_hit": 1, "ray_id": 1}],
        )
        self.assertFalse(payload["authors_code_reproduction"])
        self.assertFalse(payload["same_contract_native_timing"])

    def test_rt_graph_1a2_generic_rt_mapping_matches_oracle_count(self) -> None:
        payload = _run_app(
            "--mode",
            "rt_graph_1a2_generic_rt",
            "--fixture",
            "degree_oriented_two_triangles",
            "--backend",
            "cpu",
        )

        self.assertEqual(payload["contract"], "rt_graph_1a2_mapped_to_generic_ray_triangle_hit_count")
        self.assertEqual(payload["primitive_layout"]["paper_method"], "RT-1A2")
        self.assertEqual(payload["primitive_count"], 2)
        self.assertEqual(payload["ray_count"], 5)
        self.assertEqual(payload["oracle_triangle_count"], 2)
        self.assertEqual(payload["generic_rt_triangle_count"], 2)
        self.assertTrue(payload["triangle_count_matches_oracle"])
        self.assertEqual(
            payload["hit_count_rows"],
            [
                {"hit_count": 0, "ray_id": 0},
                {"hit_count": 0, "ray_id": 1},
                {"hit_count": 1, "ray_id": 2},
                {"hit_count": 0, "ray_id": 3},
                {"hit_count": 1, "ray_id": 4},
            ],
        )
        self.assertFalse(payload["authors_code_reproduction"])
        self.assertFalse(payload["same_contract_native_timing"])

    def test_bulk_3d_packers_preserve_generic_abi_shape(self) -> None:
        try:
            import numpy as np
        except ImportError:
            self.skipTest("numpy is required for bulk 3-D packing")

        triangles = rt.pack_triangles_3d_from_arrays(
            ids=np.array([7], dtype=np.uint32),
            x0=[1.0],
            y0=[2.0],
            z0=[3.0],
            x1=[4.0],
            y1=[5.0],
            z1=[6.0],
            x2=[7.0],
            y2=[8.0],
            z2=[9.0],
        )
        rays = rt.pack_rays_3d_from_arrays(
            ids=np.array([3], dtype=np.uint32),
            ox=[1.0],
            oy=[2.0],
            oz=[3.0],
            dx=[0.0],
            dy=[1.0],
            dz=[0.0],
            tmax=[0.2],
        )

        self.assertEqual(triangles.dimension, 3)
        self.assertEqual(triangles.count, 1)
        self.assertIsNotNone(triangles.owner)
        self.assertEqual(triangles.records[0].id, 7)
        self.assertEqual(triangles.records[0].z2, 9.0)
        self.assertEqual(rays.dimension, 3)
        self.assertEqual(rays.count, 1)
        self.assertIsNotNone(rays.owner)
        self.assertEqual(rays.records[0].id, 3)
        self.assertEqual(rays.records[0].dy, 1.0)

    def test_vectorized_optix_summary_lowering_matches_tuple_geometry(self) -> None:
        try:
            import numpy as np
        except ImportError:
            self.skipTest("numpy is required for vectorized summary lowering")

        contract = build_rt_graph_triangle_contract(fixture_edges("degree_oriented_two_triangles"))

        tuple_triangles_1a2, tuple_rays_1a2 = triangle_app._build_rt_graph_1a2_geometry(contract)
        packed_triangles_1a2, packed_rays_1a2 = triangle_app._build_rt_graph_1a2_packed_geometry(contract)
        self.assertEqual(packed_triangles_1a2.count, len(tuple_triangles_1a2))
        self.assertEqual(packed_rays_1a2.count, len(tuple_rays_1a2))
        self.assertEqual(packed_triangles_1a2.records[0].id, tuple_triangles_1a2[0].id)
        self.assertEqual(packed_triangles_1a2.records[0].x0, tuple_triangles_1a2[0].x0)
        self.assertEqual(packed_triangles_1a2.records[0].z2, tuple_triangles_1a2[0].z2)

        tuple_triangles_2a1, tuple_rays_2a1, tuple_weights_2a1 = triangle_app._build_rt_graph_2a1_geometry(contract)
        packed_triangles_2a1, packed_rays_2a1, packed_weights_2a1 = (
            triangle_app._build_rt_graph_2a1_packed_geometry(contract)
        )
        self.assertIsInstance(packed_weights_2a1, np.ndarray)
        self.assertEqual(packed_triangles_2a1.count, len(tuple_triangles_2a1))
        self.assertEqual(packed_rays_2a1.count, len(tuple_rays_2a1))
        self.assertEqual([int(weight) for weight in packed_weights_2a1.tolist()], list(tuple_weights_2a1))

    def test_cupy_summary_contract_matches_python_contract_when_available(self) -> None:
        try:
            import cupy  # noqa: F401
        except ImportError:
            self.skipTest("cupy is required for partner summary contract")

        for fixture in ("degree_oriented_two_triangles", "duplicates_self_and_leaf"):
            edges = fixture_edges(fixture)
            with self.subTest(fixture=fixture):
                with tempfile.TemporaryDirectory() as tmpdir:
                    path = Path(tmpdir) / "graph.edge"
                    write_binary_edges(path, edges)
                    partner_contract = build_rt_graph_triangle_summary_contract_cupy_binary(path)

                python_contract = build_rt_graph_triangle_contract(edges, include_id_ascending_adapter=False)
                self.assertEqual(partner_contract.partner, "cupy")
                self.assertEqual(partner_contract.triangle_count, python_contract.triangle_count)
                self.assertEqual(
                    partner_contract.directed_edges.tolist(),
                    [list(edge) for edge in python_contract.directed_edges],
                )
                self.assertEqual(partner_contract.row_offsets.tolist(), list(python_contract.row_offsets))
                self.assertEqual(partner_contract.column_indices.tolist(), list(python_contract.column_indices))
                self.assertEqual(
                    partner_contract.two_hop_rays_2a1.tolist(),
                    [list(row) for row in python_contract.two_hop_rays_2a1],
                )
                self.assertIsInstance(partner_contract.device_arrays, dict)
                triangles_2a1, rays_2a1, weights_2a1 = triangle_app._build_rt_graph_2a1_device_geometry(
                    partner_contract
                )
                triangles_1a2, rays_1a2 = triangle_app._build_rt_graph_1a2_device_geometry(partner_contract)
                self.assertEqual(int(triangles_2a1["ids"].size), len(python_contract.directed_edges))
                self.assertEqual(int(rays_2a1["ids"].size), len(python_contract.two_hop_rays_2a1))
                self.assertEqual(int(weights_2a1.size), len(python_contract.two_hop_rays_2a1))
                self.assertEqual(int(rays_1a2["ids"].size), len(python_contract.directed_edges))
                self.assertEqual(int(triangles_1a2["ids"].size), sum(1 for _ in triangle_app._build_rt_graph_1a2_geometry(python_contract)[0]))
                self.assertEqual(
                    partner_contract.removed_low_degree_edge_count,
                    python_contract.removed_low_degree_edge_count,
                )
                self.assertEqual(
                    partner_contract.removed_duplicate_or_self_edge_count,
                    python_contract.removed_duplicate_or_self_edge_count,
                )


if __name__ == "__main__":
    unittest.main()
