from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


REPO_ROOT = Path(__file__).resolve().parents[1]
TRITON_CONTINUATION = REPO_ROOT / "src" / "rtdsl" / "triton_partner_continuation.py"
PARTNER_ADAPTERS = REPO_ROOT / "src" / "rtdsl" / "partner_adapters.py"
REPORT = REPO_ROOT / "docs" / "reports" / "goal2790_tiled_dense_point_nearest_hausdorff_strategy_2026-05-31.md"
REVIEW = REPO_ROOT / "docs" / "reviews" / "goal2790_gemini_review_tiled_dense_point_nearest_hausdorff_strategy_2026-05-31.md"
CONSENSUS = REPO_ROOT / "docs" / "reports" / "goal2790_tiled_dense_point_nearest_hausdorff_strategy_consensus_2026-05-31.md"
ARTIFACT = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2790_pod_artifacts"
    / "goal2790_tiled_dense_point_nearest_hausdorff_pod_69_30_85_171_2026-05-31.json"
)


class Goal2790HausdorffTiledDensePointNearestTest(unittest.TestCase):
    def test_tiled_strategy_is_generic_and_explicit(self) -> None:
        triton_source = TRITON_CONTINUATION.read_text(encoding="utf-8")
        adapter_source = PARTNER_ADAPTERS.read_text(encoding="utf-8")

        self.assertIn("run_triton_dense_point_nearest_2d_tiled", triton_source)
        self.assertIn("dense_point_nearest_2d_tiled_adapter_kernel", triton_source)
        self.assertIn('"dense_point_nearest_tiled"', adapter_source)
        self.assertIn("triton_candidate_block_size", adapter_source)
        self.assertNotIn("hausdorff", triton_source.lower())

    def test_report_and_artifact_record_boundary(self) -> None:
        import json

        report = REPORT.read_text(encoding="utf-8")
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertIn("accept-with-boundary", report)
        self.assertIn("dense_point_nearest_tiled", report)
        self.assertFalse(artifact["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertFalse(artifact["claim_boundary"]["true_zero_copy_claim_authorized"])
        for row in artifact["rows"]:
            self.assertLessEqual(row["best_tiled_distance_error"], 1.0e-12)
            self.assertEqual(row["best_tiled_source_id_match"], True)
            self.assertEqual(row["best_tiled_target_id_match"], True)

    def test_review_and_consensus_record_thresholded_acceptance(self) -> None:
        review = REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("accept-with-boundary", review)
        self.assertIn("thresholded", review)
        self.assertIn("Codex + Gemini", consensus)
        self.assertIn("accept-with-boundary", consensus)
        self.assertIn("16K", consensus)
        self.assertIn("not a blanket speedup claim", consensus)

    def test_tiled_dense_point_nearest_matches_torch_when_cuda_available(self) -> None:
        try:
            import torch
        except ImportError:  # pragma: no cover
            self.skipTest("torch is not installed")
        if not torch.cuda.is_available():
            self.skipTest("CUDA torch is not available")

        source = {
            "ids": torch.tensor([10, 11, 12, 13], dtype=torch.int64, device="cuda"),
            "x": torch.tensor([0.0, 3.0, 6.0, 9.0], dtype=torch.float64, device="cuda"),
            "y": torch.tensor([0.0, 4.0, 0.0, 9.0], dtype=torch.float64, device="cuda"),
        }
        target = {
            "ids": torch.tensor([20, 21, 22, 23, 24], dtype=torch.int64, device="cuda"),
            "x": torch.tensor([0.0, 4.0, 6.0, 8.0, 11.0], dtype=torch.float64, device="cuda"),
            "y": torch.tensor([0.0, 3.0, 1.0, 8.0, 10.0], dtype=torch.float64, device="cuda"),
        }

        tiled_result = rt.directed_hausdorff_2d_partner_columns(
            source,
            target,
            partner="triton",
            triton_strategy="dense_point_nearest_tiled",
            triton_candidate_block_size=2,
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
                tiled_result["columns"]["nearest_distances"],
                torch_result["columns"]["nearest_distances"],
            )
        )
        self.assertEqual(tiled_result["metadata"]["source_id"], torch_result["metadata"]["source_id"])
        self.assertEqual(tiled_result["metadata"]["target_id"], torch_result["metadata"]["target_id"])
        self.assertAlmostEqual(tiled_result["metadata"]["distance"], torch_result["metadata"]["distance"])
        self.assertEqual(tiled_result["metadata"]["v2_5_triton_strategy"], "dense_point_nearest_tiled")
        self.assertEqual(
            tiled_result["metadata"]["v2_5_partner_continuation_operations"],
            ("dense_point_nearest_2d_tiled", "grouped_argmin_f64", "grouped_argmax_f64"),
        )
        self.assertFalse(tiled_result["metadata"]["rt_core_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
