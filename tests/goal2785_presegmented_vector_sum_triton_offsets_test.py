from __future__ import annotations

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
TRITON_CONTINUATION = REPO_ROOT / "src" / "rtdsl" / "triton_partner_continuation.py"
PARTNER_ADAPTERS = REPO_ROOT / "src" / "rtdsl" / "partner_adapters.py"
REPORT = REPO_ROOT / "docs" / "reports" / "goal2785_presegmented_vector_sum_triton_offsets_2026-05-31.md"
CONSENSUS = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2785_presegmented_vector_sum_triton_offsets_consensus_2026-05-31.md"
)
GEMINI_REVIEW = (
    REPO_ROOT
    / "docs"
    / "reviews"
    / "goal2785_gemini_review_presegmented_vector_sum_offsets_2026-05-31.md"
)


class Goal2785PresegmentedVectorSumTritonOffsetsTest(unittest.TestCase):
    def test_presegmented_offsets_kernel_is_generic_and_atomic_free(self) -> None:
        continuation = TRITON_CONTINUATION.read_text(encoding="utf-8")
        adapters = PARTNER_ADAPTERS.read_text(encoding="utf-8")

        self.assertIn("def run_triton_grouped_vector_sum_f64x2_by_offsets", continuation)
        self.assertIn("def _triton_grouped_vector_sum_f64x2_offsets_kernel", continuation)
        self.assertIn('"presegmented_row_offsets": True', continuation)
        self.assertIn('"global_atomic_add_used": False', continuation)
        self.assertIn("row_offsets", adapters)
        self.assertIn('"v2_5_triton_presegmented_offsets_used"', adapters)
        self.assertIn('"v2_5_triton_global_atomic_add_used"', adapters)

    def test_report_review_and_consensus_keep_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")
        gemini = GEMINI_REVIEW.read_text(encoding="utf-8")

        self.assertIn("accept-with-boundary", report)
        self.assertIn("accept-with-boundary", consensus)
        self.assertIn("accept-with-boundary", gemini)
        self.assertIn("not promoted", consensus)
        self.assertIn("Torch remains faster", consensus)
        self.assertIn("RT-core, true-zero-copy, whole-app, public speedup, and release claims remain", consensus)
        self.assertIn("without embedding Barnes-Hut/app force logic", gemini)

    def test_presegmented_offsets_match_torch_when_cuda_available(self) -> None:
        try:
            import torch
        except ImportError:  # pragma: no cover
            self.skipTest("torch is not installed")
        if not torch.cuda.is_available():
            self.skipTest("CUDA torch is not available")

        import rtdsl as rt

        group_count = 4
        group_ids = torch.tensor([0, 0, 1, 2, 2, 2], dtype=torch.int64, device="cuda")
        row_offsets = torch.tensor([0, 2, 3, 6, 6], dtype=torch.int64, device="cuda")
        values_x = torch.tensor([1.5, 2.5, -1.0, 4.0, 5.0, -2.0], dtype=torch.float64, device="cuda")
        values_y = torch.tensor([10.0, -4.0, 3.0, 0.25, 0.75, 1.0], dtype=torch.float64, device="cuda")
        columns = {
            "group_ids": group_ids,
            "row_offsets": row_offsets,
            "values_x": values_x,
            "values_y": values_y,
        }
        triton_result = rt.grouped_vector_sum_2d_partner_columns(
            columns,
            group_count=group_count,
            partner="triton",
            return_metadata=True,
        )
        torch_result = rt.grouped_vector_sum_2d_partner_columns(
            {"group_ids": group_ids, "values_x": values_x, "values_y": values_y},
            group_count=group_count,
            partner="torch",
            return_metadata=True,
        )

        self.assertTrue(torch.allclose(triton_result["columns"]["sum_x"], torch_result["columns"]["sum_x"]))
        self.assertTrue(torch.allclose(triton_result["columns"]["sum_y"], torch_result["columns"]["sum_y"]))
        metadata = triton_result["metadata"]
        self.assertTrue(metadata["v2_5_triton_presegmented_offsets_used"])
        self.assertEqual(metadata["v2_5_triton_adapter_kernel"], "grouped_vector_sum_f64x2_offsets_kernel")
        self.assertFalse(metadata["v2_5_triton_global_atomic_add_used"])
        self.assertFalse(metadata["rt_core_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
