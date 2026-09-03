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

    owner._execute = execute
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
