from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3538_v2_9_performance_first_kickoff_plan_2026-06-06.md"
CLAUDE_HANDOFF = ROOT / "docs" / "handoff" / "HANDOFF_CLAUDE_GOAL3537_3538_V2_8_CLOSEOUT_V2_9_PERF_KICKOFF_REVIEW_2026-06-06.md"
GEMINI_HANDOFF = ROOT / "docs" / "handoff" / "HANDOFF_GEMINI_GOAL3537_3538_V2_8_CLOSEOUT_V2_9_PERF_KICKOFF_REVIEW_2026-06-06.md"


class Goal3538V29PerformanceFirstKickoffPlanTest(unittest.TestCase):
    def setUp(self) -> None:
        self.text = REPORT.read_text(encoding="utf-8")
        self.lowered = self.text.lower()

    def test_goal_is_performance_first_and_goal3536_grounded(self) -> None:
        self.assertIn("v2.9 is the performance-first version", self.text)
        self.assertIn("The starting point is Goal3536", self.text)
        self.assertIn("near parity, not a performance leap", self.text)
        self.assertIn("Barnes-Hut and LibRTS remain weak rows", self.text)

    def test_engine_and_partner_rules_are_explicit(self) -> None:
        for phrase in (
            "Primitive-first remains the default",
            "App-specific native-engine code is forbidden",
            "Users choose partners explicitly",
            "must not silently choose",
            "Do not compare evolved contracts as fake same-contract ratios",
        ):
            self.assertIn(phrase, self.text)

    def test_repeat_coverage_targets_all_partial_rows(self) -> None:
        for phrase in (
            "Barnes-Hut node coverage",
            "spatial RayJoin promoted contracts",
            "Hausdorff X-HD threshold",
            "robot collision prepared buffers",
            "LibRTS AABB index",
            "10-second hot-loop evidence",
            "no row is silently partial",
        ):
            self.assertIn(phrase, self.text)

    def test_weak_row_close_rules_are_quantitative(self) -> None:
        for phrase in ("0.464x", "0.894x", "0.95x", "RayDB count/sum", "0.973x / 0.998x"):
            self.assertIn(phrase, self.text)
        self.assertIn("no weak row is hidden behind an average", self.text)

    def test_table_policy_separates_same_and_promoted_contracts(self) -> None:
        self.assertIn("same-contract diagnostic view", self.lowered)
        self.assertIn("promoted-contract view", self.lowered)
        self.assertIn("evolved-contract", self.text)
        self.assertIn("capability-new", self.text)
        self.assertIn("weighting rule is", self.text)
        self.assertIn("written down before measurement", self.text)

    def test_initial_goal_sequence_and_review_handoffs_exist(self) -> None:
        for goal in ("V2.9-G1", "V2.9-G2", "V2.9-G3", "V2.9-G4", "V2.9-G5", "V2.9-G6", "V2.9-G7"):
            self.assertIn(goal, self.text)
        for path, expected in (
            (CLAUDE_HANDOFF, "goal3539_claude_review"),
            (GEMINI_HANDOFF, "goal3540_gemini_review"),
        ):
            handoff = path.read_text(encoding="utf-8")
            self.assertIn(expected, handoff)
            self.assertIn("Do not edit source files", handoff)
            self.assertIn("accept-with-boundary", handoff)

    def test_no_public_claim_authorized(self) -> None:
        self.assertIn("No public release", self.text)
        for forbidden in (
            "release authorized",
            "public speedup claim authorized",
            "true-zero-copy authorized",
            "paper-reproduction claim authorized",
        ):
            self.assertNotIn(forbidden, self.lowered)


if __name__ == "__main__":
    unittest.main()
