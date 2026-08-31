from __future__ import annotations

from pathlib import Path
import unittest

from examples.current.research_benchmarks.rt_dbscan.rtdl_rt_dbscan_benchmark_app import (
    explain_rt_dbscan_explicit_route_choice,
    plan_rt_dbscan_execution,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4151_rt_dbscan_single_pass_advisor_metadata_2026-06-09.md"


class Goal4151RtDbscanSinglePassAdvisorMetadataTest(unittest.TestCase):
    def test_advisor_exposes_single_pass_as_explicit_candidate(self) -> None:
        packet = explain_rt_dbscan_explicit_route_choice(
            "clustered3d",
            repeated_component_signature=True,
            point_count=1048576,
        )

        self.assertFalse(packet["automatic_dispatch_authorized"])
        self.assertFalse(packet["automatic_partner_selection_authorized"])
        self.assertFalse(packet["automatic_partition_cell_factor_selection_authorized"])
        self.assertFalse(packet["automatic_convergence_mode_selection_authorized"])
        first = packet["options"][0]
        self.assertEqual("partner_cupy_prepared_direct_status_union_component_signature_3d", first["mode"])
        self.assertEqual("cupy", first["partner"])
        self.assertEqual(0.25, first["partition_cell_factor"])
        self.assertEqual(1048576, first["tested_point_count"])
        self.assertEqual("single_pass_candidate", first["direct_status_convergence_mode"])
        self.assertEqual(
            "explicit_user_selected_same_signature_candidate_not_default",
            first["direct_status_convergence_mode_status"],
        )
        self.assertTrue(first["single_pass_same_signature_vs_until_stable"])
        self.assertGreater(first["single_pass_replay_speedup_vs_until_stable"], 1.9)
        self.assertGreater(first["single_pass_total_speedup_vs_until_stable"], 1.3)
        self.assertFalse(first["single_pass_promoted_default"])
        self.assertIn("Goal4149", first["single_pass_evidence_refs"])

    def test_legacy_plan_points_to_current_advisor_without_dispatching(self) -> None:
        plan = plan_rt_dbscan_execution("road3d", 1048576)

        self.assertEqual("explain_rt_dbscan_explicit_route_choice_goal4151", plan["current_route_guidance_source"])
        self.assertFalse(plan["automatic_partner_selection_authorized"])
        self.assertFalse(plan["automatic_partition_cell_factor_selection_authorized"])
        option = plan["current_route_first_option"]
        self.assertEqual("single_pass_candidate", option["direct_status_convergence_mode"])
        self.assertFalse(option["single_pass_promoted_default"])

    def test_report_blocks_promotion_and_hidden_selection(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for fragment in (
            "accept-with-boundary",
            "metadata and",
            "guidance update only",
            "explicit user choices",
            "not a universal default",
            "automatic convergence-mode selection",
            "does not authorize release",
        ):
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
