from __future__ import annotations

import json
import unittest

from scripts import goal5793_x1_close_postreview as close
from scripts.goal5793_x1_canonical import seal_document


class Goal5793X1PostreviewClosureTest(unittest.TestCase):
    def setUp(self) -> None:
        self.docs = close.build_documents()

    def test_amendment_preserves_ordering_violation_and_future_invariant(self) -> None:
        value = json.loads(self.docs[close.AMENDMENT_NAME])
        self.assertTrue(value["admitted_facts"]["governance_ordering_violation_occurred"])
        self.assertFalse(value["admitted_facts"]["action_was_pre_authorized_by_s0_artifact"])
        self.assertFalse(value["one_time_disposition"]["retroactively_relabelled_as_pre_authorized"])
        self.assertFalse(value["permanent_future_invariants"]["goal5793_pod_or_ssh_allowed_ever"])
        self.assertFalse(value["authorization"]["authorizes_future_ssh_or_pod"])
        self.assertEqual(value["amendment_sha256"], seal_document(
            value, seal_field="amendment_sha256", domain="rtdl.goal5793.x1.governance_ordering_amendment", version=1,
        ))

    def test_absorption_keeps_both_p2_open_and_nonblocking(self) -> None:
        value = json.loads(self.docs[close.ABSORPTION_NAME])
        self.assertIn("OPEN_NONBLOCKING", value["finding_disposition"]["P2_1_single_self_contained_delivery"])
        self.assertIn("OPEN_NONBLOCKING", value["finding_disposition"]["P2_2_missing_strong_identifiers_179_of_186"])
        self.assertFalse(value["authorization"]["x2"])
        self.assertEqual(value["absorption_sha256"], seal_document(
            value, seal_field="absorption_sha256", domain="rtdl.goal5793.x1.owner_returned_external_review_absorption", version=1,
        ))

    def test_closure_only_unlocks_x2_offline(self) -> None:
        value = json.loads(self.docs[close.CLOSURE_NAME])
        self.assertTrue(value["x1_result"]["x1_complete"])
        self.assertEqual(value["closure_findings"]["conditional_p1_remaining_after_exact_amendment"], 0)
        self.assertTrue(value["authorization"]["authorizes_x2_offline_implementation"])
        true_keys = [key for key, enabled in value["authorization"].items() if enabled]
        self.assertEqual(true_keys, ["authorizes_x2_offline_implementation"])
        self.assertFalse(value["permanent_invariants"]["goal5793_pod_or_ssh_allowed_ever"])
        self.assertEqual(value["x1_result"]["prospective_generality_exam_count"], 0)
        self.assertEqual(value["x1_result"]["usability_evidence_count"], 0)
        self.assertEqual(value["closure_sha256"], seal_document(
            value, seal_field="closure_sha256", domain="rtdl.goal5793.x1.postreview_closure_and_x2_offline_entry", version=1,
        ))


if __name__ == "__main__":
    unittest.main()
