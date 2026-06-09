from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4180_current_route_decision_after_goal4177_timing_2026-06-09.md"


class Goal4179CurrentRouteDecisionAfterDeclaredRefactorTest(unittest.TestCase):
    def test_registry_version_tracks_declared_refactor_without_timing_promotion(self) -> None:
        self.assertEqual(
            rt.CURRENT_BENCHMARK_ROUTE_DECISION_VERSION,
            "rtdl.v2_10.current_benchmark_route_decisions.goal4180.v1",
        )
        validation = rt.validate_current_benchmark_route_decisions()
        self.assertEqual(validation["status"], "accept")
        self.assertEqual(validation["errors"], ())

    def test_rtdbscan_route_records_generic_all_items_contract_and_pod_timing(self) -> None:
        route = rt.explain_current_benchmark_route("rt_dbscan")
        self.assertIn("Goal4176", route["current_reader_decision"])
        self.assertIn("Goal4177", route["current_reader_decision"])
        self.assertIn("generic all-items direct-status component-signature primitive", route["current_reader_decision"])
        self.assertIn("post-refactor pod timing", route["current_reader_decision"])
        self.assertIn("caller-declared all-items direct-status", route["primary_route"])
        self.assertIn("synthetic predicate columns", route["user_choice_guidance"])
        self.assertIn("1.704x elapsed speedup", route["user_choice_guidance"])
        self.assertIn("1.269x over the measured all-true", route["user_choice_guidance"])
        self.assertNotIn("Goal4177 post-refactor declared-route pod timing", route["next_runtime_action"])
        for ref in ("Goal4173", "Goal4176", "Goal4177"):
            self.assertIn(ref, route["evidence_refs"])

    def test_rtdbscan_boundaries_remain_blocked(self) -> None:
        route = rt.explain_current_benchmark_route("rt_dbscan")
        self.assertIn(
            "mixed predicate direct-status broad promotion after Goal4165 policy-variant probe",
            route["rejected_or_unpromoted_candidates"],
        )
        self.assertIn("hidden border-policy selection", route["next_runtime_action"])
        self.assertFalse(route["automatic_partner_selection_authorized"])
        self.assertFalse(route["release_authorized"])
        self.assertFalse(route["public_speedup_claim_authorized"])
        self.assertFalse(route["broad_rt_core_claim_authorized"])
        self.assertFalse(route["true_zero_copy_claim_authorized"])

    def test_report_records_next_major_runtime_direction(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in (
            "accepted registry refresh; no automatic route promotion",
            "rtdl.v2_10.current_benchmark_route_decisions.goal4180.v1",
            "`1.704x` elapsed speedup",
            "`1.269x` over measured all-true",
            "generic border-assignment policy primitive",
            "does not authorize release",
        ):
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
