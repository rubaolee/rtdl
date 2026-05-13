from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "docs" / "handoff" / "HANDOFF_EXTERNAL_GOAL1844_V2_VS_V1_8_PERF_READINESS_REVIEW.md"
REVIEW = ROOT / "docs" / "reviews" / "goal1844_claude_review_goal1843_v2_vs_v1_8_perf_readiness_2026-05-13.md"


class Goal1844ExternalReviewGoal1843PerfReadinessTest(unittest.TestCase):
    def test_handoff_records_review_scope_and_expected_output(self) -> None:
        text = HANDOFF.read_text(encoding="utf-8")
        self.assertIn("Goal1844 External Review", text)
        self.assertIn("goal1843_v2_0_vs_v1_8_total_perf_readiness", text)
        self.assertIn("goal1844_claude_review_goal1843_v2_vs_v1_8_perf_readiness", text)
        self.assertIn("Do not edit source files", text)

    def test_claude_review_accepts_goal1843_boundaries_without_release_authorization(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")
        self.assertIn("Reviewer: Claude", text)
        self.assertIn("distinct from Codex and Gemini", text)
        self.assertEqual(text.count("**Verdict: `accept`**"), 5)
        self.assertIn("primitive-level proof, not all-app proof", text)
        self.assertIn("No public app has been rewritten", text)
        self.assertIn("3-AI consensus", text)
        self.assertIn("No finding in this review authorizes v2.0 release", text)


if __name__ == "__main__":
    unittest.main()
