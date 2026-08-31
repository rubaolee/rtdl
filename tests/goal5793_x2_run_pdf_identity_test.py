from __future__ import annotations

import base64
import copy
from pathlib import Path
import unittest

from scripts import goal5793_x2_run_pdf_identity as runner


ROOT = Path(__file__).resolve().parents[1]
PDF = base64.b64decode((ROOT / "tests/fixtures/goal5793_x2_pdf/synthetic_identity.pdf.b64").read_text(encoding="ascii").strip(), validate=True)
COMPONENT = {
    "component_id": "doi:10.9999/goal5793.synthetic",
    "doi": ["10.9999/goal5793.synthetic"],
    "arxiv": ["2501.01234"],
    "title": ["synthetic hardware ray tracing work"],
    "first_author": ["smith"],
    "year": [2025],
}


class Goal5793X2RunPdfIdentityTest(unittest.TestCase):
    def test_01_fresh_isolated_child_returns_pinned_parser_receipt(self):
        result = runner.run_isolated_pdf_identity(PDF, COMPONENT)
        self.assertTrue(result["process"]["isolated_flag"])
        self.assertTrue(result["pdf_identity_receipt"]["identity_checks"]["matched"])
        self.assertEqual(result["pdf_identity_receipt"]["parser_authority"]["rows_sha256"], "3df52f80b93fbcb44dd793e0ba27ee2438ad7cf06de7ab355e1755c0078a9bd1")

    def test_02_identity_mismatch_is_preserved_not_replaced(self):
        component = copy.deepcopy(COMPONENT)
        component.update(doi=["10.9999/other"], arxiv=["2501.99999"], title=["other"], first_author=["jones"], year=[2024])
        result = runner.run_isolated_pdf_identity(PDF, component)
        self.assertFalse(result["pdf_identity_receipt"]["identity_checks"]["matched"])

    def test_03_malformed_pdf_fails_without_in_process_fallback(self):
        with self.assertRaisesRegex(RuntimeError, "PDF_CHILD_FAILED__NO_IN_PROCESS_FALLBACK"):
            runner.run_isolated_pdf_identity(b"not-pdf", COMPONENT)

    def test_04_timeout_parameter_is_bounded(self):
        with self.assertRaisesRegex(RuntimeError, "PDF_CHILD_TIMEOUT_INVALID"):
            runner.run_isolated_pdf_identity(PDF, COMPONENT, timeout_seconds=0)


if __name__ == "__main__":
    unittest.main()
