from __future__ import annotations

import copy
import unittest

from scripts import goal5793_x2_build_nist_normative_authority as builder
from scripts.goal5793_x1_canonical import seal_document


class Goal5793X2NistNormativeAuthorityTest(unittest.TestCase):
    def test_01_deterministic_authority_and_shared_seal(self) -> None:
        first = builder.build_authority()
        second = builder.build_authority()
        self.assertEqual(first, second)
        self.assertEqual(
            first["authority_sha256"],
            seal_document(first, seal_field="authority_sha256", domain=builder.AUTHORITY_DOMAIN, version=1),
        )
        self.assertTrue(first["implementation"]["all_new_seals_import_shared_canonical"])

    def test_02_xsd_contract_and_three_conflicts_are_exact(self) -> None:
        authority = builder.build_authority()
        self.assertEqual(authority["xsd_contract"]["schema_version"], "2.0.0")
        self.assertEqual(len(authority["xsd_contract"]["pulse_field_order"]), 15)
        self.assertEqual(len(authority["source_interpretation_boundary"]["conflicts"]), 3)
        self.assertEqual(authority["source_interpretation_boundary"]["xsd_scope"], "TRANSPORT_STRUCTURE_AND_FIELD_LEXICAL_CONSTRAINTS_ONLY")

    def test_03_live_boundary_and_every_authorization_remain_false(self) -> None:
        authority = builder.build_authority()
        self.assertFalse(authority["unresolved_live_boundary"]["exact_live_nist_root_and_intermediate_bundle_issued"])
        self.assertFalse(authority["claim_boundary"]["live_nist_verifier_complete"])
        self.assertFalse(any(authority["authorization"].values()))
        self.assertEqual(authority["activity"]["beacon_calls"], 0)

    def test_04_coordinated_live_claim_escalation_changes_seal_and_is_detectable(self) -> None:
        authority = builder.build_authority()
        mutated = copy.deepcopy(authority)
        mutated["claim_boundary"]["live_nist_verifier_complete"] = True
        self.assertNotEqual(
            authority["authority_sha256"],
            seal_document(mutated, seal_field="authority_sha256", domain=builder.AUTHORITY_DOMAIN, version=1),
        )


if __name__ == "__main__":
    unittest.main()

