import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SUMMARY = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5329_external_response_intake_protocol.json"
)
TEMPLATE = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "requests"
    / "external_response_intake_template.json"
)
INCOMING_README = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "requests"
    / "incoming"
    / "README.md"
)


class Goal5329ExternalResponseIntakeProtocolTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with SUMMARY.open("r", encoding="utf-8") as f:
            cls.summary = json.load(f)
        with TEMPLATE.open("r", encoding="utf-8") as f:
            cls.template = json.load(f)
        cls.incoming_text = INCOMING_README.read_text(encoding="utf-8")

    def test_all_goal5326_response_types_are_supported(self):
        types = {entry["response_type"] for entry in self.summary["supported_response_types"]}
        self.assertEqual(
            types,
            {
                "author_hash_manifest",
                "author_input_archive",
                "byte_identical_regeneration_script",
                "acm_supplement_artifact_instructions",
                "exact_equivalence_verdict",
                "explicit_non_availability_statement",
                "other",
            },
        )

    def test_each_response_type_has_minimum_fields_and_boundaries(self):
        for entry in self.summary["supported_response_types"]:
            self.assertTrue(entry["minimum_fields"], entry["response_type"])
            self.assertIn("sufficient_to_run_pod_gate", entry)
            self.assertIn("sufficient_to_claim_exact_input", entry)

    def test_intake_template_is_fail_closed(self):
        t = self.template
        self.assertEqual(t["status"], "template_not_filled")
        self.assertFalse(t["validation_status"]["validated_by_codex"])
        self.assertFalse(t["validation_status"]["sufficient_to_run_pod_gate"])
        self.assertFalse(t["validation_status"]["sufficient_to_claim_exact_input"])
        self.assertTrue(t["validation_status"]["requires_external_review_before_use"])
        for key in [
            "request_sent_claimed",
            "external_response_received",
            "external_artifacts_acquired",
            "acm_supplement_inspected",
            "exact_equivalence_accepted",
            "exact_paper_dataset_reproduction_claimed",
            "figure5_reproduction_claimed",
            "full_paper_reproduction_claimed",
            "performance_ratio_claimed",
        ]:
            self.assertFalse(t["claim_boundary"][key])

    def test_intake_decision_rules_map_positive_and_negative_responses(self):
        rules = "\n".join(rule["condition"] + " " + rule["next_action"] for rule in self.summary["intake_decision_rules"])
        self.assertIn("verified author input bytes or archive", rules)
        self.assertIn("hashes but no bytes", rules)
        self.assertIn("byte-identical regeneration procedure", rules)
        self.assertIn("ACM supplement artifact instructions", rules)
        self.assertIn("accepts WaterBodies/BG exact-equivalence", rules)
        self.assertIn("rejects exact-equivalence", rules)
        self.assertIn("keep full-paper claims blocked", rules)

    def test_privacy_boundary_prevents_committing_raw_private_messages(self):
        privacy = self.summary["privacy_and_repository_boundary"]
        self.assertTrue(privacy["raw_private_messages_should_not_be_committed"])
        self.assertTrue(privacy["requires_sender_permission_for_raw_content"])
        self.assertIn("minimal metadata", privacy["allowed_repo_record"])
        self.assertIn("raw private material outside the repo", self.incoming_text)

    def test_claim_boundary_and_pod_boundary(self):
        boundary = self.summary["claim_boundary"]
        self.assertTrue(boundary["intake_protocol_claimed"])
        for key in [
            "external_response_received",
            "external_artifacts_acquired",
            "acm_supplement_inspected",
            "exact_equivalence_accepted",
            "exact_paper_dataset_reproduction_claimed",
            "figure5_reproduction_claimed",
            "full_paper_reproduction_claimed",
            "performance_ratio_claimed",
            "pod_execution_claimed",
        ]:
            self.assertFalse(boundary[key])
        self.assertFalse(self.summary["pod_usage"]["used"])
        self.assertFalse(self.summary["pod_usage"]["expected_next"])

    def test_incoming_readme_contains_allowed_categories_and_fail_closed_rule(self):
        for needle in [
            "author_hash_manifest",
            "author_input_archive",
            "byte_identical_regeneration_script",
            "acm_supplement_artifact_instructions",
            "exact_equivalence_verdict",
            "explicit_non_availability_statement",
            "No response may upgrade X-HD",
        ]:
            self.assertIn(needle, self.incoming_text)


if __name__ == "__main__":
    unittest.main()
