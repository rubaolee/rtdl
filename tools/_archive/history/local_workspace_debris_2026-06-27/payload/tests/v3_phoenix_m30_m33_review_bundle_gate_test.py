import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "docs" / "reviews" / "call_for_review_phoenix_v3_m30_m33_external_review_bundle_2026-06-23.md"
M33_PACKET = ROOT / "docs" / "reviews" / "call_for_review_phoenix_v3_m33_step4_promotion_ledger_2026-06-23.md"


class V3PhoenixM30M33ReviewBundleGateTest(unittest.TestCase):
    def test_bundle_preserves_non_authorization_boundaries(self):
        text = BUNDLE.read_text(encoding="utf-8")

        for phrase in (
            "Status: `request_m30_m33_external_review_bundle_not_release`",
            "release_authorized: false",
            "public_speedup_claim_authorized: false",
            "broad_v3_faster_than_v2_claim_authorized: false",
            "all_app_pod_spend_authorized: false",
            "v4_work_authorized: false",
            "M22 all-app remains failed for release purposes",
            "does not authorize all-app",
            "Gemini attempted M30, M31, M32, M33, this M30-M33 bundle, and the final",
            "M30-M33 bundle after the review-bundle gate",
            "IneligibleTierError",
            "UNSUPPORTED_CLIENT",
            "those attempts are not consensus",
            "Full local V3 rebuild matrix after M34 also passes",
            "local contract/gate evidence only",
            "does not authorize",
            "V4 work, C ABI work, or",
            "embedding work",
            "accept_m30_m33_continue_trunk_first",
            "accept_with_amendments",
            "blocked_needs_code_or_classification_changes",
            "reject_m30_m33_wrong_direction",
            "explicit non-authorization block",
        ):
            self.assertIn(phrase, text)

        self.assertIn("module_count: 113", text)
        self.assertIn("Ran 590 tests in 73.107s", text)
        self.assertIn(
            "stdout: docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_m34_final_",
            text,
        )
        self.assertIn(
            "stderr: docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_m34_final_",
            text,
        )

        self.assertNotIn("release_authorized: true", text)
        self.assertNotIn("all_app_pod_spend_authorized: true", text)
        self.assertNotIn("public_speedup_claim_authorized: true", text)

    def test_bundle_paths_exist_for_external_reviewer(self):
        text = BUNDLE.read_text(encoding="utf-8")
        paths = sorted(set(re.findall(r"`([^`]+\.(?:md|json|txt|py|ps1))`", text)))

        self.assertGreaterEqual(len(paths), 10)
        missing = [path for path in paths if not (ROOT / path).exists()]
        self.assertEqual(missing, [])

    def test_m33_packet_keeps_local_matrix_separate_from_consensus(self):
        text = M33_PACKET.read_text(encoding="utf-8")

        for phrase in (
            "Status: `request_m33_external_review_not_release`",
            "The full matrix is local contract/gate evidence only.",
            "It is not external",
            "consensus, POD evidence, release authorization, all-app authorization, or a",
            "public performance claim",
            "Gemini interim review",
            "is not consensus",
        ):
            self.assertIn(phrase, text)

        self.assertNotIn("release_authorized: true", text)
        self.assertNotIn("all_app_pod_spend_authorized: true", text)


if __name__ == "__main__":
    unittest.main()
