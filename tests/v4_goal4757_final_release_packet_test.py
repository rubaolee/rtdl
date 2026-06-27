from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.v4_goal4757_final_release_packet import V4_GOAL4757_DECISION
from rtdsl.v4_goal4757_final_release_packet import validate_v4_goal4757_final_release_packet


class V4Goal4757FinalReleasePacketTest(unittest.TestCase):
    def test_goal4757_packet_is_machine_validated_but_not_authorized(self) -> None:
        decision = validate_v4_goal4757_final_release_packet(ROOT)

        self.assertEqual(V4_GOAL4757_DECISION, decision["decision"])
        self.assertEqual("ready_for_external_review_not_public_tag_authorized", decision["status"])
        self.assertEqual(
            "complete_rt_core_app_matrix__bounded_material_wins__no_broad_all_app_speedup_claim",
            decision["current_decision_label"],
        )
        self.assertFalse(decision["release_authorized"])
        self.assertFalse(decision["public_tag_authorized"])
        self.assertTrue(decision["external_review_debt_open"])

    def test_goal4757_matrix_facts_match_goal4756(self) -> None:
        decision = validate_v4_goal4757_final_release_packet(ROOT)

        self.assertEqual(10, decision["app_count"])
        self.assertEqual(30, decision["matrix_row_count"])
        self.assertFalse(decision["embree_primary_denominator_used"])
        self.assertEqual((), decision["regression_apps"])
        self.assertEqual({"triangle_counting", "barnes_hut"}, set(decision["material_candidate_apps"]))
        self.assertAlmostEqual(2.100691970706828, decision["v4_over_v2_14_hot_geomean"])

    def test_goal4757_forbidden_claims_match_current_superset_boundary(self) -> None:
        decision = validate_v4_goal4757_final_release_packet(ROOT)

        self.assertIn("Barnes-Hut new V4-over-V3 speedup", decision["forbidden_claims"])
        self.assertIn("Spatial RayJoin speedup", decision["forbidden_claims"])
        self.assertNotIn("Barnes-Hut covered by V4.0", decision["forbidden_claims"])
        self.assertNotIn("Spatial RayJoin covered by V4.0", decision["forbidden_claims"])
        self.assertFalse(decision["barnes_hut_new_v4_over_v3_speedup_authorized"])
        self.assertFalse(decision["spatial_rayjoin_speedup_authorized"])


if __name__ == "__main__":
    unittest.main()
