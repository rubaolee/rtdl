from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rtdsl.v4_tier3_spike_decision import V4_GOAL4631_DECISION
from rtdsl.v4_tier3_spike_decision import validate_v4_goal4631_tier3_spike_decision
from rtdsl.v4_tier3_spike_decision import v4_goal4631_tier3_spike_decision


class V4Goal4631Tier3SpikeDecisionTest(unittest.TestCase):
    def test_decision_defers_tier3_support(self) -> None:
        decision = validate_v4_goal4631_tier3_spike_decision()

        self.assertEqual(decision["decision"], V4_GOAL4631_DECISION)
        self.assertFalse(decision["tier3_public_support_authorized"])
        self.assertTrue(decision["tier3_spike_can_continue_in_v4x"])
        self.assertFalse(decision["v4_0_release_can_depend_on_tier3"])

    def test_stage1_is_narrow_evidence_not_protocol_pass(self) -> None:
        decision = v4_goal4631_tier3_spike_decision()

        self.assertTrue(decision["stage1_numba_ptx_generation_attempted"])
        self.assertTrue(decision["stage1_observed_ptx_generated"])
        self.assertFalse(decision["stage1_numba_ptx_generation_protocol_passed"])
        self.assertEqual(1, decision["stage1_observed_attempt_count"])
        self.assertEqual(20, decision["stage1_required_attempt_count"])
        self.assertEqual(4, decision["stage1_required_callback_variant_count"])

    def test_stage2_failure_blocks_correctness_and_overhead(self) -> None:
        decision = v4_goal4631_tier3_spike_decision()

        self.assertTrue(decision["stage2_optix_module_link_attempted"])
        self.assertFalse(decision["stage2_optix_module_link_succeeded"])
        self.assertEqual("optix_module_create", decision["stage2_blocked_stage"])
        self.assertEqual("Invalid input", decision["stage2_optix_error"])
        self.assertIn("No functions with semantic types found", decision["stage2_optix_log_key_phrase"])
        self.assertFalse(decision["stage3_correctness_parity_attempted"])
        self.assertFalse(decision["stage4_overhead_ceiling_attempted"])

    def test_decision_matches_existing_pod_evidence_files(self) -> None:
        ptx_payload = json.loads(
            (ROOT / "tools/_archive/future/v4/evidence/v4_tier3_numba_ptx_probe_2026-06-24.json").read_text(encoding="utf-8")
        )
        link_payload = json.loads(
            (ROOT / "tools/_archive/future/v4/evidence/v4_tier3_optix_module_link_probe_2026-06-24.json").read_text(encoding="utf-8")
        )

        self.assertTrue(ptx_payload["ptx_generated"])
        self.assertFalse(ptx_payload["optix_module_link_attempted"])
        self.assertTrue(link_payload["ptx_generated"])
        self.assertTrue(link_payload["optix_module_link_attempted"])
        self.assertFalse(link_payload["optix_module_link_succeeded"])
        self.assertEqual("blocked", link_payload["status"])
        self.assertEqual("optix_module_create", link_payload["blocked_stage"])
        self.assertIn("No functions with semantic types found", link_payload["module_probe"]["stdout"])

    def test_decision_preserves_non_authorization_flags(self) -> None:
        decision = v4_goal4631_tier3_spike_decision()

        for flag in (
            "release_claim_authorized",
            "broad_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "measured_catalog_claim_authorized",
            "true_zero_copy_claim_authorized",
            "tier3_callback_claim_authorized",
            "raw_optix_callback_claim_authorized",
            "cupy_performance_claim_authorized",
            "c_abi_or_embedding_claim_authorized",
            "app_specific_native_kernel_authorized",
        ):
            self.assertFalse(decision[flag])


if __name__ == "__main__":
    unittest.main()

