from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
CONSENSUS = ROOT / "docs" / "reports" / "goal3541_v2_8_final_closeout_v2_9_kickoff_3ai_consensus_2026-06-06.md"
GOAL3537 = ROOT / "docs" / "reports" / "goal3537_v2_8_final_internal_closeout_after_10s_evidence_2026-06-06.md"
GOAL3538 = ROOT / "docs" / "reports" / "goal3538_v2_9_performance_first_kickoff_plan_2026-06-06.md"
CLAUDE = ROOT / "docs" / "reviews" / "goal3539_claude_review_v2_8_final_closeout_and_v2_9_kickoff_2026-06-06.md"
GEMINI = ROOT / "docs" / "reviews" / "goal3540_gemini_review_v2_8_final_closeout_and_v2_9_kickoff_2026-06-06.md"


class Goal3541V28FinalCloseoutV29KickoffConsensusTest(unittest.TestCase):
    def test_reviews_exist_and_have_verdicts(self) -> None:
        claude = CLAUDE.read_text(encoding="utf-8").lower()
        gemini = GEMINI.read_text(encoding="utf-8").lower()
        self.assertIn("accept-with-boundary", claude)
        self.assertIn("accept", gemini)

    def test_claude_boundaries_are_incorporated_in_reports(self) -> None:
        goal3537 = GOAL3537.read_text(encoding="utf-8")
        goal3538 = GOAL3538.read_text(encoding="utf-8")
        self.assertIn("median `1.006x`, geomean `0.946x`", goal3537)
        self.assertIn("Hardware continuity is required", goal3538)
        self.assertIn("at", goal3538)
        self.assertIn("least one independent external AI review", goal3538)
        self.assertIn("Workstream 3 starts only after V2.9-G2", goal3538)

    def test_consensus_authorizes_v29_internal_start_only(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        lowered = text.lower()
        self.assertIn("v2.8 is closed internally", lowered)
        self.assertIn("v2.9 is authorized to begin as a performance-first internal development lane", lowered)
        self.assertIn("V2.9-G1", text)
        self.assertIn("V2.9-G2", text)
        self.assertIn("five Goal3536 partial rows", text)
        self.assertIn("accept-with-boundary", text)

    def test_public_claims_remain_blocked(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        lowered = text.lower()
        for phrase in (
            "public v2.8 or v2.9 release wording",
            "public speedup wording",
            "broad RT-core speedup wording",
            "true zero-copy wording",
            "app-specific native-engine shortcuts",
            "hidden partner selection",
        ):
            self.assertIn(phrase, text)
        for forbidden in (
            "release authorized",
            "public speedup claim authorized",
            "true zero-copy authorized",
            "broad rt-core speedup authorized",
        ):
            self.assertNotIn(forbidden, lowered)


if __name__ == "__main__":
    unittest.main()
