from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
CONSENSUS = ROOT / "docs" / "reports" / "goal2191_rayjoin_pod_evidence_3ai_consensus_2026-05-17.md"
GEMINI = ROOT / "docs" / "reviews" / "goal2189_gemini_review_goal2188_rayjoin_pod_evidence_2026-05-17.md"
CLAUDE = ROOT / "docs" / "reviews" / "goal2190_claude_review_goal2188_rayjoin_pod_evidence_2026-05-17.md"


class Goal2191RayjoinPodEvidence3AiConsensusTest(unittest.TestCase):
    def test_consensus_names_three_distinct_reviewers_and_verdicts(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("Codex", text)
        self.assertIn("Gemini", text)
        self.assertIn("Claude", text)
        self.assertEqual(text.count("`accept-with-boundary`"), 3)
        self.assertIn("3-AI consensus complete", text)

    def test_external_reviews_exist_and_match_boundary(self) -> None:
        gemini = GEMINI.read_text(encoding="utf-8")
        claude = CLAUDE.read_text(encoding="utf-8")

        self.assertIn("accept-with-boundary", gemini)
        self.assertIn("accept-with-boundary", claude)
        self.assertIn("does not claim full paper reproduction", gemini)
        self.assertIn("not RTDL changes", claude)

    def test_consensus_blocks_public_overclaims(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("does not authorize", text)
        self.assertIn("claiming full RayJoin paper reproduction", text)
        self.assertIn("claiming RTDL beats the RayJoin implementation", text)
        self.assertIn("claiming broad RT-core speedup", text)
        self.assertIn("claiming v2.0 release readiness", text)
        self.assertIn("same-contract reproduction run", text)


if __name__ == "__main__":
    unittest.main()
