from __future__ import annotations

from dataclasses import replace
import json
import unittest

from rtdsl.v4_fusion_ablation import (
    FusionVariant,
    build_checked_u64_product_sum_ablation_plan,
    load_verified_shared_contract_freeze,
)
from rtdsl.v4_operation_evidence import (
    OPERATION_EVIDENCE_TCB,
    OperationEvidenceError,
    OperationKind,
    OperationRequirement,
    OperationSequenceContract,
    OperationTrace,
    receipt_from_mapping,
    verify_operation_evidence_receipt,
)

from tests.goal5790_fusion_ablation_contract_test import (
    BUNDLE,
    FREEZE,
    _authority,
    _sha,
)


def _plan(variant: FusionVariant):
    return build_checked_u64_product_sum_ablation_plan(
        load_verified_shared_contract_freeze(FREEZE.read_bytes()),
        variant=variant,
        target_materialization=_authority(),
        input_sha256=_sha("5"),
        output_contract_sha256=_sha("6"),
        oracle_sha256=_sha("7"),
        timer_contract_sha256=_sha("8"),
        lifecycle_contract_sha256=_sha("9"),
        value_count=5,
    )


def _complete(variant: FusionVariant):
    plan = _plan(variant)
    trace = OperationTrace(
        plan.operation_contract(),
        execution_nonce=f"goal5790-test-{variant.value}-0001",
        value_count=plan.value_count,
    )
    calls: list[str] = []
    for requirement in plan.operation_requirements:
        result = trace.execute(
            requirement.operation_id,
            lambda item=requirement.operation_id: calls.append(item),
        )
        assert result is None
    receipt = trace.finalize(
        output_sha256=_sha("c"),
        traversal_receipt_sha256=_sha("d"),
    )
    return plan, trace, calls, receipt


