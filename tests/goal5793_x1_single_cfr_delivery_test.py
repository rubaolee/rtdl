from __future__ import annotations

import json
import unittest

from scripts import goal5793_x1_correct_single_cfr_delivery as correction
from scripts.goal5793_x1_canonical import seal_document


class Goal5793X1SingleCfrDeliveryTest(unittest.TestCase):
    def test_exactly_one_cfr_is_authorized_for_delivery(self) -> None:
        docs = correction.build_documents()
        cfr = docs[correction.CFR_NAME].decode("utf-8")
        self.assertEqual(cfr.count("SEND ONLY THIS CFR FILE TO THE REVIEWER"), 1)
        self.assertIn("Do not send a packet", cfr)
        self.assertIn("All supporting materials are already prepared at the exact local paths", cfr)

    def test_result_v2_is_sealed_and_all_authorization_false(self) -> None:
        docs = correction.build_documents()
        result = json.loads(docs[correction.RESULT_NAME])
        self.assertEqual(result["schema"], "rtdl.goal5793.x1.external_review_result.v2")
        self.assertEqual(result["result_sha256"], seal_document(
            result, seal_field="result_sha256", domain="rtdl.goal5793.x1.external_review_result", version=2,
        ))
        self.assertFalse(any(result["authorization"].values()))
        self.assertEqual(result["claim_boundary"]["prospective_generality_exam_count"], 0)
        self.assertEqual(result["claim_boundary"]["usability_evidence_count"], 0)

    def test_correction_preserves_old_bytes_and_forbids_packet_delivery(self) -> None:
        docs = correction.build_documents()
        value = json.loads(docs[correction.CORRECTION_NAME])
        self.assertEqual(value["correction_sha256"], seal_document(
            value, seal_field="correction_sha256", domain="rtdl.goal5793.x1.single_cfr_delivery_correction", version=1,
        ))
        self.assertFalse(value["claim_or_authorization_changed"])
        self.assertFalse(value["authorization"]["packet_delivery"])
        self.assertTrue(value["controlling_successor"]["only_single_cfr_may_be_sent"])


if __name__ == "__main__":
    unittest.main()
