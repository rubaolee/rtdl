from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs" / "reports" / "goal962_next_rtx_pod_execution_packet_2026-04-25.md"


class Goal962NextRtxPodExecutionPacketTest(unittest.TestCase):
    def test_packet_exists_and_records_valid_local_preflight(self) -> None:
        text = PACKET.read_text()
        self.assertIn("Accepted with 2-AI consensus", text)
        self.assertIn('"valid": true', text)
        self.assertIn("active_count: 8", text)
        self.assertIn("deferred_count: 9", text)
        self.assertIn("public_command_audit.command_count: 296", text)
        self.assertIn("goal992_scalar_fixed_radius_command_exact: 4", text)
        self.assertIn("Ran 1927 tests", text)
        self.assertIn("OK (skipped=196)", text)
        for goal in ("Goal996", "Goal997", "Goal998", "Goal999", "Goal1000"):
            self.assertIn(goal, text)

    def test_packet_contains_all_oom_safe_groups(self) -> None:
        text = PACKET.read_text()
        expected_groups = {
            "Group A: Robot Flagship": ["prepared_pose_flags"],
            "Group B: Fixed-Radius Scalar Counts": [
                "prepared_fixed_radius_density_summary",
                "prepared_fixed_radius_core_flags",
            ],
            "Group C: Database Analytics": [
                "prepared_db_session_sales_risk",
                "prepared_db_session_regional_dashboard",
            ],
            "Group D: Spatial Prepared Summaries": [
                "prepared_gap_summary",
                "prepared_count_summary",
                "coverage_threshold_prepared",
            ],
            "Group E: Segment/Polygon And Road Gates": [
                "road_hazard_native_summary_gate",
                "segment_polygon_hitcount_native_experimental",
                "segment_polygon_anyhit_rows_prepared_bounded_gate",
            ],
            "Group F: Graph Gate": ["graph_visibility_edges_gate"],
            "Group G: Prepared Decision Apps": [
                "directed_threshold_prepared",
                "candidate_threshold_prepared",
                "node_coverage_prepared",
            ],
            "Group H: Polygon Apps": [
                "polygon_pair_overlap_optix_native_assisted_phase_gate",
                "polygon_set_jaccard_optix_native_assisted_phase_gate",
            ],
        }
        for group, targets in expected_groups.items():
            with self.subTest(group=group):
                self.assertIn(group, text)
                for target in targets:
                    self.assertIn(f"--only {target}", text)

        self.assertIn("density_count", text)
        self.assertIn("core_count", text)
        self.assertIn("do not treat this group as per-point", text)

    def test_packet_lists_required_copyback_artifacts(self) -> None:
        text = PACKET.read_text()
        for artifact in (
            "goal763_rtx_cloud_bootstrap_check.json",
            "goal761_group_a_robot_summary.json",
            "goal761_group_b_fixed_radius_summary.json",
            "goal761_group_c_database_summary.json",
            "goal761_group_d_spatial_summary.json",
            "goal761_group_e_segment_polygon_summary.json",
            "goal761_group_f_graph_summary.json",
            "goal761_group_g_prepared_decision_summary.json",
            "goal761_group_h_polygon_summary.json",
            "goal933_road_hazard_prepared_summary_rtx.json",
            "goal934_segment_polygon_anyhit_rows_prepared_bounded_rtx.json",
            "goal877_jaccard_phase_rtx.json",
        ):
            with self.subTest(artifact=artifact):
                self.assertIn(artifact, text)

    def test_packet_preserves_copyback_and_shutdown_rules(self) -> None:
        text = PACKET.read_text()
        self.assertIn("copy that group summary plus any created `--output-json`", text)
        self.assertIn("Do not wait for all groups to finish", text)
        self.assertIn("After artifacts are copied back, stop or terminate the pod", text)

    def test_packet_keeps_claim_boundary(self) -> None:
        text = PACKET.read_text()
        self.assertIn("collects evidence only", text)
        self.assertIn("does not authorize release", text)
        self.assertIn("public speedup claims", text)
        self.assertEqual(text.count("--skip-validation"), 1)
        self.assertIn("Do not add\n`--skip-validation`", text)


if __name__ == "__main__":
    unittest.main()
