from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.v4_goal4773_release_authorization_status import V4_GOAL4773_STATUS
from rtdsl.v4_goal4773_release_authorization_status import V4_GOAL4773_VERDICT
from rtdsl.v4_goal4773_release_authorization_status import (
    validate_v4_goal4773_release_authorization_status,
)


class V4Goal4773ReleaseAuthorizationStatusTest(unittest.TestCase):
    def test_antigravity_verdict_closes_gemini_debt_and_authorizes_tag(self) -> None:
        status = validate_v4_goal4773_release_authorization_status(ROOT)

        self.assertEqual(V4_GOAL4773_STATUS, status["status"])
        self.assertEqual(V4_GOAL4773_VERDICT, status["verdict"])
        self.assertTrue(status["public_tag_externally_authorized"])

    def test_git_tag_is_not_claimed_before_clean_release_commit(self) -> None:
        status = validate_v4_goal4773_release_authorization_status(ROOT)

        self.assertFalse(status["git_tag_created"])
        self.assertTrue(status["clean_release_commit_required"])
        self.assertTrue(status["clean_wheel_smoke_passed"])
        self.assertTrue(status["tag_target_ready"])

    def test_forbidden_claims_remain_blocked(self) -> None:
        status = validate_v4_goal4773_release_authorization_status(ROOT)

        self.assertFalse(status["broad_speedup_authorized"])
        self.assertFalse(status["paper_reproduction_authorized"])
        self.assertFalse(status["tier3_callback_authorized"])


if __name__ == "__main__":
    unittest.main()
