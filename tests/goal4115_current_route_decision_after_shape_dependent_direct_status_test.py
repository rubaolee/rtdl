from __future__ import annotations

import pathlib
import unittest

import rtdsl as rt


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4115_current_route_decision_after_shape_dependent_direct_status_2026-06-09.md"


class Goal4115CurrentRouteDecisionAfterShapeDependentDirectStatusTest(unittest.TestCase):
    def test_rtdbscan_route_records_shape_dependent_direct_status_guidance(self) -> None:
        route = rt.explain_current_benchmark_route("rt_dbscan")

        self.assertEqual("rtdl.v2_10.current_benchmark_route_decisions.goal4139.v1", route["version"])
        self.assertIn("Goal4114", route["current_reader_decision"])
        self.assertIn("1.796x", route["current_reader_decision"])
        self.assertIn("1.439x", route["current_reader_decision"])
        self.assertIn("0.178x", route["current_reader_decision"])
        self.assertIn("explicit profile-aware choice", route["current_reader_decision"])
        self.assertIn("clustered/road-like", route["user_choice_guidance"])
        self.assertIn("dense NGSIM-like", route["user_choice_guidance"])
        self.assertIn("conservative fallback/reference", route["user_choice_guidance"])
        self.assertIn(
            "partition_convergence_hybrid universal default promotion after Goal4114 shape-dependent repeated app-route timing",
            route["rejected_or_unpromoted_candidates"],
        )
        self.assertIn("profile/reuse advisor", route["next_runtime_action"])
        self.assertIn("hidden factor selection", route["next_runtime_action"])
        self.assertIn("universal default promotion remain blocked", route["next_runtime_action"])
        self.assertIn("Goal4114", route["evidence_refs"])
        self.assertFalse(route["automatic_partner_selection_authorized"])
        self.assertFalse(route["release_authorized"])
        self.assertFalse(route["public_speedup_claim_authorized"])
        self.assertFalse(route["true_zero_copy_claim_authorized"])

    def test_registry_summary_stays_non_authorizing(self) -> None:
        summary = rt.summarize_current_benchmark_route_decisions()
        validation = rt.validate_current_benchmark_route_decisions()

        self.assertEqual("accept", validation["status"])
        self.assertEqual((), validation["errors"])
        self.assertEqual("rtdl.v2_10.current_benchmark_route_decisions.goal4139.v1", summary["version"])
        self.assertEqual(10, summary["row_count"])
        self.assertFalse(summary["automatic_partner_selection_authorized"])
        self.assertFalse(summary["release_authorized"])
        self.assertFalse(summary["public_speedup_claim_authorized"])
        self.assertFalse(summary["broad_rt_core_claim_authorized"])
        self.assertFalse(summary["paper_reproduction_claim_authorized"])
        self.assertFalse(summary["amd_performance_claim_authorized"])

    def test_report_documents_mixed_guidance_and_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in [
            "rtdl.v2_10.current_benchmark_route_decisions.goal4115.v1",
            "clustered/road-like repeated component-signature workloads",
            "dense NGSIM-like repeated component-signature workloads",
            "1.796x",
            "1.439x",
            "0.178x",
            "universal `partition_convergence_hybrid` promotion remains rejected",
            "does not promote",
            "does not authorize release",
            "No automatic partner selection",
        ]:
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
