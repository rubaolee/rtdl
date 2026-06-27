import unittest
from pathlib import Path

import numpy as np

import rtdsl as rt
from examples.benchmark_apps.raydb_style import (
    rtdl_raydb_style_benchmark_app as raydb,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
ADAPTER = REPO_ROOT / "src" / "rtdsl" / "v2_8_segmented_typed_stream_adapter.py"
APP = REPO_ROOT / "examples" / "v2_0" / "research_benchmarks" / "raydb_style" / "rtdl_raydb_style_benchmark_app.py"
REPORT = REPO_ROOT / "docs" / "reports" / "goal3162_raydb_grouped_reduction_typed_stream_front_door_2026-06-03.md"


def _to_host(value):
    if hasattr(value, "copy_to_host"):
        return value.copy_to_host().tolist()
    if hasattr(value, "get"):
        return value.get().tolist()
    if hasattr(value, "tolist"):
        return value.tolist()
    return value


class Goal3162RaydbGroupedReductionTypedStreamFrontDoorTest(unittest.TestCase):
    def test_generic_grouped_reduction_front_door_is_exported_and_non_authorizing(self) -> None:
        adapter = ADAPTER.read_text(encoding="utf-8")
        self.assertIn("def execute_grouped_reduction_typed_stream_partner_columns", adapter)
        self.assertIn("caller_supplied_partner_columns_no_hidden_host_rows", adapter)
        self.assertTrue(hasattr(rt, "execute_grouped_reduction_typed_stream_partner_columns"))

        request = rt.execute_grouped_reduction_typed_stream_partner_columns(
            group_ids=np.asarray([0, 0, 1], dtype=np.int64),
            values=np.asarray([1.0, 2.0, 5.0], dtype=np.float64),
            group_count=2,
            operation="segmented_sum_f64",
            partner="numba",
            stream_id="goal3162_dry_run",
            dry_run=True,
        )
        self.assertEqual(request["status"], "dry_run_partner_consumer_request")
        self.assertEqual(request["typed_stream"]["stream_kind"], "grouped_reduction_stream")
        self.assertEqual(request["continuation_plan"]["operation"], "segmented_sum_f64")
        self.assertEqual(request["source_materialization"], "caller_supplied_partner_columns_no_hidden_host_rows")
        self.assertFalse(request["automatic_partner_selection_allowed"])
        self.assertFalse(request["release_authorized"])
        self.assertFalse(request["true_zero_copy_claim_authorized"])

        with self.assertRaisesRegex(ValueError, "explicit partner"):
            rt.execute_grouped_reduction_typed_stream_partner_columns(
                group_ids=np.asarray([0], dtype=np.int64),
                group_count=1,
                operation="segmented_count_i64",
                partner="auto",
                stream_id="goal3162_auto_reject",
                dry_run=True,
            )

    def test_raydb_v2_8_descriptor_is_typed_stream_and_preserves_v2_6_compatibility(self) -> None:
        descriptor = raydb.describe_raydb_v2_8_typed_stream_continuation("avg_as_sum_count")
        self.assertEqual(descriptor["contract_version"], raydb.RAYDB_V2_8_TYPED_STREAM_CONTINUATION_VERSION)
        self.assertEqual(descriptor["execution_path"], raydb.RAYDB_V2_8_TYPED_STREAM_EXECUTION_PATH)
        self.assertEqual(descriptor["operations"], ("segmented_sum_f64", "segmented_count_i64"))
        self.assertTrue(descriptor["uses_v2_8_typed_result_stream"])
        self.assertTrue(descriptor["uses_v2_8_grouped_reduction_front_door"])
        self.assertTrue(descriptor["uses_v2_6_neutral_partner_handoff"])
        self.assertFalse(descriptor["uses_legacy_torch_carrier"])
        self.assertFalse(descriptor["true_zero_copy_claim_authorized"])

        app = APP.read_text(encoding="utf-8")
        self.assertIn("run_raydb_v2_6_numba_neutral_continuation_preview", app)
        self.assertIn("run_raydb_v2_8_typed_stream_continuation_preview", app)
        self.assertIn(raydb.RAYDB_V2_8_TYPED_STREAM_EXECUTION_PATH, app)

    def test_v2_8_raydb_execution_matches_expected_when_numba_cuda_available(self) -> None:
        if not rt.numba_partner_available():
            self.skipTest("Numba CUDA is required for executable typed-stream validation")
        from numba import cuda

        group_ids = cuda.to_device(np.asarray([0, 0, 1, 2, 2], dtype=np.int64))
        values = cuda.to_device(np.asarray([1.5, 2.5, 10.0, -1.0, 5.0], dtype=np.float64))
        inputs = {"group_ids": group_ids, "values": values, "group_count": 3}

        avg = raydb.run_raydb_v2_8_typed_stream_continuation_preview("avg_as_sum_count", inputs)
        self.assertEqual(avg["metadata"]["execution_path"], raydb.RAYDB_V2_8_TYPED_STREAM_EXECUTION_PATH)
        self.assertEqual(_to_host(avg["outputs"]["counts"]), [2, 1, 2])
        self.assertEqual(_to_host(avg["outputs"]["sums"]), [4.0, 10.0, 4.0])
        for result in avg["continuation_results"]:
            self.assertEqual(result["path"], raydb.RAYDB_V2_8_TYPED_STREAM_EXECUTION_PATH)
            self.assertEqual(result["typed_stream"]["stream_kind"], "grouped_reduction_stream")
            self.assertFalse(result["typed_stream"]["release_authorized"])
            self.assertFalse(result["continuation_plan"]["automatic_partner_selection_allowed"])

        min_payload = raydb.run_raydb_v2_8_typed_stream_continuation_preview("min", inputs)
        self.assertEqual(min_payload["outputs"]["group_ids"], [0, 1, 2])
        self.assertEqual(min_payload["outputs"]["mins"], [1.5, 10.0, -1.0])
        max_payload = raydb.run_raydb_v2_8_typed_stream_continuation_preview("max", inputs)
        self.assertEqual(max_payload["outputs"]["group_ids"], [0, 1, 2])
        self.assertEqual(max_payload["outputs"]["maxes"], [2.5, 10.0, 5.0])

    def test_report_records_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "execute_grouped_reduction_typed_stream_partner_columns",
            "run_raydb_v2_8_typed_stream_continuation_preview",
            "does not build hidden host row placeholders",
            "`automatic_partner_selection_allowed: False`",
            "Numba CUDA execution cases",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
