from __future__ import annotations

from contextlib import ExitStack
import copy
import sys
import unittest
from unittest import mock

from rtdsl import v4_operation_evidence as operation_evidence
from rtdsl import v4_triangle_reduction_device_runtime as runtime
from rtdsl.v4_fusion_ablation import FusionAblationPlan, FusionVariant

from tests.goal5790_deferred_triangle_segment_evidence_test import (
    _Audit,
    _Cupy,
    _columns,
    _executor,
    _reduction,
)
from tests.goal5790_operation_evidence_test import _plan
from tests.goal5790_triangle_runtime_integration_test import (
    _Array as runtime_test_array,
)


def _admit(
    owner,
    plan,
    *,
    ordinal=3,
    primitives=4,
    queries=5,
    descriptor=None,
    plan_input_binding=None,
):
    descriptor = plan.input_sha256 if descriptor is None else descriptor
    kwargs = {}
    if plan_input_binding is not None:
        kwargs["plan_input_binding_sha256"] = plan_input_binding
    with mock.patch.dict(sys.modules, {"cupy": _Cupy}):
        return owner.admit_fusion_execution_token(
            plan,
            operation_execution_nonce=(
                f"goal5791-token-{plan.variant.value}-{ordinal:04d}"
            ),
            segment_ordinal=ordinal,
            primitive_count=primitives,
            query_count=queries,
            segment_descriptor_sha256=descriptor,
            **kwargs,
        )


def _execute(
    owner,
    plan,
    token,
    *,
    ordinal=3,
    primitive_count=4,
    query_count=5,
    descriptor=None,
):
    descriptor = plan.input_sha256 if descriptor is None else descriptor
    audit = _Audit()
    triangles = _columns(runtime._TRIANGLE_KEYS, primitive_count)
    rays = _columns(runtime._RAY_KEYS, query_count)
    weights = runtime_test_array([1, 2, 3, 2, 1][:query_count])

    def reduction(_values, _weights, *, value_upper_bound, operation_trace):
        if value_upper_bound != primitive_count:
            raise AssertionError("unexpected primitive bound")
        return _reduction(plan, operation_trace)

    with ExitStack() as stack:
        stack.enter_context(mock.patch.dict(sys.modules, {"cupy": _Cupy}))
        stack.enter_context(mock.patch.object(
            runtime,
            "_device_columns",
            side_effect=(
                (triangles, primitive_count, 0),
                (rays, query_count, 0),
            ),
        ))
        stack.enter_context(mock.patch.object(
            runtime.OptixTraversalAuditSession, "open", return_value=audit))
        stack.enter_context(mock.patch.object(
            runtime, "checked_u64_weighted_sum_device", side_effect=reduction))
        stack.enter_context(mock.patch.object(
            runtime,
            "checked_u64_weighted_sum_unfused_device",
            side_effect=reduction,
        ))
        return owner.execute_segment_unsealed(
            triangles,
            rays,
            ray_weights=weights,
            fusion_execution_token=token,
            segment_ordinal=ordinal,
            segment_descriptor_sha256=descriptor,
        )

