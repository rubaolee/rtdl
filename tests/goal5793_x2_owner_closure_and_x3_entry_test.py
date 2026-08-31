from __future__ import annotations

import copy
import unittest

from scripts.goal5793_x1_canonical import seal_document
from scripts import goal5793_x2_build_owner_closure_and_x3_entry as closure


class Goal5793X2OwnerClosureAndX3EntryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = closure.build_closure()

    def test_01_closure_is_deterministic_and_sealed(self) -> None:
        self.assertEqual(self.document, closure.build_closure())
        self.assertEqual(
            self.document["closure_sha256"],
            seal_document(self.document, seal_field="closure_sha256", domain=closure.DOMAIN, version=1),
        )

    def test_02_controlling_bindings_are_exact_and_v1_is_not_stage_of_record(self) -> None:
        controlling = self.document["controlling_implementations"]
        self.assertEqual(controlling["preentropy_enumerator"]["sha256"], closure.PINNED["scripts/goal5793_x2_preentropy_enumerator_v2.py"][1])
        self.assertEqual(controlling["structural_friction"]["sha256"], closure.PINNED["scripts/goal5793_x2_structural_friction_v2.py"][1])
        self.assertEqual(controlling["exposure_alias_authority"]["sha256"], closure.PINNED["history/internal_docs/goal5793_x2_exposure_alias_authority_v2_20260822.json"][1])
        self.assertFalse(controlling["v1_predecessors_may_produce_a_stage_of_record_output"])
        self.assertEqual(controlling["any_future_enumeration_or_friction_output_not_produced_by_the_named_successors"], "INVALID__NOT_A_STAGE_OF_RECORD")

    def test_03_only_x3_provider_search_is_authorized(self) -> None:
        authorization = self.document["authorization"]
        self.assertTrue(authorization["x3_provider_search"])
        self.assertEqual([key for key, value in authorization.items() if value], ["x3_provider_search"])

    def test_04_open_p2s_cannot_be_hidden_or_used_as_claims(self) -> None:
        findings = self.document["p2_p3_absorption"]
        self.assertFalse(findings["friction_v2_device_language_and_CU_lowercase_coverage_complete"])
        self.assertFalse(findings["friction_v2_C_CPP_literal_masker_sound_for_digit_separators_and_unterminated_literals"])
        self.assertFalse(findings["friction_number_may_appear_in_any_written_claim"])
        self.assertFalse(findings["science_row_set_digest_bound_to_harvested_components"])
        self.assertFalse(findings["sampling_frame_funnel_ledger_complete"])

    def test_05_binding_or_authorization_mutation_changes_seal(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["closure_sha256"] = ""
        changed["controlling_implementations"]["v1_predecessors_may_produce_a_stage_of_record_output"] = True
        changed_seal = seal_document(changed, seal_field="closure_sha256", domain=closure.DOMAIN, version=1)
        self.assertNotEqual(changed_seal, self.document["closure_sha256"])


if __name__ == "__main__":
    unittest.main()
