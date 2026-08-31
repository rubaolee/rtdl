from __future__ import annotations

import unittest

from scripts.goal5793_x1_canonical import seal_document
from scripts import goal5793_x3_absorb_terminal_review as absorb


class Goal5793X3TerminalReviewAbsorptionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.first = absorb.build_documents()
        cls.second = absorb.build_documents()
        cls.absorption = absorb.json.loads(cls.first[absorb.ABSORPTION_NAME])
        cls.amendment = absorb.json.loads(cls.first[absorb.AMENDMENT_NAME])
        cls.closure = absorb.json.loads(cls.first[absorb.CLOSURE_NAME])

    def test_01_external_verdict_is_absorbed_without_regrading(self) -> None:
        verdict = self.absorption["external_review_verdict"]
        self.assertEqual((verdict["p0"], verdict["p1"], verdict["p2"], verdict["p3"]), (0, 1, 3, 2))
        self.assertFalse(verdict["verdict_rewritten_by_internal_review"])
        self.assertFalse(verdict["p1_blocks_terminal_marking"])
        self.assertTrue(verdict["p1_blocks_successor_prospective_generalization_preregistration"])

    def test_02_internal_findings_are_preserved_without_changing_verdict(self) -> None:
        register = self.amendment["deduplicated_finding_register"]
        self.assertEqual((register["p0"], register["p1"], register["p2"], register["p3"]), (0, 4, 6, 4))
        self.assertTrue(register["external_verdict_remains_exactly_p0_0_p1_1_p2_3_p3_2"])
        self.assertFalse(self.amendment["historical_transition_conformance"]["exact_transition_receipt_present"])
        self.assertFalse(self.amendment["one_attempt_boundary"]["global_exactly_once_mechanically_enforced"])
        self.assertFalse(self.amendment["controlling_alias_implementation_gap"]["alias_v2_rows_operationally_consumed"])

    def test_03_terminal_label_cannot_be_read_as_scientific_zero_of_three(self) -> None:
        resolution = self.amendment["branch_label_resolution"]
        self.assertTrue(resolution["terminal_negative_means_only_no_further_prospective_generalization_work_inside_goal5793"])
        self.assertFalse(resolution["terminal_negative_means_zero_candidates_or_scientific_zero_of_three"])
        disposition = self.closure["terminal_disposition"]
        self.assertIsNone(disposition["candidate_count"])
        self.assertEqual(disposition["generalization_exam_count"], 0)
        self.assertFalse(disposition["x3_search_completed"])
        self.assertFalse(disposition["candidate_population_constructed"])

    def test_04_only_bounded_offline_a1_is_authorized(self) -> None:
        authorization = self.closure["authorization"]
        self.assertEqual(
            [key for key, value in authorization.items() if value],
            ["goal5793_x3_a1_observed_exposure_and_terminal_record_correction"],
        )
        self.assertFalse(self.closure["open_review_findings"]["current_runtime_alias_implementation_reuse_allowed"])
        self.assertFalse(self.closure["a1_scope"]["successful_a1_review_automatically_authorizes_successor_preregistration"])

    def test_05_all_seals_and_bytes_are_deterministic(self) -> None:
        self.assertEqual(self.first, self.second)
        checks = (
            (self.absorption, "absorption_sha256", absorb.ABSORPTION_DOMAIN),
            (self.amendment, "amendment_sha256", absorb.AMENDMENT_DOMAIN),
            (self.closure, "closure_sha256", absorb.CLOSURE_DOMAIN),
        )
        for document, field, domain in checks:
            self.assertEqual(
                document[field],
                seal_document(document, seal_field=field, domain=domain, version=1),
            )


if __name__ == "__main__":
    unittest.main()
