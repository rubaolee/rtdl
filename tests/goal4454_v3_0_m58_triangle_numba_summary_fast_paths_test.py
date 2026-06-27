from __future__ import annotations

import importlib
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from examples.benchmark_apps.triangle_counting import rt_graph_contract as contract_mod


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "examples/benchmark_apps/triangle_counting/rt_graph_contract.py"
REPORT = ROOT / "docs" / "reports" / "goal4454_v3_0_m58_triangle_numba_summary_fast_paths_2026-06-16.md"
EVIDENCE = (
    ROOT
    / "docs"
    / "reports"
    / "goal4454_v3_0_m58_triangle_numba_summary_fast_paths_200000_2026-06-16.json"
)

routes = importlib.import_module("rtdsl.current_benchmark_route_decisions")


def _has_numba_cuda() -> bool:
    try:
        from numba import cuda
    except Exception:
        return False
    try:
        return bool(cuda.is_available())
    except Exception:
        return False


class Goal4454V30M58TriangleNumbaSummaryFastPathsTest(unittest.TestCase):
    def test_dense_label_helper_accepts_dense_and_rejects_gapped_inputs(self) -> None:
        dense_edges = np.asarray(((0, 1), (0, 2), (1, 2)), dtype=np.int64)
        dense = contract_mod._try_dense_label_triangle_summary_inputs_numpy(
            dense_edges,
            dense_edges.reshape(-1),
        )
        self.assertIsNotNone(dense)
        compacted_edges, node_count, degree = dense
        self.assertEqual(node_count, 3)
        np.testing.assert_array_equal(compacted_edges, dense_edges)
        np.testing.assert_array_equal(degree, np.asarray((2, 2, 2), dtype=np.int64))

        gapped_edges = np.asarray(((0, 2), (2, 4)), dtype=np.int64)
        self.assertIsNone(
            contract_mod._try_dense_label_triangle_summary_inputs_numpy(
                gapped_edges,
                gapped_edges.reshape(-1),
            )
        )

    def test_sorted_key_helpers_match_numpy_unique(self) -> None:
        keys = np.asarray((1, 2, 2, 4), dtype=np.int64)
        unique_keys, used_fast_path = contract_mod._unique_int64_keys_numpy(keys)
        counted_keys, counts, counted_fast_path = contract_mod._unique_int64_keys_counts_numpy(keys)

        np.testing.assert_array_equal(unique_keys, np.asarray((1, 2, 4), dtype=np.int64))
        np.testing.assert_array_equal(counted_keys, np.asarray((1, 2, 4), dtype=np.int64))
        np.testing.assert_array_equal(counts, np.asarray((1, 2, 1), dtype=np.int64))
        self.assertTrue(used_fast_path)
        self.assertTrue(counted_fast_path)

        unsorted = np.asarray((2, 1, 2), dtype=np.int64)
        counted_keys, counts, counted_fast_path = contract_mod._unique_int64_keys_counts_numpy(unsorted)
        np.testing.assert_array_equal(counted_keys, np.asarray((1, 2), dtype=np.int64))
        np.testing.assert_array_equal(counts, np.asarray((1, 2), dtype=np.int64))
        self.assertFalse(counted_fast_path)

    def test_dense_k4_summary_uses_fast_paths_and_matches_reference(self) -> None:
        edges = np.asarray(
            (
                (0, 1),
                (0, 2),
                (0, 3),
                (1, 2),
                (1, 3),
                (2, 3),
            ),
            dtype=np.int64,
        )
        reference = contract_mod.build_rt_graph_triangle_contract(tuple(map(tuple, edges.tolist())))
        summary = contract_mod._build_rt_graph_triangle_summary_arrays_numpy(edges)

        self.assertTrue(summary["dense_label_fast_path"])
        self.assertTrue(summary["directed_sorted_unique_fast_path"])
        self.assertTrue(summary["two_hop_sorted_rle_fast_path"])
        self.assertEqual(summary["triangle_count"], reference.triangle_count)
        self.assertEqual(summary["directed_edges"].tolist(), [list(edge) for edge in reference.directed_edges])
        self.assertEqual(summary["row_offsets"].tolist(), list(reference.row_offsets))
        self.assertEqual(summary["column_indices"].tolist(), list(reference.column_indices))
        self.assertEqual(
            summary["two_hop_rays_2a1"].tolist(),
            [list(row) for row in reference.two_hop_rays_2a1],
        )

    @unittest.skipUnless(_has_numba_cuda(), "Numba CUDA device is not available")
    def test_live_numba_binary_builder_exposes_fast_path_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            edge_file = Path(tmp) / "k4.edge"
            contract_mod.write_binary_edges(
                edge_file,
                (
                    (0, 1),
                    (0, 2),
                    (0, 3),
                    (1, 2),
                    (1, 3),
                    (2, 3),
                ),
            )
            summary = contract_mod.build_rt_graph_triangle_summary_contract_numba_binary(edge_file)

        self.assertEqual(summary.triangle_count, 4)
        self.assertTrue(summary.partner_timing_ms["dense_label_fast_path"])
        self.assertTrue(summary.partner_timing_ms["directed_sorted_unique_fast_path"])
        self.assertTrue(summary.partner_timing_ms["two_hop_sorted_rle_fast_path"])

    def test_report_evidence_and_route_record_m58_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        route = routes.explain_current_benchmark_route("triangle_counting")

        self.assertIn("Goal4454", report)
        self.assertIn("Dense nonnegative contiguous vertex labels", report)
        self.assertIn("does not authorize a triangle-counting RT-core speedup claim", report)
        self.assertEqual(4454, evidence["goal"])
        self.assertEqual("numba_summary_fast_paths", evidence["implementation"])
        self.assertTrue(evidence["comparison"]["all_fast_paths_active_on_dense_k4_fixture"])
        self.assertIn("Goal4454", route["evidence_refs"])
        self.assertIn("dense-label", route["current_reader_decision"])
        self.assertFalse(route["public_speedup_claim_authorized"])
        self.assertFalse(route["automatic_partner_selection_authorized"])


if __name__ == "__main__":
    unittest.main()
