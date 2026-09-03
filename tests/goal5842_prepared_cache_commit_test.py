from __future__ import annotations

import ctypes
import os
import threading
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from rtdsl import v4_bounded_relation_prepared_runtime as relation
from rtdsl import v4_triangle_reduction_prepared_runtime as triangle


class _NativeDigestState:
    def __init__(self) -> None:
        self.digest: bytes | None = None
        self.pending = False
        self.reuse_flags: list[int] = []
        self.scalar_multiplier_flags: list[tuple[int, int]] = []
        self.scalar_reuse_digests: list[bytes] = []
        self.commit_count = 0

    def begin_execution(self, reuse: int) -> int:
        self.reuse_flags.append(reuse)
        if reuse:
            return 0 if self.digest is not None else 1
        self.pending = True
        self.digest = None
        return 0

    def commit(self, _token, digest, size, _error, _error_size) -> int:
        if not self.pending or int(size) != 32:
            return 1
        self.digest = bytes(digest[:32])
        self.pending = False
        self.commit_count += 1
        return 0

    def query(self, _token, digest, size, present, _error, _error_size) -> int:
        if int(size) != 32:
            return 1
        ctypes.cast(present, ctypes.POINTER(ctypes.c_uint32))[0] = int(
            self.digest is not None
        )
        if self.digest is not None:
            ctypes.memmove(digest, self.digest, 32)
        return 0


class _Audit:
    def __init__(self) -> None:
        self.aborted = False

    def finish(self, **_kwargs):
        return {"physical_executor_classification": "optix_traversal_observed"}

    def abort(self) -> None:
        self.aborted = True


class _RejectingAudit(_Audit):
    def finish(self, **_kwargs):
        raise RuntimeError("injected traversal-audit rejection")


def _relation_owner(state: _NativeDigestState):
    owner = object.__new__(relation.PreparedBoundedRelationOwner)
    owner._token = 7
    owner._fresh = SimpleNamespace(authority_nonce="authority")
    owner._contract = SimpleNamespace(capacity=4, contract_sha256="contract")
    owner._abi = SimpleNamespace(abi_sha256="abi")
    owner._library = object()
    owner._commit = state.commit
    owner._cache_digest = state.query
    owner._indexed_count = 1
    owner._native_sha = "a" * 64
    owner._ptx_sha = "b" * 64
    owner._pid = os.getpid()
    owner._thread = threading.get_ident()
    owner._active = threading.Lock()
    owner._closed = False
    owner._execution_count = 0
    owner._cached_source_object = None
    owner._cached_source_native = None
    owner._cached_source_digest = None
    owner._cached_expected_object = None
    owner._cached_expected_rows = None
    owner._cached_output_rows = None
    owner._cached_output_sha = None
    owner._row_storage = (ctypes.c_uint32 * 8)()
    owner._status_capacity = 1
    owner._statuses = (relation._Status * 1)()
    owner._counters = (ctypes.c_uint64 * 7)()
    owner._raw_count = ctypes.c_uint64()
    owner._unique_count = ctypes.c_uint64()
    owner._overflowed = ctypes.c_uint32()
    owner._error = ctypes.create_string_buffer(16384)

    def execute(*args):
        reuse = int(args[4])
        if state.begin_execution(reuse):
            return 1
        ctypes.cast(args[5], ctypes.POINTER(ctypes.c_uint64))[0] = 1
        ctypes.cast(args[6], ctypes.POINTER(ctypes.c_uint64))[0] = 1
        ctypes.cast(args[7], ctypes.POINTER(ctypes.c_uint32))[0] = 0
        args[8][0] = int(args[2][0])
        args[8][1] = 99
        for index in range(7):
            args[10][index] = 0
        launch_count = int(args[3]) + owner._indexed_count
        args[10][1] = launch_count
        args[10][4] = 1
        args[10][5] = launch_count - 1
        args[10][6] = launch_count
        return 0

    owner._execute = execute
    return owner


