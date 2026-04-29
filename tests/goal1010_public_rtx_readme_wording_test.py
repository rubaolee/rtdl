from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
V1_STATUS = ROOT / "docs" / "v1_0_rtx_app_status.md"
APP_MATRIX = ROOT / "docs" / "app_engine_support_matrix.md"


class Goal1010PublicRtxReadmeWordingTest(unittest.TestCase):
    def test_reviewed_rtx_wording_is_present_and_scoped(self) -> None:
        text = README.read_text(encoding="utf-8")
        self.assertIn("bounded public", text)
        self.assertIn("Goal1123", text)
        self.assertIn("not a whole-app, default-mode, Python-postprocess", text)
        self.assertIn("broad RT-core acceleration claim", text)
        self.assertIn("service_coverage_gaps / prepared_gap_summary", text)
        self.assertIn("event_hotspot_screening / prepared_count_summary", text)
        self.assertIn("outlier_detection / prepared_fixed_radius_density_summary", text)
        self.assertIn("dbscan_clustering / prepared_fixed_radius_core_flags", text)
        self.assertIn("segment_polygon_hitcount / segment_polygon_hitcount_native_experimental", text)
        self.assertIn("segment_polygon_anyhit_rows_prepared_bounded_gate", text)
        self.assertIn("ann_candidate_search / candidate_threshold_prepared", text)
        self.assertIn("facility_knn_assignment / coverage_threshold_prepared_recentered", text)
        self.assertIn("barnes_hut_force_app / node_coverage_prepared_rich", text)
        self.assertIn("robot_collision_screening / prepared_pose_flags", text)
        self.assertIn("917.75x` per-pose throughput", text)
        self.assertIn("Goal1123", text)

    def test_robot_has_normalized_public_speedup_wording(self) -> None:
        text = README.read_text(encoding="utf-8")
        compact = " ".join(text.split())
        self.assertIn("robot_collision_screening / prepared_pose_flags", text)
        self.assertIn("reviewed normalized", text)
        self.assertIn("not a same-total-work wall-time claim", compact)
        self.assertIn("not a whole-app robot-planning claim", text)
        self.assertIn("witness-row output", text)

    def test_artifact_trail_points_to_goal1008_and_goal1009(self) -> None:
        text = README.read_text(encoding="utf-8")
        self.assertIn("docs/reports/goal1008_large_repeat_artifact_intake_2026-04-26.md", text)
        self.assertIn("docs/reports/goal1009_public_rtx_wording_review_packet_2026-04-26.md", text)
        self.assertIn("docs/reports/goal1058_three_ai_same_semantics_consensus_2026-04-28.md", text)
        self.assertIn("docs/reports/goal1121_rtx_pod_current_source_run_report_2026-04-29.md", text)
        self.assertIn("docs/reports/goal1123_two_ai_consensus_2026-04-29.md", text)
        self.assertIn("docs/reports/goal1126_three_ai_consensus_2026-04-29.md", text)

    def test_secondary_public_status_docs_match_robot_boundary(self) -> None:
        v1 = V1_STATUS.read_text(encoding="utf-8")
        matrix = APP_MATRIX.read_text(encoding="utf-8")
        self.assertIn("reviewed public RTX sub-path wording rows: `10`", v1)
        self.assertIn("robot_collision_screening / prepared_pose_flags", v1)
        self.assertIn("917.75x", v1)
        self.assertIn("facility_knn_assignment / coverage_threshold_prepared_recentered", v1)
        self.assertIn("barnes_hut_force_app / node_coverage_prepared_rich", v1)
        self.assertIn("Goal1126 accepted normalized per-pose public wording", v1)
        self.assertIn("normalized per-pose", v1)
        self.assertIn("Goal1126 reviewed normalized per-pose public wording", matrix)
        self.assertIn("Goal1126 accepted normalized per-pose public wording", matrix)
        self.assertIn("Goal1123 reviewed narrow public wording", matrix)
        self.assertIn("rtdsl.rtx_public_wording_matrix()", v1)
        self.assertIn("rtdsl.rtx_public_wording_matrix()", matrix)
        self.assertIn("public_wording_reviewed", matrix)


if __name__ == "__main__":
    unittest.main()
