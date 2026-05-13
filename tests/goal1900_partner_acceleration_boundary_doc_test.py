from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "partner_acceleration_boundaries.md"
REPORT = ROOT / "docs" / "reports" / "goal1900_partner_acceleration_boundary_doc_2026-05-13.md"
README = ROOT / "README.md"
DOCS_README = ROOT / "docs" / "README.md"
TUTORIALS_README = ROOT / "docs" / "tutorials" / "README.md"


class Goal1900PartnerAccelerationBoundaryDocTest(unittest.TestCase):
    def test_doc_states_positive_and_negative_partner_acceleration_rules(self) -> None:
        text = DOC.read_text(encoding="utf-8")

        self.assertIn("RTDL accelerates the RTDL primitive call you explicitly make", text)
        self.assertIn("RTDL does not accelerate arbitrary PyTorch or CuPy programs", text)
        self.assertIn("Partner-Owned Columns Are Not Whole-Program Acceleration", text)
        self.assertIn("exact primitive", text)
        self.assertIn("exact backend", text)
        self.assertIn("exact partner", text)
        self.assertIn("reviewed artifact path", text)

    def test_doc_contains_blocked_wording_examples(self) -> None:
        text = DOC.read_text(encoding="utf-8")

        for phrase in (
            "RTDL accelerates arbitrary PyTorch code",
            "RTDL accelerates arbitrary CuPy code",
            "RTDL optimizes partner programs automatically",
            "RTDL makes whole applications faster by default",
            "RTDL provides broad RT-core acceleration for all partner workloads",
        ):
            self.assertIn(phrase, text)

    def test_report_keeps_release_blocked_until_review_and_linking(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: source-doc-ready-needs-external-review", text)
        self.assertIn("docs/partner_acceleration_boundaries.md", text)
        self.assertIn("does not accelerate arbitrary PyTorch or CuPy programs", text)
        self.assertIn("linked from the", text)
        self.assertIn("front-page README, docs index, and tutorial ladder", text)
        self.assertIn("still needs external", text)
        self.assertIn("v2.0 release readiness", text)

    def test_boundary_doc_is_linked_from_public_doc_path(self) -> None:
        self.assertIn("docs/partner_acceleration_boundaries.md", README.read_text(encoding="utf-8"))
        self.assertIn("partner_acceleration_boundaries.md", DOCS_README.read_text(encoding="utf-8"))
        self.assertIn("../partner_acceleration_boundaries.md", TUTORIALS_README.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
