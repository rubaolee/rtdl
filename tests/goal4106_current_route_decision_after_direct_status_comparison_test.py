from __future__ import annotations

import pathlib
import unittest

import rtdsl as rt


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4106_current_route_decision_after_direct_status_comparison_2026-06-09.md"


class Goal4106CurrentRouteDecisionAfterDirectStatusComparisonTest(unittest.TestCase):
    def test_rtdbscan_route_records_direct_status_without_promoting_it(self) -> None:
        route = rt.explain_current_benchmark_route("rt_dbscan")

        self.assertEqual("rtdl.v2_10.current_benchmark_route_decisions.goal4168.v1", route["version"])
        self.assertIn("Goal4104", route["current_reader_decision"])
        self.assertIn("1.239x", route["current_reader_decision"])
        self.assertIn("1.508x", route["current_reader_decision"])
        self.assertIn("1.311x", route["current_reader_decision"])
        self.assertIn("Goal4105", route["current_reader_decision"])
        self.assertIn("not route-promotable", route["current_reader_decision"])
        self.assertIn("0.475x", route["current_reader_decision"])
        self.assertIn("0.380x", route["current_reader_decision"])
        self.assertIn("0.206x", route["current_reader_decision"])
        self.assertIn(
            "partition_convergence_hybrid direct-status app-level promotion after Goal4105 setup-boundary comparison",
            route["rejected_or_unpromoted_candidates"],
        )
        self.assertIn("profile/reuse advisor", route["next_runtime_action"])
        self.assertIn("hidden factor selection", route["next_runtime_action"])
        self.assertIn("Goal4104", route["evidence_refs"])
        self.assertIn("Goal4105", route["evidence_refs"])
        self.assertIn("Goal4108", route["evidence_refs"])
        self.assertIn("Goal4109", route["evidence_refs"])
        self.assertFalse(route["automatic_partner_selection_authorized"])
        self.assertFalse(route["release_authorized"])
        self.assertFalse(route["public_speedup_claim_authorized"])
        self.assertFalse(route["true_zero_copy_claim_authorized"])

    def test_registry_summary_stays_non_authorizing(self) -> None:
        summary = rt.summarize_current_benchmark_route_decisions()
        validation = rt.validate_current_benchmark_route_decisions()

        self.assertEqual("accept", validation["status"])
        self.assertEqual((), validation["errors"])
        self.assertEqual("rtdl.v2_10.current_benchmark_route_decisions.goal4168.v1", summary["version"])
        self.assertEqual(10, summary["row_count"])
        self.assertFalse(summary["automatic_partner_selection_authorized"])
        self.assertFalse(summary["release_authorized"])
        self.assertFalse(summary["public_speedup_claim_authorized"])
        self.assertFalse(summary["broad_rt_core_claim_authorized"])
        self.assertFalse(summary["paper_reproduction_claim_authorized"])

    def test_report_documents_goal4104_goal4105_route_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in [
            "rtdl.v2_10.current_benchmark_route_decisions.goal4106.v1",
            "current route remains",
            "1.239x",
            "1.508x",
            "1.311x",
            "0.475x",
            "0.380x",
            "0.206x",
            "not route-promotable",
            "prepared/resident direct-status fixed-radius grouped-union handle",
            "does not promote",
            "does not authorize release action",
        ]:
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
