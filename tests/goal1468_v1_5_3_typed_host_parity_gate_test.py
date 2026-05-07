from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]


class Goal1468V153TypedHostParityGateTest(unittest.TestCase):
    def test_parity_gate_records_required_pod_parity_accepted(self) -> None:
        gate = rt.validate_v1_5_3_typed_host_buffer_parity_gate()

        self.assertEqual(gate["status"], "accepted_required_embree_optix_pod_parity")
        self.assertEqual(gate["required_backends"], ("embree", "optix"))
        self.assertTrue(gate["backend_parity_where_claimed_satisfied"])
        self.assertTrue(gate["required_pod_parity_accepted"])
        self.assertFalse(gate["pod_run_required"])
        self.assertTrue(gate["accepted"])
        self.assertEqual(gate["contract_missing_evidence"], ())

    def test_parity_gate_required_evidence_exists(self) -> None:
        gate = rt.validate_v1_5_3_typed_host_buffer_parity_gate()

        for relative_path in gate["required_evidence"]:
            with self.subTest(relative_path=relative_path):
                self.assertTrue((ROOT / relative_path).exists())

    def test_parity_gate_keeps_claims_blocked(self) -> None:
        gate = rt.validate_v1_5_3_typed_host_buffer_parity_gate()

        for flag in (
            "true_zero_copy_authorized",
            "public_speedup_wording_authorized",
            "whole_app_speedup_claim_authorized",
            "stable_public_primitive_authorized",
            "release_action_authorized",
        ):
            with self.subTest(flag=flag):
                self.assertIs(gate[flag], False)
        self.assertIn("accepted required Embree+OptiX pod evidence", gate["claim_boundary"])
        self.assertIn("does not authorize true zero-copy", gate["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
