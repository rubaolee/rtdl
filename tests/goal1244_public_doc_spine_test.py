from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1244PublicDocSpineTest(unittest.TestCase):
    def test_public_doc_map_names_the_four_current_surfaces(self) -> None:
        text = (ROOT / "docs" / "public_documentation_map.md").read_text(encoding="utf-8")

        for phrase in (
            "Current Public Surfaces",
            "Front page",
            "Tutorials",
            "Apps and examples",
            "Architecture, model, IR, and performance",
            "Use this table before opening historical reports",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_docs_index_routes_by_surface(self) -> None:
        text = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")

        for phrase in (
            "Public Surfaces",
            "What RTDL is, what the current release is, and what not to overclaim.",
            "How to run a first kernel and learn the authoring shape.",
            "Which apps exist, what RTDL accelerates, and which app phases remain outside.",
            "How the runtime is structured, how lowering works, and how to read evidence.",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_architecture_and_app_quickstart_explain_v1_5_customization_boundary(self) -> None:
        arch = (ROOT / "docs" / "current_architecture.md").read_text(encoding="utf-8")
        quickstart = (ROOT / "docs" / "app_example_quickstart.md").read_text(encoding="utf-8")

        for phrase in (
            "## v1.5 Lens",
            "v1.5 is the current release line",
            "Some app paths use app-specific native continuations",
            "not the final engine architecture",
            "not yet a zero-app-knowledge native",
            "v2.0 is the broader end-to-end performance target",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, arch)

        for phrase in (
            "## Engine Customization Boundary",
            "v1.0 includes app-specific native continuations",
            "intentional proof machinery",
            "the authoritative per-app list",
            "whether public RTX wording is reviewed, blocked, not reviewed, or not a NVIDIA target",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, quickstart)


if __name__ == "__main__":
    unittest.main()
