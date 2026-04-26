from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"


class Goal1010PublicRtxReadmeWordingTest(unittest.TestCase):
    def test_reviewed_rtx_wording_is_present_and_scoped(self) -> None:
        text = README.read_text(encoding="utf-8")
        self.assertIn("Goal1009", text)
        self.assertIn("not a whole-app, default-mode, Python-postprocess", text)
        self.assertIn("broad RT-core acceleration claim", text)
        self.assertIn("service_coverage_gaps / prepared_gap_summary", text)
        self.assertIn("outlier_detection / prepared_fixed_radius_density_summary", text)
        self.assertIn("dbscan_clustering / prepared_fixed_radius_core_flags", text)
        self.assertIn("facility_knn_assignment / coverage_threshold_prepared", text)
        self.assertIn("segment_polygon_hitcount / segment_polygon_hitcount_native_experimental", text)
        self.assertIn("segment_polygon_anyhit_rows_prepared_bounded_gate", text)
        self.assertIn("ann_candidate_search / candidate_threshold_prepared", text)

    def test_robot_remains_excluded_from_public_speedup_wording(self) -> None:
        text = README.read_text(encoding="utf-8")
        self.assertIn("robot_collision_screening / prepared_pose_flags", text)
        self.assertIn("remains excluded from public", text)
        self.assertIn("RTX speedup wording", text)
        self.assertIn("below the 100 ms", text)
        self.assertIn("public-review timing floor", text)

    def test_artifact_trail_points_to_goal1008_and_goal1009(self) -> None:
        text = README.read_text(encoding="utf-8")
        self.assertIn("docs/reports/goal1008_large_repeat_artifact_intake_2026-04-26.md", text)
        self.assertIn("docs/reports/goal1009_public_rtx_wording_review_packet_2026-04-26.md", text)


if __name__ == "__main__":
    unittest.main()
