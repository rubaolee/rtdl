from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "reports" / "goal4080_fixed_radius_grouped_union_work_reduction_plan_2026-06-09.md"
INTAKE = ROOT / "docs" / "reports" / "goal4084_goal4080_external_review_intake_2026-06-09.md"
CLAUDE = ROOT / "docs" / "reviews" / "goal4081_claude_review_goal4080_grouped_union_work_reduction_plan_2026-06-09.md"
GEMINI = ROOT / "docs" / "reviews" / "goal4082_gemini_review_goal4080_grouped_union_work_reduction_plan_2026-06-09.md"


class Goal4084Goal4080ExternalReviewIntakeTest(unittest.TestCase):
    def test_external_reviews_exist_and_record_distinct_verdicts(self) -> None:
        claude = CLAUDE.read_text(encoding="utf-8")
        gemini = GEMINI.read_text(encoding="utf-8")
        self.assertIn("Reviewer: Claude", claude)
        self.assertIn("Verdict", claude)
        self.assertIn("accept-with-boundary", claude)
        self.assertIn("Gemini Review", gemini)
        self.assertIn("accept", gemini)

    def test_plan_was_hardened_with_review_findings(self) -> None:
        plan = PLAN.read_text(encoding="utf-8")
        for fragment in [
            "at least 50% lower candidate hits or root calls",
            "ngsim_dense_65536",
            "partition_summary_build_sec",
            "include it in net production-route timing",
            "production timing, not telemetry timing",
        ]:
            self.assertIn(fragment, plan)

    def test_intake_records_consensus_and_next_step(self) -> None:
        intake = INTAKE.read_text(encoding="utf-8")
        for fragment in [
            "Claude verdict: `accept-with-boundary`",
            "Gemini verdict: `accept`",
            "`accept-with-boundary`",
            "Proceed to Goal4081 native/API feasibility",
            "does not authorize implementation promotion",
        ]:
            self.assertIn(fragment, intake)


if __name__ == "__main__":
    unittest.main()
