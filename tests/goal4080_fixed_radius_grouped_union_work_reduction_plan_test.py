from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4080_fixed_radius_grouped_union_work_reduction_plan_2026-06-09.md"
HANDOFF = ROOT / "docs" / "handoff" / "HANDOFF_EXTERNAL_REVIEW_GOAL4080_GROUPED_UNION_WORK_REDUCTION_PLAN_2026-06-09.md"


class Goal4080FixedRadiusGroupedUnionWorkReductionPlanTest(unittest.TestCase):
    def test_plan_names_generic_candidate_and_forbids_app_vocabulary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("prepared_fixed_radius_partition_convergence_grouped_union_3d", report)
        self.assertIn("Forbidden in native ABI names and core internals", report)
        self.assertIn("DBSCAN", report)
        self.assertIn("No app-shaped native ABI", report)
        self.assertIn("no hidden dispatch", report)
        self.assertIn("no automatic partner selection", report)

    def test_plan_requires_correctness_performance_and_work_reduction(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in [
            "Same component-size signature as the current grouped-stream route",
            "Beat the current recommended route",
            "Demonstrate at least 50% lower candidate hits or root calls than Goal4079",
            "Fail closed on overflow",
            "production timing, not telemetry timing",
        ]:
            self.assertIn(fragment, report)

    def test_plan_uses_current_evidence_chain(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for goal in ["Goal4071", "Goal4074", "Goal4075", "Goal4078", "Goal4079", "Goal3999", "Goal4014", "Goal4066"]:
            self.assertIn(goal, report)

    def test_external_review_handoff_is_executable(self) -> None:
        handoff = HANDOFF.read_text(encoding="utf-8")
        self.assertIn("goal4081_claude_review_goal4080_grouped_union_work_reduction_plan", handoff)
        self.assertIn("goal4082_gemini_review_goal4080_grouped_union_work_reduction_plan", handoff)
        self.assertIn("Do not mutate source files", handoff)


if __name__ == "__main__":
    unittest.main()
