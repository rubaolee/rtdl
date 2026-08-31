from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "docs" / "handoff" / "HANDOFF_GEMINI_GOAL3930_REVIEW_GOAL3928_3929_NUMBA_DISCOVERY_PARITY_2026-06-08.md"
REVIEW = ROOT / "docs" / "reviews" / "goal3930_gemini_review_goal3928_3929_numba_discovery_parity_2026-06-08.md"


class Goal3930GeminiReviewGoal3928_3929NumbaDiscoveryParityTest(unittest.TestCase):
    def test_review_accepts_discovery_and_parity_helpers_with_boundary(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("**Verdict:** `accept`", text)
        self.assertIn("avoid creating a second source of truth", text)
        self.assertIn("without auto-selecting a partner", text)
        self.assertIn("six benchmark apps with active Numba references", text)
        self.assertIn("blocked-mode evidence is still awaiting A5000 timing", text)
        self.assertIn("automatic_partner_selection_allowed: False", text)
        self.assertIn("users must choose partners explicitly", text)

    def test_handoff_requested_read_only_review_and_next_gap_is_goal3920(self) -> None:
        handoff = HANDOFF.read_text(encoding="utf-8")
        review = REVIEW.read_text(encoding="utf-8")

        self.assertIn("read-only review", handoff)
        self.assertIn("Goal3928", handoff)
        self.assertIn("Goal3929", handoff)
        self.assertIn("Goal 3920", review)
        self.assertIn("A5000 performance packet", review)


if __name__ == "__main__":
    unittest.main()
