from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3492_overlay_area_public_cdb_tile_task_executor.py"
REPORT = ROOT / "docs" / "reports" / "goal3498_overlay_area_device_tile_task_planner_2026-06-05.md"


def _cupy_available() -> tuple[bool, str]:
    try:
        import cupy as cp  # type: ignore

        if int(cp.cuda.runtime.getDeviceCount()) <= 0:
            return False, "no CUDA device"
        return True, ""
    except Exception as exc:  # pragma: no cover
        return False, str(exc)


class Goal3498OverlayAreaDeviceTileTaskPlannerTest(unittest.TestCase):
    def test_device_tile_task_planner_api_is_exported(self) -> None:
        self.assertTrue(hasattr(rt, "prepare_overlay_area_tile_task_cupy_inputs_from_relation_ordinals"))

    def test_device_planner_matches_host_planner_on_fixture_when_cupy_available(self) -> None:
        available, reason = _cupy_available()
        if not available:
            self.skipTest(f"CuPy/CUDA unavailable: {reason}")
        import cupy as cp  # type: ignore

        left = rt.prepare_simple_polygon_component_payload(
            (
                ((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0)),
                ((3.0, 0.0), (4.0, 0.0), (4.0, 1.0), (3.0, 1.0)),
            ),
            source_shape_ids=(10, 20),
        )
        right = rt.prepare_simple_polygon_component_payload(
            (
                ((1.0, 1.0), (3.0, 1.0), (3.0, 3.0), (1.0, 3.0)),
            ),
            source_shape_ids=(5,),
        )
        host_rows = rt.prepare_overlay_area_pair_rows(left, right, ((0, 0), (1, 0)))
        host_tasks = rt.plan_prepared_overlay_area_tile_tasks(
            host_rows,
            max_triangle_pairs_per_task=3,
            relation_row_ordinals=(0, 1),
        )
        device_inputs = rt.prepare_overlay_area_tile_task_cupy_inputs_from_relation_ordinals(
            left,
            right,
            relation_row_ordinals=cp.asarray([0, 1], dtype=cp.uint32),
            left_relation_ordinals=cp.asarray([10, 20], dtype=cp.uint32),
            right_relation_ordinals=cp.asarray([5, 5], dtype=cp.uint32),
            left_shape_component_starts=[0] * 20 + [1],
            left_shape_component_counts=[0] * 10 + [1] + [0] * 9 + [1],
            right_shape_component_starts=[0] * 6,
            right_shape_component_counts=[0] * 5 + [1],
            relation_row_count=2,
            max_triangle_pairs_per_task=3,
        )
        one_shot = rt.evaluate_prepared_overlay_area_tile_tasks_cupy(left, right, host_tasks, relation_row_count=2)
        planned = rt.evaluate_prepared_overlay_area_tile_task_cupy_inputs(
            device_inputs,
            input_contract="device_planned_prepared_overlay_area_tile_task_cupy_inputs",
        )

        self.assertEqual(device_inputs.task_count, len(host_tasks))
        self.assertEqual(device_inputs.to_metadata()["planner_summary"]["task_count"], len(host_tasks))
        self.assertEqual(device_inputs.to_metadata()["planner_summary"]["pair_row_count"], len(host_rows))
        self.assertAlmostEqual(float(cp.asnumpy(one_shot.relation_areas)[0]), float(cp.asnumpy(planned.relation_areas)[0]))
        self.assertAlmostEqual(float(cp.asnumpy(one_shot.relation_areas)[1]), float(cp.asnumpy(planned.relation_areas)[1]))
        self.assertEqual(
            planned.to_metadata()["input_contract"],
            "device_planned_prepared_overlay_area_tile_task_cupy_inputs",
        )

    def test_runner_exposes_device_tile_task_planner_flag(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        for phrase in (
            "--device-tile-task-planner",
            "prepare_overlay_area_tile_task_cupy_inputs_from_relation_ordinals",
            "device_tile_task_planning",
            "rtdl.goal3498.overlay_area_device_tile_task_planner.v1",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_report_documents_copy_and_payload_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "component-pair and tile-task expansion on device",
            "does not solve Shapely geometry construction",
            "copies relation ordinals into CuPy-owned arrays",
            "does not authorize release",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
