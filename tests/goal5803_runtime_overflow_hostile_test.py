from __future__ import annotations

import ctypes
import os
from pathlib import Path
from types import SimpleNamespace
import threading
import unittest
from unittest.mock import patch

import rtdsl.v4_rtdlexe as runtime


# This is the exact fail-closed status emitted by the frozen v7 bounded-
# relation native owner when semantic capacity is exceeded.  It is deliberately
# not a public error code: the public runtime must translate it only when the
# independently returned overflow/count control agrees.
_NATIVE_RELATION_OUTPUT_OVERFLOW = 0xFFFF5102


def _set_pointer(argument, ctype, value) -> None:
    ctypes.cast(argument, ctypes.POINTER(ctype))[0] = value


def _fill_relation_receipt(
    argument,
    *,
    capacity: int,
    compact_status: int,
    output_bytes: int,
    status_before_output: bool = True,
    failure_output_bytes: int = 0,
    failure_output_copy_call_count: int = 0,
    output_d2h_after_status_failure: int = 0,
) -> None:
    receipt = ctypes.cast(
        argument, ctypes.POINTER(runtime._FastPathReceipt)
    )[0]
    success = compact_status == 0
    key_capacity = 1
    while key_capacity < 2 * capacity:
        key_capacity <<= 1

    receipt.schema_version = 2
    receipt.optix_launch_count = 2
    receipt.host_blocking_boundary_count = 2 if success else 1
    receipt.control_d2h_bytes = 28
    receipt.output_d2h_bytes = (
        output_bytes if success else failure_output_bytes
    )
    receipt.status_before_output = int(status_before_output)
    receipt.output_d2h_after_status_failure = output_d2h_after_status_failure
    receipt.role_counters_materialized = 0
    receipt.prepared_input_reused = 0
    receipt.dynamic_device_upload_call_count = 2
    receipt.dynamic_accel_build_count = 1
    receipt.dynamic_explicit_sync_count = 0
    receipt.dynamic_blocking_upload_call_count = 0
    receipt.dynamic_device_upload_bytes = 40
    receipt.dynamic_input_generation = 1
    receipt.semantic_compaction_launch_count = 1
    receipt.semantic_compaction_key_capacity = key_capacity
    receipt.semantic_compaction_scratch_bytes = (
        8 * key_capacity + 8 * capacity + 2 * ctypes.sizeof(ctypes.c_uint32)
    )
    # v7 online monitoring incorporates callback status into the OptiX
    # programs; the only auxiliary launch is semantic compaction.
    receipt.callback_status_kernel_launch_count = 0
    receipt.checked_product_kernel_launch_count = 0
    receipt.compact_control_finalizer_kernel_launch_count = 0
    receipt.total_auxiliary_cuda_kernel_launch_count = 1
    receipt.execution_parameter_h2d_bytes = 240
    receipt.execution_parameter_h2d_copy_call_count = 2
    receipt.stream_ordered_memset_call_count = 4
    receipt.status_d2h_copy_call_count = 1
    receipt.output_d2h_copy_call_count = (
        int(success and output_bytes > 0)
        if success else failure_output_copy_call_count
    )


class _FakeRelationNative:
    """Exact Python-side model of the v7 native status/output ABI."""

    def __init__(
        self,
        *,
        capacity: int,
        compact_status: int,
        raw_count: int,
        unique_count: int,
        overflowed: int,
        rows: tuple[tuple[int, int], ...] = (),
        status_before_output: bool = True,
        failure_output_bytes: int = 0,
        failure_output_copy_call_count: int = 0,
        output_d2h_after_status_failure: int = 0,
    ) -> None:
        self.capacity = capacity
        self.compact_status = compact_status
        self.raw_count = raw_count
        self.unique_count = unique_count
        self.overflowed = overflowed
        self.rows = rows
        self.status_before_output = status_before_output
        self.failure_output_bytes = failure_output_bytes
        self.failure_output_copy_call_count = failure_output_copy_call_count
        self.output_d2h_after_status_failure = output_d2h_after_status_failure
        self.call_count = 0

    def __call__(self, *arguments) -> int:
        self.call_count += 1
        # rtdl_v4_prepared_bounded_relation_callback_execute_v7 ABI:
        # token, bounds, ids, count, reuse, raw, unique, overflow, rows,
        # compact status, operation receipt, error, error capacity.
        _set_pointer(arguments[5], ctypes.c_uint64, self.raw_count)
        _set_pointer(arguments[6], ctypes.c_uint64, self.unique_count)
        _set_pointer(arguments[7], ctypes.c_uint32, self.overflowed)
        rows = ctypes.cast(arguments[8], ctypes.POINTER(ctypes.c_uint32))
        for index, (source_id, item_id) in enumerate(self.rows):
            rows[index * 2] = source_id
            rows[index * 2 + 1] = item_id
        _set_pointer(arguments[9], ctypes.c_uint32, self.compact_status)
        _fill_relation_receipt(
            arguments[10],
            capacity=self.capacity,
            compact_status=self.compact_status,
            output_bytes=8 * self.unique_count,
            status_before_output=self.status_before_output,
            failure_output_bytes=self.failure_output_bytes,
            failure_output_copy_call_count=(
                self.failure_output_copy_call_count),
            output_d2h_after_status_failure=(
                self.output_d2h_after_status_failure),
        )
        return 0


