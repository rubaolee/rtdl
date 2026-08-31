from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest

from scripts.goal5793_x1_canonical import seal_document
from scripts import goal5793_x2_build_external_review_entry as builder


ROOT = Path(__file__).resolve().parents[1]


class Goal5793X2ExternalReviewEntryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.documents = builder.build_documents()

    def test_01_deterministic(self) -> None:
        self.assertEqual(self.documents, builder.build_documents())

    def test_02_result_seal_and_all_authorizations_false(self) -> None:
        result = json.loads(self.documents[builder.RESULT_NAME].decode("utf-8"))
        self.assertEqual(
            result["result_sha256"],
            seal_document(result, seal_field="result_sha256", domain=builder.RESULT_DOMAIN, version=1),
        )
        self.assertFalse(any(result["authorization"].values()))
        self.assertEqual(result["evidence"]["generality_exam_count"], 0)
        self.assertEqual(result["evidence"]["usability_study_count"], 0)

    def test_03_single_cfr_embeds_exact_result_report_and_self_review(self) -> None:
        cfr = self.documents[builder.CFR_NAME].decode("utf-8")
        self.assertEqual(cfr.count("SEND ONLY THIS FILE"), 1)
        self.assertNotIn("SEND THE PACKET", cfr)
        for name in (builder.RESULT_NAME, builder.REPORT_NAME, builder.SELF_REVIEW_NAME):
            digest = hashlib.sha256(self.documents[name]).hexdigest()
            self.assertIn(digest, cfr)
        self.assertIn(self.documents[builder.RESULT_NAME].decode("utf-8").rstrip(), cfr)
        self.assertIn(self.documents[builder.REPORT_NAME].decode("utf-8").rstrip(), cfr)
        self.assertIn(self.documents[builder.SELF_REVIEW_NAME].decode("utf-8").rstrip(), cfr)

    def test_04_prewrite_outputs_absent(self) -> None:
        for name in self.documents:
            self.assertFalse((ROOT / "history/internal_docs" / name).exists())


if __name__ == "__main__":
    unittest.main()
