from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]


class Goal1418V151CollectKReadinessGateTest(unittest.TestCase):
    def test_readiness_gate_marks_evidence_complete_without_public_promotion(self) -> None:
        gate = rt.validate_v1_5_1_collect_k_bounded_readiness_gate()

        self.assertEqual(gate["status"], "promotion_track_evidence_ready_pending_release_surface_decision")
        self.assertEqual(gate["primitive"], "COLLECT_K_BOUNDED")
        self.assertEqual(gate["track"], "python_rtdl")
        self.assertTrue(gate["app_generic"])
        self.assertEqual(gate["backend_scope"], ("embree", "optix"))
        self.assertEqual(gate["passed_gates"], rt.V1_5_1_COLLECT_K_BOUNDED_READINESS_REQUIRED_GATES)
        self.assertEqual(gate["failed_gates"], ())
        self.assertTrue(gate["external_3_ai_consensus_ready"])

    def test_readiness_gate_preserves_false_authorization_flags(self) -> None:
        gate = rt.validate_v1_5_1_collect_k_bounded_readiness_gate()

        for flag in (
            "stable_promotion_authorized",
            "public_wording_authorized",
            "public_speedup_wording_authorized",
            "zero_copy_wording_authorized",
            "release_tag_action_authorized",
            "whole_app_speedup_claim_authorized",
        ):
            with self.subTest(flag=flag):
                self.assertIs(gate[flag], False)
        self.assertEqual(
            gate["blocked_actions"],
            rt.V1_5_1_COLLECT_K_BOUNDED_READINESS_BLOCKED_ACTIONS,
        )
        self.assertIn("public_collect_k_bounded_promotion", gate["blocked_actions"])

    def test_readiness_gate_evidence_files_exist(self) -> None:
        gate = rt.validate_v1_5_1_collect_k_bounded_readiness_gate()

        self.assertEqual(
            gate["evidence_files"],
            rt.V1_5_1_COLLECT_K_BOUNDED_READINESS_EVIDENCE,
        )
        for _name, relative_path in gate["evidence_files"]:
            with self.subTest(relative_path=relative_path):
                self.assertTrue((ROOT / relative_path).exists())

    def test_readiness_gate_claim_boundary_blocks_overclaiming(self) -> None:
        gate = rt.validate_v1_5_1_collect_k_bounded_readiness_gate()
        boundary = gate["claim_boundary"]

        self.assertIn("evidence gates are satisfied", boundary)
        self.assertIn("does not authorize public primitive promotion", boundary)
        self.assertIn("speedup wording", boundary)
        self.assertIn("zero-copy wording", boundary)
        self.assertIn("whole-app claims", boundary)
        self.assertEqual(
            gate["allowed_next_actions"],
            rt.V1_5_1_COLLECT_K_BOUNDED_READINESS_ALLOWED_NEXT_ACTIONS,
        )


if __name__ == "__main__":
    unittest.main()
