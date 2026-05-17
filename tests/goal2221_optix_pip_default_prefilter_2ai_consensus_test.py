from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONSENSUS = ROOT / "docs" / "reports" / "goal2221_optix_pip_default_prefilter_2ai_consensus_2026-05-17.md"
GEMINI = ROOT / "docs" / "reviews" / "goal2220_gemini_review_goal2219_optix_pip_default_prefilter_pod_2026-05-17.md"
EVIDENCE = ROOT / "docs" / "reports" / "goal2219_optix_pip_device_prefilter_default_pod_2026-05-17.md"


class Goal2221OptixPipDefaultPrefilter2AiConsensusTest(unittest.TestCase):
    def test_consensus_links_evidence_and_independent_review(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        self.assertIn("Codex + Gemini consensus", text)
        self.assertIn(GEMINI.name, text)
        self.assertIn(EVIDENCE.name, text)
        self.assertIn("Codex and Gemini agree", text)
        self.assertIn("Gemini's independent verdict is `accept`", text)

    def test_consensus_records_default_path_performance_result(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        self.assertIn("0.121710 s", text)
        self.assertIn("33.75x", text)
        self.assertIn("5.08x", text)
        self.assertIn("318.16x", text)
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

    def test_gemini_review_is_present_and_clear(self) -> None:
        text = GEMINI.read_text(encoding="utf-8")
        self.assertIn("Goal2220", text)
        self.assertIn("independent external AI reviewer", text)
        self.assertIn("Verdict: `accept`", text)
        self.assertIn("default path", text)


if __name__ == "__main__":
    unittest.main()
