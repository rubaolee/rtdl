from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.v4_goal4638_formal_scorecard_freeze import V4_GOAL4638_DEFERRED_EXCLUDED_FAMILIES
from rtdsl.v4_goal4638_formal_scorecard_freeze import V4_GOAL4638_MEASURED_SURFACES
from rtdsl.v4_goal4638_formal_scorecard_freeze import V4_GOAL4638_PARTIAL_CONTROL_FAMILIES
from rtdsl.v4_goal4638_formal_scorecard_freeze import V4_GOAL4638_PERFORMANCE_FLOORS
from rtdsl.v4_goal4638_formal_scorecard_freeze import V4_GOAL4638_STRONG_FAMILIES
from rtdsl.v4_goal4638_formal_scorecard_freeze import validate_v4_goal4638_formal_scorecard_freeze


DOC = ROOT / "future" / "v4" / "v4_goal4638_formal_release_scorecard_freeze_2026-06-25.md"


class V4Goal4638FormalScorecardFreezeTest(unittest.TestCase):
    def test_freeze_classifies_exactly_ten_benchmark_families(self) -> None:
        freeze = validate_v4_goal4638_formal_scorecard_freeze()
        families = freeze["benchmark_families"]
        all_families = (
            *families["release_in_scope_strong_operator"],
            *families["partial_operator_control"],
            *families["deferred_excluded"],
        )

        self.assertEqual(V4_GOAL4638_STRONG_FAMILIES, families["release_in_scope_strong_operator"])
        self.assertEqual(V4_GOAL4638_PARTIAL_CONTROL_FAMILIES, families["partial_operator_control"])
        self.assertEqual(V4_GOAL4638_DEFERRED_EXCLUDED_FAMILIES, families["deferred_excluded"])
        self.assertEqual(10, len(all_families))
        self.assertEqual(10, len(set(all_families)))

    def test_freeze_includes_eight_measured_surfaces_and_no_candidates(self) -> None:
        freeze = validate_v4_goal4638_formal_scorecard_freeze()

        self.assertEqual(V4_GOAL4638_MEASURED_SURFACES, freeze["measured_surfaces"])
        self.assertEqual(8, len(freeze["measured_surfaces"]))
        self.assertEqual((), freeze["candidate_surfaces"])
        self.assertIn(
            "v4_aabb_index_query_2d_all_ops_count_prepared_runner",
            freeze["measured_surfaces"],
        )

    def test_freeze_includes_one_numeric_performance_floor_per_surface(self) -> None:
        freeze = validate_v4_goal4638_formal_scorecard_freeze()
        floors = freeze["performance_floors"]
        floor_map = {row["surface"]: row for row in floors}

        self.assertEqual(V4_GOAL4638_PERFORMANCE_FLOORS, floors)
        self.assertEqual(V4_GOAL4638_MEASURED_SURFACES, tuple(floor_map))
        self.assertEqual(8, len(floors))
        for row in floors:
            self.assertNotIn("X.XX", row["minimum_floor"])
            self.assertTrue(row["canonical_source"].startswith("future/v4/"))

        self.assertIn(">=1.20x", floor_map["v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays"]["minimum_floor"])
        self.assertIn("geomean >=1.50x", floor_map["v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays"]["minimum_floor"])
        self.assertIn("Embree/OptiX query median >=10.0x", floor_map["v4_aabb_index_query_2d_all_ops_count_prepared_runner"]["minimum_floor"])
        self.assertIn("device_array_to_route_d_rows_gap <=100.0", floor_map["v4_fixed_radius_count_threshold_2d_device_arrays"]["minimum_floor"])

    def test_freeze_blocks_goal4639_until_external_review(self) -> None:
        freeze = validate_v4_goal4638_formal_scorecard_freeze()

        self.assertTrue(freeze["requires_external_review_before_goal4639"])
        self.assertTrue(freeze["thresholds"]["no_silent_skips"])
        self.assertTrue(freeze["aggregation"]["geomean_must_exclude_partial_and_deferred"])
        self.assertFalse(freeze["release_authorized"])
        self.assertFalse(freeze["whole_app_speedup_claim_authorized"])
        self.assertFalse(freeze["all_benchmark_speedup_claim_authorized"])

    def test_freeze_doc_records_correction_and_forbidden_wording(self) -> None:
        text = DOC.read_text(encoding="utf-8")

        self.assertIn("Correction Note", text)
        self.assertIn("not the owner-approved Goal4638 exit gate", text)
        self.assertIn("Performance Floor Reference Table", text)
        self.assertIn("Goal4639 pass/fail must use this table", text)
        self.assertIn("geomean `>=1.50x`", text)
        self.assertIn("query median `264.822x`", text)
        self.assertIn("No geomean can include partial or deferred rows", text)
        self.assertIn("Goal4639 is blocked until this scorecard freeze receives external review", text)
        self.assertIn("all benchmark apps are faster", text)
        self.assertIn("Barnes-Hut / Spatial RayJoin covered by V4.0", text)


if __name__ == "__main__":
    unittest.main()
