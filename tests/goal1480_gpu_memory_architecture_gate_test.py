from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]


class Goal1480GpuMemoryArchitectureGateTest(unittest.TestCase):
    def test_gate_records_separate_memory_ownership_tracks(self) -> None:
        gate = rt.validate_v1_5_4_gpu_memory_architecture_consensus_gate()

        self.assertEqual(
            gate["status"],
            "accepted_python_rtdl_vs_partner_rtdl_memory_boundary",
        )
        self.assertEqual(gate["python_rtdl_memory_owner"], "rtdl")
        self.assertEqual(gate["python_partner_rtdl_memory_owner"], "partner_runtime")
        self.assertFalse(gate["python_rtdl_zero_copy_default"])
        self.assertTrue(gate["python_partner_rtdl_zero_copy_plausible_with_evidence"])

    def test_gate_required_evidence_exists(self) -> None:
        gate = rt.validate_v1_5_4_gpu_memory_architecture_consensus_gate()

        for relative_path in gate["required_evidence"]:
            with self.subTest(relative_path=relative_path):
                self.assertTrue((ROOT / relative_path).exists())

    def test_gate_keeps_claims_blocked(self) -> None:
        gate = rt.validate_v1_5_4_gpu_memory_architecture_consensus_gate()

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
        self.assertIn("arbitrary Python data is not zero-copy", gate["claim_boundary"])
        self.assertIn("partner-owned GPU buffers", gate["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
