from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "future" / "v4" / "evidence" / "v4_goal4724_remaining_5_app_route_gap_audit_2026-06-26.json"
REPORT = ROOT / "future" / "v4" / "v4_goal4724_remaining_5_app_route_gap_audit_2026-06-26.md"
CALL_FOR_REVIEW = (
    ROOT
    / "future"
    / "v4"
    / "reviews"
    / "call_for_review_v4_goal4724_remaining_5_app_route_gap_audit_2026-06-26.md"
)
REVIEW_DEBT = (
    ROOT
    / "future"
    / "v4"
    / "reviews"
    / "v4_goal4724_remaining_5_app_route_gap_audit_review_debt_2026-06-26.md"
)


class V4Goal4724RemainingAppRouteGapAuditTest(unittest.TestCase):
    def setUp(self) -> None:
        self.audit = json.loads(AUDIT.read_text(encoding="utf-8"))
        self.rows = {row["app"]: row for row in self.audit["rows"]}

    def test_audit_covers_exactly_the_five_incomplete_apps(self) -> None:
        self.assertEqual(
            {
                "robot_collision",
                "contact_manifold",
                "rtnn",
                "spatial_rayjoin",
                "barnes_hut",
            },
            set(self.rows),
        )
        self.assertEqual(5, self.audit["summary"]["remaining_app_count"])

    def test_global_boundaries_block_release_claims_and_pod(self) -> None:
        rules = self.audit["global_rules"]
        self.assertTrue(rules["v2_means_v2_14"])
        self.assertFalse(rules["silent_v2_v3_fallback_authorized"])
        self.assertFalse(rules["operator_or_subprobe_counts_as_full_app_result"])
        self.assertFalse(rules["partner_migration_counts_as_v4_speed_win"])
        self.assertFalse(rules["same_primitive_productization_counts_as_v4_speed_win"])
        self.assertFalse(rules["app_identity_native_kernel_authorized"])
        self.assertFalse(rules["pod_authorized_by_goal4724"])
        self.assertFalse(rules["release_authorized"])
        self.assertTrue(rules["final_v4_tag_blocked_until_goal4733"])

    def test_each_row_has_v2_14_denominator_and_no_speed_credit_now(self) -> None:
        for app, row in self.rows.items():
            with self.subTest(app=app):
                self.assertIsInstance(row["v2_14_denominator"], str)
                self.assertGreater(len(row["v2_14_denominator"]), 20)
                self.assertTrue(row["v2_14_denominator_strength"])
                self.assertTrue(row["current_v4_artifacts"])
                self.assertTrue(row["missing_route_or_operator"])
                self.assertTrue(row["required_next_goal"].startswith("Goal47"))
                self.assertFalse(row["can_count_as_v4_speed_win_now"])
                self.assertFalse(row["pod_authorized_now"])
                self.assertGreaterEqual(len(row["not_allowed_to_claim"]), 3)

    def test_row_classes_preserve_the_important_distinctions(self) -> None:
        self.assertEqual(
            "partial_operator_exists_full_app_missing",
            self.rows["robot_collision"]["goal4724_gap_class"],
        )
        self.assertEqual(
            "partial_operator_exists_no_go_prior_for_rebranded_collect_k",
            self.rows["contact_manifold"]["goal4724_gap_class"],
        )
        self.assertEqual(
            "measured_candidate_requires_formal_no_win_row",
            self.rows["rtnn"]["goal4724_gap_class"],
        )
        self.assertEqual(
            "no_current_v4_relation_topology_route",
            self.rows["spatial_rayjoin"]["goal4724_gap_class"],
        )
        self.assertEqual(
            "aggregate_frontier_subprobe_not_complete_app_route",
            self.rows["barnes_hut"]["goal4724_gap_class"],
        )

    def test_next_goal_order_is_explicit(self) -> None:
        expected = {
            "rtnn": "Goal4725",
            "robot_collision": "Goal4726",
            "contact_manifold": "Goal4727",
            "spatial_rayjoin": "Goal4728",
            "barnes_hut": "Goal4729",
        }
        actual = {app: row["required_next_goal"] for app, row in self.rows.items()}
        self.assertEqual(expected, actual)
        self.assertIn("Goal4730", " ".join(self.audit["summary"]["next_goals"]))

    def test_rtnn_records_no_win_ratios(self) -> None:
        rtnn = self.rows["rtnn"]
        self.assertLess(rtnn["latest_known_v4_vs_v2_14_hot_by_scale"]["262144"], 1.01)
        self.assertLess(rtnn["latest_known_v4_vs_v2_14_hot_by_scale"]["1048576"], 1.01)
        self.assertIn("measured no-win", rtnn["goal4725_exit_condition"])

    def test_report_and_review_files_exist_and_preserve_non_authorization(self) -> None:
        for path in (REPORT, CALL_FOR_REVIEW, REVIEW_DEBT):
            self.assertTrue(path.exists(), path)
            text = path.read_text(encoding="utf-8")
            self.assertIn("Non-Authorization", text)
            self.assertIn("final", text.lower())
            self.assertIn("tag", text.lower())

    def test_external_review_debt_is_recorded_without_authorization(self) -> None:
        review = self.audit["external_review"]
        self.assertTrue(review["required"])
        self.assertEqual("review_debt_allowed_not_blocking_engineering", review["status"])
        self.assertFalse(self.audit["claim_boundary"]["goal4724_authorizes_release"])
        self.assertFalse(self.audit["claim_boundary"]["goal4724_authorizes_pod"])


if __name__ == "__main__":
    unittest.main()
