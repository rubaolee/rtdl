from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "future" / "v4" / "evidence" / "v4_goal4672_next_target_selection_after_v2_14_audit_2026-06-25.json"
REPORT = ROOT / "future" / "v4" / "v4_goal4672_next_target_selection_after_v2_14_audit_2026-06-25.md"


class V4Goal4672NextTargetSelectionAfterAuditTest(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = json.loads(SUMMARY.read_text(encoding="utf-8"))

    def test_no_existing_app_target_selected(self) -> None:
        self.assertEqual(
            "no_clean_existing_app_second_target_found__new_generic_runtime_lever_required",
            self.payload["decision_label"],
        )
        self.assertFalse(self.payload["selection_result"]["selected_existing_app_target_found"])
        self.assertIsNone(self.payload["selection_result"]["selected_existing_app_target"])
        self.assertFalse(self.payload["claim_boundary"]["pod_run_authorized_by_this_artifact"])
        self.assertFalse(self.payload["claim_boundary"]["whole_app_high_performance_claim_authorized"])

    def test_rejections_include_problematic_candidate_classes(self) -> None:
        by_app = {row["app"]: row for row in self.payload["rejected_existing_targets"]}
        self.assertEqual("preexisting_same_primitive_not_clean_new_win", by_app["robot_collision"]["rejected_as"])
        self.assertEqual("no_go_after_focused_evidence", by_app["rt_dbscan"]["rejected_as"])
        self.assertEqual("deferred_app_identity_or_not_generic_enough", by_app["barnes_hut"]["rejected_as"])
        self.assertIn("V2.14 already used", by_app["raydb_style"]["reason"])

    def test_goal4673_gate_blocks_premature_pod_and_partner_migration(self) -> None:
        gate = self.payload["goal4673_candidate_gate"]
        self.assertIn("prove whether V2.14 already had the same primitive route", gate["required_before_coding"])
        self.assertIn("freeze numeric material-speed bar before running", gate["required_before_coding"])
        self.assertIn("partner certification or front-door cleanup counted as speed", gate["forbidden_target_classes"])
        self.assertIn(
            "material same-primitive improvement over V2.14 for an existing primitive, with V2.14 as the explicit denominator",
            gate["allowed_target_classes"],
        )

    def test_report_states_no_clean_existing_target(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("does not select an existing benchmark app", text)
        self.assertIn("Goal4673 must not start with a POD run", text)
        self.assertIn("existing aggregate-tree fused weighted-vector", text)
        self.assertIn("implementation does not pass as-is", text)
        self.assertIn("Non-Authorization", text)


if __name__ == "__main__":
    unittest.main()
