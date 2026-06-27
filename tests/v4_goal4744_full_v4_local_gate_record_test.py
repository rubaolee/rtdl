from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "future" / "v4" / "v4_goal4744_full_v4_local_gate_after_current_frontdoor_cleanup_2026-06-26.md"
EVIDENCE = (
    ROOT
    / "future"
    / "v4"
    / "evidence"
    / "v4_goal4744_full_v4_local_gate_after_current_frontdoor_cleanup_2026-06-26.json"
)
CALL_FOR_REVIEW = (
    ROOT
    / "future"
    / "v4"
    / "reviews"
    / "call_for_review_v4_goal4744_full_v4_local_gate_after_current_frontdoor_cleanup_2026-06-26.md"
)
REVIEW_DEBT = (
    ROOT
    / "future"
    / "v4"
    / "reviews"
    / "v4_goal4744_full_v4_local_gate_review_debt_2026-06-26.md"
)


class V4Goal4744FullLocalGateRecordTest(unittest.TestCase):
    def test_goal4744_record_exists_and_carries_gate_result(self) -> None:
        self.assertTrue(REPORT.exists())
        self.assertTrue(EVIDENCE.exists())
        payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))

        self.assertEqual("Goal4744", payload["goal"])
        self.assertEqual("complete_pending_external_review_debt", payload["status"])
        self.assertEqual(554, payload["validation"]["v4_discover_tests_run"])
        self.assertEqual("OK", payload["validation"]["v4_discover_status"])
        self.assertEqual("OK", payload["validation"]["public_examples_and_catalog_gate_status"])
        self.assertEqual(0, payload["validation"]["current_path_stale_scan_matches"])

    def test_goal4744_frontdoor_payload_is_current_goal4742_boundary(self) -> None:
        payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        facts = payload["frontdoor_payload_facts"]

        self.assertEqual(
            "v4_python_edsl_operator_pushdown_front_door_goal4742_current_release_framing",
            facts["front_door_status"],
        )
        self.assertEqual(
            "bounded_high_performance_python_edsl_release_candidate__not_all_benchmark_apps_faster",
            facts["current_app_level_decision_label"],
        )
        self.assertEqual(10, facts["measured_surface_count"])
        self.assertEqual(0, facts["candidate_surface_count"])
        self.assertFalse(facts["all_historical_benchmark_apps_faster_claim_authorized"])
        self.assertFalse(facts["broad_v4_over_v2_14_speedup_claim_authorized"])
        self.assertFalse(facts["release_claim_authorized"])

    def test_goal4744_review_debt_exists_without_authorizing_release(self) -> None:
        self.assertTrue(CALL_FOR_REVIEW.exists())
        self.assertTrue(REVIEW_DEBT.exists())
        text = REPORT.read_text(encoding="utf-8") + "\n" + REVIEW_DEBT.read_text(encoding="utf-8")

        self.assertIn("complete_pending_external_review_debt", text)
        self.assertIn("authorizes no final V4 tag", text)
        self.assertIn("no all-benchmark speedup claim", text)


if __name__ == "__main__":
    unittest.main()
