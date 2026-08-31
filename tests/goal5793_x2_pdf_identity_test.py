from __future__ import annotations

import base64
import copy
import hashlib
from pathlib import Path
import unittest

from scripts import goal5793_x2_pdf_identity as pdf_identity
from scripts.goal5793_x2_offline_core import X2Error


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/goal5793_x2_pdf/synthetic_identity.pdf.b64"
PDF_SHA256 = "c24e8553f80928f98c80c2c2f88c3dff2970adb264f95be1e731f0f55ae01189"


def _component():
    return {
        "doi": ["10.9999/goal5793.synthetic"], "arxiv": ["2501.01234"], "openalex": ["W123"],
        "title": ["synthetic hardware ray tracing work"], "first_author": ["smith"], "year": [2025],
    }


class Goal5793X2PdfIdentityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pdf = base64.b64decode(FIXTURE.read_text(encoding="ascii").strip(), validate=True)

    def test_01_fixed_pdf_and_parser_tree_are_exact(self):
        self.assertEqual(len(self.pdf), 1800)
        self.assertEqual(hashlib.sha256(self.pdf).hexdigest(), PDF_SHA256)
        authority = pdf_identity.parser_authority()
        self.assertEqual(authority["version"], "6.14.2")
        self.assertEqual(authority["file_count"], 56)
        self.assertEqual(authority["rows_sha256"], pdf_identity.PYPDF_ROWS_SHA256)

    def test_02_strong_and_fallback_identity_and_annotation_match(self):
        receipt = pdf_identity.extract_pdf_identity(self.pdf, _component())
        self.assertEqual(receipt["status"], "PDF_IDENTITY_MATCH")
        self.assertTrue(receipt["identity_checks"]["strong_identifier_match"])
        self.assertTrue(receipt["identity_checks"]["fallback_title_author_year_match"])
        self.assertEqual(receipt["extraction"]["observed_doi"], ["10.9999/goal5793.synthetic"])
        self.assertEqual(receipt["extraction"]["observed_arxiv"], ["2501.01234"])
        self.assertEqual(receipt["extraction"]["annotation_urls_in_object_order"], ["https://github.com/example/goal5793-synthetic"])

    def test_03_wrong_work_is_source_gap_not_manual_rescue(self):
        component = _component()
        component.update(doi=["10.9999/other"], arxiv=["2501.99999"], title=["Other Work"], first_author=["jones"], year=[2024])
        receipt = pdf_identity.extract_pdf_identity(self.pdf, component)
        self.assertFalse(receipt["identity_checks"]["matched"])
        self.assertFalse(receipt["manual_version_or_paper_choice_allowed"])

    def test_04_non_pdf_and_encrypted_or_parse_failure_fail_closed(self):
        with self.assertRaisesRegex(X2Error, "PDF_BYTES_INVALID_OR_LIMIT_EXCEEDED"):
            pdf_identity.extract_pdf_identity(b"not a pdf", _component())
        with self.assertRaisesRegex(X2Error, "PDF_PARSE_FAILED"):
            pdf_identity.extract_pdf_identity(b"%PDF-broken", _component())


if __name__ == "__main__":
    unittest.main()
