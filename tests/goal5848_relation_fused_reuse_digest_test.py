from __future__ import annotations

import ctypes
import os
import struct
import threading
import unittest

from rtdsl import v4_rtdlexe as runtime
from scripts import build_v4_optix_native_snapshot as native_builder

ROOT = native_builder.ROOT


def _set_pointer(argument, ctype, value) -> None:
    ctypes.cast(argument, ctypes.POINTER(ctype))[0] = value


class _FakeV9RelationNative:
    capacity = 8

    def __init__(self) -> None:
        self.reuse_flags: list[int] = []
        self.expected_digests: list[bytes] = []

    def __call__(self, *arguments) -> int:
        # v9: token, bounds, ids, count, reuse, digest, digest-size,
        # raw, unique, overflow, rows, status, receipt, error, error-size.
        reuse = int(arguments[4])
        self.reuse_flags.append(reuse)
        self.expected_digests.append(bytes(arguments[5][:int(arguments[6])]))
        _set_pointer(arguments[7], ctypes.c_uint64, 2)
        _set_pointer(arguments[8], ctypes.c_uint64, 1)
        _set_pointer(arguments[9], ctypes.c_uint32, 0)
        rows = ctypes.cast(arguments[10], ctypes.POINTER(ctypes.c_uint32))
        rows[0] = 10
        rows[1] = 20
        _set_pointer(arguments[11], ctypes.c_uint32, 0)
        receipt = ctypes.cast(
            arguments[12], ctypes.POINTER(runtime._FastPathReceipt)
        )[0]
        key_capacity = 1
        while key_capacity < 2 * self.capacity:
            key_capacity <<= 1
        receipt.schema_version = 2
        receipt.optix_launch_count = 2
        receipt.host_blocking_boundary_count = 2
        receipt.control_d2h_bytes = 28
        receipt.output_d2h_bytes = 8
        receipt.status_before_output = 1
        receipt.output_d2h_after_status_failure = 0
        receipt.role_counters_materialized = 0
        receipt.prepared_input_reused = reuse
        receipt.dynamic_device_upload_call_count = 0 if reuse else 2
        receipt.dynamic_device_upload_bytes = 0 if reuse else 40
        receipt.dynamic_accel_build_count = 0 if reuse else 1
        receipt.dynamic_explicit_sync_count = 0
        receipt.dynamic_blocking_upload_call_count = 0
        receipt.dynamic_input_generation = 1
        receipt.semantic_compaction_launch_count = 1
        receipt.semantic_compaction_key_capacity = key_capacity
        receipt.semantic_compaction_scratch_bytes = (
            8 * key_capacity + 8 * self.capacity
            + 2 * ctypes.sizeof(ctypes.c_uint32)
        )
        receipt.callback_status_kernel_launch_count = 0
        receipt.checked_product_kernel_launch_count = 0
        receipt.compact_control_finalizer_kernel_launch_count = 0
        receipt.total_auxiliary_cuda_kernel_launch_count = 1
        receipt.execution_parameter_h2d_bytes = 240
        receipt.execution_parameter_h2d_copy_call_count = 2
        receipt.stream_ordered_memset_call_count = 4
        receipt.status_d2h_copy_call_count = 1
        receipt.output_d2h_copy_call_count = 1
        return 0


def _owner(native: _FakeV9RelationNative):
    owner = object.__new__(runtime._PreparedBoundedOwner)
    owner._closed = False
    owner._pid = os.getpid()
    owner._thread = threading.get_ident()
    owner._active = threading.Lock()
    owner._capacity = native.capacity
    owner._indexed_count = 1
    owner._minimum_overlap = 1.0
    owner._token = 1
    owner._library = object()
    owner._execute_fast = native
    owner._execute_diagnostic = object()
    owner._last_batch_key = None
    owner._last_source_arrays = None
    owner._last_fast_operation_receipt = None
    owner._last_fast_compact_control = None
    owner._row_storage = (ctypes.c_uint32 * (native.capacity * 2))()
    owner._fast_raw_count = ctypes.c_uint64()
    owner._fast_unique_count = ctypes.c_uint64()
    owner._fast_overflowed = ctypes.c_uint32()
    owner._fast_compact_status = ctypes.c_uint32()
    owner._call_error = ctypes.create_string_buffer(16384)
    owner._cached_output_packed = None
    owner._cached_output_rows = None
    owner._cached_output_sha = None
    owner._cached_validated_expected_rows = None
    owner._online_monitor = True
    owner._lean_monitor = True
    owner._fused_reuse_digest = True
    owner._artifact_identity = "a" * 64
    owner._ptx_sha = "b" * 64
    owner._native_sha = "c" * 64
    owner._commit_source_cache = lambda _digest: None
    return owner


