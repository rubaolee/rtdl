from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONSENSUS = ROOT / "docs" / "reports" / "goal2272_prepared_segment_pair_count_2ai_consensus_2026-05-17.md"
GEMINI = ROOT / "docs" / "reviews" / "goal2271_gemini_review_goal2269_2270_segment_pair_count_2026-05-17.md"
REPORT = ROOT / "docs" / "reports" / "goal2270_prepared_segment_pair_count_probe_2026-05-17.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal2270_prepared_segment_pair_count_probe_pod_2026-05-17.json"


class Goal2272PreparedSegmentPairCount2AiConsensusTest(unittest.TestCase):
    def test_consensus_references_required_artifacts(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn(str(ARTIFACT.relative_to(ROOT)).replace("\\", "/"), text)
        self.assertIn(str(GEMINI.relative_to(ROOT)).replace("\\", "/"), text)
        self.assertIn("Codex + Gemini consensus", text)
        self.assertIn("accept-with-boundary", text)

    def test_gemini_review_accepts_with_boundary(self) -> None:
        text = GEMINI.read_text(encoding="utf-8")

        self.assertIn("Verdict:** accept-with-boundary", text)
        self.assertIn("No blockers identified", text)
        self.assertIn("generic", text)

    def test_consensus_keeps_claims_narrow(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("Still not allowed from this evidence", text)
        self.assertIn("whole RayJoin application speedup", text)
        self.assertIn("RayJoin paper dataset reproduction", text)
        self.assertIn("true zero-copy", text)
        self.assertIn("v2.5+ work", text)

    def test_underlying_report_and_artifact_exist(self) -> None:
        self.assertTrue(REPORT.exists())
        self.assertTrue(ARTIFACT.exists())


if __name__ == "__main__":
    unittest.main()
