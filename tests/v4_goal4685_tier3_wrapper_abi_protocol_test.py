from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4_maintainer as v4


class V4Goal4685Tier3WrapperAbiProtocolTest(unittest.TestCase):
    def test_goal4685_protocol_names_real_wrapper_stage_not_bare_ptx(self) -> None:
        protocol = v4.v4_goal4685_tier3_wrapper_abi_protocol().as_dict()

        self.assertEqual(
            "goal4685_tier3_wrapper_direct_callable_abi_protocol_gate_no_pod",
            protocol["status"],
        )
        stage_names = {stage["stage"] for stage in protocol["required_stages"]}
        self.assertIn("stage2_semantic_optix_wrapper_or_direct_callable", stage_names)
        self.assertIn("semantic OptiX", str(protocol["required_stages"]))
        self.assertIn("bare Numba helper PTX", " ".join(protocol["forbidden_paths"]))
        self.assertIn("Goal4686", protocol["next_goal"])

    def test_goal4685_preserves_planner_boundary_for_scalar_and_action_callbacks(self) -> None:
        validation = v4.validate_v4_goal4685_tier3_wrapper_abi_protocol()

        self.assertEqual("passed", validation["status"])
        self.assertEqual("tier3_spike_only_not_v4_0_release_surface", validation["scalar_plan_status"])
        self.assertEqual("rejected_action_shaped_callback_deferred", validation["action_plan_status"])

    def test_goal4685_does_not_authorize_pod_implementation_or_support(self) -> None:
        protocol = v4.v4_goal4685_tier3_wrapper_abi_protocol().as_dict()

        self.assertTrue(protocol["local_protocol_gate_authorized"])
        self.assertFalse(protocol["pod_authorized"])
        self.assertFalse(protocol["implementation_authorized"])
        self.assertFalse(protocol["tier3_public_support_authorized"])
        self.assertFalse(protocol["raw_optix_callback_authorized"])
        self.assertFalse(protocol["release_authorized"])
        self.assertFalse(protocol["public_speedup_claim_authorized"])
        self.assertFalse(protocol["whole_app_speedup_claim_authorized"])
        self.assertFalse(protocol["app_identity_kernel_authorized"])

    def test_goal4685_all_required_stages_are_present(self) -> None:
        protocol = v4.v4_goal4685_tier3_wrapper_abi_protocol().as_dict()
        stages = {stage["stage"]: stage for stage in protocol["required_stages"]}

        self.assertIn("stage0_planner_boundary", stages)
        self.assertIn("stage1_ptx_generation_reliability", stages)
        self.assertIn("stage2_semantic_optix_wrapper_or_direct_callable", stages)
        self.assertIn("stage3_correctness_parity", stages)
        self.assertIn("stage4_overhead_ceiling", stages)
        self.assertIn(">=95%", stages["stage1_ptx_generation_reliability"]["pass_condition"])
        self.assertIn("<=1.50x", stages["stage4_overhead_ceiling"]["required_evidence"][-2])


if __name__ == "__main__":
    unittest.main()
