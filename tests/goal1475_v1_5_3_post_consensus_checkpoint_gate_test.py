from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]


class Goal1475V153PostConsensusCheckpointGateTest(unittest.TestCase):
    def test_gate_accepts_internal_evidence_checkpoint_only(self) -> None:
        gate = rt.validate_v1_5_3_post_consensus_checkpoint_gate()

        self.assertEqual(gate["status"], "accepted_internal_evidence_checkpoint_claims_blocked")
        self.assertTrue(gate["internal_evidence_checkpoint_accepted"])
        self.assertTrue(gate["same_contract_embree_optix_parity_accepted"])
        self.assertTrue(gate["diagnostic_typed_host_reuse_data_accepted"])
        self.assertTrue(gate["external_review_consensus_accepted"])
        self.assertIn(
            "typed_host_input_plus_prepared_host_output_same_contract_parity",
            gate["closed_items"],
        )
        self.assertIn(
            "diagnostic_typed_host_reuse_materialization_count_evidence",
            gate["closed_items"],
        )

    def test_gate_required_evidence_exists(self) -> None:
        gate = rt.validate_v1_5_3_post_consensus_checkpoint_gate()

        self.assertEqual(gate["required_evidence"], rt.V1_5_3_POST_CONSENSUS_REQUIRED_EVIDENCE)
        for relative_path in gate["required_evidence"]:
            with self.subTest(relative_path=relative_path):
                self.assertTrue((ROOT / relative_path).exists())

    def test_gate_keeps_public_and_release_claims_blocked(self) -> None:
        gate = rt.validate_v1_5_3_post_consensus_checkpoint_gate()

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
        for blocked in (
            "true_zero_copy_claim",
            "public_speedup_wording",
            "whole_app_speedup_claim",
            "stable_public_primitive_promotion",
            "partner_tensor_handoff_claim",
            "release_action",
        ):
            with self.subTest(blocked=blocked):
                self.assertIn(blocked, gate["still_blocked_items"])
        self.assertIn("does not authorize true zero-copy", gate["claim_boundary"])
        self.assertIn("partner tensor handoff", gate["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
