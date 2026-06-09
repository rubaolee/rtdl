from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4118_current_route_decision_after_tuned_direct_status_2026-06-09.md"


class Goal4118CurrentRouteDecisionAfterTunedDirectStatusTest(unittest.TestCase):
    def test_rtdbscan_route_is_mixed_explicit_after_tuned_factor_sweep(self) -> None:
        route = rt.explain_current_benchmark_route("rt_dbscan")

        self.assertEqual("rtdl.v2_10.current_benchmark_route_decisions.goal4168.v1", route["version"])
        self.assertEqual("mixed_explicit", route["decision_kind"])
        self.assertEqual("mixed_explicit_user_choice", route["partner_policy"])
        self.assertIn("conservative one-shot/default route", route["current_reader_decision"])
        self.assertIn("Goal4116", route["current_reader_decision"])
        self.assertIn("Goal4117", route["current_reader_decision"])
        self.assertIn("2.961x", route["current_reader_decision"])
        self.assertIn("1.866x", route["current_reader_decision"])
        self.assertIn("1.312x", route["current_reader_decision"])
        self.assertIn("not automatic tuning", route["current_reader_decision"])
        self.assertIn("partition_cell_factor", route["user_choice_guidance"])
        self.assertIn("0.25 for clustered/road-like", route["user_choice_guidance"])
        self.assertIn("repeated replay ranks 0.5", route["user_choice_guidance"])
        self.assertIn("131k/262k/524k/1M rank 0.25", route["user_choice_guidance"])
        self.assertIn("Do not auto-select", route["user_choice_guidance"])
        self.assertIn(
            "automatic partition-cell-factor tuning after Goal4117 explicit factor sweep",
            route["rejected_or_unpromoted_candidates"],
        )
        self.assertIn("profile/reuse advisor", route["next_runtime_action"])
        self.assertIn("hidden factor selection", route["next_runtime_action"])
        self.assertIn("Goal4116", route["evidence_refs"])
        self.assertIn("Goal4117", route["evidence_refs"])
        self.assertFalse(route["automatic_partner_selection_authorized"])
        self.assertFalse(route["release_authorized"])
        self.assertFalse(route["public_speedup_claim_authorized"])
        self.assertFalse(route["true_zero_copy_claim_authorized"])

    def test_registry_summary_stays_non_authorizing(self) -> None:
        summary = rt.summarize_current_benchmark_route_decisions()
        validation = rt.validate_current_benchmark_route_decisions()

        self.assertEqual("accept", validation["status"])
        self.assertEqual((), validation["errors"])
        self.assertEqual("rtdl.v2_10.current_benchmark_route_decisions.goal4168.v1", summary["version"])
        self.assertEqual(10, summary["row_count"])
        self.assertFalse(summary["automatic_partner_selection_authorized"])
        self.assertFalse(summary["release_authorized"])
        self.assertFalse(summary["public_speedup_claim_authorized"])
        self.assertFalse(summary["broad_rt_core_claim_authorized"])
        self.assertFalse(summary["paper_reproduction_claim_authorized"])
        self.assertFalse(summary["amd_performance_claim_authorized"])

    def test_report_documents_tuned_route_and_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in (
            "mixed explicit route",
            "0.25",
            "0.5",
            "2.961x",
            "1.866x",
            "1.312x",
            "not automatic dispatch",
            "not automatic tuning",
            "does not authorize release",
            "automatic factor selection",
        ):
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