def _triangle_owner(state: _NativeDigestState):
    owner = object.__new__(triangle.PreparedTriangleReductionOwner)
    query_channel = SimpleNamespace(
        domain=triangle.MetadataDomain.QUERY,
        semantic_id="query.weight",
    )
    reducer = SimpleNamespace(
        algebra=triangle.ReducerAlgebra.CHECKED_U64_PRODUCT_SUM,
        multiplicand_source=SimpleNamespace(semantic_id="query.weight"),
        value_source=SimpleNamespace(
            kind=triangle.ReducerSourceKind.PER_RAY_OUTPUT,
            output_field="hit_count",
        ),
    )
    owner._token = 11
    owner._library = object()
    owner._commit = state.commit
    owner._cache_digest = state.query
    owner._fresh = SimpleNamespace(
        authority_nonce="authority",
        schema=SimpleNamespace(metadata_channels=(query_channel,), reducer=reducer),
    )
    owner._contract = SimpleNamespace(contract_sha256="contract")
    owner._abi = SimpleNamespace(abi_sha256="abi")
    owner._normalized_metadata = {}
    owner._primitive_count = 1
    owner._event_capacity = 1
    owner._event_query_host = (ctypes.c_uint32 * 1)()
    owner._event_primitive_host = (ctypes.c_uint32 * 1)()
    owner._event_stable_host = (ctypes.c_uint64 * 1)()
    owner._event_signed_host = (ctypes.c_int64 * 1)()
    owner._event_include_host = (ctypes.c_uint32 * 1)()
    owner._cached_queries = None
    owner._cached_query_metadata = None
    owner._cached_query_inputs = None
    owner._cached_query_digest = None
    owner._native_sha = "c" * 64
    owner._composed_ptx_sha = "d" * 64
    owner._pid = os.getpid()
    owner._thread = threading.get_ident()
    owner._active = threading.Lock()
    owner._closed = False
    owner._execution_count = 0

    def execute(*args):
        reuse = int(args[5])
        if state.begin_execution(reuse):
            return 1
        args[6][0] = 3
        ctypes.cast(args[7], ctypes.POINTER(ctypes.c_uint64))[0] = 0
        for index in range(7):
            args[14][index] = 0
        args[14][1] = 1
        args[14][3] = 1
        args[14][5] = 1
        args[14][6] = 1
        return 0

    def reduce_u64(values, multipliers, count, output, _error, _error_size):
        total = sum(
            int(values[index]) * int(multipliers[index]) for index in range(count)
        )
        ctypes.cast(output, ctypes.POINTER(ctypes.c_uint64))[0] = total
        return 0

    def execute_scalar(*args):
        reuse = int(args[5])
        use_multipliers = int(args[6])
        reuse_multipliers = int(args[7])
        state.scalar_multiplier_flags.append((use_multipliers, reuse_multipliers))
        if int(args[9]) != 32:
            return 1
        state.scalar_reuse_digests.append(bytes(args[8][:32]))
        if state.begin_execution(reuse):
            return 1
        count = int(args[4])
        multiplier = int(args[10][0]) if use_multipliers else 1
        ctypes.cast(args[11], ctypes.POINTER(ctypes.c_uint64))[0] = 3 * multiplier
        ctypes.cast(args[12], ctypes.POINTER(ctypes.c_uint32))[0] = 0
        receipt = ctypes.cast(
            args[13], ctypes.POINTER(triangle._FastPathReceipt)
        )[0]
        receipt.schema_version = 2
        receipt.optix_launch_count = 1
        receipt.host_blocking_boundary_count = 2
        receipt.control_d2h_bytes = 4
        receipt.output_d2h_bytes = 8
        receipt.status_before_output = 1
        receipt.output_d2h_after_status_failure = 0
        receipt.role_counters_materialized = 0
        receipt.prepared_input_reused = reuse
        receipt.dynamic_device_upload_call_count = (
            0 if reuse else 7 + use_multipliers
        )
        receipt.dynamic_device_upload_bytes = (
            0 if reuse else count * (7 * 4 + use_multipliers * 8)
        )
        receipt.dynamic_accel_build_count = 0
        receipt.dynamic_explicit_sync_count = 0
        receipt.dynamic_blocking_upload_call_count = 0
        receipt.dynamic_input_generation = 1
        receipt.semantic_compaction_launch_count = 0
        receipt.semantic_compaction_key_capacity = 0
        receipt.semantic_compaction_scratch_bytes = 0
        receipt.callback_status_kernel_launch_count = 3
        receipt.checked_product_kernel_launch_count = 2
        receipt.compact_control_finalizer_kernel_launch_count = 1
        receipt.total_auxiliary_cuda_kernel_launch_count = 6
        receipt.execution_parameter_h2d_bytes = 200
        receipt.execution_parameter_h2d_copy_call_count = 1
        receipt.stream_ordered_memset_call_count = 4
        receipt.status_d2h_copy_call_count = 1
        receipt.output_d2h_copy_call_count = 1
        return 0

    owner._execute = execute
    owner._execute_scalar = execute_scalar
    owner._reduce_u64 = reduce_u64
    return owner


