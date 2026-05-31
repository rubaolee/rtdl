from __future__ import annotations

import unittest

import rtdsl as rt


class Goal2748TritonGroupIdDeviceErrorFlagTest(unittest.TestCase):
    def test_descriptor_exposes_device_flag_without_zero_copy_claim(self) -> None:
        descriptor = rt.describe_triton_group_id_bounds_device_flag_i64()
        routed_descriptor = rt.describe_triton_partner_continuation(
            rt.TRITON_GROUP_ID_BOUNDS_DEVICE_FLAG_I64_OPERATION
        )
        validation = descriptor["group_id_bounds_validation"]

        self.assertEqual(descriptor["operation"], "group_id_bounds_device_flag_i64")
        self.assertEqual(routed_descriptor["operation"], descriptor["operation"])
        self.assertEqual(validation["mode"], "triton_device_error_flag_no_host_read")
        self.assertFalse(validation["uses_host_scalar_sync"])
        self.assertTrue(validation["device_error_flag_available"])
        self.assertTrue(validation["host_scalar_sync_required_for_python_exception"])
        self.assertFalse(validation["true_zero_copy_claim_authorized"])
        self.assertFalse(descriptor["promoted_performance_path"])

    def test_default_triton_continuation_descriptors_keep_strict_host_exception_boundary(self) -> None:
        descriptor = rt.describe_triton_partner_continuation(rt.TRITON_SEGMENTED_COUNT_I64_OPERATION)
        validation = descriptor["group_id_bounds_validation"]

        self.assertEqual(validation["mode"], "torch_cuda_precheck_host_scalar_sync")
        self.assertTrue(validation["uses_host_scalar_sync"])
        self.assertTrue(validation["device_error_flag_available"])
        self.assertEqual(validation["device_error_flag_mode"], "triton_device_error_flag_no_host_read")
        self.assertFalse(validation["device_error_flag_used_by_default"])
        self.assertFalse(validation["true_zero_copy_claim_authorized"])

    @unittest.skipUnless(rt.triton_partner_available(), "requires Triton and CUDA")
    def test_device_flag_counts_invalid_group_ids_on_cuda(self) -> None:
        import torch

        group_ids = torch.tensor([0, -1, 2, 3, 1], dtype=torch.int64, device="cuda")
        result = rt.run_triton_group_id_bounds_device_flag_i64(group_ids, group_count=3)

        self.assertEqual(int(result["outputs"]["invalid_count"].item()), 2)
        self.assertEqual(result["group_id_bounds_validation"]["mode"], "triton_device_error_flag_no_host_read")
        self.assertFalse(result["group_id_bounds_validation"]["uses_host_scalar_sync"])
        self.assertFalse(result["rt_core_speedup_claim_authorized"])
        self.assertFalse(result["promoted_performance_path"])

    @unittest.skipUnless(rt.triton_partner_available(), "requires Triton and CUDA")
    def test_device_flag_host_raise_mode_preserves_fail_closed_exception(self) -> None:
        import torch

        valid_group_ids = torch.tensor([0, 1, 1, 2], dtype=torch.int64, device="cuda")
        ok = rt.run_triton_segmented_count_i64(
            valid_group_ids,
            group_count=3,
            group_id_bounds_validation_mode=rt.TRITON_GROUP_ID_BOUNDS_DEVICE_FLAG_HOST_RAISE_MODE,
        )
        self.assertEqual(ok["group_id_bounds_validation"]["mode"], "triton_device_error_flag_host_scalar_raise")
        self.assertEqual(ok["outputs"]["counts"].cpu().tolist(), [1, 2, 1])

        invalid_group_ids = torch.tensor([0, 3], dtype=torch.int64, device="cuda")
        with self.assertRaisesRegex(ValueError, r"device_error_flag invalid_count=1"):
            rt.run_triton_segmented_count_i64(
                invalid_group_ids,
                group_count=3,
                group_id_bounds_validation_mode=rt.TRITON_GROUP_ID_BOUNDS_DEVICE_FLAG_HOST_RAISE_MODE,
            )


if __name__ == "__main__":
    unittest.main()
