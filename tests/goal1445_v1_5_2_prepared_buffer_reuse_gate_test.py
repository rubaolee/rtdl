import unittest

import rtdsl as rt


class Goal1445V152PreparedBufferReuseGateTest(unittest.TestCase):
    def test_gate_records_required_evidence_and_current_blocked_status(self) -> None:
        gate = rt.validate_v1_5_2_prepared_buffer_reuse_gate()

        self.assertEqual(gate["status"], "blocked_pending_external_review")
        self.assertEqual(gate["primitive"], "COLLECT_K_BOUNDED")
        self.assertIn("python_reference_prepared_descriptor_envelope", gate["current_envelopes"])
        self.assertIn("native_generic_symbol_prepared_descriptor_envelope", gate["current_envelopes"])
        self.assertIn("native_abi_accepts_prepared_output_buffer_pointer", gate["satisfied_evidence"])
        self.assertIn("python_wrapper_passes_prepared_output_buffer_pointer", gate["satisfied_evidence"])
        self.assertIn("host_reuse_or_device_reuse_measured", gate["satisfied_evidence"])
        self.assertIn("overflow_fail_closed_with_prepared_buffer", gate["satisfied_evidence"])
        self.assertIn("embree_optix_same_contract_parity", gate["satisfied_evidence"])
        self.assertIn("host_reuse_or_device_reuse_measured", gate["required_evidence"])
        self.assertIn("external_ai_review", gate["missing_evidence"])
        self.assertNotIn("python_wrapper_passes_prepared_output_buffer_pointer", gate["missing_evidence"])
        self.assertNotIn("host_reuse_or_device_reuse_measured", gate["missing_evidence"])
        self.assertNotIn("overflow_fail_closed_with_prepared_buffer", gate["missing_evidence"])
        self.assertNotIn("embree_optix_same_contract_parity", gate["missing_evidence"])

    def test_gate_keeps_all_public_claim_flags_closed(self) -> None:
        gate = rt.validate_v1_5_2_prepared_buffer_reuse_gate()

        for flag in (
            "prepared_buffer_reuse_proven",
            "true_zero_copy_authorized",
            "public_speedup_wording_authorized",
            "whole_app_speedup_claim_authorized",
            "stable_public_primitive_authorized",
            "release_action_authorized",
        ):
            with self.subTest(flag=flag):
                self.assertIs(gate[flag], False)
        self.assertIn("prepared_buffer_reuse_proven", gate["blocked_claims"])
        self.assertIn("true_zero_copy", gate["blocked_claims"])
        self.assertIn("public_speedup", gate["blocked_claims"])

    def test_gate_boundary_names_metadata_and_ctypes_wrapper_only(self) -> None:
        gate = rt.validate_v1_5_2_prepared_buffer_reuse_gate()

        self.assertIn("source-level native ABI pointer shape", gate["claim_boundary"])
        self.assertIn("Python wrapper host ctypes output pointer plumbing", gate["claim_boundary"])
        self.assertIn("host buffer reuse measurement", gate["claim_boundary"])
        self.assertIn("external claim review", gate["claim_boundary"])
        self.assertIn("true zero-copy", gate["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
