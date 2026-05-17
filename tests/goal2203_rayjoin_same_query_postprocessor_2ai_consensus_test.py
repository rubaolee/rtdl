from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
CONSENSUS = ROOT / "docs" / "reports" / "goal2203_rayjoin_same_query_postprocessor_2ai_consensus_2026-05-17.md"
REVIEW = ROOT / "docs" / "reviews" / "goal2202_gemini_review_goal2201_rayjoin_same_query_postprocessor_2026-05-17.md"
SCRIPT = ROOT / "scripts" / "goal2201_rayjoin_same_query_evidence_report.py"


class Goal2203RayJoinSameQueryPostprocessorConsensusTest(unittest.TestCase):
    def test_consensus_references_review_and_accepts_with_boundary(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("Codex and Gemini agree", text)
        self.assertIn(str(REVIEW.relative_to(ROOT)).replace("\\", "/"), text)
        self.assertIn("accept-with-boundary", text)
        self.assertIn("tooling only", text)
        self.assertIn("does not authorize", text)
        self.assertIn("v2.0 release readiness", text)

    def test_consensus_records_review_followup_fix(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("missing required RayJoin log", text)
        self.assertIn("missing required RTDL same-stream artifact", text)
        self.assertIn("_read_required_text", script)
        self.assertIn("missing required", script)

    def test_gemini_review_exists(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("Goal2202 Gemini Review", text)
        self.assertIn("accept-with-boundary", text)
        self.assertIn("Goal2201", text)


if __name__ == "__main__":
    unittest.main()
