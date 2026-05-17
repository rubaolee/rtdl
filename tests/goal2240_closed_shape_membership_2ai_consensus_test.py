from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
GOAL2238 = ROOT / "docs" / "reports" / "goal2238_closed_shape_membership_primitive_2026-05-17.md"
GOAL2239 = ROOT / "docs" / "reviews" / "goal2239_gemini_review_goal2238_closed_shape_membership_2026-05-17.md"
GOAL2240 = ROOT / "docs" / "reports" / "goal2240_closed_shape_membership_2ai_consensus_2026-05-17.md"


class Goal2240ClosedShapeMembership2AIConsensusTest(unittest.TestCase):
    def test_gemini_review_accepts_with_boundary(self) -> None:
        text = GOAL2239.read_text(encoding="utf-8")
        self.assertIn("Independent Gemini Review", text)
        self.assertIn("distinct from any Codex review", text)
        self.assertIn("`accept-with-boundary`", text)
        self.assertIn("rtdl_optix_run_point_closed_shape_membership_2d", text)
        self.assertIn("closed_shape_membership_2d_optix", text)

    def test_consensus_records_narrow_claim(self) -> None:
        text = GOAL2240.read_text(encoding="utf-8")
        self.assertIn("Status: accepted with boundary", text)
        self.assertIn("Codex and Gemini agree", text)
        self.assertIn("same performance class", text)
        self.assertIn("does not authorize", text)
        self.assertIn("full RayJoin reproduction claims", text)

    def test_source_report_records_pod_numbers(self) -> None:
        text = GOAL2238.read_text(encoding="utf-8")
        self.assertIn("0.03738784417510033", text)
        self.assertIn("0.03850874863564968", text)
        self.assertIn("0.9708922128019587", text)
        self.assertIn("row_match", text)


if __name__ == "__main__":
    unittest.main()
