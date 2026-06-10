from __future__ import annotations

from pathlib import Path
import unittest

from examples.current.research_benchmarks.rt_dbscan.rtdl_rt_dbscan_benchmark_app import (
    RT_DBSCAN_DIRECT_STATUS_APP_MODE,
    plan_rt_dbscan_execution,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4142_rt_dbscan_legacy_plan_current_advisor_bridge_2026-06-09.md"


class Goal4142RtDbscanLegacyPlanCurrentAdvisorBridgeTest(unittest.TestCase):
    def test_legacy_plan_embeds_current_1m_advisor_without_auto_factor(self) -> None:
        plan = plan_rt_dbscan_execution("road3d", 1048576)
        first = plan["current_route_first_option"]

        self.assertEqual("plan_rt_dbscan_execution", plan["adapter"])
        self.assertTrue(plan["legacy_plan_compatibility_mode"])
        self.assertEqual("explain_rt_dbscan_explicit_route_choice_goal4151", plan["current_route_guidance_source"])
        self.assertEqual(RT_DBSCAN_DIRECT_STATUS_APP_MODE, first["mode"])
        self.assertEqual(1048576, first["tested_point_count"])
        self.assertEqual(0.25, first["partition_cell_factor"])
        self.assertIn("Goal4138", first["evidence_refs"])
        self.assertFalse(plan["hidden_dispatch_allowed"])
        self.assertFalse(plan["automatic_partner_selection_authorized"])
        self.assertFalse(plan["automatic_partition_cell_factor_selection_authorized"])
        self.assertFalse(plan["release_claim_authorized"])
        self.assertFalse(plan["paper_reproduction_claim_authorized"])
        self.assertIn("legacy compatibility", plan["selected_mode_boundary"])

    def test_dense_one_shot_advisor_keeps_factor025_visible_from_plan(self) -> None:
        plan = plan_rt_dbscan_execution("ngsim_dense", 65536)
        first = plan["current_route_first_option"]
        advisor = plan["current_route_advisor"]

        self.assertEqual(0.25, first["partition_cell_factor"])
        self.assertEqual(65536, first["tested_point_count"])
        self.assertGreater(first["one_shot_total_speedup_vs_current"], 3.0)
        self.assertFalse(advisor["repeated_component_signature"])
        self.assertFalse(advisor["automatic_dispatch_authorized"])
        self.assertFalse(advisor["automatic_partition_cell_factor_selection_authorized"])

    def test_tiny_plan_remains_cpu_without_gpu_advisor(self) -> None:
        plan = plan_rt_dbscan_execution("tiny", 9)

        self.assertEqual("cpu_reference", plan["selected_mode"])
        self.assertIsNone(plan["current_route_advisor"])
        self.assertIsNone(plan["current_route_first_option"])
        self.assertFalse(plan["release_claim_authorized"])

    def test_report_states_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for fragment in (
            "legacy compatibility execution surface",
            "current_route_advisor",
            "does not promote `planned_rt_dbscan` to a hidden dispatcher",
            "does not authorize automatic route selection",
        ):
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
