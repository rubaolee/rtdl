from __future__ import annotations

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
TRITON_CONTINUATION = REPO_ROOT / "src" / "rtdsl" / "triton_partner_continuation.py"
PARTNER_ADAPTERS = REPO_ROOT / "src" / "rtdsl" / "partner_adapters.py"
REPORT = REPO_ROOT / "docs" / "reports" / "goal2786_batched_vector_sum_offsets_tuning_2026-05-31.md"
CONSENSUS = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2786_batched_vector_sum_offsets_tuning_consensus_2026-05-31.md"
)
GEMINI_REVIEW = (
    REPO_ROOT
    / "docs"
    / "reviews"
    / "goal2786_gemini_review_batched_vector_sum_offsets_tuning_2026-05-31.md"
)
ARTIFACT = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2786_pod_artifacts"
    / "goal2786_batched_vector_sum_offsets_pod_69_30_85_171_2026-05-31.json"
)


class Goal2786BatchedVectorSumOffsetsTuningTest(unittest.TestCase):
    def test_batched_offsets_kernel_is_generic_and_atomic_free(self) -> None:
        continuation = TRITON_CONTINUATION.read_text(encoding="utf-8")
        adapters = PARTNER_ADAPTERS.read_text(encoding="utf-8")

        self.assertIn("TRITON_GROUPED_VECTOR_SUM_F64X2_OFFSETS_BATCHED_KERNEL", continuation)
        self.assertIn("def _triton_grouped_vector_sum_f64x2_offsets_batched_kernel", continuation)
        self.assertIn("tl.static_range(0, GROUPS_PER_PROGRAM)", continuation)
        batched_kernel = continuation.split(
            "def _triton_grouped_vector_sum_f64x2_offsets_batched_kernel",
            1,
        )[1].split("def _triton_segmented_minmax_f64_kernel", 1)[0]
        self.assertNotIn("tl.atomic_add", batched_kernel)
        self.assertIn("triton_offset_groups_per_program", adapters)
        self.assertIn('"v2_5_triton_offset_groups_per_program"', adapters)
        self.assertIn('"v2_5_triton_offset_program_count"', adapters)

    def test_report_and_artifact_keep_negative_boundary(self) -> None:
        import json

        report = REPORT.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")
        review = GEMINI_REVIEW.read_text(encoding="utf-8")
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertIn("accept-with-boundary", report)
        self.assertIn("accept-with-boundary", consensus)
        self.assertIn("accept-with-boundary", review)
        self.assertIn("not promoted", report)
        self.assertIn("not promoted", consensus)
        self.assertIn("Torch remains the faster", report)
        self.assertIn("All tested batched values", report)
        self.assertIn("Triton auto-selection remains blocked", consensus)
        self.assertIn("interpreted honestly", review)
        self.assertFalse(artifact["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertFalse(artifact["claim_boundary"]["rt_core_speedup_claim_authorized"])
        self.assertFalse(artifact["claim_boundary"]["true_zero_copy_claim_authorized"])
        for row in artifact["rows"]:
            self.assertEqual(row["best_batched_offsets"]["groups_per_program"], 1)
            self.assertGreater(row["best_batched_offsets"]["over_torch_ratio"], 1.0)

    def test_batched_offsets_match_torch_when_cuda_available(self) -> None:
        try:
            import torch
        except ImportError:  # pragma: no cover
            self.skipTest("torch is not installed")
        if not torch.cuda.is_available():
            self.skipTest("CUDA torch is not available")

        import rtdsl as rt

        group_count = 5
        group_ids = torch.tensor([0, 0, 1, 2, 2, 2, 4, 4], dtype=torch.int64, device="cuda")
        row_offsets = torch.tensor([0, 2, 3, 6, 6, 8], dtype=torch.int64, device="cuda")
        values_x = torch.tensor([1.0, 2.0, -4.0, 1.5, 2.5, 3.5, 9.0, -1.0], dtype=torch.float64, device="cuda")
        values_y = torch.tensor([0.5, 1.5, 6.0, -1.0, -2.0, 4.0, 3.0, 7.0], dtype=torch.float64, device="cuda")
        triton_result = rt.grouped_vector_sum_2d_partner_columns(
            {
                "group_ids": group_ids,
                "row_offsets": row_offsets,
                "values_x": values_x,
                "values_y": values_y,
            },
            group_count=group_count,
            partner="triton",
            triton_offset_groups_per_program=3,
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
        self.assertEqual(metadata["v2_5_triton_adapter_kernel"], "grouped_vector_sum_f64x2_offsets_batched_kernel")
        self.assertEqual(metadata["v2_5_triton_offset_groups_per_program"], 3)
        self.assertEqual(metadata["v2_5_triton_offset_program_count"], 2)
        self.assertFalse(metadata["v2_5_triton_global_atomic_add_used"])
        self.assertFalse(metadata["rt_core_speedup_claim_authorized"])

    def test_empty_presegmented_offsets_report_program_count_when_cuda_available(self) -> None:
        try:
            import torch
        except ImportError:  # pragma: no cover
            self.skipTest("torch is not installed")
        if not torch.cuda.is_available():
            self.skipTest("CUDA torch is not available")

        import rtdsl as rt

        result = rt.grouped_vector_sum_2d_partner_columns(
            {
                "group_ids": torch.empty((0,), dtype=torch.int64, device="cuda"),
                "row_offsets": torch.tensor([0], dtype=torch.int64, device="cuda"),
                "values_x": torch.empty((0,), dtype=torch.float64, device="cuda"),
                "values_y": torch.empty((0,), dtype=torch.float64, device="cuda"),
            },
            group_count=0,
            partner="triton",
            triton_offset_groups_per_program=4,
            return_metadata=True,
        )

        self.assertEqual(int(result["columns"]["sum_x"].numel()), 0)
        self.assertEqual(result["metadata"]["v2_5_triton_offset_groups_per_program"], 4)
        self.assertEqual(result["metadata"]["v2_5_triton_offset_program_count"], 0)


if __name__ == "__main__":
    unittest.main()
