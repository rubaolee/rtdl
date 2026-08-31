from __future__ import annotations

import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3491_overlay_area_tile_task_cupy_executor_2026-06-05.md"
POD_ARTIFACT = ROOT / "docs" / "reports" / "goal3491_overlay_area_tile_task_cupy_executor_pod_2026-06-05.json"


def _cupy_available() -> tuple[bool, str]:
    try:
        import cupy as cp  # type: ignore

        if int(cp.cuda.runtime.getDeviceCount()) <= 0:
            return False, "no CUDA device"
        return True, ""
    except Exception as exc:  # pragma: no cover
        return False, str(exc)


class Goal3491OverlayAreaTileTaskCupyExecutorTest(unittest.TestCase):
    def test_cupy_tile_task_executor_matches_cpu_relation_total_when_available(self) -> None:
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
        cpu = rt.evaluate_prepared_overlay_area_scalar(left, right, pair_rows)
        gpu = rt.evaluate_prepared_overlay_area_tile_tasks_cupy(left, right, tasks, relation_row_count=1)
        metadata = gpu.to_metadata()

        self.assertEqual(metadata["task_count"], 3)
        self.assertEqual(metadata["processed_triangle_pair_count"], 8)
        self.assertEqual(metadata["status_counts"], {"0": 3})
        self.assertTrue(metadata["completed_without_truncation"])
        self.assertAlmostEqual(float(cp.asnumpy(gpu.relation_areas)[0]), cpu.total_area)
        self.assertAlmostEqual(metadata["total_area"], 1.75)
        for field in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "rt_core_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
            "runtime_kernel_authorized",
        ):
            with self.subTest(field=field):
                self.assertFalse(metadata[field])

    def test_cupy_tile_task_executor_reduces_multiple_component_pairs_to_one_relation_when_available(self) -> None:
        available, reason = _cupy_available()
        if not available:
            self.skipTest(f"CuPy/CUDA unavailable: {reason}")
        import cupy as cp  # type: ignore

        left_components = (
            ((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0)),
            ((10.0, 10.0), (12.0, 10.0), (12.0, 12.0), (10.0, 12.0)),
        )
        right_components = (
            ((1.0, 1.0), (3.0, 1.0), (3.0, 3.0), (1.0, 3.0)),
            ((10.5, 10.5), (11.5, 10.5), (11.5, 11.5), (10.5, 11.5)),
        )
        left = rt.prepare_simple_polygon_component_payload(left_components)
        right = rt.prepare_simple_polygon_component_payload(right_components)
        pair_rows = rt.prepare_overlay_area_pair_rows(left, right, ((0, 0), (1, 1)))
        tasks = rt.plan_prepared_overlay_area_tile_tasks(
            pair_rows,
            max_triangle_pairs_per_task=2,
            relation_row_ordinals=(0, 0),
        )
        gpu = rt.evaluate_prepared_overlay_area_tile_tasks_cupy(left, right, tasks, relation_row_count=1)
        metadata = gpu.to_metadata()

        self.assertEqual(metadata["task_count"], 4)
        self.assertEqual(metadata["relation_row_count"], 1)
        self.assertEqual(metadata["processed_triangle_pair_count"], 8)
        self.assertEqual(metadata["status_counts"], {"0": 4})
        self.assertAlmostEqual(float(cp.asnumpy(gpu.relation_areas)[0]), 2.0)
        self.assertAlmostEqual(metadata["total_area"], 2.0)

    def test_cupy_tile_task_executor_rejects_bad_relation_count_before_launch(self) -> None:
        concave_l = ((0.0, 0.0), (3.0, 0.0), (3.0, 1.0), (1.0, 1.0), (1.0, 3.0), (0.0, 3.0))
        square = ((0.5, 0.5), (2.5, 0.5), (2.5, 2.5), (0.5, 2.5))
        left = rt.prepare_simple_polygon_component_payload((concave_l,))
        right = rt.prepare_simple_polygon_component_payload((square,))
        pair_rows = rt.prepare_overlay_area_pair_rows(left, right, ((0, 0),))
        tasks = rt.plan_prepared_overlay_area_tile_tasks(pair_rows, max_triangle_pairs_per_task=3)

        with self.assertRaisesRegex(ValueError, "outside relation_row_count"):
            rt.evaluate_prepared_overlay_area_tile_tasks_cupy(left, right, tasks, relation_row_count=0)

    def test_cupy_tile_task_executor_rejects_malformed_task_before_launch(self) -> None:
        concave_l = ((0.0, 0.0), (3.0, 0.0), (3.0, 1.0), (1.0, 1.0), (1.0, 3.0), (0.0, 3.0))
        square = ((0.5, 0.5), (2.5, 0.5), (2.5, 2.5), (0.5, 2.5))
        left = rt.prepare_simple_polygon_component_payload((concave_l,))
        right = rt.prepare_simple_polygon_component_payload((square,))
        bad_task = rt.PreparedOverlayAreaTileTask(
            task_ordinal=0,
            relation_row_ordinal=0,
            pair_row_ordinal=0,
            pair_offset=9,
            pair_count=1,
            left_triangle_start=0,
            left_triangle_count=4,
            right_triangle_start=0,
            right_triangle_count=2,
        )

        with self.assertRaisesRegex(ValueError, "pair range is outside component triangle product"):
            rt.evaluate_prepared_overlay_area_tile_tasks_cupy(left, right, (bad_task,), relation_row_count=1)

    def test_spatial_rayjoin_gap_row_records_tile_task_executor(self) -> None:
        rows = {row["benchmark_app"]: row for row in rt.v2_8_benchmark_runtime_gap_matrix()}
        spatial = rows["spatial_rayjoin"]

        self.assertIn("CuPy tile-task executor", spatial["current_best_path"])
        self.assertIn("Goal3491", spatial["evidence_refs"])
        self.assertIn("public-CDB full-stream tile-task executor", spatial["current_bottleneck"])
        self.assertFalse(spatial["release_authorized"])

    def test_pod_artifact_records_cuda_fixture_evidence(self) -> None:
        data = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["schema"], "rtdl.goal3491.overlay_area_tile_task_cupy_pod.v1")
        self.assertEqual(data["source_commit"], "fee479b5")
        self.assertEqual(data["gpu_name"], "NVIDIA RTX A5000")
        self.assertEqual(data["cupy_version"], "14.1.1")
        results = {row["fixture"]: row for row in data["results"]}
        self.assertAlmostEqual(results["concave_l_square"]["relation_areas"][0], 1.75)
        self.assertAlmostEqual(results["concave_l_square"]["area_abs_error_vs_cpu"], 0.0)
        self.assertEqual(results["concave_l_square"]["metadata"]["status_counts"], {"0": 3})
        self.assertAlmostEqual(results["two_component_pairs_one_relation"]["relation_areas"][0], 2.0)
        self.assertAlmostEqual(results["two_component_pairs_one_relation"]["area_abs_error_vs_expected"], 0.0)
        self.assertEqual(results["two_component_pairs_one_relation"]["metadata"]["status_counts"], {"0": 4})
        for field, value in data["claim_boundary"].items():
            with self.subTest(field=field):
                self.assertFalse(value)

    def test_report_documents_executor_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "one GPU thread per tile task",
            "reduce by relation id",
            "cupy_add_at_by_relation_row_ordinal",
            "NVIDIA RTX A5000",
            "not the final native runtime path",
            "does not authorize",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
