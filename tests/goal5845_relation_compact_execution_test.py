from __future__ import annotations

import copy
import ctypes
import hashlib
import json
import os
from pathlib import Path
from types import SimpleNamespace
import threading
import unittest
from unittest.mock import patch

from rtdsl import physical_execution_provenance as provenance
from rtdsl import v4_bounded_relation_prepared_runtime as runtime
from rtdsl import v4_callback_lifecycle as callback_lifecycle
from rtdsl import v4_family_route_adapters as family_adapters
from rtdsl import v4_generic_family_lifecycle as generic_lifecycle
from scripts import goal5845_run_gpu_engineering_comparison as gpu_runner


PROGRAM_BUNDLE = "v4_custom_aabb_bounded_relation_composed"
ROUTE_IDENTITY = "v4_callback_ir:custom_aabb_bounded_relation_v1"


def _mix(state: int, value: int) -> int:
    mask = (1 << 64) - 1
    value = (value + 0x9E3779B97F4A7C15) & mask
    value = ((value ^ (value >> 30)) * 0xBF58476D1CE4E5B9) & mask
    value = ((value ^ (value >> 27)) * 0x94D049BB133111EB) & mask
    value = (value ^ (value >> 31)) & mask
    return (
        state
        ^ (
            value
            + 0x9E3779B97F4A7C15
            + ((state << 6) & mask)
            + (state >> 2)
        )
    ) & mask


