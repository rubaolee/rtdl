import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2316_v2_0_release_prep_pending_final_decision_2026-05-17.md"
RELEASE_NOTE = ROOT / "docs" / "release_reports" / "v2_0_pre_release_candidate.md"


class Goal2316V20ReleasePrepPendingFinalDecisionTest(unittest.TestCase):
    def test_release_prep_waits_for_final_decision(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("prepared-waiting-final-decision", text)
        self.assertIn("not a tag", text)
        self.assertIn("not a tag", text.lower())
        self.assertIn("user's explicit decision", text)
        self.assertIn("final 3-AI v2.0 release consensus", text)
        self.assertIn("Do not create or move a release tag", text)

    def test_release_prep_closes_rayjoin_without_overclaim(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("RayJoin-style project", text)
        self.assertIn("Closed for v2.0 with boundary", text)
        self.assertIn("Do not claim RTDL beats RayJoin", text)
        self.assertIn("true zero-copy beyond measured slices", text)

    def test_learner_release_note_mentions_rayjoin_boundary_briefly(self) -> None:
        text = RELEASE_NOTE.read_text(encoding="utf-8")
        self.assertIn("RayJoin-style LSI/PIP research lane is closed for v2.0", text)
        self.assertIn("not a claim that RTDL beats the RayJoin paper", text)
        self.assertIn("RayJoin closure and final-decision packets", text)


if __name__ == "__main__":
    unittest.main()
