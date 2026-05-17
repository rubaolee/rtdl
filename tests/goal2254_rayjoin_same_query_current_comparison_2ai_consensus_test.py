from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONSENSUS = ROOT / "docs" / "reports" / "goal2254_rayjoin_same_query_current_comparison_2ai_consensus_2026-05-17.md"
GEMINI_REVIEW = ROOT / "docs" / "reviews" / "goal2253_gemini_review_goal2252_rayjoin_current_comparison_2026-05-17.md"


class Goal2254RayjoinSameQueryCurrentComparison2AiConsensusTest(unittest.TestCase):
    def test_consensus_records_current_table(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("0.08359288796782494", text)
        self.assertIn("0.06329288892447948", text)
        self.assertIn("prepared_closed_shape_membership_2d_optix", text)
        self.assertIn("compiled_rtdl_kernel", text)

    def test_gemini_review_is_independent_acceptance(self) -> None:
        text = GEMINI_REVIEW.read_text(encoding="utf-8")

        self.assertIn("Gemini (independent review, distinct from Codex)", text)
        self.assertIn("`accept`", text)

    def test_boundary_remains_narrow(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("does not authorize full RayJoin reproduction", text)
        self.assertIn("a claim that RTDL", text)
        self.assertIn("v2.0 release readiness", text)
        self.assertIn("without putting app logic into the RTDL engine", text)


if __name__ == "__main__":
    unittest.main()
