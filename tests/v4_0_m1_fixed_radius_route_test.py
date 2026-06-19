from __future__ import annotations

import json
from pathlib import Path
import unittest
from unittest import mock

import rtdsl
from rtdsl import v4_0_device_array_operator as v4


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_REPORT = ROOT / "docs" / "reports" / "v4_0_m1_fixed_radius_cupy_stream_smoke_2026-06-19.json"
SMOKE_SCRIPT = ROOT / "scripts" / "v4_0_m1_fixed_radius_cupy_stream_smoke.py"


class _FakeCudaColumn:
    def __init__(
        self,
        ptr: int,
        *,
        dtype: str,
        shape: tuple[int, ...],
        strides: tuple[int, ...] | None = None,
        stream: int = 0,
    ) -> None:
        self._ptr = int(ptr)
        self.dtype = dtype
        self.shape = shape
        self.strides = strides
        self.__cuda_array_interface__ = {
            "version": 3,
            "shape": shape,
            "typestr": dtype,
            "data": (self._ptr, False),
            "strides": strides,
            "stream": stream,
        }


class _FakePrepared:
    def __init__(self) -> None:
        self.closed = False
        self.on_stream_call = None

    def close(self) -> None:
        self.closed = True

    def write_device_count_threshold_columns_on_stream(self, query_point_columns, **kwargs):
        self.on_stream_call = {"query_point_columns": query_point_columns, **kwargs}
        return {
            "metadata": {
                "native_symbol": "rtdl_optix_write_prepared_fixed_radius_count_threshold_2d_device_query_columns_on_stream",
                "transfer_mode": "device_fixed_radius_point_columns_output_columns_zero_copy_on_stream",
                "cuda_stream_ptr": int(kwargs["cuda_stream_ptr"]),
                "native_synchronized_before_return": True,
                "native_async_ready": False,
                "true_zero_copy_authorized": True,
            }
        }


def _point_columns(base: int, *, count: int = 3, x_dtype: str = "float64"):
    return {
        "ids": _FakeCudaColumn(base + 0x10, dtype="uint32", shape=(count,), strides=(4,)),
        "x": _FakeCudaColumn(base + 0x20, dtype=x_dtype, shape=(count,), strides=(8,)),
        "y": _FakeCudaColumn(base + 0x30, dtype="float64", shape=(count,), strides=(8,)),
    }


def _output_columns(base: int, *, count: int = 3):
    return {
        "query_ids": _FakeCudaColumn(base + 0x10, dtype="uint32", shape=(count,), strides=(4,)),
        "neighbor_counts": _FakeCudaColumn(base + 0x20, dtype="uint32", shape=(count,), strides=(4,)),
        "threshold_flags": _FakeCudaColumn(base + 0x30, dtype="uint32", shape=(count,), strides=(4,)),
    }


