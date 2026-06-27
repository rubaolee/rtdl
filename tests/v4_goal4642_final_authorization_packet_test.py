from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rtdsl.v4_goal4642_final_authorization_packet import V4_GOAL4642_REQUESTED_LABEL
from rtdsl.v4_goal4642_final_authorization_packet import validate_v4_goal4642_final_authorization_packet


class V4Goal4642FinalAuthorizationPacketTest(unittest.TestCase):
    def test_packet_is_ready_but_not_authorized(self) -> None:
        packet = validate_v4_goal4642_final_authorization_packet(ROOT)

        self.assertEqual(V4_GOAL4642_REQUESTED_LABEL, packet["requested_label"])
        self.assertEqual(3, packet["required_reviewer_count"])
        self.assertTrue(packet["scorecard_passed"])
        self.assertTrue(packet["clean_tree_passed"])
        self.assertTrue(packet["packet_clean_tree_revalidation_commit"].startswith("437b79a2"))
        self.assertTrue(packet["public_docs_cleaned"])
        self.assertFalse(packet["release_authorized"])

    def test_packet_contains_required_review_content(self) -> None:
        packet = validate_v4_goal4642_final_authorization_packet(ROOT)
        text = (ROOT / packet["packet"]).read_text(encoding="utf-8")

        for heading in (
            "Requested Publication Label",
            "Scope",
            "Measured Operators",
            "Scorecard Result",
            "Public Docs And Examples",
            "Review Debt",
            "Forbidden Claims",
            "Release Notes",
            "Goal-Level Decision Audit",
            "Non-Authorization",
        ):
            self.assertIn(heading, text)
        for forbidden in packet["forbidden_claims"]:
            self.assertIn(forbidden, text)
        for forbidden in (
            "Barnes-Hut new V4-over-V3 speedup",
            "Spatial RayJoin speedup",
            "LibRTS paper reproduction",
        ):
            self.assertIn(forbidden, packet["forbidden_claims"])

    def test_call_for_review_requests_three_ai_verdict(self) -> None:
        packet = validate_v4_goal4642_final_authorization_packet(ROOT)
        text = (ROOT / packet["call_for_review"]).read_text(encoding="utf-8")

        self.assertIn("authorize_formal_v4_0_bounded_operator_release", text)
        self.assertIn("no_go_do_not_release_v4_0", text)
        self.assertIn("3-AI", text)
        self.assertIn("Do not authorize", text)


if __name__ == "__main__":
    unittest.main()
