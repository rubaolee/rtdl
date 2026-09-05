from __future__ import annotations

import copy
import ctypes
import hashlib
import json
import os
import threading
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from rtdsl import physical_execution_provenance as provenance
from rtdsl import v4_callback_lifecycle as callback_lifecycle
from rtdsl import v4_family_route_adapters as family_adapters
from rtdsl import v4_generic_family_lifecycle as generic_lifecycle
from rtdsl import v4_triangle_reduction_prepared_runtime as runtime
from scripts import goal5844_run_gpu_engineering_comparison as gpu_runner


PROGRAM_BUNDLE = "v4_builtin_triangle_checked_reduction_composed"
ROUTE_IDENTITY = "v4_builtin_triangle_callback_ir:checked_reduction_v1"


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


def _seal(document: dict[str, object]) -> str:
    return hashlib.sha256(
        json.dumps(
            document,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
    ).hexdigest()


def _snapshot(
    *, nonce_hi: int = 17, sequence: int = 1, ray_count: int = 1
) -> provenance.NativeTraversalAuditSnapshot:
    snapshot = provenance.NativeTraversalAuditSnapshot()
    bundle_id = provenance.physical_program_bundle_id(PROGRAM_BUNDLE)
    traversable = 0x12345678
    snapshot.nonce_hi = nonce_hi
    snapshot.nonce_lo = sequence
    snapshot.attempted_launch_count = 1
    snapshot.successful_launch_count = 1
    snapshot.complete_context_launch_count = 1
    snapshot.context_bind_count = 1
    snapshot.raygen_invocation_count = ray_count
    snapshot.program_bundle_mix = _mix(0, bundle_id)
    snapshot.traversable_mix = _mix(0, traversable)
    snapshot.first_program_bundle_id = bundle_id
    snapshot.last_program_bundle_id = bundle_id
    snapshot.first_traversable = traversable
    snapshot.last_traversable = traversable
    return snapshot


def _compact_receipt(
    *, sequence: int = 1, ray_count: int = 1
) -> dict[str, object]:
    return provenance.build_compact_traversal_receipt(
        _snapshot(sequence=sequence, ray_count=ray_count),
        provider_library_sha256="c" * 64,
        route_identity=ROUTE_IDENTITY,
        semantic_digest="d" * 64,
        output_digest="e" * 64,
        expected_program_bundle=PROGRAM_BUNDLE,
        expected_raygen_invocation_count=ray_count,
        execution_sequence=sequence,
    )


class _IntegratedState:
    def __init__(self) -> None:
        self.digest: bytes | None = None
        self.pending = False
        self.generation = 0
        self.reuse_flags: list[int] = []
        self.sequences: list[int] = []
        self.cache_digest_queries = 0
        self.commit_count = 0
        self.fail_native = False
        self.corrupt_generation = False
        self.compact_status = 0
        self.snapshot_sequence_delta = 0

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
        reuse = int(args[5])
        self.reuse_flags.append(reuse)
        self.sequences.append(int(args[15]))
        if self.fail_native:
            args[17].value = b"injected integrated native failure"
            return 1
        expected_digest = bytes(args[8][:32])
        if reuse:
            if self.digest is None or expected_digest != self.digest:
                args[17].value = b"injected reuse digest mismatch"
                return 1
        else:
            self.pending = True
            self.digest = None
            self.generation += 1

        count = int(args[4])
        use_multipliers = int(args[6])
        multiplier = int(args[10][0]) if use_multipliers else 1
        success = self.compact_status == 0
        ctypes.cast(args[11], ctypes.POINTER(ctypes.c_uint64))[0] = (
            3 * multiplier if success else 0
        )
        ctypes.cast(args[12], ctypes.POINTER(ctypes.c_uint32))[0] = (
            self.compact_status
        )
        receipt = ctypes.cast(
            args[13], ctypes.POINTER(runtime._FastPathReceipt)
        )[0]
        receipt.schema_version = 2
        receipt.optix_launch_count = 1
        receipt.host_blocking_boundary_count = 2 if success else 1
        receipt.control_d2h_bytes = 12
        receipt.output_d2h_bytes = 8 if success else 0
        receipt.status_before_output = 1
        receipt.output_d2h_after_status_failure = 0
        receipt.role_counters_materialized = 0
        receipt.prepared_input_reused = reuse
        receipt.dynamic_device_upload_call_count = 0 if reuse else 7 + use_multipliers
        receipt.dynamic_device_upload_bytes = (
            0 if reuse else count * (7 * 4 + use_multipliers * 8)
        )
        receipt.dynamic_input_generation = self.generation + int(
            self.corrupt_generation
        )
        receipt.execution_parameter_h2d_bytes = 224
        receipt.execution_parameter_h2d_copy_call_count = 1
        receipt.stream_ordered_memset_call_count = 2
        receipt.status_d2h_copy_call_count = 1
        receipt.output_d2h_copy_call_count = int(success)

        snapshot_pointer = ctypes.cast(
            args[16], ctypes.POINTER(provenance.NativeTraversalAuditSnapshot)
        )
        ctypes.memset(
            snapshot_pointer,
            0,
            ctypes.sizeof(provenance.NativeTraversalAuditSnapshot),
        )
        emitted = _snapshot(
            nonce_hi=int(args[14]),
            sequence=int(args[15]) + self.snapshot_sequence_delta,
            ray_count=count,
        )
        ctypes.memmove(
            snapshot_pointer,
            ctypes.byref(emitted),
            ctypes.sizeof(emitted),
        )
        return 0


class _ConfigSymbol:
    def __call__(self, *_args) -> int:
        return 0


def _owner(state: _IntegratedState) -> runtime.PreparedTriangleReductionOwner:
    owner = object.__new__(runtime.PreparedTriangleReductionOwner)
    query_channel = SimpleNamespace(
        domain=runtime.MetadataDomain.QUERY,
        semantic_id="query.weight",
        scalar=SimpleNamespace(value="u64"),
    )
    reducer = SimpleNamespace(
        algebra=runtime.ReducerAlgebra.CHECKED_U64_PRODUCT_SUM,
        multiplicand_source=SimpleNamespace(semantic_id="query.weight"),
        value_source=SimpleNamespace(
            kind=runtime.ReducerSourceKind.PER_RAY_OUTPUT,
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
    owner._cached_query_generation = None
    owner._cached_query_pointers = None
    owner._native_sha = "c" * 64
    owner._composed_ptx_sha = "f" * 64
    owner._pid = os.getpid()
    owner._thread = threading.get_ident()
    owner._active = threading.Lock()
    owner._closed = False
    owner._execution_count = 0
    owner._last_execution_receipt = None
    owner._execute = lambda *_args: (_ for _ in ()).throw(
        AssertionError("diagnostic path reached")
    )
    owner._execute_scalar = lambda *_args: (_ for _ in ()).throw(
        AssertionError("legacy scalar path reached")
    )
    owner._execute_scalar_integrated = state.execute_v8
    owner._reduce_u64 = lambda *_args: (_ for _ in ()).throw(
        AssertionError("host reducer reached")
    )
    owner._scalar_output = ctypes.c_uint64()
    owner._fast_compact_status = ctypes.c_uint32()
    owner._fast_receipt = runtime._FastPathReceipt()
    owner._call_error = ctypes.create_string_buffer(16384)
    owner._integrated_audit_snapshot = provenance.NativeTraversalAuditSnapshot()
    owner._integrated_audit_sequence = 0
    owner._integrated_audit_nonce_hi = 17
    owner._integrated_audit_output_sha = None
    owner._integrated_status_rows = None
    owner._route_identity = ROUTE_IDENTITY
    owner._program_bundle = PROGRAM_BUNDLE
    owner._semantic_digest = "d" * 64
    owner._native_path = Path(__file__)
    owner._session_identity = "a" * 64
    return owner


class Goal5844CompactExecutionStampTest(unittest.TestCase):
    def test_cached_invariants_preserve_values_and_fail_closed_checks(self) -> None:
        for value in (-7, 0, 6, (1 << 64) - 1):
            expected = _seal(value)
            self.assertEqual(runtime._digest(value), expected)
            self.assertEqual(callback_lifecycle._digest(value), expected)
            self.assertEqual(runtime._digest(value), expected)
            self.assertEqual(callback_lifecycle._digest(value), expected)

        bundle_id = provenance.physical_program_bundle_id(PROGRAM_BUNDLE)
        self.assertEqual(
            provenance.physical_program_bundle_id(PROGRAM_BUNDLE), bundle_id
        )
        with self.assertRaisesRegex(ValueError, "nonempty string"):
            provenance.physical_program_bundle_id(())

        self.assertEqual(
            provenance._require_sha256("a" * 64, label="test"), "a" * 64
        )
        self.assertEqual(
            provenance._require_sha256("a" * 64, label="test"), "a" * 64
        )
        with self.assertRaisesRegex(RuntimeError, "malformed"):
            provenance._require_sha256("A" * 64, label="test")
        with self.assertRaises(callback_lifecycle.ProtocolLifecycleError):
            callback_lifecycle._require_sha256("g" * 64, "test")

    def test_v8_ctypes_abi_is_additive_and_v7_remains_compatible(self) -> None:
        names = (
            "rtdl_optix_v4_prepare_triangle_reduction_callback_v1",
            "rtdl_optix_v4_execute_prepared_triangle_reduction_callback_v2",
            "rtdl_optix_v4_execute_prepared_triangle_reduction_callback_v7",
            "rtdl_optix_v4_commit_prepared_triangle_reduction_cache_v1",
            "rtdl_optix_v4_prepared_triangle_reduction_cache_digest_v1",
            "rtdl_optix_v4_destroy_prepared_triangle_reduction_callback_v1",
            "rtdl_optix_v4_checked_u64_product_sum_host_v1",
        )
        legacy = SimpleNamespace(**{name: _ConfigSymbol() for name in names})
        configured_legacy = runtime._configure(legacy)
        self.assertIsNone(configured_legacy[3])

        integrated = _ConfigSymbol()
        current = SimpleNamespace(
            **{name: _ConfigSymbol() for name in names},
            rtdl_optix_v4_execute_prepared_triangle_reduction_callback_v8=(
                integrated
            ),
        )
        configured_current = runtime._configure(current)
        self.assertIs(configured_current[3], integrated)
        self.assertEqual(len(integrated.argtypes), 19)
        self.assertIs(integrated.argtypes[14], ctypes.c_uint64)
        self.assertIs(integrated.argtypes[15], ctypes.c_uint64)
        self.assertEqual(
            integrated.argtypes[16],
            ctypes.POINTER(provenance.NativeTraversalAuditSnapshot),
        )
        self.assertIs(integrated.restype, ctypes.c_int)

    def test_gpu_runner_recomputes_retained_timing_summary(self) -> None:
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
        for key, bad_value in (
            ("sample_count", 3),
            ("minimum_ns", 10),
            ("median_ns", 14),
            ("maximum_ns", 20),
        ):
            with self.subTest(key=key):
                forged = dict(summary)
                forged[key] = bad_value
                with self.assertRaisesRegex(RuntimeError, "timing values differ"):
                    gpu_runner._validate_timing_summary(
                        forged, expected_count=4, label="test"
                    )

    def test_compact_receipt_revalidates_and_binds_exact_stamp(self) -> None:
        receipt = _compact_receipt(sequence=9, ray_count=4)
        self.assertEqual(
            receipt["schema"], provenance.COMPACT_TRAVERSAL_RECEIPT_SCHEMA
        )
        self.assertEqual(
            len(receipt["native_stamp"]),
            len(provenance.COMPACT_TRAVERSAL_STAMP_FIELDS),
        )
        provenance.validate_traversal_receipt(
            receipt,
            provider_library_sha256="c" * 64,
            route_identity=ROUTE_IDENTITY,
            output_digest="e" * 64,
            expected_program_bundles=(PROGRAM_BUNDLE,),
            expected_successful_launch_count=1,
            expected_raygen_invocation_count=4,
        )

    def test_validated_compact_receipt_defers_only_transport_document(self) -> None:
        receipt = provenance.build_validated_compact_traversal_receipt(
            _snapshot(sequence=9, ray_count=4),
            provider_library_sha256="c" * 64,
            route_identity=ROUTE_IDENTITY,
            semantic_digest="d" * 64,
            output_digest="e" * 64,
            expected_program_bundle=PROGRAM_BUNDLE,
            expected_raygen_invocation_count=4,
            execution_sequence=9,
        )
        self.assertFalse(receipt.materialized)
        self.assertIs(
            provenance.validate_bound_compact_traversal_receipt(
                receipt,
                provider_library_sha256="c" * 64,
                route_identity=ROUTE_IDENTITY,
                output_digest="e" * 64,
                expected_program_bundle=PROGRAM_BUNDLE,
                expected_raygen_invocation_count=4,
            ),
            receipt,
        )
        self.assertFalse(receipt.materialized)
        with self.assertRaises(AttributeError):
            receipt._output_digest = "f" * 64
        document = dict(receipt)
        self.assertTrue(receipt.materialized)
        self.assertIsInstance(document["native_stamp"], tuple)
        provenance.validate_traversal_receipt(
            receipt,
            provider_library_sha256="c" * 64,
            route_identity=ROUTE_IDENTITY,
            output_digest="e" * 64,
            expected_program_bundles=(PROGRAM_BUNDLE,),
            expected_successful_launch_count=1,
            expected_raygen_invocation_count=4,
        )

    def test_self_resealed_invalid_dynamic_fields_are_rejected(self) -> None:
        mutations = {
            "nonce_hi": (0, 0),
            "nonce_sequence_relation": (1, 2),
            "attempted": (3, 0),
            "successful": (4, 0),
            "failed": (5, 1),
            "complete": (6, 0),
            "incomplete": (7, 1),
            "context_bind": (8, 0),
            "raygen": (9, 3),
            "bundle": (10, 1),
            "last_bundle": (11, 1),
            "first_traversable": (12, 0),
            "last_traversable": (13, 2),
            "pending": (14, 1),
            "session_error": (15, 1),
            "incomplete_callsite": (16, 1),
            "bundle_mix": (17, 0),
            "traversable_mix": (18, 0),
        }
        for label, (index, replacement) in mutations.items():
            with self.subTest(label=label):
                forged = copy.deepcopy(_compact_receipt(sequence=1, ray_count=4))
                forged["native_stamp"][index] = replacement
                body = dict(forged)
                body.pop("receipt_sha256")
                forged["receipt_sha256"] = _seal(body)
                with self.assertRaisesRegex(
                    RuntimeError, "compact traversal native stamp differs"
                ):
                    provenance.validate_compact_traversal_receipt(
                        forged,
                        provider_library_sha256="c" * 64,
                        route_identity=ROUTE_IDENTITY,
                        output_digest="e" * 64,
                        expected_program_bundles=(PROGRAM_BUNDLE,),
                        expected_successful_launch_count=1,
                        expected_raygen_invocation_count=4,
                    )

    def test_integrated_owner_skips_separate_audit_and_steady_digest_query(self) -> None:
        state = _IntegratedState()
        owner = _owner(state)
        queries = (((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 2.0),)
        weights = (2,)
        with patch.object(
            runtime.OptixTraversalAuditSession,
            "open",
            side_effect=AssertionError("separate traversal audit reached"),
        ):
            first = owner.execute(
                queries,
                query_metadata={"query.weight": weights},
                include_diagnostics=False,
            )
            second = owner.execute(
                queries,
                query_metadata={"query.weight": weights},
                include_diagnostics=False,
            )
        self.assertEqual((first.reduced_output, second.reduced_output), (6, 6))
        self.assertEqual(state.reuse_flags, [0, 1])
        self.assertEqual(state.sequences, [1, 2])
        self.assertEqual(state.cache_digest_queries, 1)
        self.assertEqual(state.commit_count, 1)
        self.assertIsInstance(
            second.traversal_receipt,
            provenance.ValidatedCompactTraversalReceipt,
        )
        self.assertFalse(second.traversal_receipt.materialized)
        self.assertEqual(
            second.traversal_receipt["schema"],
            provenance.COMPACT_TRAVERSAL_RECEIPT_SCHEMA,
        )
        self.assertTrue(second.traversal_receipt.materialized)
        self.assertEqual(
            owner._last_execution_receipt["execution_path"],
            "device_resident_checked_u64_scalar_v8_integrated_audit",
        )
        lifecycle = owner.lifecycle_receipt
        self.assertIsInstance(
            lifecycle["last_execution"]["fast_operation_receipt"], dict
        )
        json.dumps(lifecycle, sort_keys=True)
        provenance.validate_traversal_receipt(
            second.traversal_receipt,
            provider_library_sha256="c" * 64,
            route_identity=ROUTE_IDENTITY,
            output_digest=second.output_sha256,
            expected_program_bundles=(PROGRAM_BUNDLE,),
            expected_successful_launch_count=1,
            expected_raygen_invocation_count=1,
        )

        forensic = owner.last_forensic_traversal_receipt()
        self.assertEqual(
            forensic["schema"], "rtdl.physical_execution.traversal_receipt.v1"
        )
        self.assertEqual(forensic["output_digest"], second.output_sha256)
        self.assertEqual(forensic["native_snapshot"]["nonce_lo"], 2)
        self.assertEqual(
            forensic["native_snapshot"]["first_program_bundle_id"],
            second.traversal_receipt["expected_program_bundle_id"],
        )

    def test_generation_mismatch_is_fail_closed_and_clears_local_cache(self) -> None:
        state = _IntegratedState()
        owner = _owner(state)
        queries = (((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 2.0),)
        metadata = {"query.weight": (2,)}
        owner.execute(queries, query_metadata=metadata, include_diagnostics=False)
        state.corrupt_generation = True
        with self.assertRaisesRegex(RuntimeError, "fast-path receipt is invalid"):
            owner.execute(queries, query_metadata=metadata, include_diagnostics=False)
        self.assertIsNone(owner._cached_queries)
        self.assertIsNone(owner._cached_query_digest)
        self.assertIsNone(owner._cached_query_generation)
        self.assertIsNone(owner._integrated_audit_output_sha)

    def test_compact_receipt_passes_ordinary_public_protocol_gate(self) -> None:
        state = _IntegratedState()
        owner = _owner(state)
        identity = SimpleNamespace(
            native_library_sha256="c" * 64,
            composed_ptx_sha256="f" * 64,
        )
        prepared = callback_lifecycle.PreparedProtocolProgram(
            family=callback_lifecycle.ProtocolFamily.TRIANGLE_REDUCTION,
            owner=owner,
            identity=identity,
            materialize_seconds=0.0,
            protocol_contract_decision=SimpleNamespace(
                verdict="ACCEPT", to_mapping=lambda: {"decision_sha256": "b" * 64}
            ),
        )
        batch = callback_lifecycle.TriangleReductionBatch(
            queries=(((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 2.0),),
            query_metadata={"query.weight": (2,)},
        )
        result = prepared.execute(batch, include_diagnostics=False)
        self.assertEqual(result.output, 6)
        self.assertIsInstance(
            result.traversal_receipt,
            provenance.ValidatedCompactTraversalReceipt,
        )
        self.assertFalse(result.traversal_receipt.materialized)
        bridge_identity = generic_lifecycle.FamilyExecutableIdentityV1(
            *(str(index) * 64 for index in range(1, 8))
        )
        bridge = family_adapters._PreparedBridge(
            prepared,
            bridge_identity,
            "1" * 64,
            family_adapters._stable_output,
        )
        bridged = bridge.execute(batch)
        self.assertIs(
            type(bridged), family_adapters._ValidatedScalarProviderExecution
        )
        self.assertFalse(bridged.traversal_receipt.materialized)
        self.assertEqual(
            result.traversal_receipt["schema"],
            provenance.COMPACT_TRAVERSAL_RECEIPT_SCHEMA,
        )

    def test_compact_receipt_survives_frozen_generic_execution_envelope(self) -> None:
        receipt = _compact_receipt(sequence=3, ray_count=1)
        output = 6
        execution = generic_lifecycle.FamilyProviderExecutionV1(
            "1" * 64,
            "2" * 64,
            "OK",
            0,
            output,
            _seal(output),
            receipt,
        )
        self.assertEqual(
            execution.traversal_receipt["schema"],
            provenance.COMPACT_TRAVERSAL_RECEIPT_SCHEMA,
        )
        self.assertEqual(
            list(execution.traversal_receipt["native_stamp"]),
            receipt["native_stamp"],
        )
        provenance.validate_traversal_receipt(
            execution.traversal_receipt,
            provider_library_sha256="c" * 64,
            route_identity=ROUTE_IDENTITY,
            output_digest="e" * 64,
            expected_program_bundles=(PROGRAM_BUNDLE,),
            expected_successful_launch_count=1,
            expected_raygen_invocation_count=1,
        )

    def test_native_failure_consumes_nonce_and_clears_cache_identity(self) -> None:
        state = _IntegratedState()
        owner = _owner(state)
        queries = (((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 2.0),)
        metadata = {"query.weight": (2,)}
        owner.execute(queries, query_metadata=metadata, include_diagnostics=False)
        state.fail_native = True
        with self.assertRaisesRegex(RuntimeError, "injected integrated native failure"):
            owner.execute(queries, query_metadata=metadata, include_diagnostics=False)
        self.assertEqual(owner._integrated_audit_sequence, 2)
        self.assertIsNone(owner._integrated_audit_output_sha)
        self.assertIsNone(owner._cached_queries)
        state.fail_native = False
        owner.execute(queries, query_metadata=metadata, include_diagnostics=False)
        self.assertEqual(state.sequences, [1, 2, 3])

    def test_replayed_native_snapshot_fails_closed_before_publication(self) -> None:
        state = _IntegratedState()
        owner = _owner(state)
        queries = (((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 2.0),)
        metadata = {"query.weight": (2,)}
        owner.execute(queries, query_metadata=metadata, include_diagnostics=False)
        state.snapshot_sequence_delta = -1
        with self.assertRaisesRegex(
            RuntimeError, "compact traversal native stamp differs"
        ):
            owner.execute(queries, query_metadata=metadata, include_diagnostics=False)
        self.assertIsNone(owner._cached_queries)
        self.assertIsNone(owner._integrated_audit_output_sha)
        state.snapshot_sequence_delta = 0
        result = owner.execute(
            queries, query_metadata=metadata, include_diagnostics=False
        )
        self.assertEqual(result.reduced_output, 6)
        self.assertEqual(state.reuse_flags, [0, 1, 0])
        self.assertEqual(state.sequences, [1, 2, 3])

    def test_device_status_failure_returns_no_scalar_and_clears_cache(self) -> None:
        state = _IntegratedState()
        owner = _owner(state)
        queries = (((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 2.0),)
        metadata = {"query.weight": (2,)}
        owner.execute(queries, query_metadata=metadata, include_diagnostics=False)
        state.compact_status = 17
        with self.assertRaisesRegex(
            RuntimeError, "compact device status rejected execution: 17"
        ):
            owner.execute(queries, query_metadata=metadata, include_diagnostics=False)
        self.assertIsNone(owner._cached_queries)
        self.assertIsNone(owner._integrated_audit_output_sha)
        state.compact_status = 0
        result = owner.execute(
            queries, query_metadata=metadata, include_diagnostics=False
        )
        self.assertEqual(result.reduced_output, 6)
        self.assertEqual(state.reuse_flags, [0, 1, 0])

    def test_native_source_integrates_audit_and_cleans_failure(self) -> None:
        source = (
            Path("src/native/optix/rtdl_optix_api.cpp")
            .read_text(encoding="utf-8")
        )
        self.assertIn(
            "rtdl_optix_v4_execute_prepared_triangle_reduction_callback_v8",
            source,
        )
        self.assertIn("rtdl_optix_traversal_audit_begin_checked", source)
        self.assertIn("rtdl_optix_traversal_audit_finish_checked", source)
        self.assertIn("rtdl_optix_traversal_audit_abort_checked", source)
        self.assertNotIn("raydb", source.lower())
        self.assertNotIn("barnes", source.lower())


if __name__ == "__main__":
    unittest.main()