class V40M1FixedRadiusRouteTest(unittest.TestCase):
    def test_route_descriptor_freezes_fixed_radius_count_threshold_2d(self) -> None:
        route = rtdsl.describe_v4_fixed_radius_count_threshold_2d_route()

        self.assertEqual(route["scope"], "python_gpu_rt_core_operator")
        self.assertEqual(route["route_id"], "fixed_radius_count_threshold_2d")
        self.assertEqual(route["backend"], "optix")
        self.assertEqual(route["output_shape"], "fixed one row per query, no variable neighbor rows")
        self.assertTrue(route["native_stream_propagation_ready"])
        self.assertFalse(route["native_async_ready"])
        self.assertFalse(route["v4_true_zero_copy_claim_authorized"])
        self.assertIn("variable_length_neighbor_rows", route["blocked_generalizations"])
        self.assertIn("ray_triangle_any_hit", route["blocked_generalizations"])

    def test_plan_captures_borrowed_pointers_and_producer_streams(self) -> None:
        search = _point_columns(0x1000)
        query = _point_columns(0x2000)
        outputs = _output_columns(0x3000)
        query["x"] = _FakeCudaColumn(0x2020, dtype="float64", shape=(3,), strides=(8,), stream=77)

        plan = rtdsl.plan_v4_fixed_radius_count_threshold_2d(
            query,
            search,
            output_columns=outputs,
        )
        metadata = plan.to_metadata()

        self.assertEqual(metadata["route_id"], "fixed_radius_count_threshold_2d")
        self.assertEqual(metadata["query_count"], 3)
        self.assertEqual(metadata["search_count"], 3)
        self.assertEqual(metadata["borrowed_device_pointers"]["search.x"], 0x1020)
        self.assertEqual(metadata["borrowed_device_pointers"]["query.x"], 0x2020)
        self.assertEqual(metadata["descriptors"]["query.x"]["producer_stream_handle"], 77)
        self.assertEqual(metadata["output_contract"], "caller_owned_cuda_output_columns")

    def test_plan_fails_closed_for_wrong_dtype_and_captures_caller_stream(self) -> None:
        search = _point_columns(0x1000)
        query = _point_columns(0x2000, x_dtype="float32")
        outputs = _output_columns(0x3000)

        with self.assertRaisesRegex(ValueError, "V4 query column 'x' must use dtype"):
            rtdsl.plan_v4_fixed_radius_count_threshold_2d(query, search, output_columns=outputs)

        plan = rtdsl.plan_v4_fixed_radius_count_threshold_2d(
            _point_columns(0x2000),
            search,
            output_columns=outputs,
            stream=123,
        )
        self.assertEqual(plan.to_metadata()["caller_stream_handle"], 123)
        self.assertTrue(plan.to_metadata()["caller_stream_native_propagation_ready"])

    def test_operator_wraps_existing_prepared_optix_device_column_route(self) -> None:
        search = _point_columns(0x1000)
        query = _point_columns(0x2000)
        outputs = _output_columns(0x3000)
        prepared = _FakePrepared()
        native_result = {
            "columns": outputs,
            "metadata": {
                "adapter": "fixed_radius_count_threshold_2d_optix_prepared_partner_device_columns",
                "true_zero_copy_authorized": True,
                "native_metadata": {
                    "native_symbol": "rtdl_optix_write_prepared_fixed_radius_count_threshold_2d_device_query_columns",
                    "true_zero_copy_authorized": True,
                },
            },
        }

        with mock.patch.object(v4, "_prepare_scene", return_value=prepared) as prepare_scene, mock.patch.object(
            v4,
            "_run_prepared",
            return_value=native_result,
        ) as run_prepared:
            with rtdsl.prepare_v4_fixed_radius_count_threshold_2d(
                search,
                max_radius=2.0,
                partner="cupy",
            ) as operator:
                result = operator.run(
                    query,
                    radius=1.5,
                    threshold=2,
                    output_columns=outputs,
                    return_metadata=True,
                )

        prepare_scene.assert_called_once()
        run_prepared.assert_called_once()
        self.assertTrue(prepared.closed)
        self.assertIs(result["columns"], outputs)
        metadata = result["metadata"]
        self.assertEqual(metadata["v4_route_id"], "fixed_radius_count_threshold_2d")
        self.assertEqual(metadata["v4_backend"], "optix")
        self.assertTrue(metadata["native_true_zero_copy_authorized"])
        self.assertFalse(metadata["v4_true_zero_copy_claim_authorized"])
        self.assertEqual(metadata["v4_true_zero_copy_claim_blocker"], "M4_evidence_packet_pending")

    def test_cupy_stream_smoke_report_preserves_claim_boundaries(self) -> None:
        report = json.loads(EVIDENCE_REPORT.read_text(encoding="utf-8"))

        self.assertEqual(report["status"], "pass-with-boundary")
        self.assertEqual(report["code_commit"], "7bca09024")
        self.assertEqual(report["route"]["route_id"], "fixed_radius_count_threshold_2d")
        self.assertEqual(report["validation"]["build_optix"], "pass")
        self.assertEqual(report["validation"]["cupy_stream_smoke"], "pass")
        self.assertIn(
            "PYTHONPATH=src:. python3 scripts/v4_0_m1_fixed_radius_cupy_stream_smoke.py",
            report["commands"],
        )
        self.assertEqual(report["cupy_stream_smoke_observed"]["neighbor_counts"], [1, 1, 0])
        self.assertTrue(all(report["pointer_identity"].values()))
        self.assertTrue(all(report["source_audit"].values()))
        self.assertFalse(report["route"]["async_claim_authorized"])
        self.assertFalse(report["claim_boundaries"]["public_speedup_claim_authorized"])
        self.assertFalse(report["claim_boundaries"]["rt_core_speedup_claim_authorized"])
        self.assertFalse(report["claim_boundaries"]["v4_true_zero_copy_claim_authorized"])

    def test_cupy_stream_smoke_script_is_reproducible_route_gate(self) -> None:
        script = SMOKE_SCRIPT.read_text(encoding="utf-8")

        for token in (
            "run_v4_fixed_radius_count_threshold_2d",
            "cp.cuda.Stream(non_blocking=True)",
            "pointer_identity",
            "source_audit",
            "native_async_ready",
            "v4_true_zero_copy_claim_authorized",
        ):
            self.assertIn(token, script)

    def test_operator_uses_on_stream_route_for_nonzero_caller_stream(self) -> None:
        search = _point_columns(0x1000)
        query = _point_columns(0x2000)
        outputs = _output_columns(0x3000)
        prepared = _FakePrepared()

        with mock.patch.object(v4, "_prepare_scene", return_value=prepared), mock.patch.object(
            v4,
            "_run_prepared",
        ) as run_prepared:
            result = rtdsl.run_v4_fixed_radius_count_threshold_2d(
                query,
                search,
                radius=1.0,
                threshold=1,
                partner="cupy",
                output_columns=outputs,
                stream=456,
                return_metadata=True,
            )

        run_prepared.assert_not_called()
        self.assertEqual(prepared.on_stream_call["cuda_stream_ptr"], 456)
        self.assertIs(prepared.on_stream_call["query_ids_out"], outputs["query_ids"])
        metadata = result["metadata"]
        self.assertEqual(metadata["caller_stream_handle"], 456)
        self.assertTrue(metadata["caller_stream_native_propagation_ready"])
        self.assertTrue(metadata["native_synchronized_before_return"])
        self.assertFalse(metadata["native_async_ready"])
        self.assertTrue(metadata["native_true_zero_copy_authorized"])
        self.assertFalse(metadata["v4_true_zero_copy_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
