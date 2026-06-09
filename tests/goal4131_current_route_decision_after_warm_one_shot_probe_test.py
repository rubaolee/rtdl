from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt
from examples.v2_0.research_benchmarks.rt_dbscan.rtdl_rt_dbscan_benchmark_app import (
    RT_DBSCAN_DIRECT_STATUS_APP_MODE,
    explain_rt_dbscan_explicit_route_choice,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4131_current_route_decision_after_warm_one_shot_probe_2026-06-09.md"


class Goal4131CurrentRouteDecisionAfterWarmOneShotProbeTest(unittest.TestCase):
    def test_advisor_exposes_one_shot_direct_status_without_dispatch(self) -> None:
        packet = explain_rt_dbscan_explicit_route_choice(
            "ngsim_dense",
            repeated_component_signature=False,
            point_count=262144,
        )
        first = packet["options"][0]

        self.assertEqual(RT_DBSCAN_DIRECT_STATUS_APP_MODE, first["mode"])
        self.assertEqual("cupy", first["partner"])
        self.assertEqual(0.25, first["partition_cell_factor"])
        self.assertEqual(262144, first["tested_point_count"])
        self.assertGreater(first["one_shot_total_speedup_vs_current"], 2.9)
        self.assertIn("Goal4130", first["evidence_refs"])
        self.assertIn("one-shot", first["when"])
        self.assertFalse(packet["automatic_dispatch_authorized"])
        self.assertFalse(packet["automatic_partner_selection_authorized"])
        self.assertFalse(packet["automatic_partition_cell_factor_selection_authorized"])

    def test_route_registry_records_one_shot_evidence_without_auto_promotion(self) -> None:
        route = rt.explain_current_benchmark_route("rt_dbscan")

        self.assertEqual("rtdl.v2_10.current_benchmark_route_decisions.goal4131.v1", route["version"])
        self.assertEqual("mixed_explicit", route["decision_kind"])
        self.assertEqual("mixed_explicit_user_choice", route["partner_policy"])
        for fragment in ("Goal4130", "one-shot", "1.819x", "3.410x", "Do not auto-select"):
            self.assertIn(fragment, route["current_reader_decision"] + route["user_choice_guidance"])
        self.assertIn("Goal4130", route["evidence_refs"])
        self.assertTrue(
            any(
                "automatic one-shot route promotion" in candidate
                for candidate in route["rejected_or_unpromoted_candidates"]
            )
        )
        self.assertFalse(route["automatic_partner_selection_authorized"])
        self.assertFalse(route["release_authorized"])
        self.assertFalse(route["public_speedup_claim_authorized"])

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
            "one-shot",
            "grouped-stream Numba route as the conservative fallback",
            "no hidden dispatch",
            "does not authorize automatic route selection",
        ):
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