class Goal5790OperationEvidenceTest(unittest.TestCase):
    def test_event_is_appended_only_after_callable_success(self) -> None:
        plan = _plan(FusionVariant.FUSION_ON)
        trace = OperationTrace(
            plan.operation_contract(), execution_nonce="goal5790-failure-0001",
            value_count=plan.value_count)

        def fail():
            raise RuntimeError("synthetic operation failure")

        with self.assertRaisesRegex(RuntimeError, "synthetic operation failure"):
            trace.execute("checked_summary.kernel_launch", fail)
        self.assertEqual(trace.state, "aborted")
        with self.assertRaisesRegex(OperationEvidenceError, "trace_state"):
            trace.finalize(
                output_sha256=_sha("c"), traversal_receipt_sha256=_sha("d"))

    def test_missing_duplicate_reordered_and_extra_events_fail_closed(self) -> None:
        plan = _plan(FusionVariant.FUSION_OFF)
        for operation in (
            "weight_sum.logical_reduce",  # reordered
            "maximum_weight.logical_reduce",  # duplicate attempt after first below
        ):
            trace = OperationTrace(
                plan.operation_contract(),
                execution_nonce=f"goal5790-order-{operation.replace('.', '-')}-0001",
                value_count=plan.value_count,
            )
            if operation == "maximum_weight.logical_reduce":
                trace.execute(operation, lambda: None)
            with self.assertRaisesRegex(OperationEvidenceError, "operation_order"):
                trace.execute(operation, lambda: None)
            self.assertEqual(trace.state, "aborted")

        trace = OperationTrace(
            plan.operation_contract(), execution_nonce="goal5790-missing-0001",
            value_count=plan.value_count)
        trace.execute("maximum_weight.logical_reduce", lambda: None)
        with self.assertRaisesRegex(OperationEvidenceError, "sequence_incomplete"):
            trace.finalize(
                output_sha256=_sha("c"), traversal_receipt_sha256=_sha("d"))

        on_plan, _, _, receipt = _complete(FusionVariant.FUSION_ON)
        finalized = OperationTrace(
            on_plan.operation_contract(), execution_nonce="goal5790-extra-0001",
            value_count=on_plan.value_count)
        for requirement in on_plan.operation_requirements:
            finalized.execute(requirement.operation_id, lambda: None)
        finalized.finalize(
            output_sha256=receipt.output_sha256,
            traversal_receipt_sha256=receipt.traversal_receipt_sha256)
        with self.assertRaisesRegex(OperationEvidenceError, "trace_state"):
            finalized.execute("checked_summary.kernel_launch", lambda: None)

    def test_receipt_round_trip_reconstructs_exact_extents(self) -> None:
        plan, trace, calls, receipt = _complete(FusionVariant.FUSION_OFF)
        self.assertEqual(trace.state, "finalized")
        self.assertEqual(calls, [item.operation_id for item in plan.operation_requirements])
        verified = verify_operation_evidence_receipt(
            receipt, plan.operation_contract(),
            expected_execution_nonce=receipt.execution_nonce)
        self.assertEqual(verified, receipt)
        portable = json.loads(json.dumps(receipt.to_dict()))
        parsed = receipt_from_mapping(portable)
        self.assertEqual(
            verify_operation_evidence_receipt(
                parsed, plan.operation_contract(),
                expected_execution_nonce=receipt.execution_nonce),
            receipt,
        )
        self.assertEqual(
            [(event.accounted_units, event.accounted_bytes) for event in receipt.events],
            [(5, 0), (1, 8), (5, 0), (1, 8), (5, 40), (5, 0), (1, 8)],
        )
        self.assertEqual(receipt.payload_without_digest()["event_evidence_tcb"],
                         OPERATION_EVIDENCE_TCB)
        self.assertFalse(receipt.payload_without_digest()["hardware_introspection_claimed"])

    def test_fused_receipt_counts_compiler_kernel_and_four_scalar_summary(self) -> None:
        plan, trace, _, receipt = _complete(FusionVariant.FUSION_ON)
        verify_operation_evidence_receipt(receipt, plan.operation_contract())
        self.assertEqual(trace.successful_event_counts(), {
            "device_materialization": 0,
            "logical_reduction": 0,
            "compiler_kernel_invocation": 1,
            "host_copy_synchronization": 1,
        })
        self.assertEqual(
            [(event.kind, event.accounted_units, event.accounted_bytes)
             for event in receipt.events],
            [
                ("compiler_kernel_invocation", 5, 0),
                ("host_copy_synchronization", 4, 32),
            ],
        )

    def test_post_action_extent_failure_aborts_trace(self) -> None:
        contract = OperationSequenceContract(
            plan_sha256=_sha("a"),
            mechanism_id="checked_u64_product_sum_downstream_lowering.v1",
            variant="fusion_on",
            declared_value_count=2,
            requirements=(OperationRequirement(
                ordinal=0,
                operation_id="checked_summary.kernel_launch",
                kind=OperationKind.COMPILER_KERNEL_INVOCATION,
                units_per_value=(1 << 64) - 1,
            ),),
        )
        trace = OperationTrace(
            contract,
            execution_nonce="goal5790-post-action-overflow-0001",
            value_count=2,
        )
        side_effects = []
        with self.assertRaisesRegex(OperationEvidenceError, "resolved_units"):
            trace.execute(
                "checked_summary.kernel_launch",
                lambda: side_effects.append("executed"),
            )
        self.assertEqual(side_effects, ["executed"])
        self.assertEqual(trace.state, "aborted")

    def test_forged_event_count_chain_and_receipt_digest_fail_closed(self) -> None:
        plan, _, _, receipt = _complete(FusionVariant.FUSION_ON)
        forged_event = replace(receipt.events[0], accounted_units=999)
        forged = replace(receipt, events=(forged_event, receipt.events[1]))
        with self.assertRaisesRegex(OperationEvidenceError, "event_content"):
            verify_operation_evidence_receipt(forged, plan.operation_contract())

        forged = replace(receipt, event_chain_sha256=_sha("e"))
        with self.assertRaisesRegex(OperationEvidenceError, "event_chain"):
            verify_operation_evidence_receipt(forged, plan.operation_contract())

        forged = replace(receipt, receipt_sha256=_sha("f"))
        with self.assertRaisesRegex(OperationEvidenceError, "receipt_digest"):
            verify_operation_evidence_receipt(forged, plan.operation_contract())

    def test_receipt_replay_nonce_mismatch_fails_closed(self) -> None:
        plan, _, _, receipt = _complete(FusionVariant.FUSION_ON)
        with self.assertRaisesRegex(OperationEvidenceError, "receipt_replay"):
            verify_operation_evidence_receipt(
                receipt, plan.operation_contract(),
                expected_execution_nonce="goal5790-another-worker-0001")

    def test_trace_value_count_must_equal_the_input_bound_plan(self) -> None:
        plan = _plan(FusionVariant.FUSION_ON)
        with self.assertRaisesRegex(OperationEvidenceError, "value_count_binding"):
            OperationTrace(
                plan.operation_contract(), execution_nonce="goal5790-count-0001",
                value_count=plan.value_count + 1)

    def test_mapping_rejects_decorative_or_missing_fields(self) -> None:
        _, _, _, receipt = _complete(FusionVariant.FUSION_ON)
        portable = receipt.to_dict()
        portable["performance_seconds"] = 1.0
        with self.assertRaisesRegex(OperationEvidenceError, "receipt_fields"):
            receipt_from_mapping(portable)
        portable = receipt.to_dict()
        del portable["event_evidence_tcb"]
        with self.assertRaisesRegex(OperationEvidenceError, "receipt_fields"):
            receipt_from_mapping(portable)


if __name__ == "__main__":
    unittest.main()
