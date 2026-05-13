from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "docs" / "handoff" / "GOAL1942_EXTERNAL_REVIEW_ALL_APP_V2_ROLLUP.md"
REVIEW = ROOT / "docs" / "reviews" / "goal1942_gemini_review_all_app_v2_rollup_2026-05-13.md"


class Goal1942GeminiReviewAllAppV2RollupTest(unittest.TestCase):
    def test_handoff_and_review_are_present(self) -> None:
        self.assertTrue(HANDOFF.exists())
        self.assertTrue(REVIEW.exists())

    def test_review_accepts_rollup_with_boundaries(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("independent Gemini review, distinct from Codex", text)
        self.assertIn("`accept-with-boundary`", text)
        self.assertIn('"control": 4, "positive": 11, "positive-subsecond": 1', text)
        self.assertIn("repeat-3 fixed-radius", text)
        self.assertIn("Goal1940 segment any-hit", text)
        self.assertIn("robot subsecond-but-positive", text)
        self.assertIn("control rows", text)
        self.assertIn("v2 partner speedup claims", text)
        self.assertIn("claim boundary remains intact", text)

    def test_review_keeps_remaining_release_work_separate(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("source-tree vs package policy", text)
        self.assertIn("final multi-AI release consensus", text)
        self.assertIn("explicit user release action", text)
        self.assertIn("remaining work required for a full release", text)


if __name__ == "__main__":
    unittest.main()
