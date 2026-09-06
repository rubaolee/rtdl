from __future__ import annotations

import ctypes
import os
import threading
import unittest
from pathlib import Path

from rtdsl import v4_rtdlexe as runtime

ROOT = Path(__file__).resolve().parents[1]


def _batch(expected: int = 7) -> runtime.TriangleReductionBatch:
    return runtime.TriangleReductionBatch(
        queries=(((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 2.0),),
        query_weights=(7,),
        expected_reduced_u64=expected,
    )


def _batch_key(batch: runtime.TriangleReductionBatch) -> tuple[object, ...]:
    return (
        batch._device_input_sha256,
        len(batch.queries),
        len(batch._packed_origins_f32),
        len(batch._packed_directions_f32),
        len(batch._packed_tmax_f32),
        len(batch._packed_weights_u64 or b""),
    )


def _owner(batch: runtime.TriangleReductionBatch):
    owner = runtime._PreparedTriangleOwner.__new__(
        runtime._PreparedTriangleOwner)
    owner._token = 17
    owner._closed = False
    owner._pid = os.getpid()
    owner._thread = threading.get_ident()
    owner._active = threading.Lock()
    owner._library = object()
    owner._mode = "weighted_hit_count"
    owner._online_monitor = True
    owner._lean_monitor = True
    owner._fused_replay = True
    owner._last_batch_key = _batch_key(batch)
    owner._last_query_arrays = (object(), object(), object(), object())
    owner._last_fast_operation_receipt = None
    owner._fast_reduced = ctypes.c_uint64()
    owner._fast_compact_status = ctypes.c_uint32()
    owner._call_error = ctypes.create_string_buffer(16384)
    owner._execute_fast = lambda *_args: (_ for _ in ()).throw(
        AssertionError("full-column v7 execute reached during exact replay"))
    return owner


def _publish_success(args, *, value: int = 7) -> None:
    ctypes.cast(args[5], ctypes.POINTER(ctypes.c_uint64))[0] = value
    ctypes.cast(args[6], ctypes.POINTER(ctypes.c_uint32))[0] = 0
    receipt = ctypes.cast(
        args[7], ctypes.POINTER(runtime._FastPathReceipt))[0]
    receipt.schema_version = 2
    receipt.optix_launch_count = 1
    receipt.host_blocking_boundary_count = 2
    receipt.control_d2h_bytes = 12
    receipt.output_d2h_bytes = 8
    receipt.status_before_output = 1
    receipt.prepared_input_reused = 1
    receipt.dynamic_input_generation = 1
    receipt.execution_parameter_h2d_bytes = 224
    receipt.execution_parameter_h2d_copy_call_count = 1
    receipt.stream_ordered_memset_call_count = 2
    receipt.status_d2h_copy_call_count = 1
    receipt.output_d2h_copy_call_count = 1


class Goal5851TriangleFusedReplayTest(unittest.TestCase):
    def test_exact_replay_uses_reduced_v9_abi_and_preserves_receipt(self) -> None:
        batch = _batch()
        owner = _owner(batch)
        observed = []

        def replay(*args):
            observed.append(args)
            _publish_success(args)
            return 0

        owner._execute_replay = replay
        output, output_sha, status, counters, traversal = owner.execute(
            batch, diagnostics=False)

        self.assertEqual(output, 7)
        self.assertIsNone(output_sha)
        self.assertEqual(counters, ())
        self.assertIsNone(traversal)
        self.assertEqual(len(observed), 1)
        args = observed[0]
        self.assertEqual(len(args), 10)
        self.assertEqual(args[0], 17)
        self.assertEqual(args[1], 1)
        self.assertEqual(args[2], 1)
        self.assertEqual(args[4], 32)
        self.assertEqual(bytes(args[3][:32]).hex(), batch._device_input_sha256)
        self.assertTrue(status["ok"])
        materialized = dict(status)
        self.assertTrue(materialized["prepared_input_reused"])
        self.assertEqual(materialized["success_scalar_d2h_bytes"], 8)
        self.assertEqual(
            dict(materialized["operation_receipt"])["control_d2h_bytes"], 12)

    def test_native_replay_failure_clears_python_reuse_state(self) -> None:
        batch = _batch()
        owner = _owner(batch)

        def reject(*args):
            args[8].value = b"injected v9 digest rejection"
            return 1

        owner._execute_replay = reject
        with self.assertRaisesRegex(
                runtime.RTDLExecutableError, "injected v9 digest rejection"):
            owner.execute(batch, diagnostics=False)
        self.assertIsNone(owner._last_batch_key)
        self.assertIsNone(owner._last_query_arrays)

    def test_native_replay_allows_only_all_absent_cached_host_columns(self) -> None:
        implementation = (
            ROOT / "src/native/optix/rtdl_optix_v4_callback_poc.cpp"
        ).read_text(encoding="utf-8")
        api = (ROOT / "src/native/optix/rtdl_optix_api.cpp").read_text(
            encoding="utf-8")
        exports = (ROOT / "src/native/optix/rtdlexe_exports.map").read_text(
            encoding="utf-8")

        self.assertIn("query_host_inputs_present", implementation)
        self.assertIn("query_host_inputs_absent", implementation)
        self.assertIn(
            "(!reuse_uploaded_query_inputs && query_host_inputs_absent)",
            implementation,
        )
        self.assertIn(
            "rtdl_optix_v4_execute_prepared_triangle_reduction_callback_v9",
            api,
        )
        self.assertIn(
            "prepared_token, nullptr, nullptr, nullptr, query_count, nullptr",
            api,
        )
        self.assertIn(
            "expected_reuse_digest, expected_reuse_digest_size", api)
        self.assertIn(
            "rtdl_optix_v4_execute_prepared_triangle_reduction_callback_v9;",
            exports,
        )


if __name__ == "__main__":
    unittest.main()
