from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLAUDE = ROOT / "docs" / "reviews" / "goal1846_claude_review_goal1845_witness_contract_2026-05-13.md"
GEMINI = ROOT / "docs" / "reviews" / "goal1846_gemini_review_goal1845_witness_contract_2026-05-13.md"


class Goal1846ExternalReviewsGoal1845WitnessContractTest(unittest.TestCase):
    def test_claude_review_accepts_with_boundary_and_blocks_release_claims(self) -> None:
        text = CLAUDE.read_text(encoding="utf-8")
        self.assertIn("Reviewer: Claude", text)
        self.assertIn("Verdict: `accept-with-boundary`", text)
        self.assertIn("first-hit witness", text)
        self.assertIn("not a full multi-hit row collector", text)
        self.assertIn("v2_0_release_authorized", text)
        self.assertIn("pod validation", text)

    def test_gemini_review_accepts_core_contract_boundaries(self) -> None:
        text = GEMINI.read_text(encoding="utf-8")
        self.assertIn("Reviewer:** Gemini", text)
        self.assertGreaterEqual(text.count("`accept`"), 3)
        self.assertIn("`accept-with-boundary`", text)
        self.assertIn("first-hit witness contract", text)
        self.assertIn("not a full replacement for `segment_polygon_anyhit_rows`", text)
        self.assertIn("needs-more-evidence", text)


if __name__ == "__main__":
    unittest.main()
