from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "future" / "v4" / "v4_goal4746_final_release_candidate_review_packet_2026-06-26.md"
EVIDENCE = ROOT / "future" / "v4" / "evidence" / "v4_goal4746_final_release_candidate_review_packet_2026-06-26.json"
CALL_FOR_REVIEW = (
    ROOT / "future" / "v4" / "reviews" / "call_for_review_v4_goal4746_final_release_candidate_review_packet_2026-06-26.md"
)
REVIEW_DEBT = (
    ROOT / "future" / "v4" / "reviews" / "v4_goal4746_final_release_candidate_review_packet_review_debt_2026-06-26.md"
)


class V4Goal4746FinalReleaseCandidateReviewPacketTest(unittest.TestCase):
    def test_packet_exists_and_preserves_current_label(self) -> None:
        self.assertTrue(REPORT.exists())
        self.assertTrue(EVIDENCE.exists())
        payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))

        self.assertEqual("Goal4746", payload["goal"])
        self.assertEqual("complete_pending_external_review_debt", payload["status"])
        self.assertEqual(
            "bounded_high_performance_python_edsl_release_candidate__not_all_benchmark_apps_faster",
            payload["current_app_level_decision_label"],
        )
        self.assertFalse(payload["benchmark_app_boundary"]["all_10_historical_apps_faster_than_v2_14"])

    def test_packet_carries_latest_local_gate(self) -> None:
        payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        validation = payload["local_validation"]

        self.assertEqual(561, validation["v4_discover_tests_run"])
        self.assertEqual("OK", validation["v4_discover_status"])
        self.assertEqual("OK", validation["public_examples_and_catalog_gate_status"])
        self.assertEqual(0, validation["current_path_stale_goal_label_scan_matches"])
        self.assertEqual(
            "v4_python_edsl_operator_pushdown_front_door_goal4742_current_release_framing",
            validation["front_door_status"],
        )

    def test_packet_requests_external_verdict_without_authorizing_tag(self) -> None:
        self.assertTrue(CALL_FOR_REVIEW.exists())
        self.assertTrue(REVIEW_DEBT.exists())
        text = REPORT.read_text(encoding="utf-8") + "\n" + CALL_FOR_REVIEW.read_text(encoding="utf-8")

        self.assertIn("authorize_final_v4_tag_under_bounded_release_candidate_label", text)
        self.assertIn("approve_release_candidate_but_block_final_tag_until_amendments", text)
        self.assertIn("Goal4746 itself authorizes no final V4 tag", text)
        self.assertIn("no all-benchmark speedup claim", text)


if __name__ == "__main__":
    unittest.main()
