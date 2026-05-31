from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "reviews" / "goal2824_gemini_review_rtnn_batch_chain_2821_2823_2026-05-31.md"
CONSENSUS = ROOT / "docs" / "reports" / "goal2824_rtnn_batch_chain_consensus_2026-05-31.md"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"


class Goal2824RtnnBatchChainReviewConsensusTest(unittest.TestCase):
    def test_gemini_review_accepts_with_boundary(self) -> None:
        review = REVIEW.read_text(encoding="utf-8")

        self.assertIn("Gemini", review)
        self.assertIn("accept-with-boundary", review)
        self.assertIn("Goal2821", review)
        self.assertIn("Goal2822", review)
        self.assertIn("Goal2823", review)
        self.assertIn("0.990x regression", review)
        self.assertIn("1.020x improvement", review)
        self.assertIn("CUDA Graph Replay", review)
        self.assertIn("Event-Ordered Chaining", review)

    def test_consensus_records_current_default_and_claim_boundary(self) -> None:
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("Codex + Gemini consensus accepts Goal2821-Goal2823 with boundary", consensus)
        self.assertIn("Goal2821 | accept-with-boundary", consensus)
        self.assertIn("Goal2822 | accept-with-boundary", consensus)
        self.assertIn("Goal2823 | reject-as-default", consensus)
        self.assertIn("best current default is the Goal2822", consensus)
        self.assertIn("public RTDL-beats-CuPy wording", consensus)
        self.assertIn("single-request speedup wording", consensus)

    def test_current_main_matches_consensus_default(self) -> None:
        core = CORE.read_text(encoding="utf-8")
        workloads = WORKLOADS.read_text(encoding="utf-8")

        self.assertIn("fixed_radius_neighbors_3d_grid_ranked_summary_aggregate_f32_blocks_batch", core)
        self.assertIn("g_frn3d_grid_ranked_summary_aggregate_f32_blocks_batch", workloads)
        self.assertIn("download(partials.data(), d_partials.ptr, partials.size())", workloads)
        self.assertNotIn("fixed_radius_neighbors_3d_ranked_aggregate_partials_reduce", core)
        self.assertNotIn("g_frn3d_ranked_aggregate_partials_reduce", workloads)


if __name__ == "__main__":
    unittest.main()
