from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1230V10AppAccelerationInventoryTest(unittest.TestCase):
    def test_inventory_covers_all_public_apps_and_boundaries(self) -> None:
        text = (ROOT / "docs/v1_0_app_acceleration_inventory.md").read_text(encoding="utf-8")
        for app in (
            "database_analytics",
            "graph_analytics",
            "apple_rt_demo",
            "service_coverage_gaps",
            "event_hotspot_screening",
            "facility_knn_assignment",
            "road_hazard_screening",
            "segment_polygon_hitcount",
            "segment_polygon_anyhit_rows",
            "polygon_pair_overlap_area_rows",
            "polygon_set_jaccard",
            "hausdorff_distance",
            "ann_candidate_search",
            "outlier_detection",
            "dbscan_clustering",
            "robot_collision_screening",
            "barnes_hut_force_app",
            "hiprt_ray_triangle_hitcount",
        ):
            with self.subTest(app=app):
                self.assertIn(f"`{app}`", text)
        self.assertIn("v1.0 proof", text)
        self.assertIn("v1.5 should replace", text)
        self.assertIn("Goal1262/Goal1264 show execution-unblocked but mixed evidence", text)
        self.assertIn("warm-query median still favors Embree", text)
        self.assertIn("Goal1267 verifies direct packed-ray OptiX traversal is extremely fast", text)
        self.assertIn("scene-preparation dominated and mixed versus Embree", text)
        self.assertIn("Goal1263 reviewed bounded positive wording", text)
        self.assertIn("Goal1270 clarifies the candidate-count mismatch", text)
        self.assertIn("positive-pair parity is reported separately", text)
        self.assertIn("Goal1262 confirms correctness at chunk `1024`", text)
        self.assertIn("no positive public speedup wording is authorized", text)
        self.assertIn("Reviewed normalized per-pose sub-path wording only", text)

    def test_feature_guide_current_release_and_links_are_current(self) -> None:
        text = (ROOT / "docs/rtdl_feature_guide.md").read_text(encoding="utf-8")
        self.assertIn("The current released state is `v0.9.8`", text)
        self.assertIn("[v1.0 App Acceleration Inventory](v1_0_app_acceleration_inventory.md)", text)
        self.assertIn("`v0.9.8`: bounded RTX app evidence", text)
        self.assertNotIn("The current released state is `v0.9.6`", text)

    def test_indexes_link_inventory(self) -> None:
        docs_index = (ROOT / "docs/README.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("[v1.0 App Acceleration Inventory](v1_0_app_acceleration_inventory.md)", docs_index)
        self.assertIn("[v1.0 App Acceleration Inventory](docs/v1_0_app_acceleration_inventory.md)", readme)


if __name__ == "__main__":
    unittest.main()
