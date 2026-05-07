import unittest

import rtdsl as rt


class Goal1476V154DeviceZeroCopyEntryGateTest(unittest.TestCase):
    def test_entry_gate_is_ready_for_design_only(self) -> None:
        gate = rt.validate_v1_5_4_device_zero_copy_entry_gate()

        self.assertEqual(
            gate["status"],
            "ready_to_start_separate_device_zero_copy_design_claims_blocked",
        )
        self.assertEqual(gate["track"], "python_rtdl")
        self.assertTrue(gate["prior_checkpoint_accepted"])
        self.assertTrue(gate["ready_to_start_design"])
        self.assertFalse(gate["ready_to_claim_true_zero_copy"])
        self.assertFalse(gate["ready_to_claim_public_speedup"])
        self.assertFalse(gate["ready_to_release"])

    def test_entry_gate_separates_host_reduced_copy_from_true_zero_copy(self) -> None:
        gate = rt.validate_v1_5_4_device_zero_copy_entry_gate()

        self.assertIn("separate_device_resident_or_shareable_memory_path", gate["scope"])
        self.assertIn("explicit_host_reduced_copy_vs_device_zero_copy_boundary", gate["scope"])
        self.assertIn(
            "measured_gpu_resident_or_externally_shareable_device_memory_path",
            gate["required_future_evidence"],
        )
        self.assertIn(
            "host reduced-copy evidence is not true zero-copy evidence",
            gate["claim_boundary"],
        )

    def test_entry_gate_keeps_all_public_claims_blocked(self) -> None:
        gate = rt.validate_v1_5_4_device_zero_copy_entry_gate()

        for blocked in (
            "true_zero_copy",
            "public_speedup",
            "whole_app_speedup",
            "stable_public_primitive",
            "partner_tensor_handoff",
            "release_action",
        ):
            with self.subTest(blocked=blocked):
                self.assertIn(blocked, gate["blocked_claims"])
        for flag in (
            "true_zero_copy_authorized",
            "public_speedup_wording_authorized",
            "whole_app_speedup_claim_authorized",
            "stable_public_primitive_authorized",
            "partner_tensor_handoff_authorized",
            "release_action_authorized",
        ):
            with self.subTest(flag=flag):
                self.assertIs(gate[flag], False)

    def test_entry_gate_defers_pod_until_real_device_path_exists(self) -> None:
        gate = rt.validate_v1_5_4_device_zero_copy_entry_gate()

        self.assertFalse(gate["requires_pod_now"])
        self.assertIn("real_nvidia_device_path_validation", gate["pod_required_for"])
        self.assertIn("device_memory_transfer_or_residency_measurement", gate["pod_required_for"])


if __name__ == "__main__":
    unittest.main()
