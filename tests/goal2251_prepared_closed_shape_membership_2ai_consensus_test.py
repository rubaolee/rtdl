from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONSENSUS = ROOT / "docs" / "reports" / "goal2251_prepared_closed_shape_membership_2ai_consensus_2026-05-17.md"
GEMINI_REVIEW = ROOT / "docs" / "reviews" / "goal2250_gemini_review_goal2248_2249_prepared_closed_shape_2026-05-17.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal2249_rayjoin_pip_prepared_closed_shape_same_query_pod_2026-05-17.json"


class Goal2251PreparedClosedShapeMembership2AiConsensusTest(unittest.TestCase):
    def test_consensus_links_required_artifacts(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("Goal2248", text)
        self.assertIn("Goal2249", text)
        self.assertIn(ARTIFACT.name, text)
        self.assertIn(GEMINI_REVIEW.name, text)
        self.assertIn("9e8c60ef6ae6a1311940b76861fc9a665a52dcc5", text)
        self.assertIn("0.06389576941728592", text)

    def test_gemini_review_is_independent_and_accepts(self) -> None:
        text = GEMINI_REVIEW.read_text(encoding="utf-8")

        self.assertIn("independent Gemini review", text)
        self.assertIn("distinct from any Codex review", text)
        self.assertIn("Verdict: accept", text)

    def test_boundary_excludes_release_and_rayjoin_overclaims(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("does not authorize", text)
        self.assertIn("a claim that RTDL beats RayJoin", text)
        self.assertIn("paper-scale RayJoin speedup claims", text)
        self.assertIn("v2.0 release readiness", text)
        self.assertIn("broad PIP acceleration claims", text)


if __name__ == "__main__":
    unittest.main()
