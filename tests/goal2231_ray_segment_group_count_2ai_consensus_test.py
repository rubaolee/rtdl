from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
GOAL2229 = ROOT / "docs" / "reports" / "goal2229_ray_segment_group_count_primitive_2026-05-17.md"
GOAL2230 = ROOT / "docs" / "reviews" / "goal2230_gemini_review_goal2229_ray_segment_group_count_primitive_2026-05-17.md"
GOAL2231 = ROOT / "docs" / "reports" / "goal2231_ray_segment_group_count_2ai_consensus_2026-05-17.md"


class Goal2231RaySegmentGroupCount2AIConsensusTest(unittest.TestCase):
    def test_gemini_review_is_present_and_bounded(self) -> None:
        text = GOAL2230.read_text(encoding="utf-8")
        self.assertIn("Independent Gemini Review", text)
        self.assertIn("distinct from Codex", text)
        self.assertIn("Verdict: `accept-with-boundary`", text)
        self.assertIn("host-side aggregation", text)

    def test_consensus_accepts_only_the_narrow_primitive_claim(self) -> None:
        text = GOAL2231.read_text(encoding="utf-8")
        self.assertIn("Status: accepted with boundary", text)
        self.assertIn("Codex and Gemini agree", text)
        self.assertIn("does not prove RTDL beats RayJoin", text)
        self.assertIn("does not close the v2.0 gate", text)
        self.assertIn("app-agnostic vocabulary", text)

    def test_source_report_records_pod_probe(self) -> None:
        text = GOAL2229.read_text(encoding="utf-8")
        self.assertIn("OptiX pod build/probe passed", text)
        self.assertIn("rtdl_optix_run_ray_segment_group_count_2d", text)
        self.assertIn("Observed output", text)


if __name__ == "__main__":
    unittest.main()
