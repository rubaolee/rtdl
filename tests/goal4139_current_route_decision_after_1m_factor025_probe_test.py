from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt
from examples.v2_0.research_benchmarks.rt_dbscan.rtdl_rt_dbscan_benchmark_app import (
    explain_rt_dbscan_explicit_route_choice,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4139_current_route_decision_after_1m_factor025_probe_2026-06-09.md"


class Goal4139CurrentRouteDecisionAfter1mFactor025ProbeTest(unittest.TestCase):
    def test_advisor_ranks_1m_evidence_first_without_dispatch(self) -> None:
        packet = explain_rt_dbscan_explicit_route_choice(
            "road3d",
            repeated_component_signature=False,
            point_count=1048576,
        )
        first = packet["options"][0]

        self.assertEqual(1048576, first["tested_point_count"])
        self.assertEqual(0.25, first["partition_cell_factor"])
        self.assertGreater(first["replay_speedup_vs_current"], 1.3)
        self.assertGreater(first["one_shot_total_speedup_vs_current"], 1.7)
        self.assertIn("Goal4138", first["evidence_refs"])
        self.assertFalse(packet["automatic_dispatch_authorized"])
        self.assertFalse(packet["automatic_partner_selection_authorized"])
        self.assertFalse(packet["automatic_partition_cell_factor_selection_authorized"])

    def test_route_registry_records_limited_1m_extension(self) -> None:
        route = rt.explain_current_benchmark_route("rt_dbscan")

        self.assertEqual("rtdl.v2_10.current_benchmark_route_decisions.goal4139.v1", route["version"])
        self.assertIn("Goal4138", route["current_reader_decision"])
        self.assertIn("1M", route["user_choice_guidance"])
        self.assertIn("factor-0.25-only 1M", " ".join(route["rejected_or_unpromoted_candidates"]))
        self.assertIn("Goal4138", route["evidence_refs"])
        self.assertFalse(route["automatic_partner_selection_authorized"])
        self.assertFalse(route["release_authorized"])
        self.assertFalse(route["public_speedup_claim_authorized"])

    def test_registry_summary_and_report_stay_non_authorizing(self) -> None:
        summary = rt.summarize_current_benchmark_route_decisions()
        validation = rt.validate_current_benchmark_route_decisions()
        report = REPORT.read_text(encoding="utf-8")

        self.assertEqual("accept", validation["status"])
        self.assertEqual((), validation["errors"])
        self.assertEqual("rtdl.v2_10.current_benchmark_route_decisions.goal4139.v1", summary["version"])
        self.assertFalse(summary["automatic_partner_selection_authorized"])
        self.assertFalse(summary["release_authorized"])
        self.assertFalse(summary["public_speedup_claim_authorized"])
        for fragment in (
            "1M",
            "not run a full factor sweep",
            "no hidden dispatch",
            "does not authorize automatic route selection",
        ):
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
