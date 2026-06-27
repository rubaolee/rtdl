from __future__ import annotations

import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4 as v4


class V4Goal4682NextTargetAfterShapePairTest(unittest.TestCase):
    def test_goal4682_closes_shape_pair_route_as_no_promotion(self) -> None:
        decision = v4.v4_goal4682_next_target_after_shape_pair().as_dict()

        self.assertEqual(
            "goal4682_shape_pair_no_promotion_select_contact_witness_design_gate_no_pod",
            decision["status"],
        )
        self.assertEqual(
            "v4_shape_pair_relation_active_count_2d_prepared_left_executor",
            decision["rejected_surface"],
        )
        self.assertIn("V4/V2.14 hot 0.963x", decision["rejected_reason"])
        self.assertFalse(decision["promote_rejected_surface_authorized"])
        self.assertFalse(decision["public_speedup_claim_authorized"])

    def test_goal4682_selects_only_contact_witness_design_audit_gate(self) -> None:
        decision = v4.v4_goal4682_next_target_after_shape_pair().as_dict()

        self.assertEqual("AABB_PAIR_EXACT_WITNESS_DEVICE_COLUMNS_2D", decision["selected_design_target"])
        self.assertIn("design_audit_gate_only", decision["target_class"])
        self.assertIn("not merely rewrap V2.14 bounded collect-k", decision["target_class"])
        self.assertIn("before any implementation or POD run", decision["next_goal"])
        self.assertFalse(decision["implementation_authorized"])
        self.assertFalse(decision["pod_authorized"])
        self.assertFalse(decision["app_identity_kernel_authorized"])

    def test_goal4682_validation_passes(self) -> None:
        validation = v4.validate_v4_goal4682_next_target_after_shape_pair()

        self.assertEqual("passed", validation["status"])
        self.assertEqual((), validation["missing_or_invalid"])
        self.assertFalse(validation["release_authorized"])


if __name__ == "__main__":
    unittest.main()
