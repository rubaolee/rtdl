from __future__ import annotations

from pathlib import Path
import unittest

from examples.v2_0.research_benchmarks.rt_dbscan import rtdl_rt_dbscan_benchmark_app as app


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4167_rt_dbscan_route_advisor_policy_aware_status_2026-06-09.md"


class Goal4167RtDbscanRouteAdvisorPolicyAwareStatusTest(unittest.TestCase):
    def test_advisor_keeps_mixed_predicate_route_unpromoted_after_policy_helper(self) -> None:
        advice = app.explain_rt_dbscan_explicit_route_choice(
            "road3d",
            repeated_component_signature=True,
            point_count=65536,
        )
        self.assertEqual(advice["mixed_predicate_policy_probe"], "Goal4165")
        self.assertEqual(advice["mixed_predicate_policy_aware_contract"], "Goal4166")
        self.assertIn("not promoted for mixed rows", advice["mixed_predicate_performance_status"])
        self.assertEqual(
            advice["mixed_predicate_comparison_contracts"],
            ("policy_bound_component_sizes", "core_noise_assigned_counts_only"),
        )
        self.assertEqual(
            advice["policy_aware_semantic_signature_helper"],
            "policy_aware_rt_dbscan_semantic_signature",
        )
        self.assertEqual(advice["mixed_predicate_route_promotion_blocked_by"], ("Goal4159", "Goal4160"))
        self.assertIs(advice["automatic_dispatch_authorized"], False)
        self.assertIs(advice["public_speedup_claim_authorized"], False)

    def test_grouped_and_direct_options_name_policy_aware_boundary(self) -> None:
        advice = app.explain_rt_dbscan_explicit_route_choice(
            "road3d",
            repeated_component_signature=True,
            point_count=65536,
        )
        grouped = next(option for option in advice["options"] if option["mode"] == app.RT_DBSCAN_GROUPED_STREAM_NUMBA_APP_MODE)
        self.assertIn("policy-aware semantic contract", grouped["predicate_mix_boundary"])
        self.assertTrue(grouped["policy_aware_semantic_signature_comparison"])
        self.assertIn("Goal4165", grouped["evidence_refs"])
        self.assertIn("Goal4166", grouped["evidence_refs"])

        direct = next(option for option in advice["options"] if option["mode"] == app.RT_DBSCAN_DIRECT_STATUS_APP_MODE)
        self.assertIn("policy-aware semantic contract", direct["predicate_scope"])
        self.assertIn("not broadly faster", direct["mixed_predicate_performance_status"])
        self.assertTrue(direct["policy_aware_semantic_signature_comparison"])
        self.assertIn("Goal4165", direct["evidence_refs"])
        self.assertIn("Goal4166", direct["evidence_refs"])

    def test_report_records_route_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in (
            "accepted advisor update",
            "policy-aware counts-only semantics can pass",
            "does not promote mixed predicate direct-status",
            "Goal4165",
            "Goal4166",
            "No hidden dispatch or public speedup claim is authorized",
        ):
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
