from __future__ import annotations

import pathlib
import unittest

import rtdsl as rt


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4110_current_route_decision_after_prepared_direct_status_app_mode_2026-06-09.md"


class Goal4110CurrentRouteDecisionAfterPreparedDirectStatusAppModeTest(unittest.TestCase):
    def test_rtdbscan_route_records_prepared_direct_status_without_universal_promotion(self) -> None:
        route = rt.explain_current_benchmark_route("rt_dbscan")

        self.assertEqual("rtdl.v2_10.current_benchmark_route_decisions.goal4139.v1", route["version"])
        self.assertIn("Goal4108", route["current_reader_decision"])
        self.assertIn("1.802x", route["current_reader_decision"])
        self.assertIn("2.465x", route["current_reader_decision"])
        self.assertIn("1.488x", route["current_reader_decision"])
        self.assertIn("Goal4109", route["current_reader_decision"])
        self.assertIn("partner_cupy_prepared_direct_status_union_component_signature_3d", route["current_reader_decision"])
        self.assertIn("one-shot default-route promotion blocked", route["current_reader_decision"])
        self.assertIn("conservative fallback/reference", route["user_choice_guidance"])
        self.assertIn("repeated component-signature workloads", route["user_choice_guidance"])
        self.assertIn(
            "partition_convergence_hybrid universal default promotion after Goal4108 prepared replay and Goal4109 app smoke",
            route["rejected_or_unpromoted_candidates"],
        )
        self.assertIn("profile/reuse advisor", route["next_runtime_action"])
        self.assertIn("hidden factor selection", route["next_runtime_action"])
        self.assertIn("Goal4108", route["evidence_refs"])
        self.assertIn("Goal4109", route["evidence_refs"])
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

    def test_report_documents_split_guidance_and_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in [
            "rtdl.v2_10.current_benchmark_route_decisions.goal4110.v1",
            "one-shot default route",
            "repeated component-signature route",
            "1.802x",
            "2.465x",
            "1.488x",
            "0.560136",
            "route-level repeated prepared direct-status app packet",
            "does not promote",
            "does not promote `partition_convergence_hybrid`",
            "does not authorize release action",
        ]:
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
