from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


AUDIT = ROOT / "future" / "v4" / "evidence" / "v4_goal4658_final_recheck_guardrails_completion_audit_2026-06-25.json"
REPORT = ROOT / "future" / "v4" / "v4_goal4658_final_recheck_guardrails_completion_audit_2026-06-25.md"
DEBT = ROOT / "future" / "v4" / "reviews" / "goal4658_completion_review_debt_and_no_release_authorization_2026-06-25.md"


class V4Goal4658FinalRecheckAuditTest(unittest.TestCase):
    def setUp(self) -> None:
        self.audit = json.loads(AUDIT.read_text(encoding="utf-8"))

    def test_final_recheck_preserves_no_release_authorization(self) -> None:
        self.assertEqual(
            "goal4658_final_recheck_complete_no_release_authorization",
            self.audit["status"],
        )
        self.assertEqual(
            "bounded_operator_v4_only__formal_high_performance_not_supported",
            self.audit["decision_label"],
        )
        claim = self.audit["claim_boundary"]
        self.assertTrue(claim["bounded_operator_surface_available"])
        self.assertFalse(claim["release_authorized"])
        self.assertFalse(claim["formal_high_performance_v4_authorized"])
        self.assertFalse(claim["broad_v4_speedup_claim_authorized"])
        self.assertFalse(claim["whole_app_speedup_claim_authorized"])
        self.assertFalse(claim["cupy_blanket_performance_claim_authorized"])
        self.assertFalse(claim["arbitrary_numba_callback_claim_authorized"])
        self.assertFalse(claim["true_zero_copy_claim_authorized"])
        self.assertFalse(claim["c_abi_embedding_non_python_host_claim_authorized"])
        self.assertFalse(claim["app_specific_native_kernel_authorized"])

    def test_amendment_checklist_is_answered_without_masking_debt(self) -> None:
        checklist = self.audit["checklist"]

        for key in (
            "AM1_no_formal_claim_relies_on_partner_migration_or_parity",
            "AM2_class_aware_bars_not_naive_whole_suite_geomean",
            "AM3_routes_bound_or_blocked_before_protocol",
            "AM4_numeric_thresholds_frozen_before_runs",
            "AM5_no_process_only_truth_freeze_as_goal4647",
            "AM6_expected_outcome_stated_upfront",
        ):
            self.assertEqual("pass", checklist[key]["status"], key)

        self.assertEqual(
            "blocked_debt_no_release",
            checklist["final_3ai_before_broad_release_or_tag"]["status"],
        )
        self.assertFalse(self.audit["review_debt"]["three_ai_consensus_complete"])
        self.assertFalse(self.audit["review_debt"]["release_or_tag_authorized"])

    def test_post_goal4658_route_truth_does_not_overturn_app_level_no_go(self) -> None:
        self.assertEqual(
            "bounded_operator_v4_only__app_level_high_performance_not_supported",
            self.audit["app_level_analysis_decision"],
        )
        self.assertEqual(
            "rtnn_candidate_does_not_move_app_level_bar",
            self.audit["rtnn_decision"],
        )
        self.assertEqual(
            "protocol_refreshed__no_full_all_app_rerun_triggered",
            self.audit["goal4663_decision"],
        )

    def test_report_and_debt_files_preserve_non_authorization_wording(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        debt = DEBT.read_text(encoding="utf-8")

        self.assertIn("It does not prove formal app-level high-performance", report)
        self.assertIn("It is not formal V4 performance evidence", report)
        self.assertIn("release_or_tag_authorized: false", debt)
        self.assertIn("three_ai_consensus_complete: false", debt)
        self.assertIn("does not authorize V4 release", debt)


if __name__ == "__main__":
    unittest.main()
