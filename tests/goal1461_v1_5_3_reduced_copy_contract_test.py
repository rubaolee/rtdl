import unittest

import rtdsl as rt


class Goal1461V153ReducedCopyContractTest(unittest.TestCase):
    def test_contract_defines_reduced_copy_scope_without_zero_copy_claim(self) -> None:
        contract = rt.validate_v1_5_3_reduced_copy_contract()

        self.assertEqual(
            contract["status"],
            "typed_host_input_buffer_path_and_copy_count_measurement_present",
        )
        self.assertEqual(contract["track"], "python_rtdl")
        self.assertIn("typed_contiguous_host_buffers", contract["scope"])
        self.assertIn("preallocated_result_buffers", contract["scope"])
        self.assertIn("prepared_host_buffer_reuse", contract["scope"])
        self.assertIn("prepared_device_or_staging_buffer_reuse", contract["scope"])

    def test_contract_records_required_and_missing_evidence(self) -> None:
        contract = rt.validate_v1_5_3_reduced_copy_contract()

        self.assertEqual(contract["required_evidence"], rt.V1_5_3_REDUCED_COPY_REQUIRED_EVIDENCE)
        self.assertIn("embree_optix_same_contract_parity_where_claimed", contract["missing_evidence"])
        self.assertIn("external_ai_review_before_public_claims", contract["missing_evidence"])
        self.assertIn("typed_contiguous_host_buffer_path", contract["satisfied_evidence"])
        self.assertIn("preallocated_result_buffer_reuse_path", contract["satisfied_evidence"])
        self.assertIn("copy_count_or_transfer_count_measurement", contract["satisfied_evidence"])

    def test_contract_keeps_public_claims_blocked(self) -> None:
        contract = rt.validate_v1_5_3_reduced_copy_contract()

        for flag in (
            "true_zero_copy_authorized",
            "public_speedup_wording_authorized",
            "whole_app_speedup_claim_authorized",
            "stable_public_primitive_authorized",
            "release_action_authorized",
        ):
            with self.subTest(flag=flag):
                self.assertIs(contract[flag], False)

        for blocked in (
            "true_zero_copy",
            "public_speedup",
            "whole_app_speedup",
            "stable_public_primitive",
            "release_action",
        ):
            with self.subTest(blocked=blocked):
                self.assertIn(blocked, contract["blocked_claims"])

    def test_contract_separates_allowed_and_forbidden_wording(self) -> None:
        contract = rt.validate_v1_5_3_reduced_copy_contract()

        self.assertIn("reduced-copy candidate", contract["allowed_wording"])
        self.assertIn("reduced-transfer candidate", contract["allowed_wording"])
        self.assertIn("true zero-copy", contract["forbidden_wording"])
        self.assertIn("public speedup", contract["forbidden_wording"])
        self.assertIn("does not authorize true zero-copy", contract["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
