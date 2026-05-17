from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
CONSENSUS = ROOT / "docs" / "reports" / "goal2197_rayjoin_export_patch_2ai_consensus_2026-05-17.md"
GEMINI = ROOT / "docs" / "reviews" / "goal2196_gemini_review_goal2195_rayjoin_export_patch_2026-05-17.md"


class Goal2197RayjoinExportPatch2AiConsensusTest(unittest.TestCase):
    def test_consensus_records_two_reviewers_and_verdicts(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("2-AI consensus complete", text)
        self.assertIn("Codex", text)
        self.assertIn("Gemini", text)
        self.assertIn("accept-with-boundary", text)
        self.assertIn("accept", text)

    def test_consensus_keeps_pod_boundary(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("does not claim", text)
        self.assertIn("the patch has compiled on the RTX pod", text)
        self.assertIn("RTDL beats RayJoin", text)
        self.assertIn("ready for pod validation", text)

    def test_gemini_review_accepts_export_fields(self) -> None:
        review = GEMINI.read_text(encoding="utf-8")

        self.assertIn("`accept`", review)
        self.assertIn("unscaled coordinates", review)
        self.assertIn("zero-based query IDs", review)
        self.assertIn("optional export flag", review)


if __name__ == "__main__":
    unittest.main()
