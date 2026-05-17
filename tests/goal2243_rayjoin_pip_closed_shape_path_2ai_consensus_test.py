from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONSENSUS = ROOT / "docs" / "reports" / "goal2243_rayjoin_pip_closed_shape_path_2ai_consensus_2026-05-17.md"
REVIEW = ROOT / "docs" / "reviews" / "goal2242_gemini_review_goal2241_rayjoin_pip_closed_shape_path_2026-05-17.md"
REPORT = ROOT / "docs" / "reports" / "goal2241_rayjoin_same_query_pip_closed_shape_path_2026-05-17.md"


class Goal2243RayjoinPipClosedShapePath2AiConsensusTest(unittest.TestCase):
    def test_consensus_links_codex_and_gemini_evidence(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn(str(REVIEW.relative_to(ROOT)).replace("\\", "/"), text)
        self.assertIn(str(REPORT.relative_to(ROOT)).replace("\\", "/"), text)
        self.assertIn("Codex and Gemini agree", text)

    def test_consensus_preserves_claim_boundary(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("full RayJoin reproduction", text)
        self.assertIn("paper-scale performance claims", text)
        self.assertIn("v2.0 release readiness", text)
        self.assertIn("Pod timing from a pushed commit is still required", text)

    def test_gemini_review_accepts_wiring_change(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("independent Gemini review", text)
        self.assertIn("Verdict: `accept`", text)
        self.assertIn("closed_shape_membership_2d_optix", text)


if __name__ == "__main__":
    unittest.main()
