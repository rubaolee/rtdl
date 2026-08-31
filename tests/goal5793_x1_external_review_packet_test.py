from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest

from scripts import goal5793_x1_finalize_external_review as finalizer
from scripts import goal5793_x1_verify_external_review_packet as verifier
from scripts.goal5793_x1_canonical import canonical_json_bytes, seal_document


ROOT = Path(__file__).resolve().parents[1]


class Goal5793X1ExternalReviewPacketTest(unittest.TestCase):
    def test_fixed_markdown_documents_match_independent_pins(self) -> None:
        report, self_review, cfr = finalizer._markdown_documents()
        observed = {
            f"documents/{finalizer.REPORT_NAME}": report,
            f"documents/{finalizer.SELF_REVIEW_NAME}": self_review,
            f"ENTRYPOINT/{finalizer.CFR_NAME}": cfr,
        }
        owner = canonical_json_bytes(finalizer._owner_directive()) + b"\n"
        observed[f"documents/{finalizer.OWNER_NAME}"] = owner
        for name, payload in observed.items():
            expected_bytes, expected_sha = verifier.EXPECTED_DOCUMENTS[name]
            self.assertEqual(len(payload), expected_bytes)
            self.assertEqual(hashlib.sha256(payload).hexdigest(), expected_sha)

    def test_owner_record_is_sealed_and_grants_nothing(self) -> None:
        value = finalizer._owner_directive()
        self.assertEqual(
            value["record_sha256"],
            seal_document(value, seal_field="record_sha256",
                          domain="rtdl.goal5793.x1.owner_local_linux_directive_record", version=1),
        )
        self.assertFalse(any(value["authorization"].values()))
        self.assertEqual(value["implemented_interpretation"]["gpu_device_or_driver_api_call_count"], 0)

    def test_single_file_language_is_exact(self) -> None:
        _report, _self_review, cfr = finalizer._markdown_documents()
        text = cfr.decode("utf-8")
        self.assertEqual(text.count("SEND ONLY THE ENCLOSING"), 1)
        self.assertIn(finalizer.PACKET_NAME, text)
        self.assertIn("zero prospective Goal5793 exams", finalizer._markdown_documents()[0].decode("utf-8"))

    def test_pinned_survey_source_archive_is_exact(self) -> None:
        path = ROOT / "tmp/goal5793_survey_source_extract/goal5753/SELECTION_SOURCE/survey_source.tar"
        self.assertEqual(path.stat().st_size, 752766)
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),
                         "bfe852a1425b01b63ee0298f75646c824e9daf67429184211d446ba7f3643857")

    def test_path_validation_rejects_lexical_aliases(self) -> None:
        for name in ("", "/a", "a/", "a//b", "a/./b", "a/../b", "a\\b"):
            self.assertFalse(verifier._safe_name(name))


if __name__ == "__main__":
    unittest.main()
