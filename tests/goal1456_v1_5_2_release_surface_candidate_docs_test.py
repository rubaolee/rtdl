from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]


class Goal1456V152ReleaseSurfaceCandidateDocsTest(unittest.TestCase):
    def test_release_surface_gate_validates_candidate_docs(self) -> None:
        gate = rt.validate_v1_5_2_prepared_host_output_release_surface_gate()

        self.assertEqual(
            gate["status"],
            "candidate_docs_reviewed_unlinked_pending_public_doc_link_decision",
        )
        self.assertEqual(gate["classification"], "documented_experimental_evidence_candidate")
        self.assertEqual(gate["prepared_evidence_gate_status"], "evidence_complete_claims_blocked")
        self.assertTrue(gate["candidate_docs_drafted"])
        self.assertEqual(gate["missing_required_phrases"], ())
        self.assertEqual(gate["present_forbidden_phrases"], ())
        self.assertFalse(gate["external_release_surface_review_required"])
        self.assertTrue(gate["external_release_surface_review_accepted"])
        self.assertTrue(gate["public_docs_link_review_required"])

    def test_release_surface_gate_required_docs_exist(self) -> None:
        gate = rt.validate_v1_5_2_prepared_host_output_release_surface_gate()

        self.assertEqual(gate["required_docs"], rt.V1_5_2_RELEASE_SURFACE_REQUIRED_DOCS)
        for relative_path in gate["required_docs"]:
            with self.subTest(relative_path=relative_path):
                self.assertTrue((ROOT / relative_path).exists())

    def test_release_surface_gate_keeps_all_authorization_flags_false(self) -> None:
        gate = rt.validate_v1_5_2_prepared_host_output_release_surface_gate()

        for flag in (
            "public_docs_change_authorized_by_this_gate",
            "prepared_buffer_reuse_claim_authorized_by_this_gate",
            "stable_promotion_authorized_by_this_gate",
            "public_speedup_wording_authorized_by_this_gate",
            "zero_copy_wording_authorized_by_this_gate",
            "whole_app_speedup_claim_authorized_by_this_gate",
            "release_tag_action_authorized_by_this_gate",
        ):
            with self.subTest(flag=flag):
                self.assertIs(gate[flag], False)

    def test_candidate_docs_preserve_required_caution_wording(self) -> None:
        combined = "\n".join(
            (ROOT / path).read_text(encoding="utf-8")
            for path in rt.V1_5_2_RELEASE_SURFACE_REQUIRED_DOCS
        )

        for phrase in rt.V1_5_2_RELEASE_SURFACE_REQUIRED_PHRASES:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, combined)
        for forbidden in rt.V1_5_2_RELEASE_SURFACE_FORBIDDEN_PHRASES:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, combined)

    def test_release_surface_gate_allows_only_review_and_hardening(self) -> None:
        gate = rt.validate_v1_5_2_prepared_host_output_release_surface_gate()

        self.assertEqual(
            gate["allowed_next_actions"],
            (
                "request_public_docs_link_review",
                "keep_v1_5_2_candidate_docs_unlinked_until_link_review_accepts",
                "continue_python_rtdl_track_hardening",
            ),
        )


if __name__ == "__main__":
    unittest.main()
