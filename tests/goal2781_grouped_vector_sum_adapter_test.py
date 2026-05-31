from __future__ import annotations

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
PARTNER_ADAPTERS = REPO_ROOT / "src" / "rtdsl" / "partner_adapters.py"
INIT = REPO_ROOT / "src" / "rtdsl" / "__init__.py"
REDUCTIONS = REPO_ROOT / "src" / "rtdsl" / "adapters" / "reductions.py"
REPORT = REPO_ROOT / "docs" / "reports" / "goal2781_grouped_vector_sum_adapter_2026-05-31.md"
CONSENSUS = REPO_ROOT / "docs" / "reports" / "goal2781_grouped_vector_sum_adapter_consensus_2026-05-31.md"
GEMINI_REVIEW = REPO_ROOT / "docs" / "reviews" / "goal2781_gemini_review_grouped_vector_sum_adapter_2026-05-31.md"
CLAUDE_REVIEW = REPO_ROOT / "docs" / "reviews" / "goal2781_claude_review_grouped_vector_sum_adapter_2026-05-31.md"


class Goal2781GroupedVectorSumAdapterTest(unittest.TestCase):
    def test_generic_adapter_is_exported_without_app_specific_engine_path(self) -> None:
        adapters = PARTNER_ADAPTERS.read_text(encoding="utf-8")
        init = INIT.read_text(encoding="utf-8")
        reductions = REDUCTIONS.read_text(encoding="utf-8")

        self.assertIn("def partner_group_vector_sum_2d_by_key", adapters)
        self.assertIn("def grouped_vector_sum_2d_partner_columns", adapters)
        self.assertIn('"grouped_vector_sum_f64x2"', adapters)
        self.assertIn('"not_called_partner_continuation_only"', adapters)
        self.assertIn('"preview_not_promoted"', adapters)
        self.assertIn("partner_group_vector_sum_2d_by_key", init)
        self.assertIn("grouped_vector_sum_2d_partner_columns", init)
        self.assertIn("grouped_vector_sum_2d_partner_columns", reductions)

    def test_report_records_claim_boundary_and_negative_public_flags(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal2781", report)
        self.assertIn("grouped_vector_sum_2d_partner_columns", report)
        self.assertIn("grouped_vector_sum_f64x2", report)
        self.assertIn("preview_not_promoted", report)
        self.assertIn("no public speedup claim", report.lower())
        self.assertIn("no true zero-copy claim", report.lower())

    def test_consensus_records_external_reviews_and_boundary(self) -> None:
        consensus = CONSENSUS.read_text(encoding="utf-8")
        gemini = GEMINI_REVIEW.read_text(encoding="utf-8")
        claude = CLAUDE_REVIEW.read_text(encoding="utf-8")
        self.assertIn("accept-with-boundary", consensus)
        self.assertIn(str(GEMINI_REVIEW.relative_to(REPO_ROOT)).replace("\\", "/"), consensus)
        self.assertIn(str(CLAUDE_REVIEW.relative_to(REPO_ROOT)).replace("\\", "/"), consensus)
        self.assertIn("accept-with-boundary", gemini)
        self.assertIn("accept-with-boundary", claude)
        self.assertIn("Torch remains the better selected partner", consensus)
        self.assertIn("does not authorize", consensus)

    def test_triton_adapter_matches_torch_same_contract_when_cuda_available(self) -> None:
        try:
            import torch
        except ImportError:  # pragma: no cover - depends on local environment
            self.skipTest("torch is not installed")
        if not torch.cuda.is_available():
            self.skipTest("CUDA torch is not available")

        import rtdsl as rt

        group_ids = torch.tensor([0, 0, 1, 2, 2, 2], dtype=torch.int64, device="cuda")
        values_x = torch.tensor([1.5, 2.5, -1.0, 4.0, 5.0, -2.0], dtype=torch.float64, device="cuda")
        values_y = torch.tensor([10.0, -4.0, 3.0, 0.25, 0.75, 1.0], dtype=torch.float64, device="cuda")
        columns = {"group_ids": group_ids, "values_x": values_x, "values_y": values_y}

        triton_result = rt.grouped_vector_sum_2d_partner_columns(
            columns,
            group_count=4,
            partner="triton",
            return_metadata=True,
        )
        torch_result = rt.grouped_vector_sum_2d_partner_columns(
            columns,
            group_count=4,
            partner="torch",
            return_metadata=True,
        )

        expected_x = torch.tensor([4.0, -1.0, 7.0, 0.0], dtype=torch.float64, device="cuda")
        expected_y = torch.tensor([6.0, 3.0, 2.0, 0.0], dtype=torch.float64, device="cuda")
        self.assertTrue(torch.allclose(triton_result["columns"]["sum_x"], expected_x))
        self.assertTrue(torch.allclose(triton_result["columns"]["sum_y"], expected_y))
        self.assertTrue(torch.allclose(triton_result["columns"]["sum_x"], torch_result["columns"]["sum_x"]))
        self.assertTrue(torch.allclose(triton_result["columns"]["sum_y"], torch_result["columns"]["sum_y"]))

        metadata = triton_result["metadata"]
        self.assertEqual(metadata["v2_5_partner_continuation_operation"], "grouped_vector_sum_f64x2")
        self.assertEqual(metadata["v2_5_triton_preview_kernel_status"], "preview_not_promoted")
        self.assertFalse(metadata["direct_device_handoff_authorized"])
        self.assertFalse(metadata["rt_core_speedup_claim_authorized"])
        self.assertFalse(metadata["v2_5_release_authorized"])
        self.assertFalse(metadata["whole_app_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
