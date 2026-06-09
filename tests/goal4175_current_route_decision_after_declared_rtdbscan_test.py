from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4175_current_route_decision_after_declared_rtdbscan_2026-06-09.md"


class Goal4175CurrentRouteDecisionAfterDeclaredRtDbscanTest(unittest.TestCase):
    def test_route_registry_version_and_summary_include_declared_evidence(self) -> None:
        self.assertEqual(
            rt.CURRENT_BENCHMARK_ROUTE_DECISION_VERSION,
            "rtdl.v2_10.current_benchmark_route_decisions.goal4175.v1",
        )
        summary = rt.summarize_current_benchmark_route_decisions()
        validation = rt.validate_current_benchmark_route_decisions()
        self.assertEqual(summary["version"], "rtdl.v2_10.current_benchmark_route_decisions.goal4175.v1")
        self.assertEqual(validation["version"], "rtdl.v2_10.current_benchmark_route_decisions.goal4175.v1")
        self.assertEqual(validation["status"], "accept")
        self.assertEqual(validation["errors"], ())

    def test_rtdbscan_decision_preserves_explicit_declared_route_boundary(self) -> None:
        route = rt.explain_current_benchmark_route("rt_dbscan")
        self.assertEqual(route["version"], "rtdl.v2_10.current_benchmark_route_decisions.goal4175.v1")
        self.assertIn("Goal4173", route["current_reader_decision"])
        self.assertIn("caller-declared external-proof", route["current_reader_decision"])
        self.assertIn("external proof", route["user_choice_guidance"])
        self.assertIn("does not promote hidden selection", route["user_choice_guidance"])
        self.assertIn("mixed explicit RT-DBSCAN route", route["primary_route"])
        self.assertTrue(
            any(
                "mixed predicate direct-status broad promotion after Goal4165" in candidate
                for candidate in route["rejected_or_unpromoted_candidates"]
            )
        )
        for ref in ("Goal4169", "Goal4172", "Goal4173", "Goal4174"):
            self.assertIn(ref, route["evidence_refs"])
        self.assertFalse(route["automatic_partner_selection_authorized"])
        self.assertFalse(route["release_authorized"])
        self.assertFalse(route["public_speedup_claim_authorized"])
        self.assertFalse(route["broad_rt_core_claim_authorized"])
        self.assertFalse(route["true_zero_copy_claim_authorized"])

    def test_report_records_registry_refresh_and_boundaries(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in (
            "accepted registry refresh; no route promotion",
            "rtdl.v2_10.current_benchmark_route_decisions.goal4175.v1",
            "declared all-true predicate direct-status is available only",
            "`1.662x` versus the current grouped-stream route",
            "`1.211x` versus the measured all-true wrapper",
            "does not authorize release",
            "automatic route selection",
            "border-policy selection",
        ):
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
