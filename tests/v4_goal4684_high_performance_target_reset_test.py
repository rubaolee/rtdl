from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4_maintainer as v4


class V4Goal4684HighPerformanceTargetResetTest(unittest.TestCase):
    def test_goal4684_selects_tier3_wrapper_spike_not_existing_app_route(self) -> None:
        reset = v4.v4_goal4684_high_performance_target_reset().as_dict()

        self.assertEqual(
            "goal4684_no_clean_existing_tier2_app_target_select_tier3_wrapper_spike_protocol",
            reset["status"],
        )
        self.assertEqual("TIER3_WRAPPER_DIRECT_CALLABLE_ABI_SPIKE", reset["selected_next_track"])
        self.assertIn("No clean existing Tier-2/app target remains", reset["decision"])
        self.assertIn("Goal4685", reset["next_goal"])
        self.assertIn("bare-PTX optixModuleCreate probe", reset["next_goal"])

    def test_goal4684_records_why_prior_targets_are_not_enough(self) -> None:
        reset = v4.v4_goal4684_high_performance_target_reset().as_dict()
        rows = {row["target"]: row for row in reset["candidate_dispositions"]}

        self.assertIn("existing benchmark app route selection", rows)
        self.assertIn("V2.14 already had", rows["existing benchmark app route selection"]["reason"])
        self.assertEqual("no_go", rows["contact/witness device columns"]["disposition"])
        self.assertIn("Goal4683", rows["contact/witness device columns"]["reason"])
        self.assertEqual("deferred", rows["ranked fixed-radius summary / RTNN"]["disposition"])
        self.assertEqual(
            "selected_as_spike_only_next_track",
            rows["Tier-3 wrapper/direct-callable ABI"]["disposition"],
        )

    def test_goal4684_preserves_all_non_authorizations(self) -> None:
        reset = v4.v4_goal4684_high_performance_target_reset().as_dict()

        self.assertFalse(reset["formal_high_performance_release_authorized"])
        self.assertFalse(reset["pod_authorized"])
        self.assertFalse(reset["implementation_authorized"])
        self.assertFalse(reset["tier3_public_support_authorized"])
        self.assertFalse(reset["raw_optix_callback_authorized"])
        self.assertFalse(reset["public_speedup_claim_authorized"])
        self.assertFalse(reset["whole_app_speedup_claim_authorized"])
        self.assertFalse(reset["app_identity_kernel_authorized"])

    def test_goal4684_validation_passes(self) -> None:
        validation = v4.validate_v4_goal4684_high_performance_target_reset()

        self.assertEqual("passed", validation["status"])
        self.assertEqual((), validation["missing_or_invalid"])
        self.assertFalse(validation["release_authorized"])


if __name__ == "__main__":
    unittest.main()
