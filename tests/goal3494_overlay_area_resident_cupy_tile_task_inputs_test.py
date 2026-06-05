from __future__ import annotations

import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3492_overlay_area_public_cdb_tile_task_executor.py"
REPORT = ROOT / "docs" / "reports" / "goal3494_overlay_area_resident_cupy_tile_task_inputs_2026-06-05.md"
POD_ARTIFACT = ROOT / "docs" / "reports" / "goal3494_overlay_area_resident_cupy_tile_task_inputs_pod_2026-06-05.json"


def _cupy_available() -> tuple[bool, str]:
    try:
        import cupy as cp  # type: ignore

        if int(cp.cuda.runtime.getDeviceCount()) <= 0:
            return False, "no CUDA device"
        return True, ""
    except Exception as exc:  # pragma: no cover
        return False, str(exc)


class Goal3494OverlayAreaResidentCupyTileTaskInputsTest(unittest.TestCase):
    def test_resident_input_api_is_exported(self) -> None:
        self.assertTrue(hasattr(rt, "PreparedOverlayAreaCupyTileTaskInputs"))
        self.assertTrue(hasattr(rt, "prepare_overlay_area_tile_task_cupy_inputs"))
        self.assertTrue(hasattr(rt, "evaluate_prepared_overlay_area_tile_task_cupy_inputs"))

    def test_resident_input_replay_matches_one_shot_when_cupy_available(self) -> None:
        available, reason = _cupy_available()
        if not available:
            self.skipTest(f"CuPy/CUDA unavailable: {reason}")
        import cupy as cp  # type: ignore

        concave_l = ((0.0, 0.0), (3.0, 0.0), (3.0, 1.0), (1.0, 1.0), (1.0, 3.0), (0.0, 3.0))
        square = ((0.5, 0.5), (2.5, 0.5), (2.5, 2.5), (0.5, 2.5))
        left = rt.prepare_simple_polygon_component_payload((concave_l,))
        right = rt.prepare_simple_polygon_component_payload((square,))
        pair_rows = rt.prepare_overlay_area_pair_rows(left, right, ((0, 0),))
        tasks = rt.plan_prepared_overlay_area_tile_tasks(pair_rows, max_triangle_pairs_per_task=3)
        inputs = rt.prepare_overlay_area_tile_task_cupy_inputs(left, right, tasks, relation_row_count=1)
        first = rt.evaluate_prepared_overlay_area_tile_task_cupy_inputs(inputs)
        second = rt.evaluate_prepared_overlay_area_tile_task_cupy_inputs(inputs)
        one_shot = rt.evaluate_prepared_overlay_area_tile_tasks_cupy(left, right, tasks, relation_row_count=1)

        self.assertTrue(inputs.to_metadata()["resident_cupy_columns"])
        self.assertEqual(first.to_metadata()["input_contract"], "resident_prepared_overlay_area_tile_task_cupy_inputs")
        self.assertTrue(first.to_metadata()["resident_cupy_columns"])
        self.assertAlmostEqual(float(cp.asnumpy(first.relation_areas)[0]), 1.75)
        self.assertAlmostEqual(float(cp.asnumpy(second.relation_areas)[0]), 1.75)
        self.assertAlmostEqual(float(cp.asnumpy(one_shot.relation_areas)[0]), 1.75)

    def test_runner_exposes_resident_replay_flags(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        for phrase in (
            "--resident-cupy-inputs",
            "--executor-repeats",
            "prepare_overlay_area_tile_task_cupy_inputs",
            "evaluate_prepared_overlay_area_tile_task_cupy_inputs",
            "cupy_tile_task_executor_repeat_secs",
            "cupy_tile_task_input_prepare",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_report_documents_resident_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "resident CuPy input preparation",
            "one-shot compatibility wrapper",
            "not true zero-copy",
            "rebuild those partner arrays",
            "--executor-repeats 5",
            "0.028768520802259445",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_pod_artifact_records_resident_repeat_timing(self) -> None:
        data = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["schema"], "rtdl.goal3494.overlay_area_resident_cupy_tile_task_inputs.v1")
        self.assertEqual(data["goal"], 3494)
        self.assertTrue(data["active_shapes_only"])
        self.assertTrue(data["resident_cupy_inputs"])
        self.assertTrue(data["rtdl_commit"].startswith("15ed0780"))
        self.assertEqual(data["executor_repeats"], 5)
        self.assertEqual(data["executor_metadata"]["input_contract"], "resident_prepared_overlay_area_tile_task_cupy_inputs")
        self.assertTrue(data["executor_metadata"]["resident_cupy_columns"])
        self.assertEqual(data["executor_metadata"]["processed_triangle_pair_count"], 9653005)
        self.assertEqual(data["executor_metadata"]["status_counts"], {"0": 54232})
        self.assertLess(data["total_area_abs_error"], 1.0e-8)
        self.assertTrue(data["positive_row_count_match"])
        self.assertLess(data["timing_sec"]["cupy_tile_task_input_prepare"], 0.2)
        self.assertLess(data["timing_sec"]["cupy_tile_task_executor_best_repeat"], 0.04)
        self.assertEqual(len(data["timing_sec"]["cupy_tile_task_executor_repeat_secs"]), 5)
        for field, value in data["claim_boundary"].items():
            with self.subTest(field=field):
                self.assertFalse(value)

    def test_spatial_rayjoin_gap_row_records_resident_input_reuse(self) -> None:
        rows = {row["benchmark_app"]: row for row in rt.v2_8_benchmark_runtime_gap_matrix()}
        spatial = rows["spatial_rayjoin"]

        self.assertIn("Goal3494", spatial["evidence_refs"])
        self.assertIn("resident CuPy tile-task inputs", spatial["current_bottleneck"])
        self.assertFalse(spatial["release_authorized"])


if __name__ == "__main__":
    unittest.main()
