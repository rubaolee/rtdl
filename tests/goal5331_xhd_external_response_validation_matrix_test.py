import importlib.util
import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "validate_xhd_external_response_intake.py"
)
MATRIX = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5331_external_response_validation_matrix.json"
)


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_xhd_external_response_intake", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5331ExternalResponseValidationMatrixTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = load_validator()
        cls.matrix = json.loads(MATRIX.read_text(encoding="utf-8"))

    def test_matrix_is_synthetic_only(self):
        self.assertFalse(self.matrix["examples_are_real_external_responses"])
        self.assertEqual(
            self.matrix["exit_label"],
            "external_response_validation_matrix_ready__await_real_response",
        )
        forbidden = "\n".join(self.matrix["not_allowed"])
        self.assertIn("real external response", forbidden)
        self.assertIn("external artifacts have been acquired", forbidden)

    def test_all_examples_match_validator_expectations(self):
        for example in self.matrix["examples"]:
            with self.subTest(example=example["id"]):
                payload = json.loads((ROOT / example["path"]).read_text(encoding="utf-8"))
                result = self.validator.classify_intake(payload)
                self.assertEqual(result["valid"], example["expected_valid"])
                self.assertEqual(result["pod_expected"], example["expected_pod"])
                self.assertEqual(result["next_action"], example["expected_next_action"])
                self.assertFalse(result["sufficient_to_claim_exact_input"])
                self.assertFalse(result["claim_boundary"]["exact_paper_dataset_reproduction_claimed"])
                self.assertFalse(result["claim_boundary"]["figure5_reproduction_claimed"])
                self.assertFalse(result["claim_boundary"]["full_paper_reproduction_claimed"])
                self.assertFalse(result["claim_boundary"]["performance_ratio_claimed"])

    def test_examples_cover_positive_negative_and_review_paths(self):
        ids = {example["id"] for example in self.matrix["examples"]}
        self.assertEqual(
            ids,
            {
                "hash_manifest_hashes_only",
                "author_input_archive_private",
                "byte_identical_regeneration_script",
                "acm_listing_no_artifact",
                "water_bg_exact_equivalence_accepted",
                "explicit_non_availability_statement",
            },
        )

    def test_global_claim_boundary_is_fail_closed(self):
        boundary = self.matrix["global_expected_claim_boundary"]
        for key, value in boundary.items():
            self.assertFalse(value, key)
        self.assertFalse(self.matrix["pod_usage"]["used"])
        self.assertFalse(self.matrix["pod_usage"]["expected_next"])


if __name__ == "__main__":
    unittest.main()
