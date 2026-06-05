from __future__ import annotations

import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3492_overlay_area_public_cdb_tile_task_executor.py"
REPORT = ROOT / "docs" / "reports" / "goal3501_overlay_area_component_bounds_filtered_tile_tasks_2026-06-05.md"
POD_ARTIFACT = ROOT / "docs" / "reports" / "goal3501_overlay_area_component_bounds_filtered_tile_tasks_pod_2026-06-05.json"


def _cupy_available() -> tuple[bool, str]:
    try:
        import cupy as cp  # type: ignore

        if int(cp.cuda.runtime.getDeviceCount()) <= 0:
            return False, "no CUDA device"
        return True, ""
    except Exception as exc:  # pragma: no cover
        return False, str(exc)


class Goal3501OverlayAreaComponentBoundsFilteredTileTasksTest(unittest.TestCase):
    def test_component_records_expose_bounds(self) -> None:
        payload = rt.prepare_simple_polygon_component_payload(
            (((1.0, 2.0), (4.0, 2.0), (4.0, 6.0), (1.0, 6.0)),)
        )
        metadata = payload.components[0].to_metadata()

        self.assertEqual(metadata["bounds"], (1.0, 2.0, 4.0, 6.0))

    def test_component_bounds_predicate_accepts_only_positive_overlap(self) -> None:
        left = rt.prepare_simple_polygon_component_payload(
            (
                ((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0)),
                ((5.0, 5.0), (6.0, 5.0), (6.0, 6.0), (5.0, 6.0)),
            )
        )
        right = rt.prepare_simple_polygon_component_payload(
            (
                ((1.0, 1.0), (3.0, 1.0), (3.0, 3.0), (1.0, 3.0)),
                ((2.0, 0.0), (4.0, 0.0), (4.0, 2.0), (2.0, 2.0)),
            )
        )

        self.assertTrue(rt.prepared_overlay_area_component_bounds_overlap_positive(left, right, 0, 0))
        self.assertFalse(rt.prepared_overlay_area_component_bounds_overlap_positive(left, right, 0, 1))
        self.assertFalse(rt.prepared_overlay_area_component_bounds_overlap_positive(left, right, 1, 0))

    def test_device_planner_accepts_component_bounds_filter_when_cupy_available(self) -> None:
        available, reason = _cupy_available()
        if not available:
            self.skipTest(f"CuPy/CUDA unavailable: {reason}")
        import cupy as cp  # type: ignore

        left = rt.prepare_simple_polygon_component_payload(
            (
                ((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0)),
                ((5.0, 5.0), (6.0, 5.0), (6.0, 6.0), (5.0, 6.0)),
            ),
            source_shape_ids=(0, 0),
        )
        right = rt.prepare_simple_polygon_component_payload(
            (
                ((1.0, 1.0), (3.0, 1.0), (3.0, 3.0), (1.0, 3.0)),
            ),
            source_shape_ids=(0,),
        )
        unfiltered = rt.prepare_overlay_area_tile_task_cupy_inputs_from_relation_ordinals(
            left,
            right,
            relation_row_ordinals=cp.asarray([0], dtype=cp.uint32),
            left_relation_ordinals=cp.asarray([0], dtype=cp.uint32),
            right_relation_ordinals=cp.asarray([0], dtype=cp.uint32),
            left_shape_component_starts=[0],
            left_shape_component_counts=[2],
            right_shape_component_starts=[0],
            right_shape_component_counts=[1],
            relation_row_count=1,
            max_triangle_pairs_per_task=3,
        )
        filtered = rt.prepare_overlay_area_tile_task_cupy_inputs_from_relation_ordinals(
            left,
            right,
            relation_row_ordinals=cp.asarray([0], dtype=cp.uint32),
            left_relation_ordinals=cp.asarray([0], dtype=cp.uint32),
            right_relation_ordinals=cp.asarray([0], dtype=cp.uint32),
            left_shape_component_starts=[0],
            left_shape_component_counts=[2],
            right_shape_component_starts=[0],
            right_shape_component_counts=[1],
            relation_row_count=1,
            max_triangle_pairs_per_task=3,
            component_bounds_positive_filter=True,
        )

        self.assertGreater(unfiltered.task_count, filtered.task_count)
        self.assertTrue(filtered.to_metadata()["component_bounds_positive_filter"])
        self.assertEqual(filtered.to_metadata()["planner_summary"]["pair_row_count"], 1)

    def test_runner_exposes_component_bounds_filter(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        for phrase in (
            "--component-bounds-filter",
            "prepared_overlay_area_component_bounds_overlap_positive",
            "component_bounds_positive_filter",
            "rtdl.goal3501.overlay_area_component_bounds_filtered_tile_tasks.v1",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_report_documents_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Prepared component records now carry",
            "generic zero-area rejection rule",
            "does not authorize release",
            "24,389 -> 4,524",
            "0.0251s -> 0.0146s",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_pod_artifact_records_component_bounds_filter_evidence(self) -> None:
        data = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["schema"], "rtdl.goal3501.overlay_area_component_bounds_filtered_tile_tasks.v1")
        self.assertEqual(data["goal"], 3501)
        self.assertTrue(data["rtdl_commit"].startswith("ca5ab36a"))
        self.assertTrue(data["component_bounds_filter"])
        self.assertTrue(data["bounds_positive_filter"])
        self.assertTrue(data["device_tile_task_planner"])
        self.assertEqual(data["relation_row_count"], 4543)
        self.assertEqual(data["candidate_relation_row_count"], 2274)
        self.assertEqual(data["supported_relation_row_count"], 2149)
        self.assertEqual(data["skipped_candidate_relation_row_count"], 125)
        self.assertEqual(data["component_bounds_filtered_relation_row_count"], 122)
        self.assertEqual(data["unsupported_relation_row_count"], 3)
        self.assertEqual(data["component_pair_row_count"], 4524)
        self.assertEqual(data["tile_task_count"], 11617)
        self.assertEqual(data["planned_triangle_pair_count"], 4070240)
        self.assertEqual(data["executor_metadata"]["processed_triangle_pair_count"], 4070240)
        self.assertEqual(data["executor_metadata"]["status_counts"], {"0": 11617})
        self.assertTrue(data["task_summary"]["component_bounds_positive_filter"])
        self.assertLess(data["total_area_abs_error"], 1.0e-8)
        self.assertLess(data["max_relation_abs_error"], 2.0e-9)
        self.assertTrue(data["positive_row_count_match"])
        self.assertLess(data["timing_sec"]["cupy_tile_task_executor_best_repeat"], 0.02)
        self.assertLess(data["timing_sec"]["device_tile_task_planning_best_repeat"], 0.05)
        self.assertGreater(data["timing_sec"]["payload_build"], 6.0)
        for field, value in data["claim_boundary"].items():
            with self.subTest(field=field):
                self.assertFalse(value)


if __name__ == "__main__":
    unittest.main()
