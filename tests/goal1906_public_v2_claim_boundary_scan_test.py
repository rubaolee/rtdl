from __future__ import annotations

import json
import pathlib
import tempfile
import unittest

from scripts.goal1906_public_v2_claim_boundary_scan import scan


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1906_public_v2_claim_boundary_scan_2026-05-13.md"


class Goal1906PublicV2ClaimBoundaryScanTest(unittest.TestCase):
    def test_current_public_docs_keep_sensitive_claims_negative(self) -> None:
        payload = scan(ROOT)

        self.assertEqual(payload["status"], "pass")
        self.assertFalse(payload["findings"])
        self.assertGreater(len(payload["accepted_negative_occurrences"]), 0)
        self.assertIn("README.md", payload["public_files_scanned"])
        self.assertIn("docs/partner_acceleration_boundaries.md", payload["public_files_scanned"])
        self.assertFalse(payload["claim_boundary"]["v2_0_release_authorized"])
        self.assertFalse(payload["claim_boundary"]["package_install_claim_authorized"])

    def test_positive_forbidden_wording_fails_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "docs/tutorials").mkdir(parents=True)
            (root / "docs/README.md").write_text("", encoding="utf-8")
            (root / "docs/partner_acceleration_boundaries.md").write_text("", encoding="utf-8")
            (root / "docs/tutorials/example.md").write_text("", encoding="utf-8")
            (root / "README.md").write_text(
                "RTDL v2.0 is ready and supports pip install from PyPI.\n",
                encoding="utf-8",
            )

            payload = scan(root)
            self.assertEqual(payload["status"], "fail")
            phrases = {finding["phrase"].lower() for finding in payload["findings"]}
            self.assertIn("v2.0 is ready", phrases)
            self.assertIn("pip install", phrases)
            self.assertIn("pypi", phrases)

    def test_report_documents_scope_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: active-local-gate", text)
        self.assertIn("README.md", text)
        self.assertIn("docs/tutorials/*.md", text)
        self.assertIn("package install", text)
        self.assertIn("arbitrary PyTorch/CuPy acceleration", text)
        self.assertIn("does not authorize v2.0 release", text)


if __name__ == "__main__":
    unittest.main()
