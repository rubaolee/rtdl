from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "future" / "v4" / "evidence" / "v4_goal4723_complete_10_app_protocol_2026-06-26.json"
REPORT = ROOT / "future" / "v4" / "v4_goal4723_complete_10_app_protocol_freeze_2026-06-26.md"


EXPECTED_APPS = [
    "rt_dbscan",
    "raydb_style",
    "triangle_counting",
    "librts_spatial_index",
    "hausdorff_xhd",
    "robot_collision",
    "contact_manifold",
    "rtnn",
    "spatial_rayjoin",
    "barnes_hut",
]


class V4Goal4723CompleteAppProtocolTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
        cls.rows = cls.protocol["rows"]
        cls.by_app = {row["app"]: row for row in cls.rows}

    def test_protocol_has_all_ten_apps_once(self) -> None:
        self.assertEqual(EXPECTED_APPS, self.protocol["app_order"])
        self.assertEqual(10, len(self.rows))
        self.assertEqual(set(EXPECTED_APPS), set(self.by_app))
        self.assertEqual(10, len(self.by_app))

    def test_global_rules_block_common_escape_hatches(self) -> None:
        rules = self.protocol["global_rules"]

        self.assertTrue(rules["v2_means_v2_14"])
        self.assertTrue(rules["same_rt_hardware_required"])
        self.assertTrue(rules["correctness_parity_required_for_timed_credit"])
        self.assertFalse(rules["silent_v2_v3_fallback_authorized"])
        self.assertFalse(rules["app_specific_native_kernel_authorized"])
        self.assertFalse(rules["partner_migration_counts_as_v4_speed_win"])
        self.assertFalse(rules["same_primitive_productization_counts_as_v4_speed_win"])
        self.assertFalse(rules["operator_or_subprobe_counts_as_full_app_result"])
        self.assertTrue(rules["final_v4_tag_blocked_until_goal4733"])
        self.assertFalse(rules["pod_authorized_by_goal4723"])

    def test_row_classes_are_explicit_and_approved(self) -> None:
        allowed = set(self.protocol["allowed_row_classes"])
        for row in self.rows:
            with self.subTest(app=row["app"]):
                self.assertIn(row["row_class"], allowed)
                self.assertIn("v2_14_route", row)
                self.assertTrue(row["v2_14_route"])
                self.assertFalse(row["performance_claim_authorized"])

    def test_known_measured_rows_preserve_current_ratios(self) -> None:
        self.assertAlmostEqual(
            1.086127902760864,
            self.by_app["rt_dbscan"]["latest_known_v4_vs_v2_14_hot"],
        )
        self.assertAlmostEqual(
            0.9744073401484975,
            self.by_app["raydb_style"]["latest_known_v4_vs_v2_14_hot"],
        )
        self.assertAlmostEqual(
            4.054841666199054,
            self.by_app["triangle_counting"]["latest_known_v4_vs_v2_14_hot"],
        )
        self.assertAlmostEqual(
            1.002850507944097,
            self.by_app["librts_spatial_index"]["latest_known_v4_vs_v2_14_hot"],
        )
        self.assertAlmostEqual(
            201581.8595690473,
            self.by_app["hausdorff_xhd"]["latest_known_v4_vs_v2_14_hot"],
        )

    def test_remaining_five_have_no_fake_app_speed_claim(self) -> None:
        remaining = {
            "robot_collision",
            "contact_manifold",
            "rtnn",
            "spatial_rayjoin",
            "barnes_hut",
        }
        for app in remaining:
            with self.subTest(app=app):
                row = self.by_app[app]
                self.assertFalse(row["performance_claim_authorized"])
                if row["row_class"] != "measured_no_win_candidate":
                    self.assertTrue(row.get("missing_generic_operator_or_route"))

    def test_claim_boundary_blocks_release(self) -> None:
        boundary = self.protocol["claim_boundary"]

        self.assertFalse(boundary["release_authorized"])
        self.assertFalse(boundary["public_speed_claim_authorized"])
        self.assertFalse(boundary["whole_app_high_performance_claim_authorized"])
        self.assertFalse(boundary["all_benchmark_speedup_claim_authorized"])
        self.assertFalse(boundary["operator_catalog_substitutes_for_app_matrix"])
        self.assertFalse(boundary["final_tag_authorized"])

    def test_report_names_next_goal_and_non_authorization(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Goal4723 freezes the full 10 benchmark-app", text)
        self.assertIn("Final public tag is blocked until Goal4733", text)
        self.assertIn("Goal4723 does not authorize final V4 tag", text)


if __name__ == "__main__":
    unittest.main()
