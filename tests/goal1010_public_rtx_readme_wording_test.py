from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
V1_STATUS = ROOT / "docs" / "v1_0_rtx_app_status.md"
APP_MATRIX = ROOT / "docs" / "app_engine_support_matrix.md"


class Goal1010PublicRtxReadmeWordingTest(unittest.TestCase):
    def test_front_page_keeps_compact_claim_boundary(self) -> None:
        text = README.read_text(encoding="utf-8")
        compact = " ".join(text.split())
        self.assertIn("bounded public", text)
        self.assertIn("not a whole-app, default-mode, Python-postprocess", text)
        self.assertIn("broad RT-core acceleration claim", text)
        self.assertIn("support matrix and v1.0 inventory as the authority", compact)
        self.assertIn("Detailed evidence and review trail", text)

    def test_reviewed_rtx_wording_detail_lives_in_status_page(self) -> None:
        text = V1_STATUS.read_text(encoding="utf-8")
        compact = " ".join(text.split())
        self.assertIn("service_coverage_gaps / prepared_gap_summary", text)
        self.assertIn("event_hotspot_screening / prepared_count_summary", text)
        self.assertIn("outlier_detection / prepared_fixed_radius_density_summary", text)
        self.assertIn("dbscan_clustering / prepared_fixed_radius_core_flags", text)
        self.assertIn("segment_polygon_hitcount / segment_polygon_hitcount_native_experimental", text)
        self.assertIn("segment_polygon_anyhit_rows_prepared_bounded_gate", text)
        self.assertIn("ann_candidate_search / candidate_threshold_prepared", text)
        self.assertIn("facility_knn_assignment / coverage_threshold_prepared_recentered", text)
        self.assertIn("road_hazard_screening / prepared_native_compact_summary_40k", text)
        self.assertIn("barnes_hut_force_app / node_coverage_prepared_rich", text)
        self.assertIn("0.111619", text)
        self.assertIn("80.60x", text)
        self.assertIn("0.230652", text)
        self.assertIn("3.53x", text)
        self.assertIn("0.222256", text)
        self.assertIn("240.56x", text)
        self.assertIn("robot_collision_screening / prepared_pose_flags", text)
        self.assertIn("918.91x normalized per-pose", compact)
        self.assertIn("hausdorff_distance / directed_threshold_prepared", text)

    def test_robot_normalized_public_speedup_wording_is_scoped(self) -> None:
        text = README.read_text(encoding="utf-8") + "\n" + V1_STATUS.read_text(encoding="utf-8")
        compact = " ".join(text.split())
        self.assertIn("robot_collision_screening / prepared_pose_flags", text)
        self.assertIn("normalized per-pose", text)
        self.assertIn("not a same-total-work wall-time claim", compact)
        self.assertIn("not a whole-app robot-planning claim", text)
        self.assertIn("witness-row output", text)

    def test_artifact_trail_points_to_goal1008_and_goal1009(self) -> None:
        text = V1_STATUS.read_text(encoding="utf-8") + "\n" + APP_MATRIX.read_text(encoding="utf-8")
        for goal in (
            "Goal1008",
            "Goal1009",
            "Goal1058",
            "Goal1121",
            "Goal1123",
            "Goal1126",
            "Goal1146",
            "Goal1208",
            "Goal1224",
        ):
            with self.subTest(goal=goal):
                self.assertIn(goal, text)

    def test_secondary_public_status_docs_match_robot_boundary(self) -> None:
        v1 = V1_STATUS.read_text(encoding="utf-8")
        matrix = APP_MATRIX.read_text(encoding="utf-8")
        self.assertIn("reviewed public RTX sub-path wording rows: `13`", v1)
        self.assertIn("robot_collision_screening", v1)
        self.assertIn("Goal1146", v1)
        self.assertIn("Goal1126", v1)
        self.assertIn("Goal1208", v1)
        self.assertIn("facility_knn_assignment", v1)
        self.assertIn("road_hazard_screening", v1)
        self.assertIn("barnes_hut_force_app", v1)
        self.assertIn("Goal1142", v1)
        self.assertIn("normalized per-pose", v1)
        self.assertIn("Goal1146 reviewed narrow public wording", matrix)
        self.assertIn("Goal1208 reviewed narrow public wording", matrix)
        self.assertIn("rtdsl.rtx_public_wording_matrix()", v1)
        self.assertIn("rtdsl.rtx_public_wording_matrix()", matrix)
        self.assertIn("public_wording_reviewed", matrix)


if __name__ == "__main__":
    unittest.main()
