from __future__ import annotations

import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4_maintainer as v4


class V4Goal4679RelationTopologyTargetTest(unittest.TestCase):
    def test_goal4679_selects_generic_relation_operator_not_app_kernel(self) -> None:
        decision = v4.v4_goal4679_relation_topology_target().as_dict()

        self.assertEqual(
            "goal4679_select_relation_topology_same_primitive_target_no_pod_no_release",
            decision["status"],
        )
        self.assertEqual(
            "SHAPE_PAIR_RELATION_ACTIVE_COUNT_2D_PREPARED_LEFT_EXECUTOR",
            decision["selected_operator"],
        )
        self.assertEqual(
            "v4_shape_pair_relation_active_count_2d_prepared_left_executor",
            decision["selected_surface"],
        )
        self.assertIn("generic shape-pair relation/topology", decision["app_probe_role"])
        self.assertIn("not a RayJoin native kernel", decision["app_probe_role"])
        self.assertFalse(decision["app_identity_native_kernel_authorized"])

    def test_goal4679_locks_v2_14_same_primitive_denominator(self) -> None:
        decision = v4.v4_goal4679_relation_topology_target().as_dict()

        self.assertTrue(decision["v2_14_same_primitive_existed"])
        self.assertTrue(decision["v2_14_denominator_required"])
        self.assertFalse(decision["clean_new_v4_lever"])
        self.assertTrue(decision["same_primitive_speed_credit_requires_material_improvement"])
        self.assertIn("V2.14 already had", decision["work_class"])
        self.assertFalse(decision["partner_migration_counts_as_v4_speed_win"])

    def test_goal4679_freezes_numeric_bars_before_any_pod_run(self) -> None:
        decision = v4.v4_goal4679_relation_topology_target().as_dict()
        bars = decision["frozen_numeric_bars"]

        self.assertFalse(decision["pod_run_authorized_by_this_artifact"])
        self.assertTrue(bars["correctness_parity_required"])
        self.assertGreaterEqual(
            bars["v4_over_v2_14_same_primitive_hot_min_for_speed_credit"],
            1.20,
        )
        self.assertGreaterEqual(
            bars["v4_over_v2_14_same_primitive_wall_min_for_speed_credit"],
            1.10,
        )
        self.assertGreaterEqual(bars["v4_over_v3_0_2_hot_parity_floor"], 0.98)
        self.assertFalse(bars["hot_path_host_row_stream_materialization_allowed"])
        self.assertFalse(bars["partner_migration_counts_as_speed"])

    def test_goal4679_claim_boundary_blocks_release_and_broad_speed_wording(self) -> None:
        decision = v4.v4_goal4679_relation_topology_target().as_dict()

        self.assertFalse(decision["release_authorized"])
        self.assertFalse(decision["broad_v4_speedup_claim_authorized"])
        self.assertFalse(decision["whole_app_speedup_claim_authorized"])

    def test_goal4679_validation_passes(self) -> None:
        validation = v4.validate_v4_goal4679_relation_topology_target()

        self.assertEqual("passed", validation["status"])
        self.assertEqual((), validation["missing_or_invalid"])
        self.assertFalse(validation["release_authorized"])


if __name__ == "__main__":
    unittest.main()
