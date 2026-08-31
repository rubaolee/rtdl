from __future__ import annotations

from copy import deepcopy
import unittest

from scripts import goal5793_x1_validate_owner_exposure_disclosure as disclosure
from scripts.goal5793_x1_canonical import seal_document


def reseal(value: dict) -> None:
    value["disclosure_sha256"] = seal_document(
        value,
        seal_field="disclosure_sha256",
        domain="rtdl.goal5793.x1.owner_off_repository_exposure_disclosure",
        version=1,
    )


class OwnerExposureDisclosureTest(unittest.TestCase):
    def test_none_template_is_bounded_and_valid(self) -> None:
        value = disclosure.build_none_template()
        self.assertEqual(disclosure.validate(value), value)
        self.assertFalse(value["claim_boundary"]["complete_author_mental_exposure_claimed"])
        self.assertFalse(value["claim_boundary"]["absence_from_disclosure_proves_never_seen"])
        self.assertTrue(value["declared_scope"]["reasonable_recall_not_omniscience"])
        self.assertTrue(value["claim_boundary"]["later_recalled_preexisting_exposure_terminates_single_expansion_without_replacement"])

    def test_none_cannot_hide_rows(self) -> None:
        value = disclosure.build_none_template()
        value["disclosures"].append({})
        reseal(value)
        with self.assertRaisesRegex(disclosure.DisclosureError, "none_statement_has_rows"):
            disclosure.validate(value)

    def test_listed_row_is_permanently_ineligible(self) -> None:
        value = disclosure.build_none_template()
        value["statement"] = "ALL_KNOWN_ITEMS_LISTED_AFTER_REASONABLE_RECALL"
        value["disclosures"] = [{
            "title": "Example",
            "author": "Example Author",
            "year": "2025",
            "doi": "10.1234/example",
            "arxiv_id": None,
            "url": None,
            "exposure_kind": "DESIGN_INPUT",
            "notes": None,
            "permanently_selection_ineligible": True,
        }]
        reseal(value)
        self.assertEqual(disclosure.validate(value), value)

    def test_listed_row_requires_mechanical_identity(self) -> None:
        value = disclosure.build_none_template()
        value["statement"] = "ALL_KNOWN_ITEMS_LISTED_AFTER_REASONABLE_RECALL"
        value["disclosures"] = [{
            "title": "Example",
            "author": None,
            "year": None,
            "doi": None,
            "arxiv_id": None,
            "url": None,
            "exposure_kind": "READ",
            "notes": None,
            "permanently_selection_ineligible": True,
        }]
        reseal(value)
        with self.assertRaisesRegex(disclosure.DisclosureError, "identity_insufficient"):
            disclosure.validate(value)

    def test_resealed_overclaim_is_rejected(self) -> None:
        value = disclosure.build_none_template()
        value["claim_boundary"]["complete_author_mental_exposure_claimed"] = True
        reseal(value)
        with self.assertRaisesRegex(disclosure.DisclosureError, "claim_boundary_mismatch"):
            disclosure.validate(value)

    def test_resealed_authorization_escalation_is_rejected(self) -> None:
        value = disclosure.build_none_template()
        value["authorization"]["x2_search"] = True
        reseal(value)
        with self.assertRaisesRegex(disclosure.DisclosureError, "authorization_mismatch"):
            disclosure.validate(value)


if __name__ == "__main__":
    unittest.main()
