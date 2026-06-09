from __future__ import annotations

import pathlib
import unittest

import rtdsl as rt


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4083_current_route_decision_after_grouped_union_plan_2026-06-09.md"


class Goal4083CurrentRouteDecisionAfterGroupedUnionPlanTest(unittest.TestCase):
    def test_rtdbscan_route_points_to_grouped_union_work_reduction_plan(self) -> None:
        route = rt.explain_current_benchmark_route("rt_dbscan")

        self.assertEqual("numba_continuation", route["decision_kind"])
        self.assertEqual("numba", route["partner_policy"])
        self.assertIn("Goal4079-4100", route["current_reader_decision"])
        self.assertIn("candidate enumeration", route["current_reader_decision"])
        self.assertIn("root-read", route["current_reader_decision"])
        self.assertIn("Goal4080/4086 generic fixed-radius grouped-union work-reduction", route["next_runtime_action"])
        self.assertIn("production timing that beats the current grouped-stream Numba route", route["next_runtime_action"])
        self.assertIn("Goal4071", route["evidence_refs"])
        self.assertIn("Goal4079", route["evidence_refs"])
        self.assertIn("Goal4080", route["evidence_refs"])
        self.assertIn("Goal4088", route["evidence_refs"])
        self.assertIn("Goal4093", route["evidence_refs"])
        self.assertIn("Goal4096", route["evidence_refs"])
        self.assertFalse(route["automatic_partner_selection_authorized"])
        self.assertFalse(route["release_authorized"])

    def test_report_documents_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in [
            "rtdl.v2_10.current_benchmark_route_decisions.goal4083.v1",
            "still recommends the current accepted route",
            "partition-convergence previews remain",
            "advisory metadata only",
            "does not authorize release",
        ]:
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
