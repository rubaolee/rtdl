from __future__ import annotations

import pathlib
import unittest

import rtdsl as rt


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4101_current_route_decision_after_unordered_non_skip_2026-06-09.md"


class Goal4101CurrentRouteDecisionAfterUnorderedNonSkipTest(unittest.TestCase):
    def test_rtdbscan_route_records_goal4100_without_promoting_it(self) -> None:
        route = rt.explain_current_benchmark_route("rt_dbscan")

        self.assertEqual("rtdl.v2_10.current_benchmark_route_decisions.goal4101.v1", route["version"])
        self.assertIn("Goal4100", route["current_reader_decision"])
        self.assertIn("1.13x-1.17x", route["current_reader_decision"])
        self.assertIn("1.38x-2.32x", route["current_reader_decision"])
        self.assertIn("still does not beat the recommended route", route["current_reader_decision"])
        self.assertIn(
            "partition_convergence_hybrid unordered non-skip default promotion after Goal4100 order-insensitive stream evidence",
            route["rejected_or_unpromoted_candidates"],
        )
        self.assertIn("explicit unordered set-stream contracts", route["next_runtime_action"])
        self.assertIn("Goal4100", route["evidence_refs"])
        self.assertFalse(route["automatic_partner_selection_authorized"])
        self.assertFalse(route["release_authorized"])
        self.assertFalse(route["public_speedup_claim_authorized"])

    def test_report_documents_route_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in [
            "rtdl.v2_10.current_benchmark_route_decisions.goal4101.v1",
            "1.13x-1.17x",
            "0.851x",
            "device_atomic_append_unordered",
            "not a replacement for the current route",
            "does not authorize release action",
        ]:
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
