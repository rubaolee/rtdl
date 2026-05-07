from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]


class Goal1420V151CollectKReleaseSurfaceGateTest(unittest.TestCase):
    def test_release_surface_gate_validates_candidate_docs(self) -> None:
        gate = rt.validate_v1_5_1_collect_k_bounded_release_surface_gate()

        self.assertEqual(
            gate["status"],
            "candidate_docs_publicly_discoverable_pending_explicit_release_action",
        )
        self.assertEqual(gate["primitive"], "COLLECT_K_BOUNDED")
        self.assertEqual(gate["classification"], "documented_experimental_public_candidate")
        self.assertTrue(gate["release_surface_docs_ready"])
        self.assertEqual(gate["missing_required_phrases"], ())
        self.assertEqual(gate["present_forbidden_phrases"], ())

    def test_release_surface_gate_required_docs_exist(self) -> None:
        gate = rt.validate_v1_5_1_collect_k_bounded_release_surface_gate()

        self.assertEqual(
            gate["required_docs"],
            rt.V1_5_1_COLLECT_K_BOUNDED_RELEASE_GATE_REQUIRED_DOCS,
        )
        self.assertIn(
            "no whole-app claims",
            rt.V1_5_1_COLLECT_K_BOUNDED_RELEASE_GATE_REQUIRED_PHRASES,
        )
        for relative_path in gate["required_docs"]:
            with self.subTest(relative_path=relative_path):
                self.assertTrue((ROOT / relative_path).exists())

    def test_release_surface_gate_keeps_all_authorization_flags_false(self) -> None:
        gate = rt.validate_v1_5_1_collect_k_bounded_release_surface_gate()

        for flag in (
            "public_docs_change_authorized_by_this_gate",
            "stable_promotion_authorized_by_this_gate",
            "public_speedup_wording_authorized_by_this_gate",
            "zero_copy_wording_authorized_by_this_gate",
            "whole_app_speedup_claim_authorized_by_this_gate",
            "release_tag_action_authorized_by_this_gate",
        ):
            with self.subTest(flag=flag):
                self.assertIs(gate[flag], False)
        self.assertTrue(gate["explicit_release_approval_required"])

    def test_release_surface_gate_claim_boundary_is_narrow(self) -> None:
        gate = rt.validate_v1_5_1_collect_k_bounded_release_surface_gate()
        boundary = gate["claim_boundary"]

        self.assertIn("candidate docs are publicly discoverable", boundary)
        self.assertIn("documented experimental public-candidate", boundary)
        self.assertIn("Goal1421 3-AI public-doc-link consensus", boundary)
        self.assertIn("does not authorize public docs changes", boundary)
        self.assertIn("stable promotion", boundary)
        self.assertIn("speedup wording", boundary)
        self.assertIn("zero-copy wording", boundary)
        self.assertIn("whole-app claims", boundary)
        self.assertIn("release tag action", boundary)

    def test_release_surface_gate_allows_only_review_and_followup_prep(self) -> None:
        gate = rt.validate_v1_5_1_collect_k_bounded_release_surface_gate()

        self.assertEqual(
            gate["allowed_next_actions"],
            (
                "keep_candidate_docs_discoverable_without_broader_claims",
                "continue_python_rtdl_track_hardening",
                "request_explicit_v1_5_1_release_action_if_user_wants_release",
            ),
        )


if __name__ == "__main__":
    unittest.main()
