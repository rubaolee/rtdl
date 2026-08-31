from __future__ import annotations

from contextlib import ExitStack
import ctypes
from dataclasses import FrozenInstanceError
from pathlib import Path
from types import SimpleNamespace
import sys
import unittest
from unittest import mock

from rtdsl import physical_execution_provenance as provenance
from rtdsl import v4_operation_evidence as operation_evidence
from rtdsl import v4_triangle_reduction_device_runtime as runtime
from rtdsl.physical_execution_provenance import CapturedTraversalObservation
from rtdsl.v4_checked_u64_device_reduction import CheckedU64WeightedReduction
from rtdsl.v4_fusion_ablation import (
    FusionVariant,
    build_checked_u64_product_sum_ablation_plan,
)
from rtdsl.v4_triangle_reduction import ReducerAlgebra

from tests.goal5790_operation_evidence_test import _plan
from tests.goal5790_fusion_ablation_contract_test import _authority, _freeze, _sha
from tests.goal5790_triangle_runtime_integration_test import _Array, _FakeCupy


_PROGRAM = "v4_builtin_triangle_checked_reduction_composed"


class _Cupy(_FakeCupy):
    __version__ = "14.0.1"

    @staticmethod
    def empty(count, dtype=None):
        return _Array([0] * int(count))


class _Audit:
    def __init__(self, classification="optix_traversal_observed"):
        self.classification = classification
        self.capture_calls = 0
        self.abort_calls = 0

    def capture(self, *, expected_program_bundles=()):
        self.capture_calls += 1
        names = tuple(expected_program_bundles)
        ids = tuple(provenance.physical_program_bundle_id(name) for name in names)
        return CapturedTraversalObservation(
            provider_library_path=Path("/frozen/librtdl_optix.so"),
            provider_library_sha256="e" * 64,
            nonce_hi=17,
            nonce_lo=29,
            physical_executor_classification=self.classification,
            expected_program_bundles=names,
            expected_program_bundle_ids=ids,
            expected_program_observed_at_receipt_edge=True,
            native_snapshot_items=(
                ("nonce_hi", 17),
                ("nonce_lo", 29),
                ("successful_launch_count", 1),
                ("complete_context_launch_count", 1),
                ("first_program_bundle_id", ids[0]),
                ("last_program_bundle_id", ids[0]),
                ("pending_context_at_finish", 0),
                ("session_error", 0),
            ),
        )

    def abort(self):
        self.abort_calls += 1


def _columns(keys, count):
    return {key: _Array(range(1, count + 1)) for key in keys}


def _executor(plan):
    owner = object.__new__(runtime.VerifiedTriangleDeviceColumnCountExecutor)
    owner._closed = False
    owner._fresh = SimpleNamespace(
        authority_nonce=plan.callback_authority_nonce,
        callback=SimpleNamespace(ir_sha256=plan.callback_ir_sha256),
        target=SimpleNamespace(target_sha256=plan.target_identity_sha256),
        schema=SimpleNamespace(
            reducer=SimpleNamespace(
                algebra=ReducerAlgebra.CHECKED_U64_PRODUCT_SUM
            )
        ),
    )
    owner._contract = SimpleNamespace(contract_sha256=plan.contract_sha256)
    owner._abi = SimpleNamespace(abi_sha256=plan.abi_sha256)
    owner._library = object()
    owner._composed_ptx = "// goal5790 composed PTX"
    owner._composed_ptx_sha = plan.composed_program_sha256
    owner._native_sha = plan.native_library_sha256

    calls = SimpleNamespace(prepare=0, execute=0, destroy=0)

    def prepare(*args):
        calls.prepare += 1
        ctypes.cast(args[-3], ctypes.POINTER(ctypes.c_uint64)).contents.value = 41
        return 0

    def execute(*args):
        calls.execute += 1
        counters = args[-3]
        counters[0] = 1
        counters[1] = 5
        counters[3] = 1
        counters[5] = 5
        counters[6] = 5
        return 0

    def destroy(*_args):
        calls.destroy += 1
        return 0

    owner._prepare = prepare
    owner._execute = execute
    owner._destroy = destroy
    return owner, calls


