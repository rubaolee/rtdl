from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "reviews" / "goal2164_gemini_review_goal2163_prepared_optix_lsi_build_reuse_2026-05-16.md"
HANDOFF = ROOT / "docs" / "handoff" / "HANDOFF_GEMINI_GOAL2163_PREPARED_OPTIX_LSI_REVIEW_2026-05-16.md"


class Goal2164GeminiReviewGoal2163PreparedOptixLsiBuildReuseTest(unittest.TestCase):
    def test_review_records_independence_and_bounded_acceptance(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("independent Gemini review", text)
        self.assertIn("distinct from Codex authoring", text)
        self.assertIn("does not by itself authorize v2.0 release", text)
        self.assertIn("`accept-with-boundary`", text)

    def test_review_accepts_generic_surface_and_artifact_support(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("generic and app-agnostic", text)
        self.assertIn("rtdl_optix_prepare_segment_pair_intersection", text)
        self.assertIn("pod artifacts", text)
        self.assertIn("CuPy CUDA-core brute-force baseline", text)

    def test_handoff_named_expected_review_path(self) -> None:
        text = HANDOFF.read_text(encoding="utf-8")

        self.assertIn(
            "docs/reviews/goal2164_gemini_review_goal2163_prepared_optix_lsi_build_reuse_2026-05-16.md",
            text,
        )
        self.assertIn("Goal2163", text)


if __name__ == "__main__":
    unittest.main()
