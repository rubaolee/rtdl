from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "future" / "v4" / "evidence" / "v4_goal4740_robot_collision_boundary_recheck_2026-06-26.json"
REPORT = ROOT / "future" / "v4" / "v4_goal4740_robot_collision_boundary_recheck_2026-06-26.md"


class V4Goal4740RobotBoundaryRecheckTest(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))

    def test_clean_boundary_shows_native_route_fast(self) -> None:
        measurement = self.payload["clean_boundary_measurement"]
        self.assertGreater(measurement["embree_over_optix_flags"], 5.0)
        self.assertGreater(measurement["optix_flags_over_optix_count"], 10.0)
        self.assertLess(measurement["optix_flags_stdout_bytes"], 10_000)
        self.assertLess(measurement["embree_flags_stdout_bytes"], 10_000)

    def test_v2_14_same_primitive_blocks_speed_credit(self) -> None:
        boundary = self.payload["v2_14_boundary"]
        self.assertTrue(boundary["v2_14_already_had_same_primitive_family"])
        for surface in (
            "optix_prepared_device_buffers",
            "optix_prepared_device_count",
            "PreparedOptixGroupedSegmentQuery3D",
            "run_native_prepared_grouped_segment_any_hit_flags",
            "run_native_prepared_grouped_segment_any_hit_count",
        ):
            self.assertIn(surface, boundary["git_show_v2_14_confirmed_surfaces"])

    def test_robot_remains_no_go_for_formal_high_performance(self) -> None:
        classification = self.payload["classification"]
        self.assertTrue(classification["native_route_fast_under_clean_boundary"])
        self.assertFalse(classification["counts_as_v4_over_v2_14_speed_win"])
        self.assertFalse(classification["formal_high_performance_candidate"])
        self.assertEqual(
            classification["updated_row_status"],
            "closed_same_primitive_boundary_repaired_no_v4_over_v2_speed_credit",
        )
        self.assertIn("not a new V4 performance mechanism versus V2.14", REPORT.read_text(encoding="utf-8"))

    def test_claim_boundary_blocks_robot_overclaiming(self) -> None:
        boundary = self.payload["claim_boundary"]
        for key in (
            "release_authorized",
            "final_v4_tag_authorized",
            "robot_speedup_vs_v2_14_claim_authorized",
            "public_speedup_claim_authorized",
            "whole_app_high_performance_claim_authorized",
            "all_benchmark_speedup_claim_authorized",
            "broad_v4_over_v2_14_claim_authorized",
            "measured_catalog_promotion_authorized_from_robot",
            "app_specific_native_kernel_authorized",
            "arbitrary_callback_support_authorized",
            "raw_optix_callback_support_authorized",
            "true_zero_copy_wording_authorized",
        ):
            self.assertFalse(boundary[key], key)


if __name__ == "__main__":
    unittest.main()
