from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3537_v2_8_final_internal_closeout_after_10s_evidence_2026-06-06.md"
GOAL3536 = ROOT / "docs" / "reports" / "goal3536_v2_8_vs_v2_3_10s_steady_state_a5000_2026-06-06.md"
GOAL3522 = ROOT / "docs" / "reports" / "goal3522_v2_8_internal_closeout_3ai_consensus_2026-06-05.md"


class Goal3537V28FinalInternalCloseoutAfter10sEvidenceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.text = REPORT.read_text(encoding="utf-8")
        self.lowered = self.text.lower()

    def test_report_links_prior_closeout_and_new_10s_packet(self) -> None:
        self.assertTrue(GOAL3536.exists())
        self.assertTrue(GOAL3522.exists())
        for phrase in ("Goal3522", "Goal3536", "3-AI consensus", "10-second steady-state"):
            self.assertIn(phrase, self.text)

    def test_final_position_is_internal_foundation_not_perf_leap(self) -> None:
        self.assertIn("internally closed", self.lowered)
        self.assertIn("not positioned as a broad performance leap", self.lowered)
        self.assertIn("performance story more honest", self.lowered)
        self.assertIn("v2.9 starts", self.lowered)

    def test_goal3536_numbers_and_raydb_correction_are_recorded(self) -> None:
        for phrase in ("1.187x", "0.973x", "0.998x", "1.055x", "0.464x", "0.894x"):
            self.assertIn(phrase, self.text)
        self.assertIn("RayDB Correction", self.text)
        self.assertIn("not a", self.text)
        self.assertIn("current positive speedup headline", self.text)

    def test_carry_forward_debts_are_explicit(self) -> None:
        for phrase in (
            "Add real repeat hooks or resident benchmark loops",
            "Barnes-Hut node coverage",
            "LibRTS AABB index",
            "spatial RayJoin",
            "Keep RayDB count and sum separate",
        ):
            self.assertIn(phrase, self.text)

    def test_public_boundaries_remain_blocked(self) -> None:
        for phrase in (
            "public v2.8 release wording",
            "public speedup wording",
            "broad RT-core speedup wording",
            "true zero-copy wording",
            "app-specific native-engine shortcuts",
            "hidden partner selection",
        ):
            self.assertIn(phrase, self.text)
        for forbidden in (
            "public speedup claim authorized",
            "v2.8 release authorized",
            "true zero-copy authorized",
            "broad rt-core speedup authorized",
        ):
            self.assertNotIn(forbidden, self.lowered)


if __name__ == "__main__":
    unittest.main()
