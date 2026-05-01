from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "docs" / "reports"
CLAUDE_REVIEW = REPORTS / "goal967_claude_consensus_compliance_review_2026-04-26.md"
AUDIT_REPORT = REPORTS / "goal967_consensus_compliance_audit_2026-04-26.md"


class Goal967ConsensusExternalAiComplianceTest(unittest.TestCase):
    def test_goal945_through_goal966_have_consensus_files(self) -> None:
        for goal in range(945, 967):
            with self.subTest(goal=goal):
                matches = list(REPORTS.glob(f"goal{goal}_two_ai_consensus_*.md"))
                self.assertTrue(matches, f"missing two-AI consensus for Goal{goal}")

    def test_claude_review_accepts_each_goal(self) -> None:
        text = CLAUDE_REVIEW.read_text(encoding="utf-8")
        self.assertIn("Reviewer: Claude", text)
        self.assertIn("All 22 goals (945\u2013966) **ACCEPT**", text)
        for goal in range(945, 967):
            with self.subTest(goal=goal):
                pattern = rf"\|\s*{goal}\s*\|.*\*\*ACCEPT\*\*"
                self.assertRegex(text, pattern)

    def test_audit_records_strict_requirement_and_remedy(self) -> None:
        text = AUDIT_REPORT.read_text(encoding="utf-8")
        self.assertIn("at least one AI in that consensus chain must be Claude or Gemini", text)
        self.assertIn("did not satisfy the stricter", text)
        self.assertIn("Goal945-966 consensus compliance: PASS after Claude remediation review", text)

    def test_no_block_verdict_in_claude_review(self) -> None:
        text = CLAUDE_REVIEW.read_text(encoding="utf-8")
        self.assertIsNone(re.search(r"\bBLOCK\b", text))


if __name__ == "__main__":
    unittest.main()