class _FakeTriangleNative:
    def __init__(self, compact_status: int) -> None:
        self.compact_status = compact_status

    def __call__(self, *arguments) -> int:
        # v6 (online, non-lean) triangle ABI.
        _set_pointer(arguments[9], ctypes.c_uint64, 0)
        _set_pointer(arguments[10], ctypes.c_uint32, self.compact_status)
        receipt = ctypes.cast(
            arguments[11], ctypes.POINTER(runtime._FastPathReceipt)
        )[0]
        receipt.schema_version = 2
        receipt.optix_launch_count = 1
        receipt.host_blocking_boundary_count = 1
        receipt.control_d2h_bytes = 88
        receipt.output_d2h_bytes = 0
        receipt.status_before_output = 1
        receipt.output_d2h_after_status_failure = 0
        receipt.role_counters_materialized = 1
        receipt.prepared_input_reused = 0
        receipt.dynamic_device_upload_call_count = 7
        receipt.dynamic_device_upload_bytes = 28
        receipt.dynamic_input_generation = 1
        receipt.execution_parameter_h2d_bytes = 224
        receipt.execution_parameter_h2d_copy_call_count = 1
        receipt.stream_ordered_memset_call_count = 2
        receipt.status_d2h_copy_call_count = 1
        receipt.output_d2h_copy_call_count = 0
        return 0


def _owner(native: _FakeRelationNative):
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
    owner._online_monitor = True
    owner._lean_monitor = False
    owner._artifact_identity = "a" * 64
    owner._ptx_sha = "b" * 64
    owner._native_sha = "c" * 64
    owner._commit_source_cache = lambda _digest: None
    owner._native_source_cache_digest = lambda: None
    return owner


def _triangle_owner(native: _FakeTriangleNative):
    owner = object.__new__(runtime._PreparedTriangleOwner)
    owner._closed = False
    owner._pid = os.getpid()
    owner._thread = threading.get_ident()
    owner._active = threading.Lock()
    owner._token = 1
    owner._library = object()
    owner._execute_fast = native
    owner._execute_diagnostic = object()
    owner._last_batch_key = None
    owner._last_query_arrays = None
    owner._last_fast_operation_receipt = None
    owner._online_monitor = True
    owner._lean_monitor = False
    owner._mode = "all_hit_count"
    owner._event_capacity = 1
    owner._artifact_identity = "1" * 64
    owner._ptx_sha = "2" * 64
    owner._native_sha = "3" * 64
    owner._commit_query_cache = lambda _digest: None
    owner._native_query_cache_digest = lambda: None
    return owner


def _batch(*, expected_rows=None):
    return runtime.BoundedRelationBatch(
        ((0.0, 0.0, 1.0, 1.0, 10),), expected_rows=expected_rows
    )


def _direct_prepared(owner) -> runtime.PreparedRTDLExecutable:
    return runtime.PreparedRTDLExecutable(
        family=runtime._BOUNDED,
        executable_identity_sha256="d" * 64,
        owner=owner,
    )


def _triangle_prepared(owner) -> runtime.PreparedRTDLExecutable:
    return runtime.PreparedRTDLExecutable(
        family=runtime._TRIANGLE,
        executable_identity_sha256="4" * 64,
        owner=owner,
    )


