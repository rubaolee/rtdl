from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERSION = ROOT / "VERSION"
README = ROOT / "README.md"
DOCS_README = ROOT / "docs" / "README.md"
LEARN_README = ROOT / "docs" / "learn" / "README.md"
GLOSSARY = ROOT / "docs" / "versioning.md"
REPORT = ROOT / "docs" / "reports" / "goal4326_versioning_glossary_2026-06-11.md"


class Goal4326VersioningGlossaryTest(unittest.TestCase):
    def test_glossary_explains_current_and_internal_version_terms(self) -> None:
        text = GLOSSARY.read_text(encoding="utf-8")

        for phrase in (
            "`VERSION` file",
            "v2.10",
            "v2.11",
            "`v2_8` in Python constants or module names",
            "`goalNNNN`",
            "not a product version",
            "does not authorize",
        ):
            self.assertIn(phrase, text)

    def test_version_marker_stays_current_public_milestone(self) -> None:
        self.assertEqual(VERSION.read_text(encoding="utf-8").strip(), "v2.10")

    def test_front_doors_link_to_glossary(self) -> None:
        for path in (README, DOCS_README, LEARN_README):
            text = path.read_text(encoding="utf-8")
            self.assertIn("versioning.md", text)

    def test_report_documents_scope_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal4326",
            "versioning glossary",
            "does not bump `VERSION`",
            "does not authorize",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
