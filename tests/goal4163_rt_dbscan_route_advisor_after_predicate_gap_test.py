from __future__ import annotations

from pathlib import Path
import unittest

from examples.v2_0.research_benchmarks.rt_dbscan import rtdl_rt_dbscan_benchmark_app as app


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4163_rt_dbscan_route_advisor_after_predicate_gap_2026-06-09.md"


class Goal4163RtDbscanRouteAdvisorAfterPredicateGapTest(unittest.TestCase):
    def test_advisor_names_mixed_predicate_boundary_and_policy_target(self) -> None:
        advice = app.explain_rt_dbscan_explicit_route_choice(
            "road3d",
            repeated_component_signature=True,
            point_count=65536,
        )
        self.assertEqual(advice["status"], "advisory_only_no_dispatch")
        self.assertIs(advice["automatic_dispatch_authorized"], False)
        self.assertEqual(advice["canonical_component_size_signature_helper"], "canonical_component_size_signature")
        self.assertEqual(advice["mixed_predicate_route_promotion_blocked_by"], ("Goal4159", "Goal4160"))
        self.assertEqual(advice["current_predicate_border_assignment_policy"], "lowest_predicate_true_point_id_within_radius")
        self.assertEqual(advice["target_predicate_border_assignment_policy"], "reference_grouped_stream_compatible")

        direct_options = [
            option for option in advice["options"]
            if option["mode"] == app.RT_DBSCAN_DIRECT_STATUS_APP_MODE
        ]
        self.assertTrue(direct_options)
        first = direct_options[0]
        self.assertEqual(first["all_predicate_fast_path_evidence"], "Goal4158")
        self.assertEqual(first["border_assignment_policy"], "lowest_predicate_true_point_id_within_radius")
        self.assertIn("Goal4162", first["evidence_refs"])
        self.assertIn("custom mixed-predicate overrides remain blocked", first["predicate_scope"])

        grouped = [
            option for option in advice["options"]
            if option["mode"] == app.RT_DBSCAN_GROUPED_STREAM_NUMBA_APP_MODE
        ][0]
        self.assertIn("custom radius/min-neighbor settings", grouped["predicate_mix_boundary"])
        self.assertEqual(
            grouped["border_assignment_policy"],
            "one_predicate_true_neighbor_candidate_per_predicate_false_item_captured_during_rt_pass",
        )

    def test_report_states_advisory_only_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in (
            "accepted advisor hardening; no hidden dispatch",
            "grouped-stream Numba as the conservative route for custom mixed-predicate settings",
            "`all_predicate_fast_path_evidence: Goal4158`",
            "target border policy: `reference_grouped_stream_compatible`",
            "does not choose a route automatically",
        ):
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
