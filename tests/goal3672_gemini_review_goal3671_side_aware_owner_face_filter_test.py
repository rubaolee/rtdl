from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "reviews" / "goal3672_gemini_review_goal3671_side_aware_owner_face_filter_2026-06-06.md"


class Goal3672GeminiReviewGoal3671SideAwareOwnerFaceFilterTest(unittest.TestCase):
    def test_review_accepts_goal3671_with_boundaries(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        for phrase in (
            "`accept`",
            "app-agnostic",
            "caller explicitly supplies",
            "duplicate candidate row multiplicity",
            "47264 != 47262",
            "multiset parity",
            "avoid overclaiming",
            "owner-side derivation",
        ):
            self.assertIn(phrase, text)

    def test_review_keeps_claim_boundaries_clear(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        for phrase in (
            "automatic/default route selection",
            "release readiness",
            "RTDL-beats-RayJoin",
            "broad RT-core speedup",
            "true zero-copy",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
