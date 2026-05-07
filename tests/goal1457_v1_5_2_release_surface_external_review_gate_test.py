from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]


class Goal1457V152ReleaseSurfaceExternalReviewGateTest(unittest.TestCase):
    def test_external_release_surface_review_is_accepted_but_unlinked(self) -> None:
        gate = rt.validate_v1_5_2_prepared_host_output_release_surface_gate()

        self.assertEqual(
            gate["status"],
            "candidate_docs_reviewed_unlinked_pending_public_doc_link_decision",
        )
        self.assertTrue(gate["external_release_surface_review_accepted"])
        self.assertFalse(gate["external_release_surface_review_required"])
        self.assertTrue(gate["public_docs_link_review_required"])
        self.assertFalse(gate["public_docs_change_authorized_by_this_gate"])

    def test_external_review_artifacts_exist_and_accept(self) -> None:
        review_paths = (
            "docs/handoff/goal1457_external_release_surface_review_request_2026-05-07.md",
            "docs/reports/claude_goal1457_v1_5_2_release_surface_review_2026-05-07.md",
            "docs/reports/gemini_goal1457_v1_5_2_release_surface_review_2026-05-07.md",
            "docs/reports/three_ai_goal1457_v1_5_2_release_surface_candidate_docs_consensus_2026-05-07.md",
        )
        for relative_path in review_paths:
            with self.subTest(relative_path=relative_path):
                self.assertTrue((ROOT / relative_path).exists())

        for relative_path in review_paths[1:3]:
            with self.subTest(relative_path=relative_path):
                text = (ROOT / relative_path).read_text(encoding="utf-8")
                self.assertIn("ACCEPT", text)
                self.assertIn("Blockers", text)

    def test_reviewed_gate_still_blocks_all_public_claims(self) -> None:
        gate = rt.validate_v1_5_2_prepared_host_output_release_surface_gate()

        for flag in (
            "prepared_buffer_reuse_claim_authorized_by_this_gate",
            "stable_promotion_authorized_by_this_gate",
            "public_speedup_wording_authorized_by_this_gate",
            "zero_copy_wording_authorized_by_this_gate",
            "whole_app_speedup_claim_authorized_by_this_gate",
            "release_tag_action_authorized_by_this_gate",
        ):
            with self.subTest(flag=flag):
                self.assertIs(gate[flag], False)

        self.assertIn("unlinked candidate package", gate["claim_boundary"])
        self.assertIn("does not authorize public docs links", gate["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