class Goal5791VerifiedFusionExecutionTokenTest(unittest.TestCase):
    def test_token_path_performs_no_deep_plan_recipe_or_contract_verification(self):
        for variant in (FusionVariant.FUSION_ON, FusionVariant.FUSION_OFF):
            with self.subTest(variant=variant.value):
                plan = _plan(variant)
                owner, calls = _executor(plan)
                token = _admit(owner, plan)
                self.assertEqual(token.state, "fresh")

                with ExitStack() as stack:
                    stack.enter_context(mock.patch.object(
                        runtime,
                        "verify_fusion_ablation_plan",
                        side_effect=AssertionError("deep plan verify in timer"),
                    ))
                    stack.enter_context(mock.patch.object(
                        runtime,
                        "checked_u64_downstream_operation_sha256",
                        side_effect=AssertionError("recipe digest in timer"),
                    ))
                    stack.enter_context(mock.patch.object(
                        FusionAblationPlan,
                        "operation_contract",
                        side_effect=AssertionError("operation contract in timer"),
                    ))
                    stack.enter_context(mock.patch.object(
                        operation_evidence,
                        "verify_operation_sequence_contract",
                        side_effect=AssertionError("operation sequence verify in timer"),
                    ))
                    pending = _execute(owner, plan, token)

                self.assertEqual(token.state, "consumed")
                self.assertEqual(pending.state, "device_complete_unsealed")
                self.assertEqual(calls.prepare, 1)
                self.assertEqual(calls.execute, 1)
                self.assertEqual(calls.destroy, 1)
                sealed = pending.seal()
                self.assertEqual(
                    sealed["operation_evidence_receipt"]["successful_event_count"],
                    2 if variant is FusionVariant.FUSION_ON else 7,
                )

    def test_replay_and_failed_descriptor_attempt_consume_token(self):
        plan = _plan(FusionVariant.FUSION_ON)
        owner, _calls = _executor(plan)
        token = _admit(owner, plan)
        with self.assertRaisesRegex(
            runtime.FusionExecutionTokenError, "token_segment_descriptor"
        ):
            owner.execute_segment_unsealed(
                {}, {}, ray_weights=None,
                fusion_execution_token=token,
                segment_ordinal=3,
                segment_descriptor_sha256="0" * 64,
            )
        self.assertEqual(token.state, "consumed")
        with self.assertRaisesRegex(
            runtime.FusionExecutionTokenError, "token_replay"
        ):
            owner.execute_segment_unsealed(
                {}, {}, ray_weights=None,
                fusion_execution_token=token,
                segment_ordinal=3,
                segment_descriptor_sha256=plan.input_sha256,
            )

    def test_wrong_owner_fork_identity_drift_and_api_conflict_fail_closed(self):
        cases = ("wrong_owner", "fork", "identity_drift", "api_conflict")
        for case in cases:
            with self.subTest(case=case):
                plan = _plan(FusionVariant.FUSION_ON)
                owner, _calls = _executor(plan)
                token = _admit(owner, plan)
                target = owner
                kwargs = {}
                context = ExitStack()
                if case == "wrong_owner":
                    target, _other_calls = _executor(plan)
                    expected = "token_wrong_owner"
                elif case == "fork":
                    context.enter_context(mock.patch.object(
                        runtime.os, "getpid", return_value=runtime.os.getpid() + 1))
                    expected = "token_wrong_process"
                elif case == "identity_drift":
                    owner._abi.abi_sha256 = "0" * 64
                    expected = "token_identity_drift"
                else:
                    kwargs["fusion_ablation_plan"] = plan
                    expected = "token_api_conflict"
                with context:
                    with self.assertRaisesRegex(
                        runtime.FusionExecutionTokenError, expected
                    ):
                        target.execute_segment_unsealed(
                            {}, {}, ray_weights=None,
                            fusion_execution_token=token,
                            segment_ordinal=3,
                            segment_descriptor_sha256=plan.input_sha256,
                            **kwargs,
                        )
                self.assertEqual(token.state, "consumed")

    def test_actual_primitive_and_query_count_mismatch_fail_before_native(self):
        for field, primitive_count, query_count, expected in (
            ("primitive", 6, 5, "token_primitive_count"),
            ("query", 4, 6, "token_query_count"),
        ):
            with self.subTest(field=field):
                plan = _plan(FusionVariant.FUSION_ON)
                owner, calls = _executor(plan)
                token = _admit(owner, plan)
                triangles = _columns(runtime._TRIANGLE_KEYS, primitive_count)
                rays = _columns(runtime._RAY_KEYS, query_count)
                with ExitStack() as stack:
                    stack.enter_context(mock.patch.dict(
                        sys.modules, {"cupy": _Cupy}))
                    stack.enter_context(mock.patch.object(
                        runtime,
                        "_device_columns",
                        side_effect=(
                            (triangles, primitive_count, 0),
                            (rays, query_count, 0),
                        ),
                    ))
                    with self.assertRaisesRegex(
                        runtime.FusionExecutionTokenError, expected
                    ):
                        owner.execute_segment_unsealed(
                            triangles,
                            rays,
                            ray_weights=runtime_test_array([1] * query_count),
                            fusion_execution_token=token,
                            segment_ordinal=3,
                            segment_descriptor_sha256=plan.input_sha256,
                        )
                self.assertEqual(calls.prepare, 0)
                self.assertEqual(calls.execute, 0)
                self.assertEqual(calls.destroy, 0)
                self.assertEqual(token.state, "consumed")

    def test_admission_binds_descriptor_and_token_is_not_copyable(self):
        plan = _plan(FusionVariant.FUSION_OFF)
        owner, _calls = _executor(plan)
        with mock.patch.dict(sys.modules, {"cupy": _Cupy}):
            with self.assertRaisesRegex(
                runtime.FusionExecutionTokenError, "token_segment_descriptor"
            ):
                owner.admit_fusion_execution_token(
                    plan,
                    operation_execution_nonce="goal5791-token-admission-0001",
                    segment_ordinal=0,
                    primitive_count=4,
                    query_count=5,
                    segment_descriptor_sha256="0" * 64,
                )
        token = _admit(owner, plan)
        self.assertEqual(token.plan_sha256, plan.plan_sha256)
        self.assertEqual(token.segment_descriptor_sha256, plan.input_sha256)
        self.assertEqual(token.plan_input_sha256, plan.input_sha256)
        with self.assertRaisesRegex(TypeError, "not copyable"):
            copy.copy(token)
        with self.assertRaisesRegex(TypeError, "not copyable"):
            copy.deepcopy(token)

    def test_explicit_plan_input_binding_is_independent_of_descriptor(self):
        plan = _plan(FusionVariant.FUSION_ON)
        owner, _calls = _executor(plan)
        descriptor = "e" * 64
        token = _admit(
            owner,
            plan,
            descriptor=descriptor,
            plan_input_binding=plan.input_sha256,
        )
        self.assertEqual(token.segment_descriptor_sha256, descriptor)
        self.assertEqual(token.plan_input_sha256, plan.input_sha256)

        pending = _execute(owner, plan, token, descriptor=descriptor)
        self.assertEqual(pending.state, "device_complete_unsealed")
        pending.abort()

        with mock.patch.dict(sys.modules, {"cupy": _Cupy}):
            with self.assertRaisesRegex(
                runtime.FusionExecutionTokenError, "token_plan_input_binding"
            ):
                owner.admit_fusion_execution_token(
                    plan,
                    operation_execution_nonce="goal5791-token-input-0002",
                    segment_ordinal=4,
                    primitive_count=4,
                    query_count=5,
                    segment_descriptor_sha256=descriptor,
                    plan_input_binding_sha256="f" * 64,
                )
            with self.assertRaisesRegex(
                runtime.FusionExecutionTokenError, "token_sha256"
            ):
                owner.admit_fusion_execution_token(
                    plan,
                    operation_execution_nonce="goal5791-token-input-0003",
                    segment_ordinal=5,
                    primitive_count=4,
                    query_count=5,
                    segment_descriptor_sha256=descriptor,
                    plan_input_binding_sha256="not-a-sha",
                )

    def test_exact_token_type_and_legacy_descriptor_mix_are_rejected(self):
        plan = _plan(FusionVariant.FUSION_ON)
        owner, _calls = _executor(plan)
        with self.assertRaisesRegex(
            runtime.FusionExecutionTokenError, "token_type"
        ):
            owner.execute_segment_unsealed(
                {}, {}, fusion_execution_token=object(),
                segment_ordinal=0,
                segment_descriptor_sha256=plan.input_sha256,
            )
        with self.assertRaisesRegex(ValueError, "require a fusion execution token"):
            owner.execute_segment_unsealed(
                {}, {}, segment_ordinal=0,
                segment_descriptor_sha256=plan.input_sha256,
            )


if __name__ == "__main__":
    unittest.main()
