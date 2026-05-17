from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "reviews" / "goal2168_gemini_review_goal2167_rayjoin_count512_lsi_evidence_2026-05-16.md"
HANDOFF = ROOT / "docs" / "handoff" / "HANDOFF_GEMINI_GOAL2167_RAYJOIN_COUNT512_LSI_REVIEW_2026-05-16.md"


class Goal2168GeminiReviewGoal2167RayjoinCount512LsiEvidenceTest(unittest.TestCase):
    def test_review_records_independent_acceptance(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("independent Gemini review", text)
        self.assertIn("distinct from Codex authoring", text)
        self.assertIn("does not by itself authorize v2.0 release", text)
        self.assertIn("`accept`", text)

    def test_review_confirms_exact_count512_values_and_boundaries(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("136411275", text)
        self.assertIn("0.021676339209079742", text)
        self.assertIn("0.04105841647833586", text)
        self.assertIn("full RayJoin paper reproduction", text)
        self.assertIn("broad RT-core speedup claims", text)

    def test_handoff_named_expected_review_path(self) -> None:
        text = HANDOFF.read_text(encoding="utf-8")

        self.assertIn(
            "docs/reviews/goal2168_gemini_review_goal2167_rayjoin_count512_lsi_evidence_2026-05-16.md",
            text,
        )
        self.assertIn("Goal2167", text)


if __name__ == "__main__":
    unittest.main()
