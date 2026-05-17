from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
GOAL2233 = ROOT / "docs" / "reports" / "goal2233_prepared_ray_segment_group_count_2026-05-17.md"
GOAL2235 = ROOT / "docs" / "reports" / "goal2235_prepared_ray_segment_odd_parity_2026-05-17.md"
GOAL2236 = ROOT / "docs" / "reviews" / "goal2236_gemini_review_goal2233_2235_prepared_group_count_2026-05-17.md"
GOAL2237 = ROOT / "docs" / "reports" / "goal2237_prepared_group_count_2ai_consensus_2026-05-17.md"


class Goal2237PreparedGroupCount2AIConsensusTest(unittest.TestCase):
    def test_gemini_review_is_precise_and_bounded(self) -> None:
        text = GOAL2236.read_text(encoding="utf-8")
        self.assertIn("Independent Gemini Review", text)
        self.assertIn("distinct from any Codex review", text)
        self.assertIn("`accept-with-boundary`", text)
        self.assertIn("rtdl_optix_run_prepared_ray_segment_group_odd_parity_2d", text)
        self.assertIn("0.282348s", text)
        self.assertIn("0.031503s", text)
        self.assertNotIn("OptixDbDatasetImpl", text)
        self.assertNotIn("RtdlDbField", text)

    def test_consensus_keeps_claim_boundary(self) -> None:
        text = GOAL2237.read_text(encoding="utf-8")
        self.assertIn("Status: accepted with boundary", text)
        self.assertIn("Codex and Gemini agree", text)
        self.assertIn("does not authorize a RayJoin speedup claim", text)
        self.assertIn("do not close the v2.0 release gate", text)
        self.assertIn("closed-shape membership", text)

    def test_source_reports_record_key_numbers(self) -> None:
        goal2233 = GOAL2233.read_text(encoding="utf-8")
        goal2235 = GOAL2235.read_text(encoding="utf-8")
        self.assertIn("0.8209122363477945", goal2233)
        self.assertIn("20.642437294210346", goal2233)
        self.assertIn("0.28234790451824665", goal2235)
        self.assertIn("8.962546176503611", goal2235)


if __name__ == "__main__":
    unittest.main()
