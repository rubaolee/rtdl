from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONSENSUS = ROOT / "docs" / "reports" / "goal2225_optix_pip_one_pass_compact_2ai_consensus_2026-05-17.md"
GEMINI = ROOT / "docs" / "reviews" / "goal2224_gemini_review_goal2223_optix_pip_one_pass_compact_pod_2026-05-17.md"
EVIDENCE = ROOT / "docs" / "reports" / "goal2223_optix_pip_one_pass_compact_pod_2026-05-17.md"


class Goal2225OptixPipOnePassCompact2AiConsensusTest(unittest.TestCase):
    def test_consensus_links_evidence_and_independent_review(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        self.assertIn("Codex + Gemini consensus", text)
        self.assertIn(GEMINI.name, text)
        self.assertIn(EVIDENCE.name, text)
        self.assertIn("Codex and Gemini agree", text)
        self.assertIn("Gemini's independent verdict is `accept`", text)

    def test_consensus_records_one_pass_performance_result(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        self.assertIn("0.090235 s", text)
        self.assertIn("0.109791 s", text)
        self.assertIn("45.52x", text)
        self.assertIn("6.85x", text)
        self.assertIn("1.35x", text)
        self.assertIn("1.22x", text)
        self.assertIn("one_pass=1", text)
        self.assertIn("Fallback chunks", text)

    def test_claim_boundaries_remain_locked(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        for blocked in (
            "RTDL beats RayJoin claim",
            "Broad RT-core speedup claim",
            "v2.0 release readiness",
        ):
            self.assertIn(blocked, text)
        self.assertIn("not authorized", text)

    def test_gemini_review_is_present_and_clear(self) -> None:
        text = GEMINI.read_text(encoding="utf-8")
        self.assertIn("Goal2223", text)
        self.assertIn("Independent External AI Reviewer", text)
        self.assertIn("Verdict: accept", text)
        self.assertIn("RayJoin remains far faster", text)


if __name__ == "__main__":
    unittest.main()
