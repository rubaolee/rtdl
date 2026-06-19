from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest import mock

import numpy as np
import rtdsl
from rtdsl import v4_0_device_array_operator as v4


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_REPORT = ROOT / "docs" / "reports" / "v4_0_m1_fixed_radius_cupy_stream_smoke_2026-06-19.json"
PARITY_REPORT = ROOT / "docs" / "reports" / "v4_0_m1_fixed_radius_cupy_parity_matrix_2026-06-19.json"
NO_HOST_STAGE_REPORT = (
    ROOT / "docs" / "reports" / "v4_0_m1_fixed_radius_cupy_no_host_stage_probe_2026-06-19.json"
)
SMOKE_SCRIPT = ROOT / "scripts" / "v4_0_m1_fixed_radius_cupy_stream_smoke.py"
PARITY_SCRIPT = ROOT / "scripts" / "v4_0_m1_fixed_radius_cupy_parity_matrix.py"
NO_HOST_STAGE_SCRIPT = ROOT / "scripts" / "v4_0_m1_fixed_radius_cupy_no_host_stage_probe.py"
BENCHMARK_SCRIPT = ROOT / "scripts" / "v4_0_m1_fixed_radius_cupy_benchmark_probe.py"
CLAIM_REVIEW = ROOT / "docs" / "reviews" / "codex_v4_m1_true_zero_copy_claim_review_2026-06-19.md"
WORDING_CONSENSUS = (
    ROOT / "docs" / "reviews" / "codex_v4_m1_true_zero_copy_wording_consensus_2026-06-19.md"
)


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
        pointer_echo = {f"query.{name}": int(column._ptr) for name, column in query_point_columns.items()}
        pointer_echo.update(
            {
                "output.query_ids": int(kwargs["query_ids_out"]._ptr),
                "output.neighbor_counts": int(kwargs["neighbor_counts_out"]._ptr),
                "output.threshold_flags": int(kwargs["threshold_flags_out"]._ptr),
            }
        )
        return {
            "metadata": {
                "native_symbol": "rtdl_optix_write_prepared_fixed_radius_count_threshold_2d_device_query_columns_on_stream",
                "transfer_mode": "device_fixed_radius_point_columns_output_columns_zero_copy_on_stream",
                "cuda_stream_ptr": int(kwargs["cuda_stream_ptr"]),
                "native_call_device_pointer_echo": pointer_echo,
                "native_call_device_pointer_echo_complete": True,
                "named_cuda_columns_no_host_stage_authorized": True,
                "named_cuda_columns_no_host_stage_ready": True,
                "internal_device_staging_disclosed": True,
                "internal_device_staging_scope": "device-resident AABB/BVH staging may occur inside the native route",
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


def _host_point_columns(count: int = 3):
    return {
        "ids": np.arange(count, dtype=np.uint32),
        "x": np.arange(count, dtype=np.float64),
        "y": np.arange(count, dtype=np.float64),
    }


def _clone_handoff(handoff, **overrides):
    values = {
        "data_ptr": handoff.data_ptr,
        "dtype": handoff.dtype,
        "shape": handoff.shape,
        "strides": handoff.strides,
        "device_type": handoff.device_type,
        "device_id": handoff.device_id,
        "access_mode": handoff.access_mode,
        "source_protocol": handoff.source_protocol,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


class V40M1FixedRadiusRouteTest(unittest.TestCase):
    def test_route_descriptor_freezes_fixed_radius_count_threshold_2d(self) -> None:
        route = rtdsl.describe_v4_fixed_radius_count_threshold_2d_route()

        self.assertEqual(route["scope"], "python_gpu_rt_core_operator")
        self.assertEqual(route["route_id"], "fixed_radius_count_threshold_2d")
        self.assertEqual(route["backend"], "optix")
        self.assertEqual(route["output_shape"], "fixed one row per query, no variable neighbor rows")
        self.assertTrue(route["native_stream_propagation_ready"])
        self.assertTrue(route["native_prepare_stream_propagation_ready"])
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
        self.assertEqual(plan.to_metadata()["prepare_stream_handle"], 123)
        self.assertTrue(plan.to_metadata()["caller_stream_native_propagation_ready"])
        self.assertTrue(plan.to_metadata()["native_prepare_stream_propagation_ready"])

    def test_plan_fails_closed_for_host_arrays_bad_rank_and_noncontiguous_stride(self) -> None:
        search = _point_columns(0x1000)
        outputs = _output_columns(0x3000)

        with self.assertRaisesRegex(ValueError, "requires a CUDA partner tensor"):
            rtdsl.plan_v4_fixed_radius_count_threshold_2d(
                _host_point_columns(),
                search,
                output_columns=outputs,
            )

        bad_rank = _point_columns(0x2000)
        bad_rank["x"] = _FakeCudaColumn(0x2020, dtype="float64", shape=(3, 1), strides=(8, 8))
        with self.assertRaisesRegex(ValueError, "V4 query column 'x' must be one-dimensional"):
            rtdsl.plan_v4_fixed_radius_count_threshold_2d(bad_rank, search, output_columns=outputs)

        noncontiguous = _point_columns(0x2000)
        noncontiguous["x"] = _FakeCudaColumn(0x2020, dtype="float64", shape=(3,), strides=(16,))
        with self.assertRaisesRegex(ValueError, "V4 query column 'x' must be contiguous"):
            rtdsl.plan_v4_fixed_radius_count_threshold_2d(noncontiguous, search, output_columns=outputs)

    def test_plan_fails_closed_for_bad_output_contracts(self) -> None:
        search = _point_columns(0x1000)
        query = _point_columns(0x2000)

        wrong_count = _output_columns(0x3000, count=2)
        with self.assertRaisesRegex(ValueError, "V4 output columns must have matching lengths"):
            rtdsl.plan_v4_fixed_radius_count_threshold_2d(query, search, output_columns=wrong_count)

        wrong_dtype = _output_columns(0x3000)
        wrong_dtype["neighbor_counts"] = _FakeCudaColumn(0x3020, dtype="int32", shape=(3,), strides=(4,))
        with self.assertRaisesRegex(ValueError, "V4 output column 'neighbor_counts' must use dtype"):
            rtdsl.plan_v4_fixed_radius_count_threshold_2d(query, search, output_columns=wrong_dtype)

    def test_plan_fails_closed_for_mixed_devices(self) -> None:
        search = _point_columns(0x1000)
        query = _point_columns(0x2000)
        outputs = _output_columns(0x3000)
        original = v4._partner.prepare_direct_device_pointer_handoff

        def fake_handoff(obj, *, access="read"):
            handoff = original(obj, access=access)
            if obj is query["y"]:
                return _clone_handoff(handoff, device_id=1)
            return handoff

        with mock.patch.object(v4._partner, "prepare_direct_device_pointer_handoff", side_effect=fake_handoff):
            with self.assertRaisesRegex(ValueError, "V4 query columns must live on the same CUDA device"):
                rtdsl.plan_v4_fixed_radius_count_threshold_2d(query, search, output_columns=outputs)

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
        self.assertEqual(
            metadata["v4_true_zero_copy_claim_blocker"],
            "public_true_zero_copy_wording_blocked_by_internal_device_staging_and_sync_contract",
        )

    def test_cupy_stream_smoke_report_preserves_claim_boundaries(self) -> None:
        report = json.loads(EVIDENCE_REPORT.read_text(encoding="utf-8"))

        self.assertEqual(report["status"], "pass-with-boundary")
        self.assertRegex(report["code_commit"], r"^[0-9a-f]{9}$")
        self.assertEqual(report["route"]["route_id"], "fixed_radius_count_threshold_2d")
        self.assertEqual(report["validation"]["build_optix"], "pass")
        self.assertEqual(report["validation"]["cupy_stream_smoke"], "pass")
        self.assertIn(
            "PYTHONPATH=src:. python3 scripts/v4_0_m1_fixed_radius_cupy_stream_smoke.py",
            report["commands"],
        )
        self.assertEqual(report["cupy_stream_smoke_observed"]["neighbor_counts"], [1, 1, 0])
        self.assertTrue(all(report["pointer_identity"].values()))
        self.assertTrue(all(report["pointer_echo_identity"].values()))
        self.assertTrue(all(report["source_audit"].values()))
        self.assertTrue(all(report["promotion_blockers"].values()))
        self.assertFalse(report["route"]["async_claim_authorized"])
        self.assertFalse(report["claim_boundaries"]["public_speedup_claim_authorized"])
        self.assertFalse(report["claim_boundaries"]["rt_core_speedup_claim_authorized"])
        self.assertFalse(report["claim_boundaries"]["v4_true_zero_copy_claim_authorized"])

    def test_cupy_parity_matrix_report_preserves_claim_boundaries(self) -> None:
        report = json.loads(PARITY_REPORT.read_text(encoding="utf-8"))
        script = PARITY_SCRIPT.read_text(encoding="utf-8")

        self.assertEqual(report["status"], "pass-with-boundary")
        self.assertRegex(report["code_commit"], r"^[0-9a-f]{9}$")
        self.assertEqual(report["route"]["route_id"], "fixed_radius_count_threshold_2d")
        self.assertEqual(report["validation"]["cupy_parity_matrix"], "pass")
        self.assertEqual(report["parity_matrix"]["case_count"], 5)
        self.assertEqual(report["parity_matrix"]["pass_count"], 5)
        self.assertEqual(report["fail_closed_matrix"]["case_count"], 1)
        self.assertEqual(report["fail_closed_matrix"]["pass_count"], 1)
        self.assertTrue(all(row["passed"] for row in report["parity_matrix"]["cases"]))
        self.assertTrue(all(row["passed"] for row in report["fail_closed_matrix"]["cases"]))
        self.assertIn("boundary_inclusive", {row["name"] for row in report["parity_matrix"]["cases"]})
        self.assertIn("random_seed_7", {row["name"] for row in report["parity_matrix"]["cases"]})
        self.assertIn("empty_query_zero_length_cupy_columns_fail_closed", script)
        self.assertFalse(report["claim_boundaries"]["async_claim_authorized"])
        self.assertFalse(report["claim_boundaries"]["public_speedup_claim_authorized"])
        self.assertFalse(report["claim_boundaries"]["rt_core_speedup_claim_authorized"])
        self.assertFalse(report["claim_boundaries"]["v4_true_zero_copy_claim_authorized"])

    def test_cupy_no_host_stage_report_preserves_claim_boundaries(self) -> None:
        report = json.loads(NO_HOST_STAGE_REPORT.read_text(encoding="utf-8"))
        script = NO_HOST_STAGE_SCRIPT.read_text(encoding="utf-8")
        classification = report["transfer_counter_classification"]

        self.assertEqual(report["status"], "pass-with-boundary")
        self.assertRegex(report["code_commit"], r"^[0-9a-f]{9}$")
        self.assertEqual(report["route"]["route_id"], "fixed_radius_count_threshold_2d")
        self.assertEqual(report["validation"]["cupy_no_host_stage_probe"], "pass")
        self.assertTrue(classification["transfer_counter_observed"])
        self.assertTrue(classification["no_host_stage_ready"])
        self.assertFalse(classification["host_stage_observed"])
        self.assertEqual(classification["observed_device_to_host_calls"], 0)
        self.assertEqual(classification["observed_unknown_calls"], 0)
        self.assertLess(
            classification["observed_host_to_device_bytes"],
            classification["min_named_column_bytes"],
        )
        self.assertTrue(classification["internal_device_to_device_copy_allowed"])
        self.assertFalse(classification["v4_true_zero_copy_claim_authorized"])
        self.assertTrue(report["metadata_subset"]["named_cuda_columns_no_host_stage_authorized"])
        self.assertTrue(report["metadata_subset"]["internal_device_staging_disclosed"])
        self.assertIn("LD_PRELOAD", script)
        self.assertIn("v4_m1_fixed_radius_prepare_plus_query_after_warmup", script)
        self.assertFalse(report["claim_boundaries"]["async_claim_authorized"])
        self.assertFalse(report["claim_boundaries"]["public_speedup_claim_authorized"])
        self.assertFalse(report["claim_boundaries"]["rt_core_speedup_claim_authorized"])
        self.assertFalse(report["claim_boundaries"]["v4_true_zero_copy_claim_authorized"])

    def test_cupy_stream_smoke_script_is_reproducible_route_gate(self) -> None:
        script = SMOKE_SCRIPT.read_text(encoding="utf-8")

        for token in (
            "run_v4_fixed_radius_count_threshold_2d",
            "cp.cuda.Stream(non_blocking=True)",
            "pointer_identity",
            "pointer_echo_identity",
            "native_call_device_pointer_echo",
            "named_cuda_columns_no_host_stage_authorized",
            "internal_device_staging_disclosed",
            "source_audit",
            "promotion_blockers",
            "prepare_on_stream_symbol_present",
            "if not all(result[\"source_audit\"].values())",
            "native_async_ready",
            "v4_true_zero_copy_claim_authorized",
        ):
            self.assertIn(token, script)

    def test_cupy_benchmark_probe_keeps_speed_claims_blocked(self) -> None:
        script = BENCHMARK_SCRIPT.read_text(encoding="utf-8")

        for token in (
            "v4_one_shot_prepare_plus_query",
            "v4_prepared_query_only",
            "cupy_bruteforce_cuda_core_baseline",
            "public_speedup_claim_authorized",
            "rt_core_speedup_claim_authorized",
            "False",
            "baseline_limitations",
            "not authorize public speedup wording",
        ):
            self.assertIn(token, script)

    def test_claim_review_keeps_v4_true_zero_copy_claim_blocked(self) -> None:
        review = CLAIM_REVIEW.read_text(encoding="utf-8")

        for token in (
            "Verdict: keep `v4_true_zero_copy_claim_authorized` false",
            "Prepare caller-stream support has now landed",
            "transfer-counter or equivalent no-host-stage evidence",
            "fail-closed matrix",
            "Do not promote",
        ):
            self.assertIn(token, review)

    def test_wording_consensus_keeps_public_true_zero_copy_blocked(self) -> None:
        consensus = WORDING_CONSENSUS.read_text(encoding="utf-8")

        for token in (
            "Keep `v4_true_zero_copy_claim_authorized` false",
            "zero-copy device-column handoff with no observed host staging of named columns",
            "not end-to-end true zero-copy",
            "named_cuda_columns_no_host_stage_authorized",
            "internal device-to-device AABB/BVH staging",
            "Async remains blocked",
        ):
            self.assertIn(token, consensus)

    def test_operator_uses_on_stream_route_for_nonzero_caller_stream(self) -> None:
        search = _point_columns(0x1000)
        query = _point_columns(0x2000)
        outputs = _output_columns(0x3000)
        prepared = _FakePrepared()

        with mock.patch.object(v4, "_prepare_scene") as prepare_scene, mock.patch.object(
            v4,
            "_prepare_scene_on_stream",
            return_value=prepared,
        ) as prepare_on_stream, mock.patch.object(
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

        prepare_scene.assert_not_called()
        prepare_on_stream.assert_called_once()
        self.assertEqual(prepare_on_stream.call_args.kwargs["cuda_stream_ptr"], 456)
        run_prepared.assert_not_called()
        self.assertEqual(prepared.on_stream_call["cuda_stream_ptr"], 456)
        self.assertIs(prepared.on_stream_call["query_ids_out"], outputs["query_ids"])
        metadata = result["metadata"]
        self.assertEqual(metadata["caller_stream_handle"], 456)
        self.assertEqual(metadata["prepare_stream_handle"], 456)
        self.assertTrue(metadata["caller_stream_native_propagation_ready"])
        self.assertTrue(metadata["native_prepare_stream_propagation_ready"])
        self.assertTrue(metadata["native_synchronized_before_return"])
        self.assertFalse(metadata["native_async_ready"])
        self.assertTrue(metadata["native_true_zero_copy_authorized"])
        self.assertTrue(metadata["native_call_device_pointer_echo_complete"])
        self.assertEqual(metadata["native_call_device_pointer_echo"]["query.x"], 0x2020)
        self.assertEqual(metadata["native_call_device_pointer_echo"]["output.neighbor_counts"], 0x3020)
        self.assertTrue(metadata["named_cuda_columns_no_host_stage_authorized"])
        self.assertTrue(metadata["named_cuda_columns_no_host_stage_ready"])
        self.assertTrue(metadata["internal_device_staging_disclosed"])
        self.assertIn("AABB/BVH", metadata["internal_device_staging_scope"])
        self.assertEqual(
            metadata["v4_true_zero_copy_claim_blocker"],
            "public_true_zero_copy_wording_blocked_by_internal_device_staging_and_sync_contract",
        )
        self.assertFalse(metadata["v4_true_zero_copy_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
