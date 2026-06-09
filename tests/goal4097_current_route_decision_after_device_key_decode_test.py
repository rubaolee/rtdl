from __future__ import annotations

import pathlib
import unittest

import rtdsl as rt


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4097_current_route_decision_after_device_key_decode_2026-06-09.md"


class Goal4097CurrentRouteDecisionAfterDeviceKeyDecodeTest(unittest.TestCase):
    def test_rtdbscan_route_records_goal4096_without_promoting_it(self) -> None:
        route = rt.explain_current_benchmark_route("rt_dbscan")

        self.assertEqual("rtdl.v2_10.current_benchmark_route_decisions.goal4115.v1", route["version"])
        self.assertIn("Goal4096", route["current_reader_decision"])
        self.assertIn("1.18x-1.47x", route["current_reader_decision"])
        self.assertIn("still does not beat the recommended route", route["current_reader_decision"])
        self.assertIn(
            "partition_convergence_hybrid default promotion after Goal4096 device key decode improvement",
            route["rejected_or_unpromoted_candidates"],
        )
        self.assertIn("Goal4096", route["evidence_refs"])
        self.assertIn("Goal4105", route["evidence_refs"])
        self.assertIn("Goal4109", route["evidence_refs"])
        self.assertIn("device-resident key decoding", route["next_runtime_action"])
        self.assertFalse(route["automatic_partner_selection_authorized"])
        self.assertFalse(route["release_authorized"])
        self.assertFalse(route["public_speedup_claim_authorized"])

    def test_report_documents_updated_route_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in [
            "Goal4096",
            "1.474x",
            "0.849x",
            "partition-convergence preview remains explicit and unpromoted",
            "does not authorize release action",
        ]:
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()