def _provider_ready_prepared(owner) -> runtime.PreparedRTDLExecutable:
    class Loaded:
        family = runtime._BOUNDED
        executable_identity_sha256 = "e" * 64

        def _build_prepared_owner(self, _static_input, **_kwargs):
            return owner

    provider = object.__new__(runtime.ProviderReadyRTDLExecutable)
    provider._loaded = Loaded()
    provider._binding_library = object()
    provider._binding = SimpleNamespace(source_path=Path("sealed-native.so"))
    provider._pid = os.getpid()
    provider._closed = False
    provider._close_failure = None
    provider._active = threading.RLock()
    provider._cuda_readiness = SimpleNamespace(check=lambda: None)
    provider._binding_released = False
    provider._closing = False
    static_input = runtime.BoundedRelationStaticInput(
        ((0.0, 0.0, 2.0, 2.0, 100),)
    )
    with patch.object(
        runtime, "_admit_provider_ready_native_image_lease", return_value=object()
    ):
        return provider.prepare(static_input)


class Goal5803RuntimeOverflowHostileTest(unittest.TestCase):
    def test_genuine_capacity_overflow_is_public_rx041_and_never_downloads_output(self):
        native = _FakeRelationNative(
            capacity=1,
            compact_status=_NATIVE_RELATION_OUTPUT_OVERFLOW,
            raw_count=2,
            unique_count=2,
            overflowed=1,
        )
        owner = _owner(native)

        with self.assertRaises(runtime.RTDLExecutableError) as caught:
            _direct_prepared(owner).execute(_batch(), include_diagnostics=False)

        # Inspect the exact native operation evidence even though no public
        # result was produced.  Overflow must have one status boundary and no
        # application-output transfer or post-failure output boundary.
        operation = dict(owner._last_fast_operation_receipt)
        self.assertEqual(operation["host_blocking_boundary_count"], 1)
        self.assertIs(operation["status_before_output"], True)
        self.assertEqual(operation["output_d2h_copy_call_count"], 0)
        self.assertEqual(operation["output_d2h_bytes"], 0)
        self.assertEqual(operation["output_d2h_after_status_failure"], 0)
        self.assertEqual(owner._last_fast_compact_control["status"],
                         _NATIVE_RELATION_OUTPUT_OVERFLOW)
        self.assertEqual(owner._last_fast_compact_control["overflowed"], 1)
        self.assertEqual(owner._last_fast_compact_control["unique_event_count"], 2)
        self.assertEqual(caught.exception.code, "RX041_OUTPUT_OVERFLOW")

    def test_provider_ready_path_preserves_exact_overflow_translation(self):
        native = _FakeRelationNative(
            capacity=1,
            compact_status=_NATIVE_RELATION_OUTPUT_OVERFLOW,
            raw_count=2,
            unique_count=2,
            overflowed=1,
        )
        owner = _owner(native)
        prepared = _provider_ready_prepared(owner)

        with self.assertRaises(runtime.RTDLExecutableError) as caught:
            prepared.execute(_batch(), include_diagnostics=False)

        self.assertEqual(caught.exception.code, "RX041_OUTPUT_OVERFLOW")
        operation = dict(owner._last_fast_operation_receipt)
        self.assertEqual(operation["status_d2h_copy_call_count"], 1)
        self.assertEqual(operation["output_d2h_copy_call_count"], 0)
        self.assertEqual(operation["output_d2h_after_status_failure"], 0)

    def test_unknown_status_is_rx035_even_if_overflow_shaped(self):
        for label, status, unique_count, overflowed in (
            ("status_summary_invalid_overflow_shaped", 0xFFFF5101, 2, 1),
            ("checked_product_invalid_overflow_shaped", 0xFFFF5103, 2, 1),
            ("unknown_plain", 0xDEADBEEF, 0, 0),
            ("unknown_overflow_shaped", 0xDEADBEEF, 2, 1),
            ("overflow_code_without_overflow_evidence",
             _NATIVE_RELATION_OUTPUT_OVERFLOW, 1, 0),
            ("overflow_evidence_without_overflow_status", 0, 2, 1),
        ):
            with self.subTest(label=label):
                owner = _owner(_FakeRelationNative(
                    capacity=1,
                    compact_status=status,
                    raw_count=unique_count,
                    unique_count=unique_count,
                    overflowed=overflowed,
                ))
                with self.assertRaises(runtime.RTDLExecutableError) as caught:
                    _direct_prepared(owner).execute(
                        _batch(), include_diagnostics=False
                    )
                self.assertEqual(caught.exception.code,
                                 "RX035_DEVICE_STATUS_INVALID")

    def test_raw_event_capacity_overflow_is_rx041_even_when_unique_count_fits(self):
        capacity = 1
        owner = _owner(_FakeRelationNative(
            capacity=capacity,
            compact_status=_NATIVE_RELATION_OUTPUT_OVERFLOW,
            raw_count=2 * capacity + 1,
            unique_count=capacity,
            # Exercise raw-count corroboration independently from the compact
            # overflow bit and semantic unique-count witness.
            overflowed=0,
        ))
        with self.assertRaises(runtime.RTDLExecutableError) as caught:
            _direct_prepared(owner).execute(_batch(), include_diagnostics=False)
        operation = dict(owner._last_fast_operation_receipt)
        self.assertEqual(operation["output_d2h_bytes"], 0)
        self.assertEqual(operation["output_d2h_copy_call_count"], 0)
        self.assertEqual(caught.exception.code, "RX041_OUTPUT_OVERFLOW")

    def test_raw_capacity_uses_actual_pair_domain_not_two_times_large_k(self):
        # Native bounds the private two-pass row buffer by both 2*K and the
        # actual Cartesian domain.  With one source and one indexed box, at
        # most two pass-events exist even though semantic K is much larger.
        capacity = 8
        actual_raw_capacity = 2
        owner = _owner(_FakeRelationNative(
            capacity=capacity,
            compact_status=_NATIVE_RELATION_OUTPUT_OVERFLOW,
            raw_count=actual_raw_capacity + 1,
            unique_count=1,
            overflowed=0,
        ))
        self.assertEqual(owner._indexed_count, 1)
        batch = _batch()
        self.assertEqual(len(batch.source_boxes), 1)
        with self.assertRaises(runtime.RTDLExecutableError) as caught:
            _direct_prepared(owner).execute(batch, include_diagnostics=False)
        self.assertEqual(caught.exception.code, "RX041_OUTPUT_OVERFLOW")
        control = owner._last_fast_compact_control
        # If the public forensic control carries the native bound, it must be
        # the actual domain bound and never the looser 2*K value.
        if "raw_event_capacity" in control:
            self.assertEqual(control["raw_event_capacity"], actual_raw_capacity)

    def test_exact_overflow_status_with_forged_failure_receipt_is_rx035_first(self):
        hostile_receipts = (
            {"status_before_output": False},
            {
                "failure_output_bytes": 8,
                "failure_output_copy_call_count": 1,
                "output_d2h_after_status_failure": 1,
            },
        )
        for hostile in hostile_receipts:
            with self.subTest(hostile=hostile):
                owner = _owner(_FakeRelationNative(
                    capacity=1,
                    compact_status=_NATIVE_RELATION_OUTPUT_OVERFLOW,
                    raw_count=2,
                    unique_count=2,
                    overflowed=1,
                    **hostile,
                ))
                with self.assertRaises(runtime.RTDLExecutableError) as caught:
                    _direct_prepared(owner).execute(
                        _batch(), include_diagnostics=False
                    )
                self.assertEqual(caught.exception.code,
                                 "RX035_DEVICE_STATUS_INVALID")

    def test_receipt_boolean_fields_require_exact_zero_or_one(self):
        relation = runtime._FastPathReceipt()
        _fill_relation_receipt(
            ctypes.byref(relation),
            capacity=1,
            compact_status=_NATIVE_RELATION_OUTPUT_OVERFLOW,
            output_bytes=16,
        )

        def validate_relation(receipt):
            return runtime._validate_fast_operation_receipt(
                receipt,
                family=runtime._BOUNDED,
                compact_status=_NATIVE_RELATION_OUTPUT_OVERFLOW,
                expected_output_d2h_bytes=16,
                expected_prepared_input_reused=False,
                expected_semantic_capacity=1,
                online_monitor=True,
                lean_monitor=False,
            )

        relation_baseline = validate_relation(relation)
        self.assertIs(relation_baseline["status_before_output"], True)
        self.assertIs(relation_baseline["prepared_input_reused"], False)

        bad_status_order = runtime._FastPathReceipt.from_buffer_copy(relation)
        bad_status_order.status_before_output = 2
        with self.assertRaises(runtime.RTDLExecutableError) as caught:
            validate_relation(bad_status_order)
        self.assertEqual(caught.exception.code, "RX035_DEVICE_STATUS_INVALID")

        bad_reuse = runtime._FastPathReceipt.from_buffer_copy(relation)
        bad_reuse.prepared_input_reused = 2
        with self.assertRaises(runtime.RTDLExecutableError) as caught:
            validate_relation(bad_reuse)
        self.assertEqual(caught.exception.code, "RX035_DEVICE_STATUS_INVALID")

        triangle = runtime._FastPathReceipt()
        triangle.schema_version = 2
        triangle.optix_launch_count = 1
        triangle.host_blocking_boundary_count = 1
        triangle.control_d2h_bytes = 88
        triangle.output_d2h_bytes = 0
        triangle.status_before_output = 1
        triangle.output_d2h_after_status_failure = 0
        triangle.role_counters_materialized = 1
        triangle.prepared_input_reused = 0
        triangle.dynamic_device_upload_call_count = 7
        triangle.dynamic_device_upload_bytes = 28
        triangle.dynamic_input_generation = 1
        triangle.execution_parameter_h2d_bytes = 224
        triangle.execution_parameter_h2d_copy_call_count = 1
        triangle.stream_ordered_memset_call_count = 2
        triangle.status_d2h_copy_call_count = 1
        triangle.output_d2h_copy_call_count = 0
        def validate_triangle(receipt):
            return runtime._validate_fast_operation_receipt(
                receipt,
                family=runtime._TRIANGLE,
                compact_status=_NATIVE_RELATION_OUTPUT_OVERFLOW,
                expected_output_d2h_bytes=8,
                expected_prepared_input_reused=False,
                online_monitor=True,
                lean_monitor=False,
            )

        triangle_baseline = validate_triangle(triangle)
        self.assertIs(triangle_baseline["role_counters_materialized"], True)

        bad_role_counters = runtime._FastPathReceipt.from_buffer_copy(triangle)
        bad_role_counters.role_counters_materialized = 2
        with self.assertRaises(runtime.RTDLExecutableError) as caught:
            validate_triangle(bad_role_counters)
        self.assertEqual(caught.exception.code, "RX035_DEVICE_STATUS_INVALID")

    def test_triangle_5102_remains_rx035_not_relation_overflow(self):
        owner = _triangle_owner(
            _FakeTriangleNative(_NATIVE_RELATION_OUTPUT_OVERFLOW)
        )
        batch = runtime.TriangleReductionBatch(
            queries=(((0.0, 0.0, -1.0), (0.0, 0.0, 1.0), 10.0),)
        )
        with self.assertRaises(runtime.RTDLExecutableError) as caught:
            _triangle_prepared(owner).execute(batch, include_diagnostics=False)
        self.assertEqual(caught.exception.code, "RX035_DEVICE_STATUS_INVALID")

    def test_diagnostic_capacity_overflow_remains_rx041(self):
        owner = _owner(_FakeRelationNative(
            capacity=1, compact_status=0, raw_count=0,
            unique_count=0, overflowed=0,
        ))
        build_counts = iter((0, 1))
        owner._native_source_build_count = lambda: next(build_counts)

        def diagnostic(*arguments):
            _set_pointer(arguments[5], ctypes.c_uint64, 2)
            _set_pointer(arguments[6], ctypes.c_uint64, 2)
            _set_pointer(arguments[7], ctypes.c_uint32, 1)
            summary = ctypes.cast(
                arguments[9], ctypes.POINTER(runtime._ProductStatusSummary)
            )[0]
            summary.schema_version = 2
            summary.ok = 1
            summary.validated_row_count = 2
            summary.required_invocation_mask = (1 << 1) | (1 << 6)
            summary.terminal_invocation_mask = (1 << 4) | (1 << 5)
            summary.first_invalid_row = (1 << 64) - 1
            summary.success_status_d2h_bytes = ctypes.sizeof(
                runtime._ProductStatusSummary
            )
            counters = ctypes.cast(
                arguments[10], ctypes.POINTER(ctypes.c_uint64)
            )
            for index, value in enumerate((0, 2, 0, 0, 2, 0, 2)):
                summary.role_counters[index] = value
                counters[index] = value
            return 0

        owner._execute_diagnostic = diagnostic

        class Audit:
            aborted = False

            def abort(self):
                self.aborted = True

        audit = Audit()
        with patch.object(runtime, "_open_audit", return_value=audit):
            with self.assertRaises(runtime.RTDLExecutableError) as caught:
                _direct_prepared(owner).execute(
                    _batch(), include_diagnostics=True
                )
        self.assertEqual(caught.exception.code, "RX041_OUTPUT_OVERFLOW")
        self.assertIs(audit.aborted, True)

    def test_normal_status_and_output_are_unchanged_and_evidence_is_deferred(self):
        owner = _owner(_FakeRelationNative(
            capacity=1,
            compact_status=0,
            raw_count=1,
            unique_count=1,
            overflowed=0,
            rows=((10, 100),),
        ))
        result = _direct_prepared(owner).execute(
            _batch(expected_rows=((10, 100),)), include_diagnostics=False
        )

        self.assertEqual(result.output, ((10, 100),))
        self.assertIsNone(result.output_sha256)
        self.assertIsNone(result.device_status._materialized)
        self.assertIsNone(owner._last_fast_operation_receipt._materialized)
        self.assertIs(result.device_status["ok"], True)
        self.assertEqual(result.device_status["compact_status"], 0)
        self.assertEqual(result.device_status["validated_unique_event_count"], 1)
        operation = result.device_status["operation_receipt"]
        self.assertIs(operation["status_before_output"], True)
        self.assertEqual(operation["status_d2h_copy_call_count"], 1)
        self.assertEqual(operation["output_d2h_copy_call_count"], 1)
        self.assertEqual(operation["output_d2h_after_status_failure"], 0)

    def test_identical_canonical_output_reuses_immutable_python_rows(self):
        native = _FakeRelationNative(
            capacity=1,
            compact_status=0,
            raw_count=1,
            unique_count=1,
            overflowed=0,
            rows=((10, 100),),
        )
        owner = _owner(native)
        prepared = _direct_prepared(owner)
        batch = _batch(expected_rows=((10, 100),))

        first = prepared.execute(batch, include_diagnostics=False)
        second = prepared.execute(batch, include_diagnostics=False)

        self.assertIs(second.output, first.output)
        self.assertIs(owner._cached_output_rows, first.output)
        self.assertEqual(native.call_count, 2)

    def test_oracle_failure_cannot_publish_output_cache(self):
        native = _FakeRelationNative(
            capacity=1,
            compact_status=0,
            raw_count=1,
            unique_count=1,
            overflowed=0,
            rows=((10, 100),),
        )
        owner = _owner(native)
        prepared = _direct_prepared(owner)
        batch = _batch(expected_rows=((10, 100),))
        first = prepared.execute(batch, include_diagnostics=False)

        native.rows = ((10, 101),)
        with self.assertRaises(runtime.RTDLExecutableError) as caught:
            prepared.execute(batch, include_diagnostics=False)
        self.assertEqual(caught.exception.code, "RX043_ORACLE_MISMATCH")
        self.assertIs(owner._cached_output_rows, first.output)

        native.rows = ((10, 100),)
        recovered = prepared.execute(batch, include_diagnostics=False)
        self.assertIs(recovered.output, first.output)

    def test_impossible_success_control_is_rx035_before_public_output(self):
        hostile_controls = (
            {
                "label": "unique_count_exceeds_raw_count",
                "raw_count": 0,
                "unique_count": 1,
                "overflowed": 0,
            },
            {
                "label": "overflow_flag_outside_boolean_domain",
                "raw_count": 0,
                "unique_count": 0,
                "overflowed": 2,
            },
        )
        for control in hostile_controls:
            with self.subTest(label=control["label"]):
                owner = _owner(_FakeRelationNative(
                    capacity=1,
                    compact_status=0,
                    raw_count=control["raw_count"],
                    unique_count=control["unique_count"],
                    overflowed=control["overflowed"],
                    rows=((10, 100),) if control["unique_count"] else (),
                ))
                with self.assertRaises(runtime.RTDLExecutableError) as caught:
                    # The assertion surrounds execute itself: rejection after
                    # observing device_status would be too late because output
                    # would already have crossed the public API boundary.
                    _direct_prepared(owner).execute(
                        _batch(), include_diagnostics=False
                    )
                self.assertEqual(caught.exception.code,
                                 "RX035_DEVICE_STATUS_INVALID")

    def test_deferred_receipt_rejects_false_status_before_output(self):
        owner = _owner(_FakeRelationNative(
            capacity=1,
            compact_status=0,
            raw_count=1,
            unique_count=1,
            overflowed=0,
            rows=((10, 100),),
            status_before_output=False,
        ))
        result = _direct_prepared(owner).execute(
            _batch(expected_rows=((10, 100),)), include_diagnostics=False
        )
        # Semantic compact success is eager; measurement evidence is lazy.  A
        # caller that materializes that evidence must never receive a forged
        # status-before-output claim as valid.
        with self.assertRaises(runtime.RTDLExecutableError) as caught:
            dict(result.device_status)
        self.assertEqual(caught.exception.code, "RX035_DEVICE_STATUS_INVALID")


if __name__ == "__main__":
    unittest.main()
