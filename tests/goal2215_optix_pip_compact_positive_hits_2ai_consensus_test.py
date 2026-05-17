from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONSENSUS = ROOT / "docs" / "reports" / "goal2215_optix_pip_compact_positive_hits_2ai_consensus_2026-05-17.md"
GEMINI = ROOT / "docs" / "reviews" / "goal2214_gemini_review_goal2213_optix_pip_compact_pod_2026-05-17.md"
EVIDENCE = ROOT / "docs" / "reports" / "goal2213_optix_pip_compact_positive_hits_pod_2026-05-17.md"


class Goal2215OptixPipCompactPositiveHits2AiConsensusTest(unittest.TestCase):
    def test_consensus_links_evidence_and_independent_review(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        self.assertIn("Codex + Gemini consensus", text)
        self.assertIn(GEMINI.name, text)
        self.assertIn(EVIDENCE.name, text)
        self.assertIn("Codex and Gemini agree", text)
        self.assertIn("Gemini's independent verdict is `accept`", text)

    def test_consensus_records_narrow_performance_result(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        self.assertIn("4.107544 s", text)
        self.assertIn("0.618395 s", text)
        self.assertIn("6.64x", text)
        self.assertIn("8686", text)
        self.assertIn("OptiX still slower than RTDL Embree", text)

    def test_claim_boundaries_remain_locked(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        for blocked in (
            "RTDL beats RayJoin claim",
            "Broad RT-core speedup claim",
            "v2.0 release readiness",
        ):
            self.assertIn(blocked, text)
        self.assertIn("not authorized", text)
        self.assertIn("not a release gate", text)

    def test_gemini_review_is_present_and_clear(self) -> None:
        text = GEMINI.read_text(encoding="utf-8")
        self.assertIn("Goal2214", text)
        self.assertIn("independent external AI reviewer", text)
        self.assertIn("Verdict:** `accept`", text)
        self.assertIn("5.61x", text)


if __name__ == "__main__":
    unittest.main()
