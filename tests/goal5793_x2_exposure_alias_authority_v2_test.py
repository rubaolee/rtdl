from __future__ import annotations

import unittest

from scripts.goal5793_x1_canonical import seal_document
from scripts import goal5793_x2_build_exposure_alias_authority_v2 as v2


class Goal5793X2ExposureAliasAuthorityV2Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.authority = v2.build_authority()

    def test_01_exact_7_176_3_split(self) -> None:
        counts = self.authority["counts"]
        self.assertEqual(counts["strong_identifier_rows"], 7)
        self.assertEqual(counts["weak_identifier_rows_with_author_year_fallback_path"], 176)
        self.assertEqual(counts["weak_identifier_rows_exact_title_only"], 3)
        self.assertEqual(counts["rows_with_nested_protocol_alias_projection"], 186)

    def test_02_operational_alias_fields_are_nested_not_redacted(self) -> None:
        self.assertIn("FULL_NESTED_ALIAS_PROJECTION", self.authority["status"])
        self.assertFalse(self.authority["legibility_correction"]["published_v1_mechanism_inert"])
        for row in self.authority["rows"]:
            self.assertIn("first_author_family_normalized", row["protocol_aliases"])
            self.assertIn("year", row["protocol_aliases"])
            self.assertIn("fallback_sha256", row["protocol_aliases"])
            self.assertFalse(row["selection_eligible"])

    def test_03_domain_separated_seal(self) -> None:
        self.assertEqual(
            self.authority["authority_sha256"],
            seal_document(self.authority, seal_field="authority_sha256", domain=v2.DOMAIN, version=2),
        )

    def test_04_no_authorization_escalation(self) -> None:
        self.assertFalse(any(self.authority["authorization"].values()))
        self.assertEqual(self.authority["scope"]["generalization_or_usability_evidence_count"], 0)


if __name__ == "__main__":
    unittest.main()
