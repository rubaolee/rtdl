from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONSENSUS = ROOT / "docs" / "reports" / "goal2228_current_rayjoin_same_stream_snapshot_2ai_consensus_2026-05-17.md"
GEMINI = ROOT / "docs" / "reviews" / "goal2227_gemini_review_goal2226_current_rayjoin_same_stream_snapshot_2026-05-17.md"
EVIDENCE = ROOT / "docs" / "reports" / "goal2226_current_rayjoin_same_stream_snapshot_pod_2026-05-17.md"


class Goal2228CurrentRayJoinSameStreamSnapshot2AiConsensusTest(unittest.TestCase):
    def test_consensus_links_snapshot_and_independent_review(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        self.assertIn("Codex + Gemini consensus", text)
        self.assertIn(GEMINI.name, text)
        self.assertIn(EVIDENCE.name, text)
        self.assertIn("Gemini's independent verdict is `accept`", text)

    def test_consensus_records_snapshot_table(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        for value in ("1.367840", "0.084044", "0.109063", "0.091035", "8921", "8686"):
            self.assertIn(value, text)
        self.assertIn("16.28x", text)
        self.assertIn("1.20x", text)

    def test_claim_boundaries_remain_locked(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        for blocked in (
            "RTDL beats RayJoin",
            "broad RT-core speedup",
            "paper-scale RayJoin reproduction",
            "v2.0 release readiness",
        ):
            self.assertIn(blocked, text)

    def test_gemini_review_is_present_and_clear(self) -> None:
        text = GEMINI.read_text(encoding="utf-8")
        self.assertIn("independent external AI reviewer", text)
        self.assertIn("accept", text)
        self.assertIn("no overclaiming found", text)


if __name__ == "__main__":
    unittest.main()
