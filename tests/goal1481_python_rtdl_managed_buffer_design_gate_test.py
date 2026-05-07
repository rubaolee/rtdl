import unittest

import rtdsl as rt


class Goal1481PythonRtdlManagedBufferDesignGateTest(unittest.TestCase):
    def test_gate_starts_rtdl_owned_python_rtdl_buffer_lane(self) -> None:
        gate = rt.validate_v1_5_4_python_rtdl_managed_buffer_design_gate()

        self.assertEqual(
            gate["status"],
            "ready_to_design_rtdl_owned_managed_buffers_claims_blocked",
        )
        self.assertEqual(gate["track"], "python_rtdl")
        self.assertEqual(gate["memory_owner"], "rtdl")
        self.assertTrue(gate["not_partner_owned"])
        self.assertIn("prepared_host", gate["buffer_kinds"])
        self.assertIn("rtdl_device_resident", gate["buffer_kinds"])
        self.assertIn("rtdl_managed_unified", gate["buffer_kinds"])

    def test_gate_requires_metadata_for_lifetime_residency_and_transfer_counts(self) -> None:
        gate = rt.validate_v1_5_4_python_rtdl_managed_buffer_design_gate()

        self.assertEqual(gate["required_metadata"], rt.V1_5_4_PYTHON_RTDL_MANAGED_BUFFER_REQUIRED_METADATA)
        for metadata in (
            "lifetime",
            "copy_boundary",
            "residency_state",
            "transfer_count_state",
        ):
            with self.subTest(metadata=metadata):
                self.assertIn(metadata, gate["required_metadata"])

    def test_gate_does_not_need_pod_until_real_device_allocation(self) -> None:
        gate = rt.validate_v1_5_4_python_rtdl_managed_buffer_design_gate()

        self.assertFalse(gate["requires_pod_now"])
        self.assertIn("device_resident_buffer_allocation_validation", gate["pod_required_for"])
        self.assertIn("transfer_count_measurement_on_real_nvidia", gate["pod_required_for"])

    def test_gate_keeps_claims_blocked_and_separates_partner_track(self) -> None:
        gate = rt.validate_v1_5_4_python_rtdl_managed_buffer_design_gate()

        for flag in (
            "host_data_zero_copy_default",
            "managed_buffer_zero_copy_authorized",
            "true_zero_copy_authorized",
            "public_speedup_wording_authorized",
            "whole_app_speedup_claim_authorized",
            "stable_public_primitive_authorized",
            "partner_tensor_handoff_authorized",
            "release_action_authorized",
        ):
            with self.subTest(flag=flag):
                self.assertIs(gate[flag], False)
        self.assertIn("does not cover partner-owned GPU memory", gate["claim_boundary"])
        self.assertIn("Ordinary Python input data does not become zero-copy by default", gate["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
