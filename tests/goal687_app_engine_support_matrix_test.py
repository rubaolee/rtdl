from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "app_engine_support_matrix.md"


class Goal687AppEngineSupportMatrixTest(unittest.TestCase):
    def test_every_public_app_has_status_for_every_app_engine(self) -> None:
        matrix = rt.app_engine_support_matrix()
        self.assertGreaterEqual(len(matrix), 15)

        for app, entries in matrix.items():
            with self.subTest(app=app):
                self.assertEqual(set(entries), set(rt.APP_ENGINES))
                for engine in rt.APP_ENGINES:
                    support = entries[engine]
                    self.assertEqual(support.app, app)
                    self.assertEqual(support.engine, engine)
                    self.assertIn(support.status, rt.APP_SUPPORT_STATUSES)
                    self.assertTrue(support.note.strip())

    def test_primary_unified_apps_have_expected_support_shape(self) -> None:
        matrix = rt.app_engine_support_matrix()

        self.assertEqual(matrix["database_analytics"]["embree"].status, "direct_cli_native")
        self.assertEqual(matrix["database_analytics"]["hiprt"].status, "not_exposed_by_app_cli")
        self.assertEqual(matrix["graph_analytics"]["vulkan"].status, "direct_cli_native")
        self.assertEqual(matrix["graph_analytics"]["apple_rt"].status, "not_exposed_by_app_cli")
        self.assertEqual(matrix["apple_rt_demo"]["apple_rt"].status, "direct_cli_native_assisted")
        self.assertEqual(matrix["apple_rt_demo"]["embree"].status, "apple_specific")

    def test_doc_table_matches_machine_readable_matrix(self) -> None:
        text = DOC.read_text(encoding="utf-8")
        rows: dict[str, dict[str, str]] = {}
        label_to_app = {
            "examples/rtdl_database_analytics_app.py": "database_analytics",
            "examples/rtdl_graph_analytics_app.py": "graph_analytics",
            "examples/rtdl_apple_rt_demo_app.py": "apple_rt_demo",
            "examples/rtdl_service_coverage_gaps.py": "service_coverage_gaps",
            "examples/rtdl_event_hotspot_screening.py": "event_hotspot_screening",
            "examples/rtdl_facility_knn_assignment.py": "facility_knn_assignment",
            "examples/rtdl_road_hazard_screening.py": "road_hazard_screening",
            "examples/rtdl_segment_polygon_hitcount.py": "segment_polygon_hitcount",
            "examples/rtdl_segment_polygon_anyhit_rows.py": "segment_polygon_anyhit_rows",
            "examples/rtdl_polygon_pair_overlap_area_rows.py": "polygon_pair_overlap_area_rows",
            "examples/rtdl_polygon_set_jaccard.py": "polygon_set_jaccard",
            "examples/rtdl_hausdorff_distance_app.py": "hausdorff_distance",
            "examples/rtdl_ann_candidate_app.py": "ann_candidate_search",
            "examples/rtdl_outlier_detection_app.py": "outlier_detection",
            "examples/rtdl_dbscan_clustering_app.py": "dbscan_clustering",
            "examples/rtdl_robot_collision_screening_app.py": "robot_collision_screening",
            "examples/rtdl_barnes_hut_force_app.py": "barnes_hut_force_app",
            "examples/rtdl_hiprt_ray_triangle_hitcount.py": "hiprt_ray_triangle_hitcount",
        }

        for line in text.splitlines():
            if not line.startswith("| `examples/"):
                continue
            cells = [cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]
            if len(cells) != 1 + len(rt.APP_ENGINES):
                continue
            app = label_to_app[cells[0]]
            rows[app] = dict(zip(rt.APP_ENGINES, cells[1:], strict=True))

        matrix = rt.app_engine_support_matrix()
        self.assertEqual(set(rows), set(matrix))
        for app, entries in matrix.items():
            for engine, support in entries.items():
                with self.subTest(app=app, engine=engine):
                    self.assertEqual(rows[app][engine], support.status)

    def test_retired_scenario_specific_apps_are_not_public_matrix_rows(self) -> None:
        matrix = rt.app_engine_support_matrix()
        retired = {
            "sales_risk_screening",
            "regional_order_dashboard",
            "regional_order_dashboard_kernel_form",
            "apple_rt_closest_hit",
            "apple_rt_visibility_count",
        }

        self.assertTrue(retired.isdisjoint(matrix))

    def test_public_docs_link_app_engine_support_matrix(self) -> None:
        for rel_path in (
            "README.md",
            "docs/README.md",
            "docs/application_catalog.md",
            "docs/release_facing_examples.md",
            "examples/README.md",
        ):
            with self.subTest(path=rel_path):
                text = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
                self.assertIn("app_engine_support_matrix.md", text)


if __name__ == "__main__":
    unittest.main()
