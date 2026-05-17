from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "reviews" / "goal2160_gemini_review_goal2159_rayjoin_warm_state_audit_2026-05-16.md"
HANDOFF = ROOT / "docs" / "handoff" / "HANDOFF_GEMINI_GOAL2159_RAYJOIN_WARM_STATE_AUDIT_REVIEW_2026-05-16.md"


class Goal2160GeminiReviewGoal2159RayjoinWarmStateAuditTest(unittest.TestCase):
    def test_review_records_independent_boundary_verdict(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("independent Gemini review", text)
        self.assertIn("distinct from Codex", text)
        self.assertIn("does not authorize v2.0 release by itself", text)
        self.assertIn("accept-with-boundary", text)

    def test_review_accepts_conservative_warm_state_narrowing(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("conservative single-case result", text)
        self.assertIn("1.05x", text)
        self.assertIn("5.28x", text)
        self.assertIn("warm-state sensitivity", text)

    def test_handoff_names_expected_output_path(self) -> None:
        text = HANDOFF.read_text(encoding="utf-8")

        self.assertIn("goal2160_gemini_review_goal2159_rayjoin_warm_state_audit_2026-05-16.md", text)
        self.assertIn("public performance interpretation", text)


if __name__ == "__main__":
    unittest.main()