class Goal5848RelationFusedReuseDigestTest(unittest.TestCase):
    def test_tuple_and_buffer_batches_precompute_exact_digest_storage(self):
        rows = ((0.0, 0.0, 1.0, 1.0, 10),)
        tuple_batch = runtime.BoundedRelationBatch(rows)
        buffer_batch = runtime.BoundedRelationBufferBatch(
            source_bounds_f32le=struct.pack("<4f", *rows[0][:4]),
            source_ids_u32le=struct.pack("<I", rows[0][4]),
            source_count=1,
        )
        self.assertEqual(
            tuple_batch._device_input_sha256,
            buffer_batch._device_input_sha256,
        )
        expected = bytes.fromhex(tuple_batch._device_input_sha256)
        self.assertEqual(bytes(tuple_batch._device_input_digest_u8), expected)
        self.assertEqual(bytes(buffer_batch._device_input_digest_u8), expected)

    def test_fast_reuse_fuses_digest_check_into_single_execute_boundary(self):
        native = _FakeV9RelationNative()
        owner = _owner(native)
        digest_queries = []
        owner._native_source_cache_digest = lambda: digest_queries.append(True)
        batch = runtime.BoundedRelationBatch(
            ((0.0, 0.0, 1.0, 1.0, 10),),
            expected_rows=((10, 20),),
        )

        first = owner.execute(batch, diagnostics=False)
        second = owner.execute(batch, diagnostics=False)

        self.assertEqual(first[0], ((10, 20),))
        self.assertIs(second[0], first[0])
        self.assertEqual(native.reuse_flags, [0, 1])
        self.assertEqual(digest_queries, [])
        expected = bytes.fromhex(batch._device_input_sha256)
        self.assertEqual(native.expected_digests, [expected, expected])
        self.assertIs(dict(second[2])["prepared_input_reused"], True)

    def test_v9_is_bound_by_projection_native_descriptor_and_aot_exports(self):
        source = (
            ROOT / "src/native/optix/rtdl_optix_v4_callback_poc.cpp"
        ).read_text(encoding="utf-8")
        relation = source.split(
            "static void execute_v4_prepared_bounded_relation_callback(", 1
        )[1].split(
            "static void execute_v4_prepared_bounded_relation_callback_summary(",
            1,
        )[0]
        self.assertLess(
            relation.index("std::lock_guard<std::mutex> execution_lock"),
            relation.index("std::memcmp(expected_reuse_digest"),
        )
        self.assertIn("source_cache_digest_valid", relation)
        api = (ROOT / "src/native/optix/rtdl_optix_api.cpp").read_text(
            encoding="utf-8-sig"
        )
        symbol = (
            "rtdl_optix_v4_execute_prepared_bounded_relation_callback_v9"
        )
        self.assertIn(symbol, api)
        self.assertIn(symbol, native_builder.RTDLEXE_AOT_REQUIRED_SYMBOLS)
        export_map = native_builder.RTDLEXE_EXPORT_MAP.read_text(encoding="utf-8")
        self.assertIn(symbol + ";", export_map)

    def test_v9_runtime_schema_is_current_but_v7_remains_admissible(self):
        current = runtime._validate_runtime({
            "family": runtime._BOUNDED,
            "native_abi": "rtdl.v4.prepared_bounded_relation_callback.v9",
            "capacity": 8,
            "minimum_overlap_f32": 0.0,
            "triangle_mode": None,
            "dynamic_status": "static_protocol_checked_compact_device_status_v5",
        })
        legacy = runtime._validate_runtime({
            **dict(current),
            "native_abi": "rtdl.v4.prepared_bounded_relation_callback.v7",
        })
        self.assertEqual(str(current["native_abi"]).rsplit(".", 1)[-1], "v9")
        self.assertEqual(str(legacy["native_abi"]).rsplit(".", 1)[-1], "v7")


if __name__ == "__main__":
    unittest.main()
