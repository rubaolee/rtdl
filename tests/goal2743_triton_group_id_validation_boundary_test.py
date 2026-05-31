from __future__ import annotations

import unittest

import rtdsl as rt


class Goal2743TritonGroupIdValidationBoundaryTest(unittest.TestCase):
    def test_triton_descriptors_expose_host_scalar_sync_validation_boundary(self) -> None:
        for operation in (
            rt.TRITON_SEGMENTED_COUNT_I64_OPERATION,
            rt.TRITON_SEGMENTED_SUM_F64_OPERATION,
            rt.TRITON_SEGMENTED_MIN_F64_OPERATION,
            rt.TRITON_SEGMENTED_MAX_F64_OPERATION,
            rt.TRITON_GROUPED_ARGMIN_F64_OPERATION,
            rt.TRITON_BOUNDED_COLLECT_FINALIZE_I64_OPERATION,
        ):
            descriptor = rt.describe_triton_partner_continuation(operation)
            validation = descriptor["group_id_bounds_validation"]

            self.assertEqual(validation["mode"], "torch_cuda_precheck_host_scalar_sync")
            self.assertTrue(validation["checked_before_kernel_launch"])
            self.assertTrue(validation["uses_host_scalar_sync"])
            self.assertFalse(validation["device_error_flag_available"])
            self.assertFalse(validation["true_zero_copy_claim_authorized"])

    def test_compact_mask_descriptor_marks_group_id_validation_not_applicable(self) -> None:
        descriptor = rt.describe_triton_partner_continuation(rt.TRITON_COMPACT_MASK_I64_OPERATION)
        validation = descriptor["group_id_bounds_validation"]

        self.assertEqual(validation["mode"], "not_applicable_no_group_ids")
        self.assertFalse(validation["checked_before_kernel_launch"])
        self.assertFalse(validation["uses_host_scalar_sync"])
        self.assertFalse(validation["device_error_flag_available"])

    def test_runtime_result_helper_source_records_same_boundary(self) -> None:
        import inspect
        from rtdsl import triton_partner_continuation

        source = inspect.getsource(triton_partner_continuation)

        self.assertIn("TRITON_GROUP_ID_BOUNDS_VALIDATION_MODE", source)
        self.assertIn("torch_cuda_precheck_host_scalar_sync", source)
        self.assertIn("device_error_flag_available", source)
        self.assertIn("true_zero_copy_claim_authorized", source)


if __name__ == "__main__":
    unittest.main()
