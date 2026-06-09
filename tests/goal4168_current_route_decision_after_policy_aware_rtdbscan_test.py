from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4168_current_route_decision_after_policy_aware_rtdbscan_2026-06-09.md"


class Goal4168CurrentRouteDecisionAfterPolicyAwareRtDbscanTest(unittest.TestCase):
    def test_registry_version_and_summary_refresh(self) -> None:
        self.assertEqual(
            rt.CURRENT_BENCHMARK_ROUTE_DECISION_VERSION,
            "rtdl.v2_10.current_benchmark_route_decisions.goal4169.v1",
        )
        summary = rt.summarize_current_benchmark_route_decisions()
        validation = rt.validate_current_benchmark_route_decisions()
        self.assertEqual(summary["version"], "rtdl.v2_10.current_benchmark_route_decisions.goal4169.v1")
        self.assertEqual(validation["status"], "accept")
        self.assertEqual(validation["errors"], ())
        self.assertFalse(summary["automatic_partner_selection_authorized"])
        self.assertFalse(summary["release_authorized"])
        self.assertFalse(summary["public_speedup_claim_authorized"])

    def test_rtdbscan_route_records_policy_aware_status_without_promotion(self) -> None:
        route = rt.explain_current_benchmark_route("rt_dbscan")
        self.assertEqual(route["version"], "rtdl.v2_10.current_benchmark_route_decisions.goal4169.v1")
        self.assertIn("Goal4164 exposes the all-predicate path", route["current_reader_decision"])
        self.assertIn("Goal4166 adds a policy-aware semantic", route["current_reader_decision"])
        self.assertIn("grouped-stream Numba for conservative mixed predicate rows", route["primary_route"])
        self.assertIn("explicit all-predicate-only", route["primary_route"])
        self.assertIn("choose a policy-aware semantic contract", route["user_choice_guidance"])
        self.assertIn("does not justify broad mixed direct-status promotion", route["user_choice_guidance"])
        self.assertIn(
            "mixed predicate direct-status broad promotion after Goal4165 policy-variant probe",
            route["rejected_or_unpromoted_candidates"],
        )
        self.assertIn("hidden border-policy selection", route["next_runtime_action"])
        for ref in ("Goal4158", "Goal4159", "Goal4160", "Goal4164", "Goal4165", "Goal4166", "Goal4167"):
            self.assertIn(ref, route["evidence_refs"])
        self.assertFalse(route["automatic_partner_selection_authorized"])
        self.assertFalse(route["release_authorized"])
        self.assertFalse(route["public_speedup_claim_authorized"])

    def test_report_records_non_authorizing_refresh(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in (
            "accepted current-route registry refresh",
            "all-predicate-only mode",
            "policy-aware semantic signature",
            "mixed predicate direct-status remains unpromoted",
            "No automatic route, partner, factor, or border-policy selection is authorized",
        ):
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
