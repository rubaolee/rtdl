import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = (
    ROOT
    / "docs"
    / "reports"
    / "goal1716_goal1659_current_pod_rows_after_geos_and_graph_binding_fix_2026-05-12.md"
)
RAW = ROOT / "docs" / "reports" / "goal1716_goal1659_current_pod_rows_raw_2026-05-12.json"
GRAPH = ROOT / "docs" / "reports" / "goal1659_graph_visibility_optix.json"
MAKEFILE = ROOT / "Makefile"
OPTIX_RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
EMBREE_RUNTIME = ROOT / "src" / "rtdsl" / "embree_runtime.py"
ORACLE_RUNTIME = ROOT / "src" / "rtdsl" / "oracle_runtime.py"


class Goal1716Goal1659CurrentPodRowsAfterFixTest(unittest.TestCase):
    def test_makefile_links_geos_c_without_pkg_config(self):
        text = MAKEFILE.read_text(encoding="utf-8")
        self.assertIn("pkg-config --libs geos-c", text)
        self.assertIn("/usr/lib/x86_64-linux-gnu/libgeos_c.so", text)
        self.assertIn("echo -lgeos_c", text)

    def test_python_native_build_helpers_prefer_geos_c(self):
        for path in (EMBREE_RUNTIME, ORACLE_RUNTIME):
            text = path.read_text(encoding="utf-8")
            geos_c_index = text.index('_pkg_config_flags("geos_c", option)')
            geos_index = text.index('_pkg_config_flags("geos", option)')
            self.assertLess(geos_c_index, geos_index)
            self.assertIn('return ["-lgeos_c"] if option == "--libs" else []', text)

    def test_optix_graph_csr_binding_uses_generic_field_count(self):
        text = OPTIX_RUNTIME.read_text(encoding="utf-8")
        self.assertIn("field_index_count=len(normalized.column_indices)", text)
        self.assertNotIn("column_index_count=len(normalized.column_indices)", text)

    def test_raw_pod_summary_has_all_active_rows_green(self):
        payload = json.loads(RAW.read_text(encoding="utf-8"))
        self.assertTrue(payload["done"])
        self.assertEqual(payload["entry_count"], 16)
        self.assertEqual(payload["completed_count"], 16)
        self.assertFalse(
            [
                row
                for row in payload["results"]
                if row["returncode"] != 0 or not row.get("output_json_exists")
            ]
        )
        self.assertEqual({row["app"] for row in payload["results"]}, {
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
            "dbscan_clustering",
            "robot_collision_screening",
            "barnes_hut_force_app",
        })

    def test_graph_artifact_records_native_graph_subpath_success(self):
        payload = json.loads(GRAPH.read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "pass")
        self.assertTrue(payload["strict_pass"])
        by_label = {record["label"]: record for record in payload["records"]}
        for label in (
            "optix_visibility_anyhit",
            "optix_native_graph_ray_bfs",
            "optix_native_graph_ray_triangle_count",
        ):
            with self.subTest(label=label):
                self.assertEqual(by_label[label]["status"], "ok")
                self.assertTrue(by_label[label]["parity_vs_analytic_expected"])

    def test_report_preserves_release_boundary(self):
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "all 16 active current-version pod rows completed and wrote artifacts",
            "not a full v1.6.11-versus-v1.0 timed",
            "cross-version performance comparison",
            "needs-more-evidence",
            "GEOSPreparedGeom_destroy_r",
            "field_index_count=len(normalized.column_indices)",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
