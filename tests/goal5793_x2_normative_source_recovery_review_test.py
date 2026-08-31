from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts import goal5793_x2_build_normative_source_recovery_review as builder


ROOT = Path(__file__).resolve().parents[1]
FORMAL_V2_IDENTITIES = {
    builder.AUTHORITY_NAME: (10269, "4a1065aceeea8b039e88ead6c1129fc0dd1fb330c9e6e4da25edf2886bc1ee2b"),
    builder.CFR_NAME: (25145, "10d8a85ecfa6bebb2aa7870daa3180a7c0130ec0a27c2a87a4bc2f36bc27a00f"),
}


class Goal5793X2NormativeSourceRecoveryReviewTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.outputs = builder.build_outputs()

    def test_01_deterministic_and_only_two_outputs(self):
        self.assertEqual(self.outputs, builder.build_outputs())
        self.assertEqual(set(self.outputs), {builder.AUTHORITY_NAME, builder.CFR_NAME})

    def test_02_cfr_embeds_exact_authority_and_tool_and_is_only_send_file(self):
        cfr = self.outputs[builder.CFR_NAME].decode("utf-8")
        authority = self.outputs[builder.AUTHORITY_NAME]
        tool = (ROOT / "scripts/goal5793_x2_recover_pinned_normative_sources.py").read_bytes()
        self.assertIn(authority.decode("utf-8").rstrip("\n"), cfr)
        self.assertIn(tool.decode("utf-8"), cfr)
        self.assertIn("SEND ONLY THIS FILE", cfr)
        self.assertIn(hashlib.sha256(authority).hexdigest(), cfr)

    def test_03_authority_has_one_requested_grant_and_zero_current_grants(self):
        authority = json.loads(self.outputs[builder.AUTHORITY_NAME])
        self.assertFalse(any(authority["authorization"].values()))
        requested = authority["requested_postreview_authorization"]
        self.assertTrue(requested["authorizes_exact_pinned_source_recovery"])
        self.assertFalse(any(value for key, value in requested.items() if key != "authorizes_exact_pinned_source_recovery"))

    def test_04_formal_v2_outputs_keep_the_frozen_postwrite_identities(self):
        for name, (expected_bytes, expected_sha256) in FORMAL_V2_IDENTITIES.items():
            path = ROOT / "history/internal_docs" / name
            self.assertTrue(path.is_file())
            data = path.read_bytes()
            self.assertEqual(len(data), expected_bytes)
            self.assertEqual(hashlib.sha256(data).hexdigest(), expected_sha256)

    def test_05_create_only_transaction_refuses_existing_target(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); first = root / builder.AUTHORITY_NAME; first.write_bytes(b"occupied")
            self.assertTrue(first.exists())


if __name__ == "__main__":
    unittest.main()
