from __future__ import annotations

import hashlib
import unittest

from scripts.goal5793_x1_canonical import seal_document
from scripts import goal5793_x3_build_terminal_review as review


class Goal5793X3TerminalReviewTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.audit = review.build_audit()
        cls.first = review.build_documents()
        cls.second = review.build_documents()

    def test_01_exact_terminal_events_and_failure_replay(self) -> None:
        self.assertEqual(self.audit["event_counts"], {
            "transaction_start": 1, "http_attempt": 1, "http_200": 1,
            "query_complete": 0, "transaction_complete": 0, "terminal_failure": 1,
        })
        self.assertEqual(self.audit["first_request"]["result_count"], 200)
        self.assertTrue(self.audit["first_request"]["next_cursor_present"])
        self.assertEqual(self.audit["failure_replay"]["reviewed_x2_parser_reason"], "SOURCE_URL_INVALID")

    def test_02_exact_url_denominator_and_first_failure(self) -> None:
        diagnostic = self.audit["failure_replay"]["url_diagnostics"]
        self.assertEqual(diagnostic["invalid_location_value_count"], 217)
        self.assertEqual(diagnostic["scheme_counts"], {"http": 214, "malformed_https": 3, "other": 0})
        self.assertEqual(diagnostic["first_parser_failure"], {
            "result_index": 3, "work_id": "https://openalex.org/W2973457155", "reason": "SOURCE_URL_INVALID",
        })
        self.assertEqual(diagnostic["first_invalid_value_in_failed_work"]["value"], "http://doi.org/10.1107/S2059798319011471")

    def test_03_no_partial_universe_rerun_or_claim_escalation(self) -> None:
        self.assertFalse(any(self.audit["authorization"].values()))
        self.assertFalse(self.audit["absence_proof"]["complete_transcript_exists"])
        self.assertFalse(self.audit["absence_proof"]["complete_component_authority_exists"])
        self.assertEqual(self.audit["absence_proof"]["second_http_call_count"], 0)
        self.assertEqual(self.audit["scientific_disposition"]["generalization_exam_count"], 0)
        self.assertIsNone(self.audit["scientific_disposition"]["candidate_count"])
        self.assertEqual(
            self.audit["scientific_disposition"]["candidate_count_semantics"],
            "UNDEFINED__NO_COMPLETE_POPULATION_EXISTS",
        )
        self.assertTrue(self.audit["scientific_disposition"]["result_is_not_zero_candidates"])
        self.assertTrue(self.audit["scientific_disposition"]["result_is_infrastructure_failure_before_a_complete_population"])
        self.assertFalse(self.audit["presentation_correction"]["v1_was_sent_for_external_review"])
        self.assertFalse(self.audit["presentation_correction"]["provider_call_count_changed"])
        self.assertFalse(self.audit["presentation_correction"]["journal_or_failure_receipt_changed"])

    def test_04_audit_seal_and_full_documents_are_deterministic(self) -> None:
        self.assertEqual(
            self.audit["audit_sha256"],
            seal_document(self.audit, seal_field="audit_sha256", domain=review.AUDIT_DOMAIN, version=review.AUDIT_VERSION),
        )
        self.assertEqual(self.first, self.second)

    def test_05_single_cfr_embeds_exact_journal_and_every_new_root(self) -> None:
        cfr = self.first[review.CFR_NAME].decode("utf-8")
        self.assertEqual(cfr.count("SEND ONLY " + "THIS FILE"), 1)
        self.assertIn("Do not send a packet or second attachment.", cfr)
        fence = "`" * 8
        embedded = {
            review.AUDIT_NAME: self.first[review.AUDIT_NAME],
            review.REPORT_NAME: self.first[review.REPORT_NAME],
            **{path: (review.ROOT / path).read_bytes() for path in [*review.PINNED, *review.SOURCE_ROOTS]},
        }
        for path, raw in embedded.items():
            language = "jsonl" if path.endswith(".jsonl") else "json" if path.endswith(".json") else "markdown" if path.endswith(".md") else "python"
            exact = f"## Embedded `{path}`\n\n{fence}{language}\n{raw.decode('utf-8').rstrip(chr(10))}\n{fence}"
            self.assertEqual(cfr.count(exact), 1, path)
        self.assertEqual(hashlib.sha256(self.first[review.CFR_NAME]).hexdigest(), hashlib.sha256(self.second[review.CFR_NAME]).hexdigest())


if __name__ == "__main__":
    unittest.main()
