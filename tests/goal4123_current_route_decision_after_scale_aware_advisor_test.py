from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt
from examples.v2_0.research_benchmarks.rt_dbscan.rtdl_rt_dbscan_benchmark_app import (
    explain_rt_dbscan_explicit_route_choice,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4123_current_route_decision_after_scale_aware_advisor_2026-06-09.md"


class Goal4123CurrentRouteDecisionAfterScaleAwareAdvisorTest(unittest.TestCase):
    def test_route_registry_records_scale_aware_tuned_direct_status_guidance(self) -> None:
        route = rt.explain_current_benchmark_route("rt_dbscan")

        self.assertEqual("rtdl.v2_10.current_benchmark_route_decisions.goal4131.v1", route["version"])
        self.assertEqual("mixed_explicit", route["decision_kind"])
        self.assertEqual("mixed_explicit_user_choice", route["partner_policy"])
        self.assertIn("Goal4121", route["current_reader_decision"])
        self.assertIn("Goal4122", route["current_reader_decision"])
        self.assertIn("3.211x", route["current_reader_decision"])
        self.assertIn("1.545x", route["current_reader_decision"])
        self.assertIn("1.399x", route["current_reader_decision"])
        self.assertIn("0.5 at 65k", route["user_choice_guidance"])
        self.assertIn("0.25 at 131k", route["user_choice_guidance"])
        self.assertIn("Do not auto-select", route["user_choice_guidance"])
        self.assertIn("scale-aware", route["next_runtime_action"])
        self.assertIn("65k/131k/262k", route["next_runtime_action"])
        self.assertIn("Goal4121", route["evidence_refs"])
        self.assertIn("Goal4122", route["evidence_refs"])
        self.assertFalse(route["automatic_partner_selection_authorized"])
        self.assertFalse(route["release_authorized"])
        self.assertFalse(route["public_speedup_claim_authorized"])
        self.assertFalse(route["true_zero_copy_claim_authorized"])

    def test_advisor_ranks_ngsim_factor_by_supplied_scale(self) -> None:
        packet_65k = explain_rt_dbscan_explicit_route_choice(
            "ngsim_dense",
            repeated_component_signature=True,
            point_count=65536,
        )
        packet_131k = explain_rt_dbscan_explicit_route_choice(
            "ngsim_dense",
            repeated_component_signature=True,
            point_count=131072,
        )

        self.assertEqual(0.5, packet_65k["options"][0]["partition_cell_factor"])
        self.assertEqual(65536, packet_65k["options"][0]["tested_point_count"])
        self.assertEqual(0.25, packet_131k["options"][0]["partition_cell_factor"])
        self.assertEqual(131072, packet_131k["options"][0]["tested_point_count"])
        self.assertFalse(packet_65k["automatic_partition_cell_factor_selection_authorized"])
        self.assertFalse(packet_131k["automatic_partition_cell_factor_selection_authorized"])

    def test_registry_summary_and_report_stay_non_authorizing(self) -> None:
        summary = rt.summarize_current_benchmark_route_decisions()
        validation = rt.validate_current_benchmark_route_decisions()
        report = REPORT.read_text(encoding="utf-8")

        self.assertEqual("accept", validation["status"])
        self.assertEqual((), validation["errors"])
        self.assertEqual("rtdl.v2_10.current_benchmark_route_decisions.goal4131.v1", summary["version"])
        self.assertFalse(summary["automatic_partner_selection_authorized"])
        self.assertFalse(summary["release_authorized"])
        self.assertFalse(summary["public_speedup_claim_authorized"])
        for fragment in (
            "scale-aware",
            "factor `0.5` best at 65k",
            "factor `0.25` best at 131k",
            "does not authorize automatic factor selection",
            "does not authorize automatic factor selection, hidden dispatch",
        ):
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
