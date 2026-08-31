from __future__ import annotations

from contextlib import ExitStack
from types import SimpleNamespace
from unittest import mock
import sys
import unittest

from rtdsl.v4_checked_u64_device_reduction import (
    U64_MAX,
    checked_u64_downstream_operation_sha256,
    checked_u64_weighted_sum_device,
    checked_u64_weighted_sum_unfused_device,
)
from rtdsl.v4_fusion_ablation import FusionVariant
from rtdsl.v4_operation_evidence import (
    OperationTrace,
    verify_operation_evidence_receipt,
)

from tests.goal5790_operation_evidence_test import _plan, _sha


class _U64(int):
    pass


class _HostList(list):
    def tolist(self):
        return list(self)


class _Array:
    def __init__(self, values):
        self.values = [int(value) for value in values]
        self.dtype = _U64
        self.ndim = 1
        self.flags = SimpleNamespace(c_contiguous=True)
        self.device = SimpleNamespace(id=0)
        self.data = SimpleNamespace(ptr=id(self))

    @property
    def size(self):
        return len(self.values)

    def __mul__(self, other):
        return _Array([left * right for left, right in zip(
            self.values, other.values, strict=True)])


class _Summary(_Array):
    def get(self):
        return _HostList(self.values)


class _FakeCupy:
    ndarray = _Array
    uint64 = _U64
    cuda = SimpleNamespace(Device=lambda: SimpleNamespace(id=0))

    @staticmethod
    def max(values):
        return SimpleNamespace(item=lambda: max(values.values))

    @staticmethod
    def sum(values, dtype=None):
        return SimpleNamespace(item=lambda: sum(values.values))

    @staticmethod
    def zeros(count, dtype=None):
        return _Summary([0] * int(count))


def _trace(variant: FusionVariant):
    plan = _plan(variant)
    return plan, OperationTrace(
        plan.operation_contract(),
        execution_nonce=f"goal5790-runtime-{variant.value}-0001",
        value_count=plan.value_count,
    )


class Goal5790TriangleRuntimeIntegrationTest(unittest.TestCase):
    def test_target_local_downstream_recipes_are_distinct_and_stable(self) -> None:
        target = _sha("e")
        on = checked_u64_downstream_operation_sha256(
            "fusion_on", target_identity_sha256=target, cupy_version="14.0.1")
        off = checked_u64_downstream_operation_sha256(
            "fusion_off", target_identity_sha256=target, cupy_version="14.0.1")
        self.assertNotEqual(on, off)
        self.assertEqual(
            on,
            checked_u64_downstream_operation_sha256(
                "fusion_on", target_identity_sha256=target,
                cupy_version="14.0.1"),
        )
        self.assertNotEqual(
            on,
            checked_u64_downstream_operation_sha256(
                "fusion_on", target_identity_sha256=_sha("f"),
                cupy_version="14.0.1"),
        )

    def test_unfused_reference_executes_exact_seven_event_graph(self) -> None:
        plan, trace = _trace(FusionVariant.FUSION_OFF)
        values = _Array([1, 3, 0, 2, 4])
        weights = _Array([2, 1, 5, 3, 2])
        with mock.patch.dict(sys.modules, {"cupy": _FakeCupy}):
            result = checked_u64_weighted_sum_unfused_device(
                values, weights, value_upper_bound=4,
                operation_trace=trace)
        self.assertEqual(result.value, 19)
        self.assertEqual(result.logical_reduction_count, 3)
        self.assertEqual(result.device_materialization_count, 1)
        self.assertEqual(result.host_synchronization_count, 3)
        self.assertEqual(result.device_kernel_launch_count, 0)
        self.assertTrue(result.operation_counts_event_derived)
        self.assertFalse(result.maximum_value_is_device_observed)
        receipt = trace.finalize(
            output_sha256=_sha("a"), traversal_receipt_sha256=_sha("b"))
        verify_operation_evidence_receipt(receipt, plan.operation_contract())
        self.assertEqual(len(receipt.events), 7)

    def test_unfused_overflow_aborts_and_cannot_emit_receipt(self) -> None:
        _plan_value, trace = _trace(FusionVariant.FUSION_OFF)
        values = _Array([1, 1, 1, 1, 1])
        weights = _Array([U64_MAX, 0, 0, 0, 0])
        with mock.patch.dict(sys.modules, {"cupy": _FakeCupy}):
            with self.assertRaisesRegex(OverflowError, "query-weight"):
                checked_u64_weighted_sum_unfused_device(
                    values, weights, value_upper_bound=1,
                    operation_trace=trace)
        self.assertEqual(trace.state, "aborted")

    def test_fused_reference_records_kernel_only_after_launch_returns(self) -> None:
        plan, trace = _trace(FusionVariant.FUSION_ON)
        values = _Array([1, 3, 0, 2, 4])
        weights = _Array([2, 1, 5, 3, 2])

        def kernel_factory():
            def launch(_grid, _block, arguments):
                device_values, device_weights, _count, summary = arguments
                summary.values[:] = [
                    max(device_values.values),
                    max(device_weights.values),
                    sum(device_weights.values),
                    sum(left * right for left, right in zip(
                        device_values.values, device_weights.values, strict=True)),
                ]
            return launch

        module = "rtdsl.v4_checked_u64_device_reduction._weighted_reduction_kernel"
        with ExitStack() as stack:
            stack.enter_context(mock.patch.dict(sys.modules, {"cupy": _FakeCupy}))
            stack.enter_context(mock.patch(module, side_effect=kernel_factory))
            result = checked_u64_weighted_sum_device(
                values, weights, value_upper_bound=4,
                operation_trace=trace)
        self.assertEqual(result.value, 19)
        self.assertEqual(result.device_kernel_launch_count, 1)
        self.assertEqual(result.host_synchronization_count, 1)
        self.assertEqual(result.logical_reduction_count, 0)
        self.assertEqual(result.device_materialization_count, 0)
        self.assertTrue(result.operation_counts_event_derived)
        self.assertTrue(result.maximum_value_is_device_observed)
        receipt = trace.finalize(
            output_sha256=_sha("c"), traversal_receipt_sha256=_sha("d"))
        verify_operation_evidence_receipt(receipt, plan.operation_contract())
        self.assertEqual(len(receipt.events), 2)


if __name__ == "__main__":
    unittest.main()
