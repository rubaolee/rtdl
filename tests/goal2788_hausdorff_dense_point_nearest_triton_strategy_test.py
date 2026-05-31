from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


REPO_ROOT = Path(__file__).resolve().parents[1]
TRITON_CONTINUATION = REPO_ROOT / "src" / "rtdsl" / "triton_partner_continuation.py"
PARTNER_ADAPTERS = REPO_ROOT / "src" / "rtdsl" / "partner_adapters.py"
REPORT = REPO_ROOT / "docs" / "reports" / "goal2788_dense_point_nearest_hausdorff_strategy_2026-05-31.md"
REVIEW = REPO_ROOT / "docs" / "reviews" / "goal2788_gemini_review_dense_point_nearest_hausdorff_strategy_2026-05-31.md"
CONSENSUS = REPO_ROOT / "docs" / "reports" / "goal2788_dense_point_nearest_hausdorff_strategy_consensus_2026-05-31.md"
ARTIFACT = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2788_pod_artifacts"
    / "goal2788_dense_point_nearest_hausdorff_pod_69_30_85_171_2026-05-31.json"
)


class Goal2788DensePointNearestHausdorffStrategyTest(unittest.TestCase):
    def test_dense_point_nearest_strategy_is_generic(self) -> None:
        triton_source = TRITON_CONTINUATION.read_text(encoding="utf-8")
        adapter_source = PARTNER_ADAPTERS.read_text(encoding="utf-8")

        self.assertIn("run_triton_dense_point_nearest_2d", triton_source)
        self.assertIn("dense_point_nearest_2d_adapter_kernel", triton_source)
        self.assertIn('triton_strategy: str = "generic_score_rows"', adapter_source)
        self.assertIn('"dense_point_nearest"', adapter_source)
        self.assertNotIn("hausdorff", triton_source.lower())

    def test_report_and_artifact_record_bounded_claims(self) -> None:
        import json

        report = REPORT.read_text(encoding="utf-8")
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertIn("accept-with-boundary", report)
        self.assertIn("dense_point_nearest", report)
        self.assertFalse(artifact["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertFalse(artifact["claim_boundary"]["rt_core_speedup_claim_authorized"])
        self.assertFalse(artifact["claim_boundary"]["true_zero_copy_claim_authorized"])
        self.assertFalse(artifact["claim_boundary"]["v2_5_release_authorized"])
        for row in artifact["rows"]:
            self.assertLessEqual(row["distance_error"], 1.0e-12)
            self.assertEqual(row["source_id_match"], True)
            self.assertEqual(row["target_id_match"], True)

    def test_review_and_consensus_record_bounded_acceptance(self) -> None:
        review = REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("accept-with-boundary", review)
        self.assertIn("3.77x to 30.73x slower than Torch", review)
        self.assertIn("Codex + Gemini", consensus)
        self.assertIn("accept-with-boundary", consensus)
        self.assertIn("Goal2788 is faster", consensus)
        self.assertIn("a selected Triton performance path", consensus)

    def test_dense_point_nearest_matches_torch_when_cuda_available(self) -> None:
        try:
            import torch
            from rtdsl.triton_partner_continuation import run_triton_dense_point_nearest_2d
        except ImportError:  # pragma: no cover
            self.skipTest("torch/triton is not installed")
        if not torch.cuda.is_available():
            self.skipTest("CUDA torch is not available")

        query = {
            "ids": torch.tensor([10, 11, 12], dtype=torch.int64, device="cuda"),
            "x": torch.tensor([0.0, 3.0, 6.0], dtype=torch.float64, device="cuda"),
            "y": torch.tensor([0.0, 4.0, 0.0], dtype=torch.float64, device="cuda"),
        }
        candidate = {
            "ids": torch.tensor([20, 21, 22], dtype=torch.int64, device="cuda"),
            "x": torch.tensor([0.0, 4.0, 6.0], dtype=torch.float64, device="cuda"),
            "y": torch.tensor([0.0, 3.0, 1.0], dtype=torch.float64, device="cuda"),
        }

        result = run_triton_dense_point_nearest_2d(
            query["ids"],
            query["x"],
            query["y"],
            candidate["ids"],
            candidate["x"],
            candidate["y"],
        )
        dx = query["x"].reshape(-1, 1) - candidate["x"].reshape(1, -1)
        dy = query["y"].reshape(-1, 1) - candidate["y"].reshape(1, -1)
        scores = dx * dx + dy * dy
        expected_scores, expected_indices = torch.min(scores, dim=1)

        self.assertTrue(torch.equal(result["outputs"]["query_ids"], query["ids"]))
        self.assertTrue(torch.equal(result["outputs"]["neighbor_ids"], candidate["ids"][expected_indices]))
        self.assertTrue(torch.allclose(result["outputs"]["scores"], expected_scores))
        self.assertEqual(result["adapter_kernel"], "dense_point_nearest_2d_adapter_kernel")

    def test_directed_hausdorff_dense_strategy_matches_torch_when_cuda_available(self) -> None:
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

        dense_result = rt.directed_hausdorff_2d_partner_columns(
            source,
            target,
            partner="triton",
            triton_strategy="dense_point_nearest",
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
                dense_result["columns"]["nearest_distances"],
                torch_result["columns"]["nearest_distances"],
            )
        )
        self.assertEqual(dense_result["metadata"]["source_id"], torch_result["metadata"]["source_id"])
        self.assertEqual(dense_result["metadata"]["target_id"], torch_result["metadata"]["target_id"])
        self.assertAlmostEqual(dense_result["metadata"]["distance"], torch_result["metadata"]["distance"])
        self.assertEqual(
            dense_result["metadata"]["v2_5_partner_continuation_operations"],
            ("dense_point_nearest_2d", "grouped_argmax_f64"),
        )
        self.assertEqual(dense_result["metadata"]["v2_5_triton_strategy"], "dense_point_nearest")
        self.assertFalse(dense_result["metadata"]["rt_core_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
