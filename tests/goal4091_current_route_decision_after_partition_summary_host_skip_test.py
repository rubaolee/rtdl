from __future__ import annotations

import pathlib
import unittest

import rtdsl as rt


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4091_current_route_decision_after_partition_summary_host_skip_2026-06-09.md"


class Goal4091CurrentRouteDecisionAfterPartitionSummaryHostSkipTest(unittest.TestCase):
    def test_rtdbscan_route_keeps_current_default_after_goal4088(self) -> None:
        route = rt.explain_current_benchmark_route("rt_dbscan")

        self.assertEqual("rtdl.v2_10.current_benchmark_route_decisions.goal4131.v1", route["version"])
        self.assertIn("unblocked RTDL/OptiX grouped stream plus Numba", route["current_reader_decision"])
        self.assertIn("Goal4088", route["current_reader_decision"])
        self.assertIn("1.6x-2.3x", route["current_reader_decision"])
        self.assertIn("still does not beat the recommended route", route["current_reader_decision"])
        self.assertIn("partition_convergence_hybrid default promotion after Goal4088 host-AABB skip improvement", route["rejected_or_unpromoted_candidates"])
        self.assertIn("partition_convergence_hybrid non-skip default promotion after Goal4093 active-pair stream evidence", route["rejected_or_unpromoted_candidates"])
        self.assertIn("full partition-pair materialization", route["current_reader_decision"])
        self.assertIn("hidden factor selection", route["next_runtime_action"])
        self.assertIn("Goal4088", route["evidence_refs"])
        self.assertIn("Goal4093", route["evidence_refs"])
        self.assertIn("Goal4096", route["evidence_refs"])
        self.assertIn("Goal4105", route["evidence_refs"])
        self.assertIn("Goal4109", route["evidence_refs"])
        self.assertFalse(route["automatic_partner_selection_authorized"])
        self.assertFalse(route["public_speedup_claim_authorized"])

    def test_report_documents_advisory_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in [
            "still use the unblocked RTDL/OptiX grouped stream plus Numba",
            "Goal4088 cuts partition-summary build time by 1.6x-2.3x",
            "clustered break-even drops to 8.48",
            "road still never breaks even",
            "advisory route metadata only",
            "does not authorize release",
        ]:
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()

