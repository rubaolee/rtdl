from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4092_external_review_intake_goal4085_4088_partition_summary_chain_2026-06-09.md"
CLAUDE = ROOT / "docs" / "reviews" / "goal4089_claude_review_goal4085_4088_partition_summary_chain_2026-06-09.md"
GEMINI = ROOT / "docs" / "reviews" / "goal4090_gemini_review_goal4085_4088_partition_summary_chain_2026-06-09.md"


class Goal4092ExternalReviewIntakeGoal4085To4088Test(unittest.TestCase):
    def test_reviews_exist_and_use_distinct_ai_systems(self) -> None:
        claude = CLAUDE.read_text(encoding="utf-8")
        gemini = GEMINI.read_text(encoding="utf-8")
        self.assertIn("Reviewer: Claude", claude)
        self.assertIn("Gemini Review", gemini)
        self.assertIn("`accept`", claude)
        self.assertIn("`accept-with-boundary`", gemini)

    def test_consensus_report_records_accept_with_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in [
            "Consensus verdict: `accept-with-boundary`",
            "Goal4088 is a generic runtime improvement",
            "1.6x-2.3x build-time improvement",
            "current RTDL/OptiX grouped stream plus Numba route remains the default",
            "Partition convergence remains explicit and unpromoted",
            "Prepared summary reuse is a repeated-run niche",
            "does not authorize release",
        ]:
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
