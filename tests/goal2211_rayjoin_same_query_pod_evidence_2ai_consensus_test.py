from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONSENSUS = ROOT / "docs" / "reports" / "goal2211_rayjoin_same_query_pod_evidence_2ai_consensus_2026-05-17.md"
GEMINI = ROOT / "docs" / "reviews" / "goal2210_gemini_review_goal2209_rayjoin_same_query_pod_evidence_2026-05-17.md"
EVIDENCE = ROOT / "docs" / "reports" / "goal2209_rayjoin_same_query_pod_evidence_interpretation_2026-05-17.md"


class Goal2211RayJoinSameQueryPodEvidence2AiConsensusTest(unittest.TestCase):
    def test_consensus_links_evidence_and_independent_review(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        self.assertIn("accept-with-boundary", text)
        self.assertIn(GEMINI.name, text)
        self.assertIn(EVIDENCE.name, text)
        self.assertIn("Codex and Gemini agree", text)

    def test_consensus_preserves_claim_boundaries(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        self.assertIn("PIP OptiX is a weak spot", text)
        for blocked in (
            "RTDL beats RayJoin",
            "full RayJoin paper performance study",
            "Broad RT-core speedup",
            "v2.0 release readiness",
        ):
            self.assertIn(blocked, text)
        self.assertIn("diagnostic evidence", text)

    def test_gemini_review_is_present_and_bounded(self) -> None:
        text = GEMINI.read_text(encoding="utf-8")
        self.assertIn("Goal2210", text)
        self.assertIn("accept-with-boundary", text)
        self.assertIn("Timing-Contract Risk", text)
        self.assertIn("PIP OptiX", text)


if __name__ == "__main__":
    unittest.main()
