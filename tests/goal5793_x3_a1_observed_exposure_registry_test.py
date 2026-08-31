from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from scripts import goal5793_x3_a1_build_observed_exposure_registry as build
from scripts import goal5793_x3_a1_independent_verify_observed_exposure_registry as verify


class Goal5793X3A1ObservedExposureRegistryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = build.build_registry()

    def test_01_exact_200_rows_and_no_selection_eligibility(self) -> None:
        counts = self.registry["counts"]
        self.assertEqual(counts["observed_rows"], 200)
        self.assertEqual(counts["unique_openalex_ids"], 200)
        self.assertEqual(counts["unique_canonical_work_identities"], 200)
        self.assertEqual(counts["selection_eligible_rows"], 0)
        self.assertTrue(all(row["selection_eligible"] is False for row in self.registry["rows"]))

    def test_02_strong_and_fallback_counts_are_frozen(self) -> None:
        self.assertEqual(self.registry["counts"]["doi_rows"], 195)
        self.assertEqual(self.registry["counts"]["arxiv_rows"], 0)
        self.assertEqual(self.registry["counts"]["openalex_rows"], 200)
        self.assertEqual(self.registry["counts"]["fallback_rows"], 199)
        self.assertEqual(self.registry["counts"]["fallback_unavailable_rows"], 1)
        missing = [row for row in self.registry["rows"] if row["fallback_sha256"] is None]
        self.assertEqual([row["openalex"] for row in missing], ["W3106156689"])
        self.assertEqual(
            missing[0]["fallback_unavailable_reason"],
            "TITLE_MISSING_IN_OBSERVED_PROVIDER_BYTES__NO_SYNTHETIC_SUBSTITUTE",
        )

    def test_03_independent_recount_matches_exactly(self) -> None:
        result = verify.verify_registry_document(self.registry)
        self.assertEqual(result["counts"], self.registry["counts"])
        self.assertEqual(result["rows_sha256"], self.registry["rows_sha256"])

    def test_04_delete_mutate_reorder_and_eligibility_attacks_reject(self) -> None:
        attacks = []
        deleted = copy.deepcopy(self.registry)
        deleted["rows"].pop()
        attacks.append(deleted)
        reordered = copy.deepcopy(self.registry)
        reordered["rows"][0], reordered["rows"][1] = reordered["rows"][1], reordered["rows"][0]
        attacks.append(reordered)
        eligible = copy.deepcopy(self.registry)
        eligible["rows"][0]["selection_eligible"] = True
        attacks.append(eligible)
        doi = copy.deepcopy(self.registry)
        doi["rows"][0]["doi"] = "10.9999/forged"
        attacks.append(doi)
        fallback = copy.deepcopy(self.registry)
        fallback["rows"][0]["fallback_sha256"] = "0" * 64
        attacks.append(fallback)
        for attack in attacks:
            with self.assertRaises(verify.VerificationError):
                verify.verify_registry_document(attack)

    def test_05_reseal_cannot_hide_row_forgery(self) -> None:
        forged = copy.deepcopy(self.registry)
        forged["rows"][0]["selection_eligible"] = True
        forged["rows_sha256"] = verify._sha(verify.canonical_json_bytes(forged["rows"]))
        forged["registry_sha256"] = verify.seal_document(
            forged,
            seal_field="registry_sha256",
            domain=verify.REGISTRY_DOMAIN,
            version=1,
        )
        with self.assertRaisesRegex(verify.VerificationError, "REGISTRY_ROWS_MISMATCH"):
            verify.verify_registry_document(forged)

    def test_06_journal_byte_mutation_rejects_before_derivation(self) -> None:
        payload = build.JOURNAL.read_bytes()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "journal.jsonl"
            mutated = bytearray(payload)
            mutated[0] ^= 1
            path.write_bytes(mutated)
            with self.assertRaisesRegex(build.RegistryError, "JOURNAL_IDENTITY_MISMATCH"):
                build.build_registry(path)

    def test_07_stored_registry_if_present_is_byte_exact(self) -> None:
        if not build.OUTPUT.exists():
            self.skipTest("stored registry not written yet")
        stored = json.loads(build.OUTPUT.read_text(encoding="utf-8", errors="strict"))
        self.assertEqual(stored, self.registry)


if __name__ == "__main__":
    unittest.main()