class Goal5842PreparedCacheCommitTest(unittest.TestCase):
    def test_relation_first_execution_commits_and_second_execution_reuses(self):
        state = _NativeDigestState()
        owner = _relation_owner(state)
        sources = ((0.0, 0.0, 1.0, 1.0, 17),)
        expected = ((17, 99),)
        with patch.object(
            relation.OptixTraversalAuditSession,
            "open",
            side_effect=lambda **_kwargs: _Audit(),
        ):
            first = owner.execute(sources, expected_rows=expected)
            second = owner.execute(sources, expected_rows=expected)
        self.assertEqual(first.rows, expected)
        self.assertEqual(second.rows, expected)
        self.assertEqual(state.reuse_flags, [0, 1])
        self.assertEqual(state.commit_count, 1)
        self.assertEqual(
            owner._native_source_cache_digest(), owner._cached_source_digest
        )

    def test_relation_native_digest_mismatch_forces_rebuild(self):
        state = _NativeDigestState()
        owner = _relation_owner(state)
        sources = ((0.0, 0.0, 1.0, 1.0, 17),)
        expected = ((17, 99),)
        with patch.object(
            relation.OptixTraversalAuditSession,
            "open",
            side_effect=lambda **_kwargs: _Audit(),
        ):
            owner.execute(sources, expected_rows=expected)
            state.digest = b"\xa5" * 32
            owner.execute(sources, expected_rows=expected)
        self.assertEqual(state.reuse_flags, [0, 0])
        self.assertEqual(state.commit_count, 2)
        self.assertEqual(
            owner._native_source_cache_digest(), owner._cached_source_digest
        )

    def test_relation_audit_rejection_does_not_publish_or_commit(self):
        state = _NativeDigestState()
        owner = _relation_owner(state)
        sources = ((0.0, 0.0, 1.0, 1.0, 17),)
        expected = ((17, 99),)
        with (
            patch.object(
                relation.OptixTraversalAuditSession,
                "open",
                side_effect=lambda **_kwargs: _RejectingAudit(),
            ),
            self.assertRaisesRegex(RuntimeError, "audit rejection"),
        ):
            owner.execute(sources, expected_rows=expected)
        self.assertEqual(state.commit_count, 0)
        self.assertIsNone(owner._cached_source_object)
        self.assertIsNone(owner._cached_source_native)
        self.assertIsNone(owner._cached_source_digest)
        with patch.object(
            relation.OptixTraversalAuditSession,
            "open",
            side_effect=lambda **_kwargs: _Audit(),
        ):
            owner.execute(sources, expected_rows=expected)
        self.assertEqual(state.reuse_flags, [0, 0])
        self.assertEqual(state.commit_count, 1)

    def test_relation_interrupt_after_native_commit_forces_rebuild(self):
        state = _NativeDigestState()
        owner = _relation_owner(state)
        sources = ((0.0, 0.0, 1.0, 1.0, 17),)
        original_commit = owner._commit_source_cache

        def interrupt_after_commit(digest_hex: str) -> None:
            original_commit(digest_hex)
            raise KeyboardInterrupt("injected after native commit")

        owner._commit_source_cache = interrupt_after_commit
        with patch.object(
            relation.OptixTraversalAuditSession,
            "open",
            side_effect=lambda **_kwargs: _Audit(),
        ):
            with self.assertRaisesRegex(KeyboardInterrupt, "injected"):
                owner.execute(sources, expected_rows=((17, 99),))
            self.assertIsNone(owner._cached_source_object)
            self.assertIsNone(owner._cached_source_native)
            self.assertIsNone(owner._cached_source_digest)
            owner._commit_source_cache = original_commit
            owner.execute(sources, expected_rows=((17, 99),))
        self.assertEqual(state.reuse_flags, [0, 0])
        self.assertEqual(state.commit_count, 2)

    def test_triangle_first_execution_commits_and_second_execution_reuses(self):
        state = _NativeDigestState()
        owner = _triangle_owner(state)
        queries = (((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 2.0),)
        metadata = {"query.weight": (2,)}
        typed = ({"query.weight": (2,)}, None, None, None)
        with (
            patch.object(
                triangle.OptixTraversalAuditSession,
                "open",
                side_effect=lambda **_kwargs: _Audit(),
            ),
            patch.object(triangle, "_typed_metadata", return_value=typed),
        ):
            first = owner.execute(queries, query_metadata=metadata)
            second = owner.execute(queries, query_metadata=metadata)
        self.assertEqual(first.reduced_output, 6)
        self.assertEqual(second.reduced_output, 6)
        self.assertEqual(tuple(second.per_ray_u64), (3,))
        self.assertEqual(state.reuse_flags, [0, 1])
        self.assertEqual(state.commit_count, 1)
        self.assertEqual(owner._native_query_cache_digest(), owner._cached_query_digest)

    def test_triangle_scalar_path_keeps_per_ray_rows_device_resident(self):
        state = _NativeDigestState()
        owner = _triangle_owner(state)
        queries = (((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 2.0),)
        metadata = {"query.weight": (2,)}
        typed = ({"query.weight": (2,)}, None, None, None)

        def forbidden(*_args):
            raise AssertionError("diagnostic/host reduction path was called")

        owner._execute = forbidden
        owner._reduce_u64 = forbidden
        with (
            patch.object(
                triangle.OptixTraversalAuditSession,
                "open",
                side_effect=lambda **_kwargs: _Audit(),
            ),
            patch.object(triangle, "_typed_metadata", return_value=typed),
        ):
            first = owner.execute(
                queries, query_metadata=metadata, include_diagnostics=False
            )
            second = owner.execute(
                queries, query_metadata=metadata, include_diagnostics=False
            )
        self.assertEqual(first.reduced_output, 6)
        self.assertEqual(second.reduced_output, 6)
        self.assertEqual(tuple(first.per_ray_u64), ())
        self.assertEqual(tuple(first.raw_reducer_rows), ())
        self.assertTrue(first.launch_status.native_validated_all_ok)
        self.assertEqual(first.launch_status[0]["validated_row_count"], 1)
        self.assertEqual(state.reuse_flags, [0, 1])
        self.assertEqual(state.scalar_multiplier_flags, [(1, 0), (1, 1)])
        self.assertEqual(len(state.scalar_reuse_digests), 2)
        self.assertEqual(
            state.scalar_reuse_digests,
            [bytes.fromhex(owner._cached_query_digest)] * 2,
        )
        self.assertEqual(state.commit_count, 1)
        boundary = owner._last_execution_receipt
        self.assertEqual(
            boundary["execution_path"], "device_resident_checked_u64_scalar_v7"
        )
        self.assertTrue(boundary["prepared_query_input_reused"])
        self.assertFalse(boundary["per_ray_u64_materialized_on_host"])
        self.assertFalse(boundary["event_rows_materialized_on_host"])
        self.assertEqual(boundary["public_output_scalar_bytes"], 8)

    def test_triangle_scalar_path_rejects_invalid_fast_receipt(self):
        state = _NativeDigestState()
        owner = _triangle_owner(state)
        valid_scalar = owner._execute_scalar

        def corrupt_receipt(*args):
            status = valid_scalar(*args)
            receipt = ctypes.cast(
                args[13], ctypes.POINTER(triangle._FastPathReceipt)
            )[0]
            receipt.status_before_output = 0
            return status

        owner._execute_scalar = corrupt_receipt
        queries = (((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 2.0),)
        typed = ({"query.weight": (2,)}, None, None, None)
        with (
            patch.object(
                triangle.OptixTraversalAuditSession,
                "open",
                side_effect=lambda **_kwargs: _Audit(),
            ),
            patch.object(triangle, "_typed_metadata", return_value=typed),
            self.assertRaisesRegex(RuntimeError, "fast-path receipt is invalid"),
        ):
            owner.execute(
                queries,
                query_metadata={"query.weight": (2,)},
                include_diagnostics=False,
            )
        self.assertEqual(state.commit_count, 0)
        self.assertIsNone(owner._cached_queries)

    def test_triangle_scalar_sum_path_uses_no_multiplier(self):
        state = _NativeDigestState()
        owner = _triangle_owner(state)
        owner._fresh.schema.metadata_channels = ()
        owner._fresh.schema.reducer = SimpleNamespace(
            algebra=triangle.ReducerAlgebra.CHECKED_U64_SUM,
            multiplicand_source=None,
            value_source=SimpleNamespace(
                kind=triangle.ReducerSourceKind.PER_RAY_OUTPUT,
                output_field="hit_count",
            ),
        )
        queries = (((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 2.0),)
        typed = ({}, None, None, None)
        with (
            patch.object(
                triangle.OptixTraversalAuditSession,
                "open",
                side_effect=lambda **_kwargs: _Audit(),
            ),
            patch.object(triangle, "_typed_metadata", return_value=typed),
        ):
            result = owner.execute(
                queries, query_metadata={}, include_diagnostics=False
            )
        self.assertEqual(result.reduced_output, 3)
        self.assertEqual(state.scalar_multiplier_flags, [(0, 0)])

    def test_triangle_native_digest_mismatch_forces_rebuild(self):
        state = _NativeDigestState()
        owner = _triangle_owner(state)
        queries = (((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 2.0),)
        metadata = {"query.weight": (2,)}
        typed = ({"query.weight": (2,)}, None, None, None)
        with (
            patch.object(
                triangle.OptixTraversalAuditSession,
                "open",
                side_effect=lambda **_kwargs: _Audit(),
            ),
            patch.object(triangle, "_typed_metadata", return_value=typed),
        ):
            owner.execute(queries, query_metadata=metadata)
            state.digest = b"\x5a" * 32
            owner.execute(queries, query_metadata=metadata)
        self.assertEqual(state.reuse_flags, [0, 0])
        self.assertEqual(state.commit_count, 2)
        self.assertEqual(owner._native_query_cache_digest(), owner._cached_query_digest)

    def test_triangle_audit_rejection_does_not_publish_or_commit(self):
        state = _NativeDigestState()
        owner = _triangle_owner(state)
        queries = (((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 2.0),)
        metadata = {"query.weight": (2,)}
        typed = ({"query.weight": (2,)}, None, None, None)
        with (
            patch.object(
                triangle.OptixTraversalAuditSession,
                "open",
                side_effect=lambda **_kwargs: _RejectingAudit(),
            ),
            patch.object(triangle, "_typed_metadata", return_value=typed),
            self.assertRaisesRegex(RuntimeError, "audit rejection"),
        ):
            owner.execute(queries, query_metadata=metadata)
        self.assertEqual(state.commit_count, 0)
        self.assertIsNone(owner._cached_queries)
        self.assertIsNone(owner._cached_query_inputs)
        self.assertIsNone(owner._cached_query_digest)
        with (
            patch.object(
                triangle.OptixTraversalAuditSession,
                "open",
                side_effect=lambda **_kwargs: _Audit(),
            ),
            patch.object(triangle, "_typed_metadata", return_value=typed),
        ):
            owner.execute(queries, query_metadata=metadata)
        self.assertEqual(state.reuse_flags, [0, 0])
        self.assertEqual(state.commit_count, 1)

    def test_triangle_interrupt_after_native_commit_forces_rebuild(self):
        state = _NativeDigestState()
        owner = _triangle_owner(state)
        queries = (((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 2.0),)
        metadata = {"query.weight": (2,)}
        typed = ({"query.weight": (2,)}, None, None, None)
        original_commit = owner._commit_query_cache

        def interrupt_after_commit(digest_hex: str) -> None:
            original_commit(digest_hex)
            raise KeyboardInterrupt("injected after native commit")

        owner._commit_query_cache = interrupt_after_commit
        with (
            patch.object(
                triangle.OptixTraversalAuditSession,
                "open",
                side_effect=lambda **_kwargs: _Audit(),
            ),
            patch.object(triangle, "_typed_metadata", return_value=typed),
        ):
            with self.assertRaisesRegex(KeyboardInterrupt, "injected"):
                owner.execute(queries, query_metadata=metadata)
            self.assertIsNone(owner._cached_queries)
            self.assertIsNone(owner._cached_query_inputs)
            self.assertIsNone(owner._cached_query_digest)
            owner._commit_query_cache = original_commit
            owner.execute(queries, query_metadata=metadata)
        self.assertEqual(state.reuse_flags, [0, 0])
        self.assertEqual(state.commit_count, 2)

    def test_only_deep_builtin_tuple_inputs_are_reuse_candidates(self):
        self.assertTrue(relation._source_rows_are_immutable(((0.0, 0.0, 1.0, 1.0, 1),)))
        self.assertFalse(
            relation._source_rows_are_immutable(([0.0, 0.0, 1.0, 1.0, 1],))
        )
        queries = (((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 2.0),)
        self.assertTrue(
            triangle._query_rows_are_immutable(queries, {"query.weight": (2,)})
        )
        self.assertFalse(
            triangle._query_rows_are_immutable(queries, {"query.weight": [2]})
        )


if __name__ == "__main__":
    unittest.main()
