from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3492_overlay_area_public_cdb_tile_task_executor.py"
REPORT = ROOT / "docs" / "reports" / "goal3501_overlay_area_component_bounds_filtered_tile_tasks_2026-06-05.md"


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
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
