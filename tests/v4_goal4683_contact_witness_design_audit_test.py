from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4 as v4


class V4Goal4683ContactWitnessDesignAuditTest(unittest.TestCase):
    def test_goal4683_kills_contact_witness_as_rebranded_existing_work(self) -> None:
        audit = v4.v4_goal4683_contact_witness_design_audit().as_dict()

        self.assertEqual(
            "goal4683_no_go_contact_witness_target_reuses_v2_14_collect_k_and_partner_witness",
            audit["status"],
        )
        self.assertEqual("AABB_PAIR_EXACT_WITNESS_DEVICE_COLUMNS_2D", audit["audited_target"])
        self.assertIn("V2.14 already contains bounded collect-k", audit["verdict"])
        self.assertTrue(audit["target_killed_for_v4_0_performance_path"])

    def test_goal4683_records_preexisting_v2_and_current_surfaces(self) -> None:
        audit = v4.v4_goal4683_contact_witness_design_audit().as_dict()

        self.assertIn("rtdl_optix_collect_k_bounded_i64", audit["v2_14_preexisting_surfaces"])
        self.assertIn("rtdl_embree_collect_k_bounded_i64", audit["v2_14_preexisting_surfaces"])
        self.assertIn(
            "segment_polygon_exact_witness_pair_page_optix_prepared_partner_columns",
            audit["current_preexisting_surfaces"],
        )
        self.assertIn(
            "ray_primitive_witness_pair_page_optix_prepared_partner_columns",
            audit["current_preexisting_surfaces"],
        )

    def test_goal4683_does_not_authorize_pod_implementation_or_release_claims(self) -> None:
        audit = v4.v4_goal4683_contact_witness_design_audit().as_dict()

        self.assertFalse(audit["implementation_authorized"])
        self.assertFalse(audit["pod_authorized"])
        self.assertFalse(audit["release_authorized"])
        self.assertFalse(audit["public_speedup_claim_authorized"])
        self.assertFalse(audit["whole_app_speedup_claim_authorized"])
        self.assertFalse(audit["app_identity_kernel_authorized"])
        self.assertFalse(audit["partner_migration_speed_credit_authorized"])
        self.assertIn("Goal4684", audit["next_goal"])

    def test_goal4683_validation_passes(self) -> None:
        validation = v4.validate_v4_goal4683_contact_witness_design_audit()

        self.assertEqual("passed", validation["status"])
        self.assertEqual((), validation["missing_or_invalid"])
        self.assertFalse(validation["release_authorized"])


if __name__ == "__main__":
    unittest.main()