def _reduction(plan, operation_trace):
    if operation_trace is not None:
        for requirement in plan.operation_requirements:
            operation_trace.execute(requirement.operation_id, lambda: None)
    fused = plan.variant is FusionVariant.FUSION_ON
    return CheckedU64WeightedReduction(
        value=19,
        maximum_value=4,
        maximum_weight=3,
        weight_sum=9,
        value_count=5,
        value_upper_bound=4,
        device_kernel_launch_count=1 if fused else 0,
        host_synchronization_count=1 if fused else 3,
        logical_reduction_count=0 if fused else 3,
        device_materialization_count=0 if fused else 1,
        operation_counts_event_derived=operation_trace is not None,
        maximum_value_is_device_observed=fused,
    )


class DeferredTriangleSegmentEvidenceTest(unittest.TestCase):
    def _invoke(
        self,
        variant: FusionVariant,
        method: str,
        *,
        hash_guard: bool = False,
        classification: str = "optix_traversal_observed",
        with_plan: bool = True,
    ):
        plan = _plan(variant)
        owner, calls = _executor(plan)
        audit = _Audit(classification)
        triangles = _columns(runtime._TRIANGLE_KEYS, 4)
        rays = _columns(runtime._RAY_KEYS, 5)
        weights = _Array([1, 2, 3, 2, 1])

        def reduction(_values, _weights, *, value_upper_bound, operation_trace):
            self.assertEqual(value_upper_bound, 4)
            return _reduction(plan, operation_trace)

        with ExitStack() as stack:
            stack.enter_context(mock.patch.dict(sys.modules, {"cupy": _Cupy}))
            stack.enter_context(mock.patch.object(
                runtime,
                "_device_columns",
                side_effect=((triangles, 4, 0), (rays, 5, 0)),
            ))
            stack.enter_context(mock.patch.object(
                runtime,
                "checked_u64_downstream_operation_sha256",
                return_value=plan.downstream_operation_recipe_sha256,
            ))
            stack.enter_context(mock.patch.object(
                runtime.OptixTraversalAuditSession,
                "open",
                return_value=audit,
            ))
            stack.enter_context(mock.patch.object(
                runtime,
                "checked_u64_weighted_sum_device",
                side_effect=reduction,
            ))
            stack.enter_context(mock.patch.object(
                runtime,
                "checked_u64_weighted_sum_unfused_device",
                side_effect=reduction,
            ))
            if hash_guard:
                stack.enter_context(mock.patch.object(
                    runtime,
                    "_digest",
                    side_effect=AssertionError("output/semantic digest in timer"),
                ))
                stack.enter_context(mock.patch.object(
                    provenance,
                    "_stable_digest",
                    side_effect=AssertionError("traversal receipt sealed in timer"),
                ))
                stack.enter_context(mock.patch.object(
                    operation_evidence.OperationTrace,
                    "seal",
                    side_effect=AssertionError("operation receipt sealed in timer"),
                ))
            result = getattr(owner, method)(
                triangles,
                rays,
                ray_weights=weights,
                fusion_ablation_plan=plan if with_plan else None,
                operation_execution_nonce=(
                    f"goal5790-{variant.value}-deferred-0001"
                    if with_plan else None
                ),
            )
        return result, plan, calls, audit

    def test_executor_exposes_live_callback_contract_and_abi_identities(self):
        plan = _plan(FusionVariant.FUSION_ON)
        owner, _calls = _executor(plan)
        self.assertEqual(owner.callback_authority_nonce,
                         plan.callback_authority_nonce)
        self.assertEqual(owner.contract_sha256, plan.contract_sha256)
        self.assertEqual(owner.abi_sha256, plan.abi_sha256)

    def test_unsealed_execution_performs_no_receipt_hashing(self):
        for variant in (FusionVariant.FUSION_ON, FusionVariant.FUSION_OFF):
            with self.subTest(variant=variant.value):
                pending, plan, calls, audit = self._invoke(
                    variant,
                    "execute_segment_unsealed",
                    hash_guard=True,
                )
                self.assertEqual(pending.state, "device_complete_unsealed")
                self.assertEqual(pending.operation_trace.state, "completed_unsealed")
                self.assertEqual(calls.prepare, 1)
                self.assertEqual(calls.execute, 1)
                self.assertEqual(calls.destroy, 1)
                self.assertEqual(audit.capture_calls, 1)
                with self.assertRaises(FrozenInstanceError):
                    pending.reduced_output = 20
                with self.assertRaises(FrozenInstanceError):
                    pending.native_library_sha256 = "0" * 64
                with self.assertRaises(FrozenInstanceError):
                    pending.traversal_observation = None

                sealed = pending.seal()
                self.assertEqual(pending.state, "sealed")
                self.assertEqual(
                    sealed["fusion_ablation_plan_sha256"], plan.plan_sha256
                )
                self.assertEqual(
                    sealed["operation_evidence_receipt"]["successful_event_count"],
                    2 if variant is FusionVariant.FUSION_ON else 7,
                )

    def test_seal_provenance_is_variant_specific(self):
        on, _plan_on, _calls, _audit = self._invoke(
            FusionVariant.FUSION_ON, "execute_segment_unsealed"
        )
        off, _plan_off, _calls, _audit = self._invoke(
            FusionVariant.FUSION_OFF, "execute_segment_unsealed"
        )
        on_receipt = on.seal()["checked_u64_weighted_reduction"]
        off_receipt = off.seal()["checked_u64_weighted_reduction"]
        self.assertTrue(on_receipt["maximum_value_is_device_observed"])
        self.assertEqual(on_receipt["maximum_value_provenance"], "device_observed")
        self.assertFalse(off_receipt["maximum_value_is_device_observed"])
        self.assertEqual(
            off_receipt["maximum_value_provenance"],
            "optix_producer_declared_primitive_bound",
        )

    def test_abort_double_seal_and_seal_failure_fail_closed(self):
        aborted, _plan_value, _calls, _audit = self._invoke(
            FusionVariant.FUSION_ON, "execute_segment_unsealed"
        )
        aborted.abort()
        self.assertEqual(aborted.state, "aborted")
        self.assertEqual(aborted.operation_trace.state, "aborted")
        with self.assertRaisesRegex(RuntimeError, "state is aborted"):
            aborted.seal()

        sealed, _plan_value, _calls, _audit = self._invoke(
            FusionVariant.FUSION_ON, "execute_segment_unsealed"
        )
        sealed.seal()
        with self.assertRaisesRegex(RuntimeError, "state is sealed"):
            sealed.seal()

        failed, _plan_value, _calls, _audit = self._invoke(
            FusionVariant.FUSION_ON, "execute_segment_unsealed"
        )
        with mock.patch.object(
            runtime, "_digest", side_effect=RuntimeError("synthetic seal failure")
        ):
            with self.assertRaisesRegex(RuntimeError, "synthetic seal failure"):
                failed.seal()
        self.assertEqual(failed.state, "aborted")
        self.assertEqual(failed.operation_trace.state, "aborted")

    def test_legacy_execute_segment_matches_explicit_unsealed_then_seal(self):
        pending, _plan_value, _calls, _audit = self._invoke(
            FusionVariant.FUSION_ON, "execute_segment_unsealed"
        )
        explicit = pending.seal()
        legacy, _plan_value, calls, _audit = self._invoke(
            FusionVariant.FUSION_ON, "execute_segment"
        )
        self.assertEqual(legacy, explicit)
        self.assertEqual(calls.destroy, 1)
        self.assertEqual(set(legacy), {
            "reduced_output",
            "role_counters",
            "traversal_receipt",
            "output_sha256",
            "native_library_sha256",
            "device_columns_preserved",
            "per_ray_host_materialized",
            "triangle_count",
            "query_count",
            "checked_u64_weighted_reduction",
            "fusion_ablation_plan_sha256",
            "operation_evidence_receipt",
        })

    def test_invalid_captured_traversal_aborts_completed_operation_trace(self):
        with self.assertRaisesRegex(RuntimeError, "lacked bound traversal"):
            self._invoke(
                FusionVariant.FUSION_OFF,
                "execute_segment_unsealed",
                classification="invalid_traversal_audit_session",
            )

    def test_live_callback_contract_abi_and_cupy_drift_fail_closed(self):
        plan = _plan(FusionVariant.FUSION_ON)
        for path, replacement in (
            ("authority", "goal5790-live-authority-drift-0001"),
            ("contract", "a" * 64),
            ("abi", "b" * 64),
        ):
            with self.subTest(path=path):
                owner, _calls = _executor(plan)
                if path == "authority":
                    owner._fresh.authority_nonce = replacement
                elif path == "contract":
                    owner._contract.contract_sha256 = replacement
                else:
                    owner._abi.abi_sha256 = replacement
                with ExitStack() as stack:
                    stack.enter_context(mock.patch.dict(sys.modules, {"cupy": _Cupy}))
                    stack.enter_context(mock.patch.object(
                        runtime,
                        "_device_columns",
                        side_effect=(({}, 4, 0), ({}, 5, 0)),
                    ))
                    with self.assertRaisesRegex(RuntimeError, "identity mismatch"):
                        owner.execute_segment_unsealed(
                            {}, {}, ray_weights=_Array([1, 2, 3, 2, 1]),
                            fusion_ablation_plan=plan,
                            operation_execution_nonce=(
                                "goal5790-live-identity-drift-0001"),
                        )

        class WrongCupy(_Cupy):
            __version__ = "99.0.0"

        owner, _calls = _executor(plan)
        with ExitStack() as stack:
            stack.enter_context(mock.patch.dict(sys.modules, {"cupy": WrongCupy}))
            stack.enter_context(mock.patch.object(
                runtime,
                "_device_columns",
                side_effect=(({}, 4, 0), ({}, 5, 0)),
            ))
            with self.assertRaisesRegex(RuntimeError, "identity mismatch"):
                owner.execute_segment_unsealed(
                    {}, {}, ray_weights=_Array([1, 2, 3, 2, 1]),
                    fusion_ablation_plan=plan,
                    operation_execution_nonce="goal5790-live-cupy-drift-0001",
                )

    def test_resigned_target_cupy_version_still_must_match_live_runtime(self):
        plan = build_checked_u64_product_sum_ablation_plan(
            _freeze(),
            variant=FusionVariant.FUSION_ON,
            target_materialization=_authority(cupy_version="99.0.0"),
            input_sha256=_sha("5"),
            output_contract_sha256=_sha("6"),
            oracle_sha256=_sha("7"),
            timer_contract_sha256=_sha("8"),
            lifecycle_contract_sha256=_sha("9"),
            value_count=5,
        )
        owner, _calls = _executor(plan)
        with ExitStack() as stack:
            stack.enter_context(mock.patch.dict(sys.modules, {"cupy": _Cupy}))
            stack.enter_context(mock.patch.object(
                runtime,
                "_device_columns",
                side_effect=(({}, 4, 0), ({}, 5, 0)),
            ))
            with self.assertRaisesRegex(RuntimeError, "identity mismatch"):
                owner.execute_segment_unsealed(
                    {}, {}, ray_weights=_Array([1, 2, 3, 2, 1]),
                    fusion_ablation_plan=plan,
                    operation_execution_nonce=(
                        "goal5790-resigned-target-cupy-drift-0001"),
                )


if __name__ == "__main__":
    unittest.main()
