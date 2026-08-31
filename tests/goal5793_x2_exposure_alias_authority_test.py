from __future__ import annotations

import base64
import hashlib
import json
import unittest

from scripts import goal5793_x2_build_exposure_alias_authority as builder
from scripts import goal5793_x2_offline_core as core


class Goal5793X2ExposureAliasAuthorityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = builder.build_authority()

    def test_01_exact_186_rows_and_risk_counts(self) -> None:
        counts = self.document["counts"]
        self.assertEqual(counts["bibliography_rows"], 186)
        self.assertEqual(counts["strong_identifier_rows"], 7)
        self.assertEqual(counts["no_strong_identifier_rows"], 179)
        self.assertEqual(counts["selection_eligible_rows"], 0)
        self.assertEqual(counts["network_or_live_lookup_count"], 0)

    def test_02_every_row_preserves_required_matching_fields(self) -> None:
        for row in self.document["rows"]:
            self.assertTrue(row["title_exact_bibtex"])
            self.assertTrue(row["authors_exact_bibtex"])
            self.assertIn("year_exact_bibtex", row)
            self.assertIn("venue_exact_fields", row)
            self.assertIn("all_fields_exact", row)
            self.assertIn("protocol_aliases", row)
            self.assertFalse(row["selection_eligible"])
            self.assertIn(
                row["matching_risk"],
                {
                    "STRONG_IDENTIFIER_PLUS_CONSERVATIVE_TEXT_ALIASES",
                    "NO_STRONG_IDENTIFIER__CONSERVATIVE_TITLE_AUTHOR_YEAR_MATCHING_REQUIRED__MISS_TERMINATES_EXPANSION_IF_LATER_DISCOVERED",
                },
            )

    def test_03_embedded_sample_bib_rehashes(self) -> None:
        payload = base64.b64decode(self.document["sample_bib_base64"], validate=True)
        self.assertEqual(len(payload), 63148)
        self.assertEqual(hashlib.sha256(payload).hexdigest(), builder.SAMPLE_BIB_SHA256)

    def test_04_deterministic_and_all_authorizations_false(self) -> None:
        self.assertEqual(self.document, builder.build_authority())
        self.assertFalse(any(self.document["authorization"].values()))
        self.assertFalse(self.document["scope"]["complete_author_mental_exposure_claimed"])
        self.assertFalse(self.document["scope"]["unseen_blind_or_held_out_claimed"])

    def test_05_protocol_fallback_matches_without_strong_id(self) -> None:
        reference = next(row for row in self.document["rows"] if not row["strong_identifier_present"] and row["year_normalized"])
        alias_rows = core.build_exposure_alias_rows(json.loads(builder.X1_REGISTRY.read_text(encoding="utf-8")))
        alias = next(row for row in alias_rows if row["citation_key"] == reference["citation_key"])
        expected = reference["protocol_aliases"]["fallback_sha256"]
        self.assertIn(expected, alias["fallback_sha256"])

    def test_06_every_available_fallback_alias_is_mechanically_excluding(self) -> None:
        alias_rows = core.build_exposure_alias_rows(json.loads(builder.X1_REGISTRY.read_text(encoding="utf-8")))
        checked = 0
        for index, alias in enumerate(alias_rows):
            if not alias["fallback_sha256"]:
                continue
            node = {
                "node_id": f"fallback-{index}", "provider": "OpenAlex Works API", "term": "OptiX",
                "query_index": 0, "page_index": 0, "ordinal": 0, "record_sha256": "0" * 64,
                "doi": None, "arxiv": None, "openalex": f"W{900000 + index}",
                "title": alias["title"], "first_author": alias["first_author"], "year": alias["year"],
                "fallback_sha256": alias["fallback_sha256"][0], "raw_title": alias["title"],
                "raw_first_author": alias["first_author"],
            }
            component = core.build_identity_components([node], alias_rows)[0]
            self.assertEqual(component["identity_disposition"], "PREEXISTING_PROJECT_EXPOSURE__SELECTION_INELIGIBLE")
            self.assertTrue(any(match["citation_key"] == alias["citation_key"] for match in component["exposure_matches"]))
            checked += 1
        self.assertEqual(checked, 183)

    def test_07_every_strong_identifier_alias_is_mechanically_excluding(self) -> None:
        alias_rows = core.build_exposure_alias_rows(json.loads(builder.X1_REGISTRY.read_text(encoding="utf-8")))
        checked = 0
        for index, alias in enumerate(alias_rows):
            for field in ("doi", "arxiv", "openalex"):
                for value in alias[field]:
                    node = {
                        "node_id": f"strong-{index}-{field}-{checked}", "provider": "OpenAlex Works API", "term": "OptiX",
                        "query_index": 0, "page_index": 0, "ordinal": 0, "record_sha256": "0" * 64,
                        "doi": value if field == "doi" else None, "arxiv": value if field == "arxiv" else None,
                        "openalex": value if field == "openalex" else None, "title": f"unrelated title {index}",
                        "first_author": "unrelated", "year": 2026,
                        "fallback_sha256": core.fallback_sha256(f"unrelated title {index}", "unrelated", 2026),
                        "raw_title": f"Unrelated Title {index}", "raw_first_author": "Unrelated",
                    }
                    component = core.build_identity_components([node], alias_rows)[0]
                    self.assertEqual(component["identity_disposition"], "PREEXISTING_PROJECT_EXPOSURE__SELECTION_INELIGIBLE")
                    checked += 1
        self.assertGreaterEqual(checked, 7)

    def test_08_cross_component_fallback_collision_never_merges_or_becomes_eligible(self) -> None:
        fallback = core.fallback_sha256("Same Ambiguous Work", "Smith", 2025)
        base = {
            "provider": "OpenAlex Works API", "term": "OptiX", "query_index": 0, "page_index": 0,
            "ordinal": 0, "record_sha256": "0" * 64, "doi": None, "arxiv": None,
            "title": "same ambiguous work", "first_author": "smith", "year": 2025,
            "fallback_sha256": fallback, "raw_title": "Same Ambiguous Work", "raw_first_author": "Smith",
        }
        nodes = [dict(base, node_id="one", openalex="W910001"), dict(base, node_id="two", openalex="W910002")]
        components = core.build_identity_components(nodes, [])
        self.assertEqual(len(components), 2)
        self.assertTrue(all(row["fallback_identity_ambiguous"] for row in components))
        self.assertTrue(all(row["identity_disposition"] == "FALLBACK_IDENTITY_AMBIGUOUS__SELECTION_INELIGIBLE" for row in components))


if __name__ == "__main__":
    unittest.main()
