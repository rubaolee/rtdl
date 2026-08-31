from __future__ import annotations

import inspect
from pathlib import Path
import unittest

from rtdsl.v4_checked_u64_device_reduction import (
    U64_MAX,
    validate_weighted_reduction_summary,
)
import rtdsl.v4_checked_u64_device_reduction as reduction
import rtdsl.v4_triangle_reduction_device_runtime as triangle_runtime
from scripts import goal5778_home_checked_u64_reduction_validation as home_validation


class Goal5778CheckedU64DeviceReductionTest(unittest.TestCase):
    def test_exact_bound_accepts(self):
        validate_weighted_reduction_summary(
            value_count=8,
            value_upper_bound=11,
            maximum_value=11,
            maximum_weight=7,
            weight_sum=20,
        )
        validate_weighted_reduction_summary(
            value_count=1,
            value_upper_bound=U64_MAX,
            maximum_value=U64_MAX,
            maximum_weight=1,
            weight_sum=1,
        )

    def test_weight_sum_bound_fails_closed(self):
        with self.assertRaisesRegex(OverflowError, "query-weight domain"):
            validate_weighted_reduction_summary(
                value_count=2,
                value_upper_bound=1,
                maximum_value=1,
                maximum_weight=U64_MAX,
                weight_sum=0,
            )

    def test_weighted_value_bound_fails_closed(self):
        with self.assertRaisesRegex(OverflowError, "weighted hit-count"):
            validate_weighted_reduction_summary(
                value_count=2,
                value_upper_bound=2,
                maximum_value=2,
                maximum_weight=1,
                weight_sum=U64_MAX,
            )

    def test_bad_scalar_contract_fails_closed(self):
        for field in (
            "value_count", "value_upper_bound", "maximum_value",
            "maximum_weight", "weight_sum",
        ):
            values = dict(
                value_count=2, value_upper_bound=3, maximum_value=3,
                maximum_weight=4, weight_sum=5)
            values[field] = -1
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_weighted_reduction_summary(**values)

    def test_value_above_declared_bound_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "device values exceed"):
            validate_weighted_reduction_summary(
                value_count=2,
                value_upper_bound=7,
                maximum_value=8,
                maximum_weight=1,
                weight_sum=2,
            )

    def test_helper_is_app_neutral_and_counts_are_not_dataclass_defaults(self):
        source = inspect.getsource(reduction).lower()
        for forbidden in ("triangle", "rt-2a1", "paper", "dataset"):
            self.assertNotIn(forbidden, source)
        self.assertIn("__shared__ unsigned long long", source)
        self.assertIn("maximum_values", source)
        self.assertIn("if (lane == 0)", source)
        self.assertNotIn("device_kernel_launch_count: int = 1", source)
        self.assertNotIn("host_synchronization_count: int = 1", source)
        self.assertIn('"checked_summary.kernel_launch"', source)
        self.assertIn('"checked_summary.summary_copy_sync"', source)
        self.assertIn("operation_counts_event_derived=operation_trace is not none", source)

    def test_triangle_weighted_path_consumes_generic_helper(self):
        execute_source = inspect.getsource(
            triangle_runtime.VerifiedTriangleDeviceColumnCountExecutor.
            execute_segment_unsealed)
        seal_source = inspect.getsource(
            triangle_runtime.UnsealedTriangleSegmentExecution.seal)
        wrapper_source = inspect.getsource(
            triangle_runtime.VerifiedTriangleDeviceColumnCountExecutor.
            execute_segment)
        self.assertIn("checked_u64_weighted_sum_device", execute_source)
        self.assertNotIn("cp.max(ray_weights)", execute_source)
        self.assertNotIn("cp.sum(ray_weights", execute_source)
        self.assertIn(
            "cp.sum(per_ray", execute_source)  # unweighted path remains unchanged
        self.assertNotIn("operation_trace.finalize", execute_source)
        self.assertIn("provisional_sum_trusted_only_after_bounds", seal_source)
        self.assertIn("operation_trace.seal", seal_source)
        self.assertIn("execute_segment_unsealed", wrapper_source)
        self.assertIn(").seal()", wrapper_source)

    def test_real_non_triangle_consumer_is_frozen_rtdbscan_contract(self):
        source = inspect.getsource(home_validation)
        self.assertIn("rtdl.goal5776.rtdbscan_real_scale_input.v1", source)
        self.assertIn("neighbor_counts_u32.npy", source)
        self.assertIn("expected_directed_edge_count", source)
        self.assertIn('"production_route_changed": False', source)
        self.assertIn("checked_u64_weighted_sum_device", source)

    def test_triangle_validation_requires_per_segment_reduction_receipts(self):
        source = (Path(__file__).parents[1] / "scripts" /
                  "goal5778_home_triangle_checked_reduction_validation.py").read_text(
                      encoding="utf-8")
        self.assertIn("checked_reduction_receipts", source)
        self.assertIn("RT-2A1 did not use checked reduction in every segment", source)
        self.assertIn("provisional_sum_trusted_only_after_bounds", source)
        self.assertIn('"registered_performance_result": False', source)


if __name__ == "__main__":
    unittest.main()
