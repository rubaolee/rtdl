from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "Paper-reproduction-apps" / "librts-paper" / "results" / "goal5525_librts_internal_closeout_packet.json"


class Goal5525LibrtsInternalCloseoutPacketTest(unittest.TestCase):
    def test_verification_and_cleanup_are_recorded(self):
        payload = json.loads(RESULT.read_text(encoding="utf-8"))
        self.assertTrue(payload["verification"]["local_librts_tests_passed"])
        self.assertEqual(payload["verification"]["local_librts_test_count"], 176)
        self.assertTrue(payload["cleanup"]["pod_transient_goal5521_5523_data_removed"])
        self.assertTrue(payload["cleanup"]["official_archive_preserved"])
        self.assertTrue(payload["cleanup"]["author_build_preserved"])
        self.assertTrue(payload["cleanup"]["rtdl_optix_build_preserved"])
        self.assertEqual(payload["cleanup"]["remaining_local_pycache_directories"], 0)

    def test_review_is_still_pending(self):
        review = json.loads(RESULT.read_text(encoding="utf-8"))["review"]
        self.assertTrue(review["goals5519_5525_external_review_pending"])
        self.assertFalse(review["self_approved"])

    def test_forbidden_claims_remain_closed(self):
        boundary = json.loads(RESULT.read_text(encoding="utf-8"))["claim_boundary"]
        self.assertTrue(all(value is False for value in boundary.values()))


if __name__ == "__main__":
    unittest.main()
