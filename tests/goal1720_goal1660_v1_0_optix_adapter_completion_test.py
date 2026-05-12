import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1720_goal1660_v1_0_optix_adapter_completion_2026-05-12.md"
GOAL1718_RAW = ROOT / "docs" / "reports" / "goal1718_goal1660_cross_version_raw_2026-05-12.json"
ADAPTER_RAW = ROOT / "docs" / "reports" / "goal1720_goal1660_v1_0_optix_adapter_raw_2026-05-12.json"


class Goal1720Goal1660V10OptixAdapterCompletionTest(unittest.TestCase):
    def test_adapter_completed_all_recoverable_optix_rows(self):
        payload = json.loads(ADAPTER_RAW.read_text(encoding="utf-8"))
        self.assertTrue(payload["done"])
        self.assertEqual(payload["attempted_count"], 12)
        self.assertEqual(payload["completed_count"], 12)
        self.assertFalse(
            [
                row
                for row in payload["results"]
                if row["returncode"] != 0 or not row.get("output_json_exists")
            ]
        )
        self.assertTrue(
            all("--backend" not in row["adapted_command"] for row in payload["results"])
        )

    def test_combined_v1_0_optix_baseline_is_complete(self):
        goal1718 = json.loads(GOAL1718_RAW.read_text(encoding="utf-8"))
        adapter = json.loads(ADAPTER_RAW.read_text(encoding="utf-8"))
        original_ok = {
            (row["app"], row["engine"])
            for row in goal1718["results"]
            if row["version"] == "v1_0"
            and row["returncode"] == 0
            and row.get("output_json_exists")
        }
        adapted_ok = {
            (row["app"], row["engine"])
            for row in adapter["results"]
            if row["returncode"] == 0 and row.get("output_json_exists")
        }
        combined = original_ok | adapted_ok
        self.assertEqual(sum(1 for _, engine in combined if engine == "optix"), 15)
        self.assertEqual(sum(1 for _, engine in combined if engine == "embree"), 1)
        self.assertEqual(len(combined), 16)
        self.assertIn(("database_analytics", "embree"), combined)

    def test_every_v1_0_optix_artifact_exists(self):
        expected = {
            "database_analytics",
            "graph_analytics",
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
            "robot_collision_screening",
            "barnes_hut_force_app",
        }
        found = set()
        for path in (ROOT / "docs" / "reports").glob("goal1660_v1_0_*_optix.json"):
            stem = path.name.removeprefix("goal1660_v1_0_").removesuffix("_optix.json")
            found.add(stem)
        self.assertEqual(found, expected)

    def test_report_preserves_release_boundary(self):
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "15 / 15 planned OptiX rows with artifacts",
            "1 / 13 planned Embree rows with artifacts",
            "16 / 28 total planned v1.0 rows with artifacts",
            "remaining unsupported v1.0 Embree rows",
            "accept-with-boundary",
            "needs-more-evidence",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
