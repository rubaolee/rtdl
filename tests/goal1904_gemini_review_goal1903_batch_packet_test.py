from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "reviews" / "goal1904_gemini_review_goal1903_batch_packet_2026-05-13.md"


class Goal1904GeminiReviewGoal1903BatchPacketTest(unittest.TestCase):
    def test_review_accepts_batch_packet_with_claim_boundaries(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("Reviewer:** Gemini CLI", text)
        self.assertIn("Goal1903", text)
        self.assertIn("Goal1899", text)
        self.assertIn("fixed-radius", text)
        self.assertIn("segment/polygon", text)
        self.assertIn("road-hazard", text)
        self.assertIn("local GTX-only dry runs", text)
        self.assertIn("claim_boundaries", text)
        self.assertIn("public claims are appropriately constrained", text)
        self.assertIn("`accept`", text)


if __name__ == "__main__":
    unittest.main()
