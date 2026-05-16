from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "reviews" / "goal2154_gemini_review_goal2153_rayjoin_public_cdb_pod_evidence_2026-05-16.md"


class Goal2154GeminiReviewGoal2153RayjoinPublicCdbPodEvidenceTest(unittest.TestCase):
    def test_review_records_independence_verdict_and_boundary(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        for phrase in (
            "independent Gemini review, distinct from Codex",
            "does not authorize v2.0 release by itself",
            "`accept-with-boundary`",
            "bounded public-sample evidence",
            "cold OptiX costs are real",
            "semantic diagnostic, not a performance win",
            "No. The reports are meticulously crafted",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