def _seal(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


def _snapshot(
    *, nonce_hi: int = 17, sequence: int = 1, ray_count: int = 2
) -> provenance.NativeTraversalAuditSnapshot:
    snapshot = provenance.NativeTraversalAuditSnapshot()
    bundle_id = provenance.physical_program_bundle_id(PROGRAM_BUNDLE)
    first_traversable = 0x12345678
    last_traversable = 0x87654321
    snapshot.nonce_hi = nonce_hi
    snapshot.nonce_lo = sequence
    snapshot.attempted_launch_count = 2
    snapshot.successful_launch_count = 2
    snapshot.complete_context_launch_count = 2
    snapshot.context_bind_count = 2
    snapshot.raygen_invocation_count = ray_count
    snapshot.program_bundle_mix = _mix(_mix(0, bundle_id), bundle_id)
    snapshot.traversable_mix = _mix(
        _mix(0, first_traversable), last_traversable
    )
    snapshot.first_program_bundle_id = bundle_id
    snapshot.last_program_bundle_id = bundle_id
    snapshot.first_traversable = first_traversable
    snapshot.last_traversable = last_traversable
    return snapshot


def _valid_fast_receipt(
    *, reused: bool, row_count: int = 1, generation: int = 1
) -> runtime._FastPathReceipt:
    receipt = runtime._FastPathReceipt()
    receipt.schema_version = 2
    receipt.optix_launch_count = 2
    receipt.host_blocking_boundary_count = 2
    receipt.control_d2h_bytes = 28
    receipt.output_d2h_bytes = row_count * 8
    receipt.status_before_output = 1
    receipt.output_d2h_after_status_failure = 0
    receipt.role_counters_materialized = 0
    receipt.prepared_input_reused = int(reused)
    receipt.dynamic_device_upload_call_count = 0 if reused else 2
    receipt.dynamic_accel_build_count = 0 if reused else 1
    receipt.dynamic_explicit_sync_count = 0
    receipt.dynamic_blocking_upload_call_count = 0
    receipt.dynamic_device_upload_bytes = 0 if reused else 52
    receipt.dynamic_input_generation = generation
    receipt.semantic_compaction_launch_count = 1
    receipt.semantic_compaction_key_capacity = 8
    receipt.semantic_compaction_scratch_bytes = 104
    receipt.callback_status_kernel_launch_count = 0
    receipt.checked_product_kernel_launch_count = 0
    receipt.compact_control_finalizer_kernel_launch_count = 0
    receipt.total_auxiliary_cuda_kernel_launch_count = 1
    receipt.execution_parameter_h2d_bytes = 240
    receipt.execution_parameter_h2d_copy_call_count = 2
    receipt.stream_ordered_memset_call_count = 4
    receipt.status_d2h_copy_call_count = 1
    receipt.output_d2h_copy_call_count = int(row_count > 0)
    return receipt


class _ConfigSymbol:
    def __call__(self, *_args) -> int:
        return 0


class _Audit:
    def __init__(self) -> None:
        self.aborted = False

    def finish(self, **_kwargs):
        return {"physical_executor_classification": "optix_traversal_observed"}

    def abort(self) -> None:
        self.aborted = True


class _IntegratedRelationState:
    def __init__(self) -> None:
        self.digest: bytes | None = None
        self.pending = False
        self.generation = 0
        self.rows = ((17, 99),)
        self.reuse_flags: list[int] = []
        self.sequences: list[int] = []
        self.commit_count = 0
        self.cache_digest_queries = 0
        self.compact_status = 0
        self.snapshot_sequence_delta = 0
        self.legacy_execute_count = 0

    def commit(self, _token, digest, size, _error, _error_size) -> int:
        if not self.pending or int(size) != 32:
            return 1
        self.digest = bytes(digest[:32])
        self.pending = False
        self.commit_count += 1
        return 0

    def query(self, _token, digest, size, present, _error, _error_size) -> int:
        self.cache_digest_queries += 1
        if int(size) != 32:
            return 1
        ctypes.cast(present, ctypes.POINTER(ctypes.c_uint32))[0] = int(
            self.digest is not None
        )
        if self.digest is not None:
            ctypes.memmove(digest, self.digest, 32)
        return 0

    def execute_v8(self, *args) -> int:
        source_count = int(args[3])
        reuse = int(args[4])
        self.reuse_flags.append(reuse)
        self.sequences.append(int(args[12]))
        if reuse:
            if self.digest is None:
                args[14].value = b"injected source-cache reuse failure"
                return 1
        else:
            self.pending = True
            self.digest = None
            self.generation += 1
        row_count = len(self.rows)
        ctypes.cast(args[5], ctypes.POINTER(ctypes.c_uint64))[0] = row_count
        ctypes.cast(args[6], ctypes.POINTER(ctypes.c_uint64))[0] = row_count
        ctypes.cast(args[7], ctypes.POINTER(ctypes.c_uint32))[0] = 0
        for index, (left, right) in enumerate(self.rows):
            args[8][index * 2] = left
            args[8][index * 2 + 1] = right
        ctypes.cast(args[9], ctypes.POINTER(ctypes.c_uint32))[0] = (
            self.compact_status
        )
        receipt = ctypes.cast(
            args[10], ctypes.POINTER(runtime._FastPathReceipt)
        )[0]
        valid = _valid_fast_receipt(
            reused=bool(reuse), row_count=row_count, generation=self.generation
        )
        if self.compact_status:
            valid.host_blocking_boundary_count = 1
            valid.output_d2h_bytes = 0
            valid.output_d2h_copy_call_count = 0
        ctypes.memmove(ctypes.byref(receipt), ctypes.byref(valid), ctypes.sizeof(valid))
        snapshot = _snapshot(
            nonce_hi=int(args[11]),
            sequence=int(args[12]) + self.snapshot_sequence_delta,
            ray_count=source_count + 1,
        )
        ctypes.memmove(args[13], ctypes.byref(snapshot), ctypes.sizeof(snapshot))
        return 0

    def execute_legacy(self, *args) -> int:
        self.legacy_execute_count += 1
        reuse = int(args[4])
        if reuse:
            if self.digest is None:
                args[11].value = b"injected legacy source-cache reuse failure"
                return 1
        else:
            self.pending = True
            self.digest = None
            self.generation += 1
        row_count = len(self.rows)
        ctypes.cast(args[5], ctypes.POINTER(ctypes.c_uint64))[0] = row_count
        ctypes.cast(args[6], ctypes.POINTER(ctypes.c_uint64))[0] = row_count
        ctypes.cast(args[7], ctypes.POINTER(ctypes.c_uint32))[0] = 0
        for index, (left, right) in enumerate(self.rows):
            args[8][index * 2] = left
            args[8][index * 2 + 1] = right
        launch_count = int(args[3]) + 1
        for index in range(launch_count):
            args[9][index].first_error_claimed = 0
            args[9][index].error_code = 0
        for index in range(7):
            args[10][index] = 0
        args[10][1] = launch_count
        args[10][4] = 1
        args[10][5] = launch_count - 1
        args[10][6] = launch_count
        return 0


def _owner(state: _IntegratedRelationState) -> runtime.PreparedBoundedRelationOwner:
    owner = object.__new__(runtime.PreparedBoundedRelationOwner)
    owner._token = 7
    owner._fresh = SimpleNamespace(authority_nonce="authority")
    owner._contract = SimpleNamespace(capacity=4, contract_sha256="contract")
    owner._abi = SimpleNamespace(abi_sha256="abi")
    owner._library = object()
    owner._execute = state.execute_legacy
    owner._execute_fast_integrated = state.execute_v8
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
    owner._cached_source_generation = None
    owner._last_observed_source_generation = 0
    owner._cached_expected_object = None
    owner._cached_expected_rows = None
    owner._cached_expected_output = None
    owner._cached_output_packed = None
    owner._cached_output_rows = None
    owner._cached_output_sha = None
    owner._row_storage = (ctypes.c_uint32 * 8)()
    owner._status_capacity = 1
    owner._statuses = (runtime._Status * 1)()
    owner._counters = (ctypes.c_uint64 * 7)()
    owner._raw_count = ctypes.c_uint64()
    owner._unique_count = ctypes.c_uint64()
    owner._overflowed = ctypes.c_uint32()
    owner._fast_compact_status = ctypes.c_uint32()
    owner._fast_receipt = runtime._FastPathReceipt()
    owner._integrated_audit_snapshot = provenance.NativeTraversalAuditSnapshot()
    owner._integrated_audit_sequence = 0
    owner._integrated_audit_nonce_hi = 17
    owner._integrated_audit_output_sha = None
    owner._integrated_status_rows = None
    owner._last_fast_operation_receipt = None
    owner._error = ctypes.create_string_buffer(16384)
    owner._route_identity = ROUTE_IDENTITY
    owner._program_bundle = PROGRAM_BUNDLE
    owner._semantic_digest = "c" * 64
    owner._native_path = Path(__file__)
    owner._session_identity = "d" * 64
    owner.prepare_seconds = 0.0
    return owner


class Goal5845RelationCompactExecutionTest(unittest.TestCase):
    def test_gpu_runner_freeze_and_balanced_schedule_are_exact(self) -> None:
        registration = gpu_runner._validate_preregistration(
            Path(
                "history/internal_docs/"
                "goal5845_relation_public_parity_20260904/PREREGISTRATION.json"
            ),
            SimpleNamespace(blocks=8, warmups=16, repetitions=128),
        )
        self.assertEqual(
            registration["preregistration_sha256"],
            "2f246a54e172ec83e32ad93fa3c796c3c73ef9c2de54ded3b3fea63daf4d00db",
        )
        schedule = gpu_runner.expected_schedule(4)
        self.assertEqual(len(schedule), 8)
        self.assertEqual(schedule[0]["arm"], gpu_runner.RTDL_ARM)
        self.assertEqual(schedule[2]["arm"], gpu_runner.PYOPTIX_ARM)
        self.assertEqual(
            [row["position"] for row in schedule], [0, 1] * 4
        )

    def test_gpu_runner_recomputes_all_retained_timing_fields(self) -> None:
        summary = {
            "sample_count": 4,
            "samples_ns": [11, 17, 13, 19],
            "minimum_ns": 11,
            "median_ns": 15,
            "maximum_ns": 19,
        }
        gpu_runner._validate_timing_summary(
            summary, expected_count=4, label="test"
        )
        for key, replacement in (
            ("sample_count", 3),
            ("minimum_ns", 10),
            ("median_ns", 14),
            ("maximum_ns", 20),
        ):
            with self.subTest(field=key):
                forged = dict(summary)
                forged[key] = replacement
                with self.assertRaisesRegex(RuntimeError, "timing values differ"):
                    gpu_runner._validate_timing_summary(
                        forged, expected_count=4, label="test"
                    )

    def test_v8_abi_is_additive_and_legacy_v3_remains_available(self) -> None:
        names = (
            "rtdl_optix_v4_prepare_bounded_relation_callback_v1",
            "rtdl_optix_v4_execute_prepared_bounded_relation_callback_v3",
            "rtdl_optix_v4_commit_prepared_bounded_relation_source_cache_v2",
            "rtdl_optix_v4_prepared_bounded_relation_source_cache_digest_v1",
            "rtdl_optix_v4_destroy_prepared_bounded_relation_callback_v1",
        )
        legacy = SimpleNamespace(**{name: _ConfigSymbol() for name in names})
        self.assertIsNone(runtime._configure(legacy)[2])
        integrated = _ConfigSymbol()
        current = SimpleNamespace(
            **{name: _ConfigSymbol() for name in names},
            rtdl_optix_v4_execute_prepared_bounded_relation_callback_v8=integrated,
        )
        self.assertIs(runtime._configure(current)[2], integrated)
        self.assertEqual(len(integrated.argtypes), 16)
        self.assertIs(integrated.argtypes[11], ctypes.c_uint64)
        self.assertIs(integrated.argtypes[12], ctypes.c_uint64)
        self.assertEqual(
            integrated.argtypes[13],
            ctypes.POINTER(provenance.NativeTraversalAuditSnapshot),
        )

    def test_two_launch_compact_stamp_accepts_distinct_traversables(self) -> None:
        receipt = provenance.build_compact_traversal_receipt(
            _snapshot(sequence=9, ray_count=17),
            provider_library_sha256="a" * 64,
            route_identity=ROUTE_IDENTITY,
            semantic_digest="b" * 64,
            output_digest="c" * 64,
            expected_program_bundle=PROGRAM_BUNDLE,
            expected_raygen_invocation_count=17,
            execution_sequence=9,
            expected_successful_launch_count=2,
        )
        provenance.validate_traversal_receipt(
            receipt,
            provider_library_sha256="a" * 64,
            route_identity=ROUTE_IDENTITY,
            output_digest="c" * 64,
            expected_program_bundles=(PROGRAM_BUNDLE,),
            expected_successful_launch_count=2,
            expected_raygen_invocation_count=17,
        )
        self.assertNotEqual(
            receipt["native_stamp"][12], receipt["native_stamp"][13]
        )

    def test_two_launch_stamp_rejects_invalid_resealed_native_facts(self) -> None:
        base = provenance.build_compact_traversal_receipt(
            _snapshot(sequence=1, ray_count=2),
            provider_library_sha256="a" * 64,
            route_identity=ROUTE_IDENTITY,
            semantic_digest="b" * 64,
            output_digest="c" * 64,
            expected_program_bundle=PROGRAM_BUNDLE,
            expected_raygen_invocation_count=2,
            execution_sequence=1,
            expected_successful_launch_count=2,
        )
        invalid = {
            0: 0,
            1: 2,
            2: 2,
            3: 1,
            4: 1,
            5: 1,
            6: 1,
            7: 1,
            8: 1,
            9: 1,
            10: 0,
            11: 0,
            12: 0,
            13: 0,
            14: 1,
            15: 1,
            16: 1,
            17: 0,
            18: 0,
        }
        for index, replacement in invalid.items():
            with self.subTest(stamp_index=index):
                forged = copy.deepcopy(base)
                forged["native_stamp"][index] = replacement
                body = dict(forged)
                body.pop("receipt_sha256")
                forged["receipt_sha256"] = _seal(body)
                with self.assertRaisesRegex(
                    RuntimeError, "compact traversal native stamp differs"
                ):
                    provenance.validate_compact_traversal_receipt(
                        forged,
                        provider_library_sha256="a" * 64,
                        route_identity=ROUTE_IDENTITY,
                        output_digest="c" * 64,
                        expected_program_bundles=(PROGRAM_BUNDLE,),
                        expected_successful_launch_count=2,
                        expected_raygen_invocation_count=2,
                    )

    def test_fast_receipt_rejects_each_mutated_field(self) -> None:
        valid = _valid_fast_receipt(reused=True)
        runtime._validate_fast_receipt(
            valid,
            compact_status=0,
            output_row_count=1,
            prepared_input_reused=True,
            source_count=1,
            semantic_capacity=4,
            previous_input_generation=0,
            expected_reused_generation=1,
        )
        for name, _ctype in runtime._FastPathReceipt._fields_:
            with self.subTest(field=name):
                forged = _valid_fast_receipt(reused=True)
                setattr(forged, name, int(getattr(forged, name)) + 1)
                with self.assertRaisesRegex(RuntimeError, "receipt is invalid"):
                    runtime._validate_fast_receipt(
                        forged,
                        compact_status=0,
                        output_row_count=1,
                        prepared_input_reused=True,
                        source_count=1,
                        semantic_capacity=4,
                        previous_input_generation=0,
                        expected_reused_generation=1,
                    )

    def test_integrated_owner_reuses_exact_immutable_rows_and_compact_receipt(self) -> None:
        state = _IntegratedRelationState()
        owner = _owner(state)
        sources = ((0.0, 0.0, 1.0, 1.0, 17),)
        expected = ((17, 99),)
        with patch.object(
            runtime.OptixTraversalAuditSession,
            "open",
            side_effect=AssertionError("separate audit path reached"),
        ):
            first = owner.execute(sources, expected_rows=expected)
            second = owner.execute(sources, expected_rows=expected)
        self.assertIs(type(first.rows), runtime.ValidatedBoundedRelationRows)
        self.assertIs(second.rows, first.rows)
        self.assertEqual(second.raw_rows, ())
        self.assertFalse(second.raw_rows_materialized)
        self.assertEqual(state.reuse_flags, [0, 1])
        self.assertEqual(state.sequences, [1, 2])
        self.assertEqual(state.commit_count, 1)
        self.assertEqual(owner._cached_source_generation, 1)
        self.assertIsInstance(
            second.traversal_receipt,
            provenance.ValidatedCompactTraversalReceipt,
        )
        self.assertFalse(second.traversal_receipt.materialized)
        runtime.validate_bound_relation_rows(
            second.rows, output_sha256=second.output_sha256
        )
        with self.assertRaises(AttributeError):
            second.rows._validated_output_sha256 = "0" * 64

    def test_changed_output_is_revalidated_before_cache_publication(self) -> None:
        state = _IntegratedRelationState()
        owner = _owner(state)
        sources = ((0.0, 0.0, 1.0, 1.0, 17),)
        expected = ((17, 99),)
        original = owner.execute(sources, expected_rows=expected).rows
        state.rows = ((17, 98),)
        with self.assertRaisesRegex(RuntimeError, "output mismatch"):
            owner.execute(sources, expected_rows=expected)
        self.assertIsNone(owner._cached_source_object)
        self.assertIsNone(owner._cached_source_generation)
        state.rows = expected
        recovered = owner.execute(sources, expected_rows=expected)
        self.assertIs(recovered.rows, original)
        self.assertEqual(state.reuse_flags, [0, 1, 0])
        self.assertEqual(state.commit_count, 2)
        self.assertEqual(owner._cached_source_generation, 2)

    def test_status_failure_returns_no_rows_and_forces_rebuild(self) -> None:
        state = _IntegratedRelationState()
        owner = _owner(state)
        sources = ((0.0, 0.0, 1.0, 1.0, 17),)
        expected = ((17, 99),)
        owner.execute(sources, expected_rows=expected)
        state.compact_status = 23
        with self.assertRaisesRegex(
            RuntimeError, "compact device status rejected execution: 23"
        ):
            owner.execute(sources, expected_rows=expected)
        self.assertIsNone(owner._cached_source_object)
        self.assertEqual(owner._integrated_audit_sequence, 2)
        state.compact_status = 0
        owner.execute(sources, expected_rows=expected)
        self.assertEqual(state.reuse_flags, [0, 1, 0])

    def test_diagnostics_explicitly_retain_legacy_rows_and_full_audit(self) -> None:
        state = _IntegratedRelationState()
        owner = _owner(state)
        sources = ((0.0, 0.0, 1.0, 1.0, 17),)
        expected = ((17, 99),)
        with patch.object(
            runtime.OptixTraversalAuditSession,
            "open",
            side_effect=lambda **_kwargs: _Audit(),
        ):
            result = owner.execute(
                sources,
                expected_rows=expected,
                include_diagnostics=True,
            )
        self.assertEqual(state.legacy_execute_count, 1)
        self.assertEqual(result.raw_rows, expected)
        self.assertTrue(result.raw_rows_materialized)
        self.assertEqual(len(result.launch_status), 2)
        self.assertEqual(len(result.role_counters), 7)
        self.assertIs(type(result.traversal_receipt), dict)

    def test_public_protocol_and_family_use_only_factory_validated_fast_types(self) -> None:
        state = _IntegratedRelationState()
        owner = _owner(state)
        identity = SimpleNamespace(
            native_library_sha256="a" * 64,
            composed_ptx_sha256="b" * 64,
        )
        protocol = callback_lifecycle.PreparedProtocolProgram(
            family=callback_lifecycle.ProtocolFamily.BOUNDED_RELATION,
            owner=owner,
            identity=identity,
            materialize_seconds=0.0,
            protocol_contract_decision=SimpleNamespace(
                verdict="ACCEPT",
                to_mapping=lambda: {"decision_sha256": "e" * 64},
            ),
        )
        batch = callback_lifecycle.BoundedRelationBatch(
            ((0.0, 0.0, 1.0, 1.0, 17),),
            expected_rows=((17, 99),),
        )
        with patch.object(
            callback_lifecycle,
            "_digest",
            side_effect=AssertionError("public output was redundantly hashed"),
        ):
            result = protocol.execute(batch)
        self.assertEqual(result.details, {})
        bridge_identity = generic_lifecycle.FamilyExecutableIdentityV1(
            *(str(index) * 64 for index in range(1, 8))
        )
        bridge = family_adapters._PreparedBridge(
            protocol,
            bridge_identity,
            "1" * 64,
            family_adapters._stable_output,
        )
        bridged = bridge.execute(batch)
        self.assertIs(
            type(bridged), family_adapters._ValidatedRelationProviderExecution
        )
        self.assertIs(bridged.output_document, result.output)

        ordinary = generic_lifecycle.FamilyProviderExecutionV1(
            "1" * 64,
            "2" * 64,
            "OK",
            0,
            ((17, 99),),
            _seal(((17, 99),)),
            {"plain": True},
        )
        self.assertIs(type(ordinary), generic_lifecycle.FamilyProviderExecutionV1)
        self.assertIsNot(type(ordinary.output_document), runtime.ValidatedBoundedRelationRows)

    def test_native_source_integrates_two_launch_audit_without_app_names(self) -> None:
        source = Path("src/native/optix/rtdl_optix_api.cpp").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "rtdl_optix_v4_execute_prepared_bounded_relation_callback_v8",
            source,
        )
        self.assertIn("rtdl_optix_traversal_audit_begin_checked", source)
        self.assertIn("rtdl_optix_traversal_audit_finish_checked", source)
        self.assertIn("rtdl_optix_traversal_audit_abort_checked", source)
        self.assertNotIn("raydb", source.lower())
        self.assertNotIn("barnes", source.lower())
        self.assertNotIn("dbscan", source.lower())


if __name__ == "__main__":
    unittest.main()
