from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal5840_build_final_authority.py"


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "goal5840_build_final_authority", SCRIPT
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Goal5840 final authority builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Goal5840FinalAuthorityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = _load_module()
        cls.authority = cls.module.build_authority()

    def test_stored_authority_rederives_exactly(self):
        stored = self.module._load(self.module.AUTHORITY_PATH)
        self.assertEqual(stored, self.authority)
        self.assertEqual(
            stored["authority_sha256"], self.module._authority_seal(stored)
        )

    def test_completion_is_exactly_bounded(self):
        self.assertEqual(
            self.authority["status"],
            "PASS__GOAL5840_COMPLETE_AT_PREREGISTERED_BOUNDED_REFINEMENT_SCOPE",
        )
        self.assertEqual(
            self.authority["result"],
            {
                "formal_attempt_number": 7,
                "route_group_count": 3,
                "mode_count": 4,
                "true_optix_mode_count": 4,
                "output_match_count": 4,
                "independent_property_pass_count": 20,
                "unique_mutation_count": 15,
                "mutation_application_count": 20,
                "mutation_rejection_count": 20,
                "frozen_core_changed_file_count": 0,
                "summary_sha256": self.module.SUMMARY_SHA256,
                "verification_sha256": self.module.VERIFICATION_SHA256,
            },
        )
        boundary = self.authority["claim_boundary"]
        self.assertTrue(boundary["three_bounded_routes_four_modes_only"])
        self.assertTrue(
            boundary["separate_target_side_structural_refinement_evidence"]
        )
        self.assertFalse(boundary["general_compiler_soundness_theorem"])
        self.assertFalse(boundary["arbitrary_callback_ir"])
        self.assertFalse(boundary["performance_or_speedup"])
        self.assertFalse(boundary["external_review_or_consensus"])

    def test_resealed_result_count_drift_is_rejected(self):
        result = self.module._load(self.module.RESULT_PATH)
        result["true_optix_mode_count"] = 3
        result["summary_sha256"] = self.module._domain_seal(
            result, "summary_sha256", self.module.SUMMARY_DOMAIN
        )
        with self.assertRaisesRegex(RuntimeError, "summary differs"):
            self.module._validate_result(result)

    def test_resealed_mutation_acceptance_is_rejected(self):
        mutation = self.module._load(self.module.MUTATION_PATH)
        mutation["applications"][0]["checker_verdict"] = "ACCEPT"
        mutation["report_sha256"] = self.module._domain_seal(
            mutation, "report_sha256", self.module.MUTATION_DOMAIN
        )
        with self.assertRaisesRegex(RuntimeError, "not rejected"):
            self.module._validate_mutations(mutation)

    def test_authority_seal_rejects_semantic_drift(self):
        tampered = copy.deepcopy(self.authority)
        tampered["claim_boundary"]["general_compiler_soundness_theorem"] = True
        self.assertNotEqual(
            tampered["authority_sha256"], self.module._authority_seal(tampered)
        )


if __name__ == "__main__":
    unittest.main()
