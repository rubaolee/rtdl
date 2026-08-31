from __future__ import annotations

import unittest

from scripts.goal5768_audit_v2_v3_v4_performance_eligibility import build_audit


class Goal5768PerformanceEligibilityTest(unittest.TestCase):
    def setUp(self) -> None:
        self.audit = build_audit()

    def test_representative_coverage_is_not_performance_admission(self) -> None:
        self.assertEqual(self.audit["paper_app_count"], 9)
        self.assertEqual(self.audit["paper_lane_count"], 13)
        self.assertEqual(self.audit["representative_functional_exact_count"], 13)
        self.assertEqual(
            self.audit["representative_behavioral_true_optix_count"], 13)
        self.assertEqual(
            self.audit["application_owned_v4_frontdoor_lane_count"], 13)
        self.assertEqual(
            self.audit["application_owned_v4_complete_timer_lane_count"], 13)
        self.assertEqual(self.audit["formal_performance_eligible_count"], 0)
        self.assertEqual(sum(
            bool(row["same_input_output_complete_timer_v2_v3_v4_frozen"])
            for row in self.audit["lanes"]), 13)

    def test_every_lane_fails_closed_with_specific_blocker(self) -> None:
        for row in self.audit["lanes"]:
            self.assertFalse(row["formal_performance_eligible"])
            self.assertTrue(row["blockers"], row["lane"])
            self.assertTrue(row["same_input_output_complete_timer_v2_v3_v4_frozen"])
            self.assertEqual(
                row["blockers"],
                ("target_functional_three_way_receipts_not_yet_recorded",),
            )

    def test_triangle_and_raydb_now_have_real_app_frontdoors(self) -> None:
        affected = [row for row in self.audit["lanes"] if row["app_id"] in {
            "raydb", "triangle_counting"}]
        self.assertEqual(len(affected), 3)
        for row in affected:
            self.assertTrue(row["application_owned_v4_frontdoor_exists"])
            self.assertTrue(
                row["application_owned_v4_complete_registered_timer_exists"])
            self.assertNotIn(
                "v4_functional_geometry_encodes_expected_events_not_end_to_end_input",
                row["blockers"])

    def test_particle_backports_are_new_and_not_relabelled_historical(self) -> None:
        row = next(row for row in self.audit["lanes"]
                   if row["app_id"] == "particle_tracking")
        self.assertEqual(
            row["predecessor_provenance"],
            "new_fair_comparison_backports_frozen_before_any_v4_timing",
        )
        self.assertTrue(row["application_owned_v4_frontdoor_exists"])
        self.assertTrue(row["application_owned_v4_complete_registered_timer_exists"])

    def test_claim_boundary_blocks_pod_and_performance(self) -> None:
        boundary = self.audit["claim_boundary"]
        self.assertFalse(boundary["formal_worker_allowed"])
        self.assertFalse(boundary["pod_authorized_or_requested"])
        self.assertFalse(boundary["performance_claimed"])
        self.assertFalse(boundary["nine_app_end_to_end_integration_claimed"])


if __name__ == "__main__":
    unittest.main()
