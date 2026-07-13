from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5326_external_artifact_request_package.json"
)


class Goal5326ExternalArtifactRequestPackageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def test_claim_boundary_remains_closed(self) -> None:
        boundary = self.payload["claim_boundary"]
        self.assertTrue(boundary["request_package_claimed"])
        self.assertFalse(boundary["request_sent_claimed"])
        self.assertFalse(boundary["external_artifacts_acquired"])
        self.assertFalse(boundary["acm_supplement_inspected"])
        self.assertFalse(boundary["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(boundary["figure5_reproduction_claimed"])
        self.assertFalse(boundary["full_paper_reproduction_claimed"])
        self.assertFalse(boundary["performance_ratio_claimed"])
        self.assertFalse(boundary["new_rtdl_route_code_added"])
        self.assertFalse(boundary["pod_execution_claimed"])

    def test_request_targets_cover_author_acm_and_review_decision(self) -> None:
        targets = {target["target"]: target for target in self.payload["request_targets"]}
        self.assertIn("paper_authors", targets)
        self.assertIn("acm_access_reviewer", targets)
        self.assertIn("owner_or_external_review", targets)
        self.assertTrue(
            any("sha256" in item for item in targets["paper_authors"]["preferred_evidence"])
        )
        self.assertTrue(
            any("zip file listing" in item for item in targets["acm_access_reviewer"]["preferred_evidence"])
        )
        self.assertTrue(
            any("exact-equivalent" in item for item in targets["owner_or_external_review"]["preferred_evidence"])
        )

    def test_author_request_mentions_all_blocked_families(self) -> None:
        body = "\n".join(self.payload["author_request_message"]["body_lines"])
        self.assertIn("/local/storage/shared/HDDatasets", body)
        self.assertIn("Dragon", body)
        self.assertIn("USADetailedWaterBodies", body)
        self.assertIn("all_nodes", body)
        self.assertIn("BraTS", body)
        self.assertIn("NIfTI-to-point", body)

    def test_acm_request_does_not_claim_contents(self) -> None:
        body = "\n".join(self.payload["acm_supplement_request_message"]["body_lines"])
        self.assertIn("ics26-106.zip", body)
        self.assertIn("HTTP 403", body)
        self.assertIn("top-level file listing", body)
        self.assertIn("will not claim", body)

    def test_response_rules_have_positive_and_negative_paths(self) -> None:
        responses = {
            item["response_type"]: item
            for item in self.payload["minimum_acceptable_positive_responses"]
        }
        self.assertTrue(responses["author_hash_manifest"]["sufficient_to_continue"])
        self.assertTrue(responses["author_input_archive"]["sufficient_to_continue"])
        self.assertTrue(responses["byte_identical_regeneration_script"]["sufficient_to_continue"])
        self.assertTrue(
            responses["acm_supplement_contains_artifact_instructions_or_hashes"][
                "sufficient_to_continue"
            ]
        )
        self.assertFalse(responses["explicit_non_availability_statement"]["sufficient_to_continue"])

    def test_water_bg_equivalence_question_is_fail_closed(self) -> None:
        question = self.payload["water_bg_exact_equivalence_question"]
        self.assertIn("WaterBodies/BG", question["question"])
        self.assertIn("no author WKT hashes", "\n".join(question["evidence_to_present"]))
        self.assertIn("rejected_keep_level_b", question["allowed_reviewer_answers"])
        self.assertEqual(question["default_without_answer"], "rejected_keep_level_b")

    def test_no_pod_and_forbidden_claims(self) -> None:
        pod = self.payload["pod_usage"]
        self.assertFalse(pod["used"])
        self.assertFalse(pod["expected_next"])
        forbidden = "\n".join(self.payload["not_allowed"])
        self.assertIn("author request has been sent", forbidden)
        self.assertIn("ACM supplement contents are known", forbidden)
        self.assertIn("full X-HD paper reproduction", forbidden)
        self.assertIn("performance ratio", forbidden)
        self.assertEqual(
            self.payload["exit_label"],
            "external_artifact_request_package_ready__await_owner_send_or_external_response",
        )


if __name__ == "__main__":
    unittest.main()
