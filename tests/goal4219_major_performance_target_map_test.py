from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4244_major_performance_target_map_after_short_row_refresh_2026-06-09.md"
GOAL4249_REPORT = ROOT / "docs" / "reports" / "goal4249_major_performance_target_map_after_public_docs_scan_2026-06-09.md"
GOAL4261_REPORT = ROOT / "docs" / "reports" / "goal4261_major_performance_target_map_after_claim_wording_closure_2026-06-09.md"


class Goal4219MajorPerformanceTargetMapTest(unittest.TestCase):
    def test_report_and_exported_api_exist(self) -> None:
        self.assertTrue(REPORT.is_file())
        self.assertTrue(GOAL4249_REPORT.is_file())
        self.assertTrue(GOAL4261_REPORT.is_file())
        self.assertEqual(
            rt.CURRENT_MAJOR_PERFORMANCE_TARGET_VERSION,
            "rtdl.v3_0.current_major_performance_targets.goal4543.v1",
        )
        self.assertTrue(callable(rt.current_major_performance_targets))
        self.assertTrue(callable(rt.summarize_current_major_performance_targets))
        self.assertTrue(callable(rt.validate_current_major_performance_targets))

    def test_target_map_validates_and_covers_required_statuses(self) -> None:
        rows = rt.current_major_performance_targets()
        validation = rt.validate_current_major_performance_targets(rows)
        summary = rt.summarize_current_major_performance_targets(rows)
        self.assertEqual(validation["status"], "accept")
        self.assertEqual(validation["errors"], ())
        self.assertEqual(summary["target_count"], 8)

        statuses = {row["target_status"] for row in rows}
        self.assertIn("done_internal_evidence", statuses)
        self.assertIn("available_explicit_not_default", statuses)
        self.assertIn("needs_broader_evidence", statuses)
        self.assertIn("blocked_pending_hardware", statuses)
        self.assertIn("pending_user_release_decision", statuses)

    def test_targets_keep_major_performance_not_app_micro_tuning_direction(self) -> None:
        rows = {row["target_id"]: row for row in rt.current_major_performance_targets()}
        self.assertEqual(
            rows["ten_app_current_route_health"]["evidence_refs"],
            ("Goal4215", "Goal4216", "Goal4217", "Goal4225", "Goal4235", "Goal4542"),
        )
        self.assertIn("all ten V3", rows["ten_app_current_route_health"]["current_reading"])
        self.assertEqual(rows["ten_app_measurement_adequacy_closure"]["target_status"], "done_internal_evidence")
        self.assertIn("Goal4230", rows["ten_app_measurement_adequacy_closure"]["evidence_refs"])
        self.assertIn("Goal4243", rows["ten_app_measurement_adequacy_closure"]["evidence_refs"])
        self.assertEqual(rows["rayjoin_contract_split_route_policy"]["target_status"], "done_internal_evidence")
        self.assertIn("Goal4239", rows["rayjoin_contract_split_route_policy"]["evidence_refs"])
        self.assertIn("Goal4239", rows["release_grade_long_run_packet"]["evidence_refs"])
        self.assertIn("Goal4243", rows["release_grade_long_run_packet"]["evidence_refs"])
        self.assertIn("Goal4248", rows["release_grade_long_run_packet"]["evidence_refs"])
        self.assertIn("Goal4248", rows["major_release_candidate_packet"]["evidence_refs"])
        self.assertIn("Goal4254", rows["release_grade_long_run_packet"]["evidence_refs"])
        self.assertIn("Goal4258", rows["release_grade_long_run_packet"]["evidence_refs"])
        self.assertIn("Goal4259", rows["release_grade_long_run_packet"]["evidence_refs"])
        self.assertIn("Goal4260", rows["release_grade_long_run_packet"]["evidence_refs"])
        self.assertIn("Goal4542", rows["release_grade_long_run_packet"]["evidence_refs"])
        self.assertIn("Goal4257", rows["major_release_candidate_packet"]["evidence_refs"])
        self.assertIn("Goal4260", rows["major_release_candidate_packet"]["evidence_refs"])
        self.assertIn("Goal4542", rows["major_release_candidate_packet"]["evidence_refs"])
        self.assertIn("public docs scan", rows["major_release_candidate_packet"]["current_reading"])
        self.assertIn("claim-wording repair loop", rows["major_release_candidate_packet"]["current_reading"])
        self.assertEqual(rows["rtdbscan_profile_aware_boundary_policy"]["target_status"], "done_internal_evidence")
        self.assertIn("contract", rows["rayjoin_contract_split_route_policy"]["theme"])
        self.assertIn("profile-aware", rows["rtdbscan_profile_aware_boundary_policy"]["theme"])
        self.assertFalse(rows["release_grade_long_run_packet"]["pod_needed_next"])
        self.assertFalse(rows["prepared_session_residency_surface"]["pod_needed_next"])
        self.assertFalse(rows["amd_hiprt_functional_parity"]["pod_needed_next"])
        self.assertTrue(rows["amd_hiprt_functional_parity"]["amd_hardware_needed"])

    def test_no_target_authorizes_release_or_hidden_dispatch(self) -> None:
        for row in rt.current_major_performance_targets():
            self.assertFalse(row["release_authorized"], row["target_id"])
            self.assertFalse(row["public_speedup_claim_authorized"], row["target_id"])
            self.assertFalse(row["whole_app_speedup_claim_authorized"], row["target_id"])
            self.assertFalse(row["broad_rt_core_claim_authorized"], row["target_id"])
            self.assertFalse(row["paper_reproduction_claim_authorized"], row["target_id"])
            self.assertFalse(row["rtdl_beats_rayjoin_claim_authorized"], row["target_id"])
            self.assertFalse(row["true_zero_copy_claim_authorized"], row["target_id"])
            self.assertFalse(row["automatic_partner_selection_authorized"], row["target_id"])
            self.assertFalse(row["app_specific_native_engine_logic_allowed"], row["target_id"])


if __name__ == "__main__":
    unittest.main()
