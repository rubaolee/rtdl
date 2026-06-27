from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "future" / "v4" / "evidence" / "v4_goal4672_v2_14_per_app_primitive_audit_2026-06-25.json"
REPORT = ROOT / "future" / "v4" / "v4_goal4672_v2_14_per_app_primitive_audit_2026-06-25.md"


class V4Goal4672V214PrimitiveAuditTest(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = json.loads(SUMMARY.read_text(encoding="utf-8"))

    def test_audit_records_all_apps_and_blocks_speed_claims(self) -> None:
        self.assertEqual(
            "v2_14_primitives_preexisting__existing_app_target_selection_requires_new_runtime_lever",
            self.payload["decision_label"],
        )
        self.assertEqual(10, self.payload["summary"]["audited_app_count"])
        self.assertTrue(self.payload["summary"]["v2_14_had_primitive_or_explicit_partner_route_for_all_apps"])
        self.assertFalse(self.payload["claim_boundary"]["public_speed_claim_authorized"])
        self.assertFalse(self.payload["claim_boundary"]["same_primitive_productization_counts_as_v4_speed_win"])

    def test_robot_collision_is_demoted_from_clean_second_win_target(self) -> None:
        by_app = {row["app"]: row for row in self.payload["apps"]}
        robot = by_app["robot_collision"]
        self.assertEqual("prepared RTDL/OptiX any-hit flag primitive", robot["v2_14_primary_route"])
        self.assertIn("not a clean second true V4 win target", robot["v4_implication"])
        self.assertTrue(self.payload["summary"]["robot_collision_is_not_clean_second_true_v4_win_target"])

    def test_raw_rows_show_v2_14_already_had_core_primitives(self) -> None:
        by_app = {row["app"]: row for row in self.payload["apps"]}
        rt_dbscan = by_app["rt_dbscan"]["v2_14_measured_goal4669_route"]
        self.assertEqual("optix_rt_core_grouped_stream_cupy_column_signature_3d", rt_dbscan["mode"])
        self.assertEqual("prepared_rt_core_grouped_union_3d_self_query", rt_dbscan["grouped_union_native_execution_path"])

        raydb = by_app["raydb_style"]["v2_14_measured_goal4669_route"]
        self.assertEqual("RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D", raydb["generic_primitive_used"])

        triangle = by_app["triangle_counting"]["v2_14_measured_goal4669_route"]
        self.assertEqual("ray_triangle_weighted_any_hit_sum_3d", triangle["prepared_session_primitive"])

    def test_report_contains_corrected_goal4672_rule(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("V2.14 was not a primitive-free baseline", text)
        self.assertIn("Immediate Correction To Goal4672", text)
        self.assertIn("robot_collision", text.replace("`", ""))
        self.assertIn("same-primitive improvement", text)
        self.assertIn("new generic primitive is required", text)


if __name__ == "__main__":
    unittest.main()
