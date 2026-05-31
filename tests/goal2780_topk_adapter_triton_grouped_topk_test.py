from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
REPORT = ROOT / "docs/reports/goal2780_topk_adapter_triton_grouped_topk_2026-05-31.md"
REVIEW = ROOT / "docs/reviews/goal2780_gemini_review_topk_adapter_triton_grouped_topk_2026-05-31.md"
CONSENSUS = ROOT / "docs/reports/goal2780_topk_adapter_triton_grouped_topk_consensus_2026-05-31.md"


def _torch_cuda_available() -> bool:
    try:
        import torch
    except Exception:
        return False
    return bool(torch.cuda.is_available())


def _to_ints(column) -> list[int]:
    if hasattr(column, "detach"):
        return [int(value) for value in column.detach().cpu().tolist()]
    tolist = getattr(column, "tolist", None)
    if callable(tolist):
        return [int(value) for value in tolist()]
    return [int(value) for value in column]


def _to_rounded_floats(column) -> list[float]:
    if hasattr(column, "detach"):
        values = column.detach().cpu().tolist()
    else:
        tolist = getattr(column, "tolist", None)
        values = tolist() if callable(tolist) else list(column)
    return [round(float(value), 12) for value in values]


class Goal2780TopKAdapterTritonGroupedTopKTest(unittest.TestCase):
    def test_adapter_source_routes_triton_through_generic_grouped_topk(self) -> None:
        source = ADAPTERS.read_text(encoding="utf-8")

        self.assertIn('"grouped_topk_f64"', source)
        self.assertIn('"v2_5_partner_continuation_operation"', source)
        self.assertIn('"v2_5_triton_preview_kernel_used"', source)
        self.assertIn('"preview_not_promoted"', source)
        self.assertIn("native_engine_row_contract", source)
        self.assertIn("not_called_partner_reference_only", source)

    def test_triton_topk_adapter_matches_same_contract_torch_reference_when_cuda_available(self) -> None:
        if not _torch_cuda_available():
            self.skipTest("Torch CUDA/Triton execution requires an NVIDIA validation host")

        queries = (
            rt.Point(100, 0.0, 0.0),
            rt.Point(101, 2.0, 0.0),
        )
        candidates = (
            rt.Point(9, 1.0, 0.0),
            rt.Point(5, -1.0, 0.0),
            rt.Point(7, 3.0, 0.0),
        )
        triton_query_columns = rt.point_rows_to_partner_columns(queries, partner="triton")
        triton_candidate_columns = rt.point_rows_to_partner_columns(candidates, partner="triton")
        torch_query_columns = rt.point_rows_to_partner_columns(queries, partner="torch")
        torch_candidate_columns = rt.point_rows_to_partner_columns(candidates, partner="torch")

        triton_result = rt.top_k_nearest_points_2d_partner_columns(
            triton_query_columns,
            triton_candidate_columns,
            k=2,
            partner="triton",
            return_metadata=True,
        )
        torch_result = rt.top_k_nearest_points_2d_partner_columns(
            torch_query_columns,
            torch_candidate_columns,
            k=2,
            partner="torch",
            return_metadata=True,
        )

        triton_columns = triton_result["columns"]
        torch_columns = torch_result["columns"]
        self.assertEqual(_to_ints(triton_columns["query_ids"]), [100, 100, 101, 101])
        self.assertEqual(_to_ints(triton_columns["neighbor_ids"]), [5, 9, 7, 9])
        self.assertEqual(_to_ints(triton_columns["neighbor_rank"]), [1, 2, 1, 2])
        self.assertEqual(_to_rounded_floats(triton_columns["distances"]), [1.0, 1.0, 1.0, 1.0])

        self.assertEqual(_to_ints(triton_columns["query_ids"]), _to_ints(torch_columns["query_ids"]))
        self.assertEqual(_to_ints(triton_columns["neighbor_ids"]), _to_ints(torch_columns["neighbor_ids"]))
        self.assertEqual(_to_ints(triton_columns["neighbor_rank"]), _to_ints(torch_columns["neighbor_rank"]))
        self.assertEqual(_to_rounded_floats(triton_columns["distances"]), _to_rounded_floats(torch_columns["distances"]))

        metadata = triton_result["metadata"]
        self.assertEqual(metadata["partner"], "triton")
        self.assertEqual(metadata["v2_5_partner_continuation_operation"], "grouped_topk_f64")
        self.assertTrue(metadata["v2_5_triton_preview_kernel_used"])
        self.assertEqual(metadata["v2_5_triton_preview_kernel_status"], "preview_not_promoted")
        self.assertFalse(metadata["rt_core_speedup_claim_authorized"])
        self.assertFalse(metadata["whole_app_speedup_claim_authorized"])

    def test_report_review_and_consensus_record_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        review = REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("top_k_nearest_points_2d_partner_columns", report)
        self.assertIn("grouped_topk_f64", report)
        self.assertIn("not an RT-core speedup claim", report)
        self.assertIn("preview_not_promoted", report)
        self.assertIn("accept-with-boundary", review)
        self.assertIn("accept-with-boundary", consensus)


if __name__ == "__main__":
    unittest.main()
