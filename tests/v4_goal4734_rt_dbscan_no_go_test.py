from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "future" / "v4" / "v4_goal4734_rt_dbscan_generic_continuation_no_go_2026-06-26.md"
EVIDENCE = ROOT / "future" / "v4" / "evidence" / "v4_goal4734_rt_dbscan_generic_continuation_no_go_2026-06-26.json"


class V4Goal4734RTDBSCANNoGoTest(unittest.TestCase):
    def test_goal4734_closes_rt_dbscan_from_existing_no_go_evidence(self) -> None:
        payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        self.assertEqual(payload["goal"], "Goal4734")
        self.assertEqual(payload["status"], "closed_no_go_pending_external_review_debt")
        joined = "\n".join(payload["controlling_evidence"])
        self.assertIn("v4_goal4670_rt_dbscan_second_win_diagnostics", joined)
        self.assertIn("v4_goal4671_rtdbscan_native_grouped_union_feasibility", joined)

    def test_no_go_does_not_promote_direct_status_or_release_claims(self) -> None:
        payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        boundary = payload["claim_boundary"]
        self.assertFalse(boundary["release_authorized"])
        self.assertFalse(boundary["public_speedup_claim_authorized"])
        self.assertFalse(boundary["rt_dbscan_high_performance_claim_authorized"])
        self.assertFalse(boundary["direct_status_rows_count_as_v4_wins"])
        self.assertFalse(boundary["app_specific_dbscan_kernel_authorized"])

    def test_next_goal_is_fresh_generic_operator_selection(self) -> None:
        payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        self.assertEqual(payload["next_goal"]["id"], "Goal4735")
        text = DOC.read_text(encoding="utf-8")
        self.assertIn("Proceed to Goal4735", text)
        self.assertIn("new generic grouped-union algorithm", text)
        self.assertIn("repeating RTDBSCAN micro-probes would be churn", text)


if __name__ == "__main__":
    unittest.main()
