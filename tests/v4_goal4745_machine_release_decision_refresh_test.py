from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.v4_goal4644_post_release_guardrails import validate_v4_goal4644_post_release_guardrails
from rtdsl.v4_release_decision import validate_v4_goal4632_release_decision


REPORT = ROOT / "future" / "v4" / "v4_goal4745_machine_release_decision_current_boundary_refresh_2026-06-26.md"
EVIDENCE = (
    ROOT
    / "future"
    / "v4"
    / "evidence"
    / "v4_goal4745_machine_release_decision_current_boundary_refresh_2026-06-26.json"
)
CALL_FOR_REVIEW = (
    ROOT
    / "future"
    / "v4"
    / "reviews"
    / "call_for_review_v4_goal4745_machine_release_decision_current_boundary_refresh_2026-06-26.md"
)
REVIEW_DEBT = (
    ROOT
    / "future"
    / "v4"
    / "reviews"
    / "v4_goal4745_machine_release_decision_refresh_review_debt_2026-06-26.md"
)


class V4Goal4745MachineReleaseDecisionRefreshTest(unittest.TestCase):
    def test_goal4745_record_exists(self) -> None:
        self.assertTrue(REPORT.exists())
        self.assertTrue(EVIDENCE.exists())
        self.assertTrue(CALL_FOR_REVIEW.exists())
        self.assertTrue(REVIEW_DEBT.exists())

        payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        self.assertEqual("Goal4745", payload["goal"])
        self.assertEqual("complete_pending_external_review_debt", payload["status"])
        self.assertEqual(
            "bounded_high_performance_python_edsl_release_candidate__not_all_benchmark_apps_faster",
            payload["current_app_level_decision_label"],
        )
        self.assertEqual(558, payload["validation"]["v4_discover_tests_run"])

    def test_release_decision_uses_current_boundary(self) -> None:
        decision = validate_v4_goal4632_release_decision()
        gates = {gate["gate"]: gate for gate in decision["gates"]}

        self.assertEqual(
            "complete_rt_core_app_matrix__bounded_material_wins__no_broad_all_app_speedup_claim",
            decision["current_app_level_decision_label"],
        )
        self.assertIn(
            "external_3ai_review_debt_open_for_goal4743_goal4744_current_release_candidate",
            decision["release_blockers"],
        )
        self.assertIn("G13_public_docs_current_frontdoor_cleanup", gates)
        self.assertIn("G14_full_v4_local_gate_after_current_frontdoor_cleanup", gates)
        self.assertTrue(gates["G14_full_v4_local_gate_after_current_frontdoor_cleanup"]["passed_for_release"])

    def test_guardrails_use_current_boundary(self) -> None:
        guardrails = validate_v4_goal4644_post_release_guardrails(ROOT)

        self.assertEqual("v4_python_edsl_release_candidate_guardrails_active_goal4744", guardrails["status"])
        self.assertEqual(
            "complete_rt_core_app_matrix__bounded_material_wins__no_broad_all_app_speedup_claim",
            guardrails["current_app_level_decision_label"],
        )
        self.assertFalse(guardrails["release_authorized"])
        self.assertFalse(guardrails["formal_release_authorized"])
        self.assertFalse(guardrails["app_level_high_performance_authorized"])

    def test_non_authorization_is_preserved(self) -> None:
        text = REPORT.read_text(encoding="utf-8") + "\n" + REVIEW_DEBT.read_text(encoding="utf-8")

        self.assertIn("authorizes no final V4 tag", text)
        self.assertIn("no all-benchmark speedup claim", text)
        self.assertIn("no app-specific native kernel", text)


if __name__ == "__main__":
    unittest.main()
