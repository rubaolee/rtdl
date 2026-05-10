from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1244PublicDocSpineTest(unittest.TestCase):
    def test_public_doc_map_names_current_layers(self) -> None:
        text = (ROOT / "docs" / "public_documentation_map.md").read_text(encoding="utf-8")

        for phrase in (
            "Public Doc Layers",
            "Front page",
            "Tutorials",
            "Apps and examples",
            "Architecture and language",
            "Performance and boundaries",
            "History and evidence",
            "Technical App Notes",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_docs_index_routes_by_current_user_task(self) -> None:
        text = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")

        for phrase in (
            "## New User Path",
            "## Read By Task",
            "Run the first example",
            "Learn the kernel shape",
            "Pick an app demo",
            "Understand features",
            "Choose a backend",
            "Interpret benchmark results",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_history_index_exists_and_sets_boundary(self) -> None:
        text = (ROOT / "docs" / "history" / "README.md").read_text(encoding="utf-8")

        for phrase in (
            "RTDL History Index",
            "The main docs intentionally describe RTDL as the current product",
            "What Belongs Here",
            "Current Documentation Rule",
            "should not embed project-evolution narratives",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
