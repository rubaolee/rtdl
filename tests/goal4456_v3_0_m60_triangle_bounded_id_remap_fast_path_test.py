from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest

import numpy as np

from examples.current.research_benchmarks.triangle_counting import rt_graph_contract as contract_mod


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4456_v3_0_m60_triangle_bounded_id_remap_fast_path_2026-06-16.md"
EVIDENCE = (
    ROOT
    / "docs"
    / "reports"
    / "goal4456_v3_0_m60_triangle_bounded_id_remap_fast_path_200000_2026-06-16.json"
)

routes = importlib.import_module("rtdsl.current_benchmark_route_decisions")


class Goal4456V30M60TriangleBoundedIdRemapFastPathTest(unittest.TestCase):
    def test_bounded_id_helper_accepts_gapped_bounded_ids(self) -> None:
        edges = np.asarray(((0, 2), (2, 4), (0, 4)), dtype=np.int64)
        bounded = contract_mod._try_bounded_id_triangle_summary_inputs_numpy(edges, edges.reshape(-1))

        self.assertIsNotNone(bounded)
        compacted_edges, node_count, degree, dense_label_fast_path = bounded
        self.assertEqual(node_count, 3)
        self.assertFalse(dense_label_fast_path)
        np.testing.assert_array_equal(compacted_edges, np.asarray(((0, 1), (1, 2), (0, 2)), dtype=np.int64))
        np.testing.assert_array_equal(degree, np.asarray((2, 2, 2), dtype=np.int64))

    def test_bounded_id_helper_rejects_sparse_huge_ranges(self) -> None:
        edges = np.asarray(((0, 1_000_000_000),), dtype=np.int64)
        self.assertIsNone(contract_mod._try_bounded_id_triangle_summary_inputs_numpy(edges, edges.reshape(-1)))

    def test_gapped_k4_summary_uses_bounded_but_not_dense_path(self) -> None:
        dense_edges = (
            (0, 1),
            (0, 2),
            (0, 3),
            (1, 2),
            (1, 3),
            (2, 3),
        )
        gapped_edges = np.asarray(tuple((src * 2, dst * 2) for src, dst in dense_edges), dtype=np.int64)
        reference = contract_mod.build_rt_graph_triangle_contract(tuple(map(tuple, gapped_edges.tolist())))
        summary = contract_mod._build_rt_graph_triangle_summary_arrays_numpy(gapped_edges)

        self.assertTrue(summary["bounded_id_remap_fast_path"])
        self.assertFalse(summary["dense_label_fast_path"])
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

    def test_report_evidence_and_route_record_m60_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        route = routes.explain_current_benchmark_route("triangle_counting")

        self.assertIn("Goal4456", report)
        self.assertIn("bounded-id remap", report)
        self.assertIn("does not authorize a triangle-counting RT-core speedup claim", report)
        self.assertEqual(4456, evidence["goal"])
        self.assertEqual("bounded_id_remap_fast_path", evidence["implementation"])
        self.assertTrue(evidence["comparison"]["bounded_id_remap_active"])
        self.assertFalse(evidence["comparison"]["dense_label_fast_path_active"])
        self.assertGreater(evidence["compaction_subphase"]["speedup_vs_old_unique"], 4.0)
        self.assertIn("Goal4456", route["evidence_refs"])
        self.assertIn("bounded-id", route["current_reader_decision"])
        self.assertFalse(route["public_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
