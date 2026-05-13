from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "reviews" / "goal1907_gemini_review_v2_boundary_and_source_tree_2026-05-13.md"
HANDOFF = ROOT / "docs" / "handoff" / "GOAL1907_GEMINI_REVIEW_V2_BOUNDARY_AND_SOURCE_TREE_2026-05-13.md"


class Goal1907GeminiReviewV2BoundaryAndSourceTreeTest(unittest.TestCase):
    def test_review_accepts_boundary_with_release_still_blocked(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("Reviewer:** Gemini CLI", text)
        self.assertIn("explicit RTDL primitive calls", text)
        self.assertIn("not accelerating arbitrary PyTorch/CuPy programs", text)
        self.assertIn("3-AI consensus", text)
        self.assertIn("Goal1906", text)
        self.assertIn("no public claims were found to be overly broad", text)
        self.assertIn("v2.0 is still not born", text)
        self.assertIn("pod evidence and final release consensus", text)
        self.assertIn("`accept-with-boundary`", text)

    def test_handoff_requested_read_only_review_and_single_output(self) -> None:
        text = HANDOFF.read_text(encoding="utf-8")

        self.assertIn("read-only review", text)
        self.assertIn("Do not authorize v2.0 release", text)
        self.assertIn("docs/reviews/goal1907_gemini_review_v2_boundary_and_source_tree_2026-05-13.md", text)
        self.assertIn("Do not edit any file except the requested review file", text)


if __name__ == "__main__":
    unittest.main()
