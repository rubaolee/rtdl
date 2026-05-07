import unittest

import rtdsl as rt


class Goal1445V152PreparedBufferReuseGateTest(unittest.TestCase):
    def test_gate_records_required_evidence_and_current_blocked_status(self) -> None:
        gate = rt.validate_v1_5_2_prepared_buffer_reuse_gate()

        self.assertEqual(gate["status"], "blocked_pending_backend_reuse_evidence")
        self.assertEqual(gate["primitive"], "COLLECT_K_BOUNDED")
        self.assertIn("python_reference_prepared_descriptor_envelope", gate["current_envelopes"])
        self.assertIn("native_generic_symbol_prepared_descriptor_envelope", gate["current_envelopes"])
        self.assertIn("native_abi_accepts_prepared_output_buffer_pointer", gate["required_evidence"])
        self.assertIn("python_wrapper_passes_prepared_output_buffer_pointer", gate["required_evidence"])
        self.assertIn("host_reuse_or_device_reuse_measured", gate["required_evidence"])
        self.assertEqual(gate["missing_evidence"], gate["required_evidence"])

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

        self.assertIn("metadata and ctypes-wrapper surfaces only", gate["claim_boundary"])
        self.assertIn("externally reviewed", gate["claim_boundary"])
        self.assertIn("true zero-copy", gate["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
