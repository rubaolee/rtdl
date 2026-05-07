import unittest

import rtdsl as rt


class Goal1466V153ReducedCopyPostReviewGateTest(unittest.TestCase):
    def test_external_review_is_satisfied_but_claims_remain_blocked(self) -> None:
        contract = rt.validate_v1_5_3_reduced_copy_contract()

        self.assertEqual(
            contract["status"],
            "reduced_copy_internal_evidence_reviewed_parity_accepted_claims_blocked",
        )
        self.assertIn("external_ai_review_before_public_claims", contract["satisfied_evidence"])
        self.assertIn("embree_optix_same_contract_parity_where_claimed", contract["satisfied_evidence"])
        self.assertEqual(contract["missing_evidence"], ())

        for flag in (
            "true_zero_copy_authorized",
            "public_speedup_wording_authorized",
            "whole_app_speedup_claim_authorized",
            "stable_public_primitive_authorized",
            "release_action_authorized",
        ):
            with self.subTest(flag=flag):
                self.assertIs(contract[flag], False)

    def test_external_review_artifacts_exist(self) -> None:
        from pathlib import Path

        root = Path(__file__).resolve().parents[1]
        for relative_path in (
            "docs/handoff/goal1465_v1_5_3_reduced_copy_external_review_request_2026-05-07.md",
            "docs/reports/claude_goal1465_v1_5_3_reduced_copy_external_review_2026-05-07.md",
            "docs/reports/gemini_goal1465_v1_5_3_reduced_copy_external_review_2026-05-07.md",
            "docs/reports/three_ai_goal1465_v1_5_3_reduced_copy_external_review_consensus_2026-05-07.md",
        ):
            with self.subTest(relative_path=relative_path):
                self.assertTrue((root / relative_path).exists())


if __name__ == "__main__":
    unittest.main()
