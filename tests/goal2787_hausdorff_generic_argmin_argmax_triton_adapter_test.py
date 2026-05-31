from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


REPO_ROOT = Path(__file__).resolve().parents[1]
PARTNER_ADAPTERS = REPO_ROOT / "src" / "rtdsl" / "partner_adapters.py"
TRITON_CONTINUATION = REPO_ROOT / "src" / "rtdsl" / "triton_partner_continuation.py"
REPORT = REPO_ROOT / "docs" / "reports" / "goal2787_hausdorff_generic_argmin_argmax_triton_adapter_2026-05-31.md"
REVIEW = (
    REPO_ROOT
    / "docs"
    / "reviews"
    / "goal2787_gemini_review_hausdorff_generic_argmin_argmax_triton_adapter_2026-05-31.md"
)
CONSENSUS = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2787_hausdorff_generic_argmin_argmax_triton_adapter_consensus_2026-05-31.md"
)
ARTIFACT = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2787_pod_artifacts"
    / "goal2787_hausdorff_generic_argmin_argmax_pod_69_30_85_171_2026-05-31.json"
)


class Goal2787HausdorffGenericArgminArgmaxTritonAdapterTest(unittest.TestCase):
    def test_generic_adapter_is_available_and_not_hausdorff_shaped(self) -> None:
        source = PARTNER_ADAPTERS.read_text(encoding="utf-8")
        triton_source = TRITON_CONTINUATION.read_text(encoding="utf-8")

        self.assertTrue(hasattr(rt, "group_argmin_then_global_argmax_partner_columns"))
        self.assertIn("def group_argmin_then_global_argmax_partner_columns", source)
        self.assertIn("run_triton_grouped_argmin_f64", source)
        self.assertIn("run_triton_grouped_argmax_f64", source)
        self.assertNotIn("hausdorff", triton_source.lower())

    def test_report_and_artifact_keep_negative_boundary(self) -> None:
        import json

        report = REPORT.read_text(encoding="utf-8")
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertIn("accept-with-boundary", report)
        self.assertIn("correct but not competitive", report)
        self.assertIn("auto-selecting Triton", report)
        self.assertFalse(artifact["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertFalse(artifact["claim_boundary"]["rt_core_speedup_claim_authorized"])
        self.assertFalse(artifact["claim_boundary"]["true_zero_copy_claim_authorized"])
        for row in artifact["rows"]:
            self.assertGreater(row["triton_over_torch_ratio"], 1.0)
            self.assertEqual(row["max_nearest_distance_error"], 0.0)

    def test_review_and_consensus_record_boundary(self) -> None:
        review = REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("accept-with-boundary", review)
        self.assertIn("31.880x to 45.145x", review)
        self.assertIn("Do not auto-select Triton", review)
        self.assertIn("Codex + Gemini", consensus)
        self.assertIn("accept-with-boundary", consensus)
        self.assertIn("negative performance evidence", consensus)
        self.assertIn("not a v2.5 release gate closure", consensus)

    def test_generic_argmin_argmax_matches_torch_when_cuda_available(self) -> None:
        try:
            import torch
        except ImportError:  # pragma: no cover
            self.skipTest("torch is not installed")
        if not torch.cuda.is_available():
            self.skipTest("CUDA torch is not available")

        group_ids = torch.tensor([0, 0, 1, 1, 2, 2], dtype=torch.int64, device="cuda")
        item_ids = torch.tensor([5, 4, 9, 8, 7, 6], dtype=torch.int64, device="cuda")
        scores = torch.tensor([2.0, 2.0, 5.0, 4.0, 4.0, 4.0], dtype=torch.float64, device="cuda")

        triton_result = rt.group_argmin_then_global_argmax_partner_columns(
            {"group_ids": group_ids, "item_ids": item_ids, "scores": scores},
            group_count=3,
            partner="triton",
            return_metadata=True,
        )
        torch_result = rt.group_argmin_then_global_argmax_partner_columns(
            {"group_ids": group_ids, "item_ids": item_ids, "scores": scores},
            group_count=3,
            partner="torch",
            return_metadata=True,
        )

        self.assertTrue(
            torch.allclose(
                triton_result["columns"]["argmin_scores"],
                torch_result["columns"]["argmin_scores"],
            )
        )
        self.assertEqual(triton_result["metadata"]["winner_group_id"], 1)
        self.assertEqual(triton_result["metadata"]["winner_item_id"], 8)
        self.assertEqual(triton_result["metadata"]["winner_score"], 4.0)
        self.assertEqual(
            triton_result["metadata"]["v2_5_partner_continuation_operations"],
            ("grouped_argmin_f64", "grouped_argmax_f64"),
        )
        self.assertFalse(triton_result["metadata"]["rt_core_speedup_claim_authorized"])

    def test_directed_hausdorff_triton_matches_torch_when_cuda_available(self) -> None:
        try:
            import torch
        except ImportError:  # pragma: no cover
            self.skipTest("torch is not installed")
        if not torch.cuda.is_available():
            self.skipTest("CUDA torch is not available")

        source = {
            "ids": torch.tensor([10, 11, 12], dtype=torch.int64, device="cuda"),
            "x": torch.tensor([0.0, 3.0, 6.0], dtype=torch.float64, device="cuda"),
            "y": torch.tensor([0.0, 4.0, 0.0], dtype=torch.float64, device="cuda"),
        }
        target = {
            "ids": torch.tensor([20, 21], dtype=torch.int64, device="cuda"),
            "x": torch.tensor([0.0, 4.0], dtype=torch.float64, device="cuda"),
            "y": torch.tensor([0.0, 3.0], dtype=torch.float64, device="cuda"),
        }

        triton_result = rt.directed_hausdorff_2d_partner_columns(
            source,
            target,
            partner="triton",
            return_metadata=True,
        )
        torch_result = rt.directed_hausdorff_2d_partner_columns(
            source,
            target,
            partner="torch",
            return_metadata=True,
        )

        self.assertTrue(
            torch.allclose(
                triton_result["columns"]["nearest_distances"],
                torch_result["columns"]["nearest_distances"],
            )
        )
        self.assertEqual(triton_result["metadata"]["source_id"], torch_result["metadata"]["source_id"])
        self.assertEqual(triton_result["metadata"]["target_id"], torch_result["metadata"]["target_id"])
        self.assertAlmostEqual(triton_result["metadata"]["distance"], torch_result["metadata"]["distance"])
        self.assertEqual(
            triton_result["metadata"]["v2_5_partner_continuation_operations"],
            ("grouped_argmin_f64", "grouped_argmax_f64"),
        )
        self.assertEqual(triton_result["metadata"]["v2_5_triton_preview_kernel_status"], "preview_not_promoted")
        self.assertFalse(triton_result["metadata"]["whole_app_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
