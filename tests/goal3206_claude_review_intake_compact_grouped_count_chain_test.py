from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3206_claude_review_intake_compact_grouped_count_chain_2026-06-03.md"
REVIEW = ROOT / "docs" / "reviews" / "goal3202_claude_review_compact_grouped_count_rayjoin_chain_2026-06-03.md"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
GOAL3203 = ROOT / "docs" / "reports" / "goal3203_rayjoin_compact_route_count_only_timing_2026-06-03.md"
GOAL3205 = ROOT / "docs" / "reports" / "goal3205_rayjoin_reusable_compact_route_timing_2026-06-03.md"


class Goal3206ClaudeReviewIntakeCompactGroupedCountChainTest(unittest.TestCase):
    def test_review_exists_and_was_intaken(self) -> None:
        review = REVIEW.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("accept-with-boundary", review)
        self.assertIn("L1", review)
        self.assertIn("L2", review)
        self.assertIn("L3", review)
        self.assertIn("L4", review)
        self.assertIn("No medium-severity", report)
        self.assertIn("does not authorize release", report)

    def test_l1_l2_clarity_debts_are_closed_in_runtime(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")

        self.assertIn("pair-column left_id axis", runtime)
        self.assertIn("direct-address array index as the implicit group key", runtime)
        self.assertIn('"group_key_semantics"', runtime)

    def test_l3_l4_followup_evidence_is_linked(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        goal3203 = GOAL3203.read_text(encoding="utf-8")
        goal3205 = GOAL3205.read_text(encoding="utf-8")

        self.assertIn("Goal3203 records a count-only timing probe", report)
        self.assertIn("Goal3203 and Goal3205", report)
        self.assertIn("include_rows=False", goal3203)
        self.assertIn("reusable prepared-handle timing", report)
        self.assertIn("right-side scene preparation is now paid once", goal3205)


if __name__ == "__main__":
    unittest.main()
