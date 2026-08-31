from __future__ import annotations

import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3492_overlay_area_public_cdb_tile_task_executor.py"
REPORT = ROOT / "docs" / "reports" / "goal3498_overlay_area_device_tile_task_planner_2026-06-05.md"
POD_ARTIFACT = ROOT / "docs" / "reports" / "goal3498_overlay_area_device_tile_task_planner_pod_2026-06-05.json"


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
            "--device-planner-repeats",
            "prepare_overlay_area_tile_task_cupy_inputs_from_relation_ordinals",
            "device_tile_task_planning",
            "device_tile_task_planning_best_repeat",
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
            "0.0415s",
            "not a first-use latency win",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_pod_artifact_records_device_planner_evidence(self) -> None:
        data = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["schema"], "rtdl.goal3498.overlay_area_device_tile_task_planner.v1")
        self.assertEqual(data["goal"], 3498)
        self.assertTrue(data["rtdl_commit"].startswith("7d69a9f9"))
        self.assertTrue(data["bounds_positive_filter"])
        self.assertTrue(data["device_tile_task_planner"])
        self.assertTrue(data["resident_cupy_inputs"])
        self.assertEqual(data["device_planner_repeats"], 5)
        self.assertEqual(data["relation_row_count"], 4543)
        self.assertEqual(data["candidate_relation_row_count"], 2274)
        self.assertEqual(data["supported_relation_row_count"], 2271)
        self.assertEqual(data["unsupported_relation_row_count"], 3)
        self.assertEqual(data["component_pair_row_count"], 24389)
        self.assertEqual(data["tile_task_count"], 36414)
        self.assertEqual(data["planned_triangle_pair_count"], 7655567)
        self.assertEqual(data["executor_metadata"]["processed_triangle_pair_count"], 7655567)
        self.assertEqual(data["executor_metadata"]["input_contract"], "device_planned_prepared_overlay_area_tile_task_cupy_inputs")
        self.assertTrue(data["executor_metadata"]["resident_cupy_columns"])
        self.assertEqual(data["executor_metadata"]["status_counts"], {"0": 36414})
        self.assertLess(data["total_area_abs_error"], 1.0e-8)
        self.assertLess(data["max_relation_abs_error"], 2.0e-9)
        self.assertTrue(data["positive_row_count_match"])
        self.assertEqual(len(data["timing_sec"]["device_tile_task_planning_repeat_secs"]), 5)
        self.assertLess(data["timing_sec"]["device_tile_task_planning_best_repeat"], 0.05)
        self.assertEqual(data["timing_sec"]["cupy_tile_task_input_prepare"], 0.0)
        self.assertLess(data["timing_sec"]["cupy_tile_task_executor_best_repeat"], 0.03)
        self.assertGreater(data["timing_sec"]["payload_build"], 6.0)
        for field, value in data["claim_boundary"].items():
            with self.subTest(field=field):
                self.assertFalse(value)


if __name__ == "__main__":
    unittest.main()
