from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]


class Goal1455V152PreparedHostOutputExternalReviewGateTest(unittest.TestCase):
    def test_external_review_moves_to_satisfied_but_claims_remain_blocked(self) -> None:
        gate = rt.validate_v1_5_2_prepared_buffer_reuse_gate()

        self.assertEqual(gate["status"], "evidence_complete_claims_blocked")
        self.assertIn("external_ai_review", gate["satisfied_evidence"])
        self.assertEqual(gate["missing_evidence"], ())
        for flag in (
            "prepared_buffer_reuse_proven",
            "true_zero_copy_authorized",
            "public_speedup_wording_authorized",
            "whole_app_speedup_claim_authorized",
            "stable_public_primitive_authorized",
            "release_action_authorized",
        ):
            with self.subTest(flag=flag):
                self.assertIs(gate[flag], False)

    def test_claude_and_gemini_reviews_accept_without_blockers(self) -> None:
        claude = (
            ROOT
            / "docs/reports/claude_goal1455_v1_5_2_prepared_host_output_external_review_2026-05-07.md"
        ).read_text(encoding="utf-8")
        gemini = (
            ROOT
            / "docs/reports/gemini_goal1455_v1_5_2_prepared_host_output_external_review_2026-05-07.md"
        ).read_text(encoding="utf-8")

        self.assertIn("ACCEPT", claude)
        self.assertIn("None", claude)
        self.assertIn("ACCEPT", gemini)
        self.assertIn("None", gemini)


if __name__ == "__main__":
    unittest.main()
