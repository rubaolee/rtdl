from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "reviews" / "goal1910_gemini_review_v2_release_skeleton_2026-05-13.md"
HANDOFF = ROOT / "docs" / "handoff" / "GOAL1910_GEMINI_REVIEW_V2_RELEASE_SKELETON_2026-05-13.md"


class Goal1910GeminiReviewV2ReleaseSkeletonTest(unittest.TestCase):
    def test_review_accepts_skeleton_without_release_authorization(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("Status: accept", text)
        self.assertIn("not a release packet", text)
        self.assertIn("Hard Missing Slots", text)
        self.assertIn("RTX pod batch execution", text)
        self.assertIn("Fresh external artifact review", text)
        self.assertIn("final 3-AI consensus", text)
        self.assertIn("does not authorize v2.0 release", text)
        self.assertIn("`accept`", text)

    def test_handoff_requested_read_only_single_output_review(self) -> None:
        text = HANDOFF.read_text(encoding="utf-8")

        self.assertIn("read-only review", text)
        self.assertIn("Goal1909 is a skeleton only", text)
        self.assertIn("RTX pod evidence and final 3-AI release consensus are still required", text)
        self.assertIn("docs/reviews/goal1910_gemini_review_v2_release_skeleton_2026-05-13.md", text)
        self.assertIn("Do not edit any file except the requested review file", text)


if __name__ == "__main__":
    unittest.main()
