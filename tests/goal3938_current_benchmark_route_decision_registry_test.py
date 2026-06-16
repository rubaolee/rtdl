from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3938_current_benchmark_route_decision_registry_2026-06-08.md"


class Goal3938CurrentBenchmarkRouteDecisionRegistryTest(unittest.TestCase):
    def test_registry_covers_all_apps_and_stays_non_authorizing(self) -> None:
        rows = rt.current_benchmark_route_decisions()
        validation = rt.validate_current_benchmark_route_decisions()
        summary = rt.summarize_current_benchmark_route_decisions()

        self.assertEqual("rtdl.v3_0.current_benchmark_route_decisions.goal4443.v1", rt.CURRENT_BENCHMARK_ROUTE_DECISION_VERSION)
        self.assertEqual("accept", validation["status"])
        self.assertEqual((), validation["errors"])
        self.assertEqual(10, summary["app_count"])
        self.assertEqual(10, len(rows))
        self.assertEqual((), summary["pod_needed_next_apps"])
        self.assertFalse(summary["automatic_partner_selection_authorized"])
        self.assertFalse(summary["release_authorized"])
        self.assertFalse(summary["public_speedup_claim_authorized"])
        self.assertFalse(summary["true_zero_copy_claim_authorized"])
        self.assertFalse(summary["amd_performance_claim_authorized"])

    def test_rayjoin_route_is_explicit_mixed_not_auto_dispatch(self) -> None:
        route = rt.explain_current_benchmark_route("spatial_rayjoin")

        self.assertEqual("current_route_decision_found", route["status"])
        self.assertEqual("mixed_explicit", route["decision_kind"])
        self.assertEqual("mixed_explicit_user_choice", route["partner_policy"])
        self.assertIn("Numba for bounded PIP one-shot", route["current_reader_decision"])
        self.assertIn("repeated PIP", route["current_reader_decision"])
        self.assertIn("LSI scalar count", route["current_reader_decision"])
        self.assertIn("overlay active count", route["current_reader_decision"])
        self.assertIn("Goal3936", route["evidence_refs"])
        self.assertIn("universal PIP dominance", route["rejected_or_unpromoted_candidates"])
        self.assertTrue(route["user_choice_remains_authority"])
        self.assertFalse(route["automatic_partner_selection_authorized"])
        self.assertFalse(route["paper_reproduction_claim_authorized"])
        self.assertFalse(route["amd_performance_claim_authorized"])

    def test_rtdbscan_blocked_mode_is_explicitly_unpromoted(self) -> None:
        route = rt.explain_current_benchmark_route("rt_dbscan")

        self.assertEqual("mixed_explicit", route["decision_kind"])
        self.assertEqual("mixed_explicit_user_choice", route["partner_policy"])
        self.assertIn("unblocked", route["current_reader_decision"])
        self.assertIn("conservative fallback/reference", route["user_choice_guidance"])
        self.assertIn("partition_cell_factor", route["user_choice_guidance"])
        self.assertIn("blocked grouped stream candidate from Goal3936", route["rejected_or_unpromoted_candidates"])
        self.assertIn("profile/reuse advisor", route["next_runtime_action"])
        self.assertIn("Goal4079", route["evidence_refs"])
        self.assertIn("Goal4080", route["evidence_refs"])
        self.assertIn("Goal4088", route["evidence_refs"])
        self.assertIn("Goal4093", route["evidence_refs"])
        self.assertIn("Goal4096", route["evidence_refs"])
        self.assertIn("Goal4100", route["evidence_refs"])
        self.assertIn("Goal4104", route["evidence_refs"])
        self.assertIn("Goal4105", route["evidence_refs"])
        self.assertIn("Goal4108", route["evidence_refs"])
        self.assertIn("Goal4109", route["evidence_refs"])
        self.assertIn(
            "partition_convergence_hybrid universal default promotion after Goal4108 prepared replay and Goal4109 app smoke",
            route["rejected_or_unpromoted_candidates"],
        )
        self.assertIn("hidden factor selection", route["next_runtime_action"])
        self.assertFalse(route["automatic_partner_selection_authorized"])

    def test_barnes_hut_is_honest_about_mixed_cpu_fastest_route(self) -> None:
        route = rt.explain_current_benchmark_route("barnes_hut")

        self.assertEqual("mixed_explicit", route["decision_kind"])
        self.assertEqual(
            "explicit_route_choice_cpu_numba_or_optix_numba_cupy_comparison",
            route["partner_policy"],
        )
        self.assertIn("fused_frontier_force_sum_bucketized_cpu_numba", route["current_reader_decision"])
        self.assertIn("prepared_aggregate_frontier_weighted_vector_optix", route["current_reader_decision"])
        self.assertIn("Goal4442", route["evidence_refs"])
        self.assertIn(
            "Barnes-Hut RT-core speedup claim after Goal4442 fused CPU/Numba evidence",
            route["rejected_or_unpromoted_candidates"],
        )

    def test_rtnn_route_is_mixed_after_large_app_bridge(self) -> None:
        route = rt.explain_current_benchmark_route("rtnn")

        self.assertEqual("mixed_explicit", route["decision_kind"])
        self.assertEqual("mixed_explicit_user_choice", route["partner_policy"])
        self.assertIn("Goal4381", route["evidence_refs"])
        self.assertIn("Goal4443", route["evidence_refs"])
        self.assertIn("exact float64 RTDL/OptiX native ranked-summary aggregate", route["current_reader_decision"])
        self.assertIn("prepared_ranked_summary_graph_partner_bridge", route["current_reader_decision"])
        self.assertIn("automatic exact-vs-float32 route selection", route["rejected_or_unpromoted_candidates"])

    def test_unknown_app_fails_to_advisory_no_current_route(self) -> None:
        route = rt.explain_current_benchmark_route("new_app")

        self.assertEqual("no_current_route_decision", route["status"])
        self.assertEqual("new_app", route["app"])
        self.assertIn("new same-contract evidence", route["recommendation"])
        self.assertFalse(route["automatic_partner_selection_authorized"])

    def test_report_documents_design_rule_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Prefer a fused generic RTDL primitive",
            "Use Numba when custom scalar or row-stream logic wins",
            "Keep CuPy only where it is honestly the fastest measured partner",
            "Do not auto-dispatch",
            "blocked grouped stream remains unpromoted",
            "does not authorize release action",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()

