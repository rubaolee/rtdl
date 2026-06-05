from __future__ import annotations

import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3492_overlay_area_public_cdb_tile_task_executor.py"
REPORT = ROOT / "docs" / "reports" / "goal3497_overlay_area_bounds_positive_filtered_tile_tasks_2026-06-05.md"
POD_ARTIFACT = ROOT / "docs" / "reports" / "goal3497_overlay_area_bounds_positive_filtered_tile_tasks_pod_2026-06-05.json"


class Goal3497OverlayAreaBoundsPositiveFilteredTileTasksTest(unittest.TestCase):
    def test_runner_exposes_bounds_positive_filter(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        for phrase in (
            "--bounds-positive-filter",
            "shape_pair_relation_bounds_overlap_area_cupy",
            "bounds_positive_relation_row_count",
            "bounds_positive_filter_metadata",
            "exact_area_for_filtered_rows",
            "rtdl.goal3497.overlay_area_bounds_positive_filtered_tile_tasks.v1",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_active_shape_ordinal_helper_accepts_row_mask(self) -> None:
        import inspect

        source = inspect.getsource(rt.shape_pair_relation_active_shape_ordinals_cupy)
        self.assertIn("row_mask=None", source)
        self.assertIn("row_filter_applied", source)
        self.assertIn("selected_row_count", source)

    def test_report_documents_candidate_filter_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Rows with bounds-overlap area equal to zero are provably zero-area",
            "preserve one output area per original relation row",
            "not device-resident tile-task planning",
            "does not authorize release",
            "4,543 -> 2,274",
            "7.7470s -> 6.8054s",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_pod_artifact_records_filtered_tile_task_evidence(self) -> None:
        data = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["schema"], "rtdl.goal3497.overlay_area_bounds_positive_filtered_tile_tasks.v1")
        self.assertEqual(data["goal"], 3497)
        self.assertTrue(data["rtdl_commit"].startswith("644184ad"))
        self.assertTrue(data["active_shapes_only"])
        self.assertTrue(data["device_active_shape_ordinals_used"])
        self.assertTrue(data["bounds_positive_filter"])
        self.assertTrue(data["resident_cupy_inputs"])
        self.assertEqual(data["relation_row_count"], 4543)
        self.assertEqual(data["candidate_relation_row_count"], 2274)
        self.assertEqual(data["bounds_positive_relation_row_count"], 2274)
        self.assertEqual(data["prepared_left_shape_count"], 1106)
        self.assertEqual(data["prepared_right_shape_count"], 949)
        self.assertEqual(data["component_pair_row_count"], 24389)
        self.assertEqual(data["tile_task_count"], 36414)
        self.assertEqual(data["planned_triangle_pair_count"], 7655567)
        self.assertEqual(data["executor_metadata"]["processed_triangle_pair_count"], 7655567)
        self.assertEqual(data["executor_metadata"]["status_counts"], {"0": 36414})
        self.assertLess(data["total_area_abs_error"], 1.0e-8)
        self.assertLess(data["max_relation_abs_error"], 2.0e-9)
        self.assertTrue(data["positive_row_count_match"])
        bounds = data["bounds_positive_filter_metadata"]
        self.assertEqual(bounds["row_filter"], "bounds_overlap_area_gt_zero")
        self.assertEqual(bounds["bounds_positive_relation_row_count"], 2274)
        self.assertFalse(bounds["exact_polygon_overlay_area"])
        active = data["active_shape_ordinal_metadata"]
        self.assertTrue(active["row_filter_applied"])
        self.assertEqual(active["selected_row_count"], 2274)
        self.assertEqual(active["left_unique_shape_count"], 1106)
        self.assertLess(data["timing_sec"]["bounds_positive_filter"], 0.1)
        self.assertLess(data["timing_sec"]["payload_build"], 7.0)
        self.assertLess(data["timing_sec"]["cupy_tile_task_executor_best_repeat"], 0.03)
        for field, value in data["claim_boundary"].items():
            with self.subTest(field=field):
                self.assertFalse(value)

    def test_spatial_rayjoin_gap_row_records_bounds_positive_filter(self) -> None:
        rows = {row["benchmark_app"]: row for row in rt.v2_8_benchmark_runtime_gap_matrix()}
        spatial = rows["spatial_rayjoin"]

        self.assertIn("Goal3497", spatial["evidence_refs"])
        self.assertIn("bounds-positive filter", spatial["current_bottleneck"])
        self.assertFalse(spatial["release_authorized"])


if __name__ == "__main__":
    unittest.main()
