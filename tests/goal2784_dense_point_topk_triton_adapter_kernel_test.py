from __future__ import annotations

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
TRITON_CONTINUATION = REPO_ROOT / "src" / "rtdsl" / "triton_partner_continuation.py"
PARTNER_ADAPTERS = REPO_ROOT / "src" / "rtdsl" / "partner_adapters.py"
REPORT = REPO_ROOT / "docs" / "reports" / "goal2784_dense_point_topk_triton_adapter_kernel_2026-05-31.md"
CONSENSUS = REPO_ROOT / "docs" / "reports" / "goal2784_dense_point_topk_triton_adapter_kernel_consensus_2026-05-31.md"
CLAUDE_REVIEW = REPO_ROOT / "docs" / "reviews" / "goal2784_claude_review_dense_point_topk_triton_adapter_2026-05-31.md"
GEMINI_REVIEW = REPO_ROOT / "docs" / "reviews" / "goal2784_gemini_review_dense_point_topk_triton_adapter_2026-05-31.md"


class Goal2784DensePointTopKTritonAdapterKernelTest(unittest.TestCase):
    def test_dense_adapter_kernel_is_present_without_rt_traversal_claims(self) -> None:
        continuation = TRITON_CONTINUATION.read_text(encoding="utf-8")
        adapters = PARTNER_ADAPTERS.read_text(encoding="utf-8")

        self.assertIn("def run_triton_dense_point_topk_2d", continuation)
        self.assertIn("def _triton_dense_point_topk_2d_kernel", continuation)
        self.assertIn('"adapter_kernel": TRITON_DENSE_POINT_TOPK_2D_ADAPTER_KERNEL', continuation)
        self.assertIn('"score_materialization": "none"', continuation)
        self.assertIn("run_triton_dense_point_topk_2d", adapters)
        self.assertIn('"v2_5_triton_adapter_kernel"', adapters)
        self.assertIn('"not_called_partner_reference_only"', adapters)

    def test_report_records_bounded_perf_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("Goal2784", report)
        self.assertIn("dense point top-k", report)
        self.assertIn("without dense score materialization", report)
        self.assertIn("does not authorize", report)
        self.assertIn("not an RT-core speedup claim", report)

    def test_consensus_records_external_review_boundary(self) -> None:
        consensus = CONSENSUS.read_text(encoding="utf-8")
        claude = CLAUDE_REVIEW.read_text(encoding="utf-8")
        gemini = GEMINI_REVIEW.read_text(encoding="utf-8")

        self.assertIn("accept-with-boundary", consensus)
        self.assertIn(str(CLAUDE_REVIEW.relative_to(REPO_ROOT)).replace("\\", "/"), consensus)
        self.assertIn(str(GEMINI_REVIEW.relative_to(REPO_ROOT)).replace("\\", "/"), consensus)
        self.assertIn("accept-with-boundary", claude)
        self.assertIn("accept-with-boundary", gemini)
        self.assertIn("Torch remains", consensus)
        self.assertIn("faster", consensus)

    def test_dense_adapter_kernel_matches_torch_same_contract_when_cuda_available(self) -> None:
        try:
            import torch
        except ImportError:  # pragma: no cover
            self.skipTest("torch is not installed")
        if not torch.cuda.is_available():
            self.skipTest("CUDA torch is not available")

        import rtdsl as rt

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

        for key in ("query_ids", "neighbor_ids", "neighbor_rank"):
            self.assertEqual(
                triton_result["columns"][key].detach().cpu().tolist(),
                torch_result["columns"][key].detach().cpu().tolist(),
            )
        self.assertTrue(
            torch.allclose(
                triton_result["columns"]["distances"],
                torch_result["columns"]["distances"],
            )
        )
        self.assertEqual(
            triton_result["metadata"]["v2_5_triton_adapter_kernel"],
            "dense_point_topk_2d_adapter_kernel",
        )
        self.assertEqual(triton_result["metadata"]["v2_5_triton_score_materialization"], "none")
        self.assertFalse(triton_result["metadata"]["rt_core_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
