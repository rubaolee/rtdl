from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]


class Goal1419V151CollectKReleaseSurfaceProposalTest(unittest.TestCase):
    def test_proposal_recommends_documented_experimental_candidate_only(self) -> None:
        proposal = rt.validate_v1_5_1_collect_k_bounded_release_surface_proposal()

        self.assertEqual(
            proposal["status"],
            "proposal_ready_for_external_release_surface_review",
        )
        self.assertEqual(proposal["primitive"], "COLLECT_K_BOUNDED")
        self.assertEqual(
            proposal["proposed_classification"],
            "documented_experimental_public_candidate",
        )
        self.assertTrue(proposal["evidence_ready"])
        self.assertIn("document COLLECT_K_BOUNDED", proposal["proposed_public_surface"])

    def test_proposal_does_not_authorize_public_changes_or_claims(self) -> None:
        proposal = rt.validate_v1_5_1_collect_k_bounded_release_surface_proposal()

        for flag in (
            "public_docs_change_authorized_by_this_proposal",
            "stable_promotion_authorized_by_this_proposal",
            "public_speedup_wording_authorized_by_this_proposal",
            "zero_copy_wording_authorized_by_this_proposal",
            "whole_app_speedup_claim_authorized_by_this_proposal",
            "release_tag_action_authorized_by_this_proposal",
        ):
            with self.subTest(flag=flag):
                self.assertIs(proposal[flag], False)
        self.assertIn("stable primitive promotion", proposal["not_proposed"])
        self.assertIn("public speedup wording", proposal["not_proposed"])
        self.assertIn("zero-copy wording", proposal["not_proposed"])

    def test_proposal_requires_external_release_surface_review(self) -> None:
        proposal = rt.validate_v1_5_1_collect_k_bounded_release_surface_proposal()

        self.assertEqual(proposal["required_review"], "3-AI release-surface review")
        self.assertEqual(proposal["required_review_partners"], ("claude", "gemini"))
        self.assertEqual(
            proposal["forbidden_wording"],
            rt.V1_5_1_COLLECT_K_BOUNDED_RELEASE_SURFACE_FORBIDDEN_WORDING,
        )
        self.assertIn("request_external_release_surface_review", proposal["allowed_next_actions"])

    def test_proposal_evidence_files_exist(self) -> None:
        proposal = rt.validate_v1_5_1_collect_k_bounded_release_surface_proposal()

        for relative_path in (
            proposal["readiness_consensus"],
            proposal["parity_consensus"],
            proposal["benchmark_consensus"],
        ):
            with self.subTest(relative_path=relative_path):
                self.assertTrue((ROOT / relative_path).exists())

    def test_proposal_claim_boundary_is_narrow(self) -> None:
        proposal = rt.validate_v1_5_1_collect_k_bounded_release_surface_proposal()
        boundary = proposal["claim_boundary"]

        self.assertIn("proposal only", boundary)
        self.assertIn("documented experimental public-candidate", boundary)
        self.assertIn("does not authorize public docs changes", boundary)
        self.assertIn("stable promotion", boundary)
        self.assertIn("speedup wording", boundary)
        self.assertIn("zero-copy wording", boundary)
        self.assertIn("release tag action", boundary)
        self.assertIn("whole-app claims", boundary)


if __name__ == "__main__":
    unittest.main()
