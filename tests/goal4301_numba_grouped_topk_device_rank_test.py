from __future__ import annotations

from pathlib import Path
import json
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
NUMBA_CONTINUATION = ROOT / "src" / "rtdsl" / "numba_partner_continuation.py"
ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
REPORT = ROOT / "docs" / "reports" / "goal4301_numba_grouped_topk_device_rank_2026-06-11.md"
SCALED_ARTIFACT = ROOT / "docs" / "reports" / "goal4301_ann_candidate_numba_device_topk_copies128_local_linux.json"
RUNNER_ARTIFACT = ROOT / "docs" / "reports" / "goal4301_v2_11_rtnn_numba_device_topk_runner_local_linux.json"


def _to_host_ints(column) -> list[int]:
    return [int(value) for value in column.copy_to_host().tolist()]


def _to_host_rounded_floats(column) -> list[float]:
    return [round(float(value), 12) for value in column.copy_to_host().tolist()]


class Goal4301NumbaGroupedTopKDeviceRankTest(unittest.TestCase):
    def test_descriptor_and_protocol_advertise_generic_numba_topk(self) -> None:
        descriptor = rt.describe_numba_grouped_topk_f64()
        self.assertEqual(descriptor["operation"], "grouped_topk_f64")
        self.assertEqual(descriptor["partner"], "numba")
        self.assertEqual(descriptor["layout_precondition"], "equal_contiguous_group_segments")
        self.assertEqual(descriptor["tie_break"], "lowest_score_then_lowest_item_id")
        self.assertFalse(descriptor["host_rank_materialization_used"])
        self.assertIn("grouped_topk_f64", rt.V2_5_NUMBA_PREVIEW_OPERATIONS)
        self.assertEqual(rt.NUMBA_GROUPED_TOPK_F64_OPERATION, "grouped_topk_f64")

    def test_source_contains_device_kernel_and_no_host_rank_path_in_current_adapter(self) -> None:
        source = NUMBA_CONTINUATION.read_text(encoding="utf-8")
        self.assertIn("def run_numba_grouped_topk_f64", source)
        self.assertIn("def _numba_grouped_topk_f64_equal_segments_kernel", source)
        self.assertIn("host_rank_materialization_used", source)
        self.assertIn("False", source)

        adapter_source = ADAPTERS.read_text(encoding="utf-8")
        self.assertIn("grouped_topk_f64_partner_columns(", adapter_source)
        self.assertIn("partner=\"numba\"", adapter_source)
        self.assertIn("device_grouped_topk_after_device_score_rows", adapter_source)
        self.assertIn("numba_grouped_topk_device_rank_used", adapter_source)

    def test_report_and_artifacts_lock_device_rank_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal4301",
            "device_grouped_topk_after_device_score_rows",
            '"host_rank_materialization_used": false',
            "equal_contiguous_group_segments",
            "does not authorize",
        ):
            self.assertIn(phrase, text)

        scaled = json.loads(SCALED_ARTIFACT.read_text(encoding="utf-8"))
        metadata = scaled["approximate_metadata"]
        self.assertEqual(metadata["v2_11_numba_preview_kernel_status"], "device_grouped_topk_after_device_score_rows")
        self.assertTrue(metadata["numba_grouped_topk_device_rank_used"])
        self.assertFalse(metadata["host_rank_materialization_used"])
        self.assertGreaterEqual(metadata["numba_score_row_count"], 100_000)

        runner = json.loads(RUNNER_ARTIFACT.read_text(encoding="utf-8"))
        self.assertTrue(runner["all_pass"])
        self.assertEqual(runner["rows"][0]["row_id"], "rtnn_numba_cpu_partner_quality_reference")
        self.assertIn("device_grouped_topk_after_device_score_rows", runner["rows"][0]["stdout_tail"])

    def test_numba_grouped_topk_matches_contract_when_cuda_available(self) -> None:
        if not rt.numba_partner_available():
            self.skipTest("Numba CUDA is required for executable grouped top-k validation")
        import numpy as np
        from numba import cuda

        group_ids = cuda.to_device(np.asarray([0, 0, 0, 1, 1, 1], dtype=np.int64))
        item_ids = cuda.to_device(np.asarray([9, 5, 7, 8, 7, 11], dtype=np.int64))
        scores = cuda.to_device(np.asarray([1.0, 1.0, 4.0, 4.0, 0.25, 9.0], dtype=np.float64))

        result = rt.run_numba_grouped_topk_f64(
            group_ids,
            item_ids,
            scores,
            group_count=2,
            k=2,
            rows_per_group=3,
        )
        columns = result["outputs"]
        self.assertEqual(_to_host_ints(columns["group_ids"]), [0, 0, 1, 1])
        self.assertEqual(_to_host_ints(columns["item_ids"]), [5, 9, 7, 8])
        self.assertEqual(_to_host_rounded_floats(columns["scores"]), [1.0, 1.0, 0.25, 4.0])
        self.assertEqual(_to_host_ints(columns["ranks"]), [1, 2, 1, 2])
        self.assertEqual(_to_host_ints(columns["row_offsets"]), [0, 2, 4])
        self.assertFalse(result["host_rank_materialization_used"])
        self.assertEqual(result["layout_precondition"], "equal_contiguous_group_segments")

    def test_topk_adapter_uses_device_rank_when_cuda_available(self) -> None:
        if not rt.numba_partner_available():
            self.skipTest("Numba CUDA is required for executable top-k adapter validation")

        queries = (
            rt.Point(100, 0.0, 0.0),
            rt.Point(101, 2.0, 0.0),
        )
        candidates = (
            rt.Point(9, 1.0, 0.0),
            rt.Point(5, -1.0, 0.0),
            rt.Point(7, 3.0, 0.0),
        )
        query_columns = rt.point_rows_to_partner_columns(queries, partner="numba")
        candidate_columns = rt.point_rows_to_partner_columns(candidates, partner="numba")

        result = rt.top_k_nearest_points_2d_partner_columns(
            query_columns,
            candidate_columns,
            k=2,
            partner="numba",
            return_metadata=True,
        )
        columns = result["columns"]
        metadata = result["metadata"]

        self.assertEqual(_to_host_ints(columns["query_ids"]), [100, 100, 101, 101])
        self.assertEqual(_to_host_ints(columns["neighbor_ids"]), [5, 9, 7, 9])
        self.assertEqual(_to_host_ints(columns["neighbor_rank"]), [1, 2, 1, 2])
        self.assertEqual(_to_host_rounded_floats(columns["distances"]), [1.0, 1.0, 1.0, 1.0])
        self.assertEqual(metadata["v2_11_numba_preview_kernel_status"], "device_grouped_topk_after_device_score_rows")
        self.assertTrue(metadata["numba_grouped_topk_device_rank_used"])
        self.assertFalse(metadata["host_rank_materialization_used"])
        self.assertFalse(metadata["rt_core_speedup_claim_authorized"])
        self.assertFalse(metadata["whole_app_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
