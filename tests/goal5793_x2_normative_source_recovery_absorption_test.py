from __future__ import annotations

import json
import hashlib
from pathlib import Path
import tempfile
import unittest

from scripts import goal5793_x2_absorb_normative_source_recovery_review as builder
from scripts import goal5793_x2_recover_pinned_normative_sources as recovery


ROOT = Path(__file__).resolve().parents[1]
POSTWRITE_IDENTITIES = {
    builder.SEND_NAME: (1902, "d2c1e290877ebc5b648fb0e571a2bfe52ce223e8b61e4f54abb0e7b11976821c"),
    builder.V3_NAME: (3919, "1e0e28a5c9e234b9ac1113625227a6ec82af40cdaae63de2d3cce53588e5b721"),
    builder.ABSORPTION_NAME: (2320, "9000bf98a426881e6a2c29941f648e14a83d76be6ef7e2d5861eac8cd45b5e75"),
    builder.CLOSURE_NAME: (2336, "3aa86c3b2f6078ac63880b3ba36d64a2a32bca34ebe9af8a10c7754e25186b30"),
}


class Goal5793X2NormativeSourceRecoveryAbsorptionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.outputs = builder.build_outputs()

    def test_01_deterministic_four_file_append_only_transaction(self):
        self.assertEqual(self.outputs, builder.build_outputs())
        self.assertEqual(set(self.outputs), {builder.SEND_NAME, builder.V3_NAME, builder.ABSORPTION_NAME, builder.CLOSURE_NAME})

    def test_02_p1_is_closed_without_pin_edit_or_causal_claim(self):
        v3 = json.loads(self.outputs[builder.V3_NAME])
        self.assertTrue(v3["pin_provenance"]["provenance_unrecorded"])
        self.assertFalse(v3["mismatch_taxonomy"]["nist_changed_the_file_claimed"])
        self.assertFalse(v3["mismatch_taxonomy"]["pin_was_wrong_claimed"])
        self.assertIn("PIN_PROVENANCE_UNVERIFIED", v3["mismatch_taxonomy"]["controlling_governance_disposition"])
        self.assertEqual(v3["mismatch_taxonomy"]["classification_rules"]["mismatch_with_historical_fetch_provenance_unrecorded"], "TERMINAL_PIN_PROVENANCE_UNVERIFIED")
        self.assertFalse(v3["mismatch_taxonomy"]["classification_rules"]["terminal_source_drift_preconditions_satisfied_here"])
        self.assertEqual(v3["exact_pins_unchanged"], [{"source_id": row["source_id"], "bytes": row["bytes"], "sha256": row["sha256"]} for row in recovery.SOURCES])

    def test_03_closure_is_accepted_by_exact_reviewed_recovery_tool(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name, data in self.outputs.items(): (root / name).write_bytes(data)
            closure = json.loads(self.outputs[builder.CLOSURE_NAME])
            self.assertEqual(closure["closure_sha256"], recovery._seal(closure, "closure_sha256", recovery.CLOSURE_DOMAIN))
            validated = recovery.validate_authorities(ROOT / builder.V2_AUTHORITY, ROOT / builder.RETURNED_REVIEW, root / builder.CLOSURE_NAME)
            self.assertTrue(validated["closure"]["authorization"]["authorizes_exact_pinned_source_recovery"])

    def test_04_only_recovery_is_authorized(self):
        closure = json.loads(self.outputs[builder.CLOSURE_NAME])
        self.assertTrue(closure["authorization"]["authorizes_exact_pinned_source_recovery"])
        self.assertFalse(any(value for key, value in closure["authorization"].items() if key != "authorizes_exact_pinned_source_recovery"))

    def test_05_postwrite_outputs_are_exact_and_match_fresh_rebuild(self):
        for name, expected in POSTWRITE_IDENTITIES.items():
            payload = (ROOT / "history/internal_docs" / name).read_bytes()
            self.assertEqual((len(payload), hashlib.sha256(payload).hexdigest()), expected)
            self.assertEqual(payload, self.outputs[name])


if __name__ == "__main__":
    unittest.main()
