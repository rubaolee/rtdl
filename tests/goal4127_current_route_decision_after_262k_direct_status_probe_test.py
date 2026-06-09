from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt
from examples.v2_0.research_benchmarks.rt_dbscan.rtdl_rt_dbscan_benchmark_app import (
    explain_rt_dbscan_explicit_route_choice,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4127_current_route_decision_after_262k_direct_status_probe_2026-06-09.md"


class Goal4127CurrentRouteDecisionAfter262kDirectStatusProbeTest(unittest.TestCase):
    def test_route_registry_records_262k_scale_evidence(self) -> None:
        route = rt.explain_current_benchmark_route("rt_dbscan")

        self.assertEqual("rtdl.v2_10.current_benchmark_route_decisions.goal4169.v1", route["version"])
        self.assertEqual("mixed_explicit", route["decision_kind"])
        self.assertEqual("mixed_explicit_user_choice", route["partner_policy"])
        for fragment in ("Goal4126", "3.118x", "1.428x", "1.642x", "131k/262k"):
            self.assertIn(fragment, route["current_reader_decision"] + route["user_choice_guidance"])
        self.assertIn("Goal4126", route["evidence_refs"])
        self.assertFalse(route["automatic_partner_selection_authorized"])
        self.assertFalse(route["release_authorized"])
        self.assertFalse(route["public_speedup_claim_authorized"])
        self.assertFalse(route["true_zero_copy_claim_authorized"])

    def test_advisor_ranks_nearest_262k_scale_first(self) -> None:
        packet = explain_rt_dbscan_explicit_route_choice(
            "ngsim_dense",
            repeated_component_signature=True,
            point_count=262144,
        )
        first = packet["options"][0]
        second = packet["options"][1]

        self.assertEqual(0.25, first["partition_cell_factor"])
        self.assertEqual(262144, first["tested_point_count"])
        self.assertIn("Goal4126", first["evidence_refs"])
        self.assertEqual(0.25, second["partition_cell_factor"])
        self.assertEqual(131072, second["tested_point_count"])
        self.assertFalse(packet["automatic_partition_cell_factor_selection_authorized"])
        self.assertFalse(packet["automatic_dispatch_authorized"])

    def test_registry_summary_and_report_stay_non_authorizing(self) -> None:
        summary = rt.summarize_current_benchmark_route_decisions()
        validation = rt.validate_current_benchmark_route_decisions()
        report = REPORT.read_text(encoding="utf-8")

        self.assertEqual("accept", validation["status"])
        self.assertEqual((), validation["errors"])
        self.assertEqual("rtdl.v2_10.current_benchmark_route_decisions.goal4169.v1", summary["version"])
        self.assertFalse(summary["automatic_partner_selection_authorized"])
        self.assertFalse(summary["release_authorized"])
        self.assertFalse(summary["public_speedup_claim_authorized"])
        for fragment in (
            "262k",
            "factor `0.25`",
            "factor `0.5`",
            "not automatic",
            "does not authorize automatic factor selection",
        ):
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
