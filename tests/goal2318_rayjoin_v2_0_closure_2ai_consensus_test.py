import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONSENSUS = ROOT / "docs" / "reports" / "goal2318_rayjoin_v2_0_closure_and_release_prep_2ai_consensus_2026-05-17.md"
GEMINI = ROOT / "docs" / "reviews" / "goal2317_gemini_review_goal2315_2316_rayjoin_closure_release_prep_2026-05-17.md"
RAYJOIN = ROOT / "docs" / "reports" / "goal2315_rayjoin_v2_0_bounded_closure_2026-05-17.md"
RELEASE_PREP = ROOT / "docs" / "reports" / "goal2316_v2_0_release_prep_pending_final_decision_2026-05-17.md"


class Goal2318RayjoinV20Closure2AiConsensusTest(unittest.TestCase):
    def test_consensus_records_codex_and_gemini_verdicts(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        review = GEMINI.read_text(encoding="utf-8")
        self.assertTrue(RAYJOIN.exists())
        self.assertTrue(RELEASE_PREP.exists())
        self.assertIn("Codex", text)
        self.assertIn("Gemini", text)
        self.assertIn("accept-with-boundary", text)
        self.assertIn("`accept`", review)

    def test_consensus_closes_rayjoin_and_blocks_release_action(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        self.assertIn("RayJoin-style project is closed for the v2.0 release lane", text)
        self.assertIn("pre-release candidate awaiting final decision", text)
        self.assertIn("final release button remains intentionally unpressed", text)
        self.assertIn("claiming RTDL beats RayJoin", text)
        self.assertIn("publishing or tagging v2.0", text)


if __name__ == "__main__":
    unittest.main()
